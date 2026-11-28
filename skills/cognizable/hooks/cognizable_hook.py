#!/usr/bin/env python3
"""cognizable のフック。Claude Code、Codex、Cursor、Gemini CLI、Antigravity CLI で使う。

1つのスクリプトで3つの働きを扱う。Claude Code、Codex、Cursor、Gemini CLI では、
イベントを標準入力の JSON の hook_event_name で見分ける。Antigravity CLI は
イベント名を渡さないため、引数で `antigravity:イベント名` を渡す。

Claude Code のイベント名で書く。他のツールの対応するイベントは HANDLERS にある。

- UserPromptSubmit: 応答に cognizable を適用し、日本語で答える指示を足す。
  依頼が質問なら、ファイルを変更せずに答えだけ返す指示も足し、印を残す。
- PreToolUse: 質問の印が残っている間は、ファイルを変更するツールを止める。
- Stop: 最後の応答に英文が3行以上あれば、日本語に直して答え直させる。

標準ライブラリだけを使う。フックが失敗しても会話を止めないよう、
想定外の入力では何も出力せずに終わる。
"""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path

SKILL_PATH = Path(__file__).resolve().parent.parent / "SKILL.md"

# 英文と数える行の数の下限。依頼の目安「3行以上の英文」に合わせる。
ENGLISH_LINE_LIMIT = 3

# 英文の行とみなす、英単語の数の下限。識別子1つだけの行を数えないため。
ENGLISH_WORDS_PER_LINE = 3

# 質問とみなす語句。
QUESTION_PATTERNS = (
    r"説明して",
    r"質問です",
    r"質問があ",
    r"教えて",
    r"とは何",
    r"とは\s*[?？]",
    r"どういう(こと|意味)",
    r"なぜ",
    r"どうして",
    r"知りたい",
    r"[?？]\s*$",
)

# 変更を頼む語句。質問の語句と一緒にあれば、変更の依頼として扱う。
CHANGE_PATTERNS = (
    r"修正して",
    r"直して",
    r"変更して",
    r"追加して",
    r"足して",
    r"書いて",
    r"書き換えて",
    r"作って",
    r"作成して",
    r"実装して",
    r"削除して",
    r"消して",
    r"更新して",
    r"反映して",
    r"コミットして",
    r"(修正|変更|追加|実装|削除|作成|更新|反映|編集)(を)?(お願い|でき|して|する)",
)

# 質問の間に止めるツール。
# apply_patch は Codex、write_file と replace は Gemini CLI、*_file_content と
# write_to_file は Antigravity CLI のファイル編集。Cursor は Edit を Write として渡す。
EDIT_TOOLS = (
    "Edit", "Write", "MultiEdit", "NotebookEdit",
    "apply_patch",
    "write_file", "replace",
    "write_to_file", "replace_file_content", "multi_replace_file_content",
)

DENY_REASON = (
    "[cognizable フック] この依頼は質問なので、ファイルを変更しない。"
    "回答だけを返す。変更が必要なら、案を回答に書いて読み手の依頼を待つ。"
)

JAPANESE_CHAR = re.compile(r"[぀-ヿ㐀-鿿ｦ-ﾟ]")
ENGLISH_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]+")
INLINE_CODE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+")
PATH_LIKE = re.compile(r"\S*[/\\]\S*")


def is_question(prompt: str) -> bool:
    """依頼が、変更を伴わない質問かを返す。"""
    text = prompt.strip()
    if not text:
        return False
    if any(re.search(p, text, re.MULTILINE) for p in CHANGE_PATTERNS):
        return False
    return any(re.search(p, text, re.MULTILINE) for p in QUESTION_PATTERNS)


def state_dir() -> Path:
    base = os.environ.get("COGNIZABLE_HOOK_STATE_DIR") or os.path.join(
        tempfile.gettempdir(), "cognizable-hooks"
    )
    return Path(base)


def session_key(data: dict) -> str:
    """会話を見分ける値を返す。Cursor と Antigravity CLI は session_id を渡さない。"""
    return str(
        data.get("session_id") or data.get("conversation_id") or data.get("conversationId") or ""
    )


def flag_path(session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id or "default")
    return state_dir() / f"{safe}.question"


def build_context(question: bool) -> str:
    lines = [
        "[cognizable フック] この応答に cognizable を適用する。",
        f"- ルールは {SKILL_PATH} の R1〜R19。このセッションでまだ読んでいなければ、答える前に読む。",
        "- 回答の自然言語は日本語で書く。英語の資料やツールの出力を引くときも、地の文は日本語に直す。コード、コマンド、識別子はそのままでよい。",
    ]
    if question:
        lines.append(
            "- この依頼は質問。ドキュメント、ソースコード、文章のファイルを変更せず、回答だけを返す。"
            "変更したほうがよいと考えたら、変更の案を回答の中に書き、読み手の依頼を待つ。"
        )
    return "\n".join(lines)


def record_prompt(key: str, prompt: str) -> bool:
    """依頼が質問かを判定し、質問なら印を残す。質問でなければ印を消す。"""
    question = is_question(prompt)
    flag = flag_path(key)
    try:
        if question:
            flag.parent.mkdir(parents=True, exist_ok=True)
            flag.write_text("question\n", encoding="utf-8")
        elif flag.exists():
            flag.unlink()
    except OSError:
        pass
    return question


def edit_blocked(key: str, tool_name: object) -> bool:
    """質問の印が残っている間の、ファイルを変更するツールかを返す。"""
    return tool_name in EDIT_TOOLS and flag_path(key).exists()


def on_user_prompt_submit(data: dict) -> dict:
    question = record_prompt(session_key(data), str(data.get("prompt", "")))
    return {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": build_context(question),
        }
    }


def on_pre_tool_use(data: dict) -> dict | None:
    if not edit_blocked(session_key(data), data.get("tool_name")):
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": DENY_REASON,
        }
    }


def is_english_line(line: str) -> bool:
    """地の文が英文の行かを返す。日本語の文字を含む行は英文と数えない。"""
    text = URL.sub(" ", INLINE_CODE.sub(" ", line))
    text = PATH_LIKE.sub(" ", text)
    if JAPANESE_CHAR.search(text):
        return False
    return len(ENGLISH_WORD.findall(text)) >= ENGLISH_WORDS_PER_LINE


def count_english_lines(text: str) -> int:
    """コードブロックの外にある、英文の行を数える。"""
    count = 0
    in_code = False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_code = not in_code
            continue
        if in_code or line.startswith(("    ", "\t")):
            continue
        if is_english_line(line):
            count += 1
    return count


def _is_human_turn(entry: dict) -> bool:
    if entry.get("type") != "user":
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, str):
        return True
    if isinstance(content, list):
        return not any(
            isinstance(block, dict) and block.get("type") == "tool_result" for block in content
        )
    return False


def last_reply_text(transcript_path: str) -> str:
    """最後の人の発言より後の、エージェントの地の文をつなげて返す。"""
    try:
        raw = Path(transcript_path).read_text(encoding="utf-8")
    except (OSError, TypeError):
        return ""
    texts: list[str] = []
    for line in raw.splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        if _is_human_turn(entry):
            texts = []
            continue
        if entry.get("type") != "assistant":
            continue
        content = (entry.get("message") or {}).get("content")
        if isinstance(content, str):
            texts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    texts.append(str(block.get("text", "")))
    return "\n".join(texts)


def on_stop(data: dict) -> dict | None:
    # 答え直しの後にもう一度止めると、終わらなくなる。1回だけ止める。
    # Cursor は stop_hook_active の代わりに loop_count を渡す。
    if data.get("stop_hook_active") or (data.get("loop_count") or 0) > 0:
        return None
    text = data.get("last_assistant_message")
    if not isinstance(text, str):
        text = last_reply_text(str(data.get("transcript_path", "")))
    reason = retry_reason(text)
    return None if reason is None else {"decision": "block", "reason": reason}


def retry_reason(text: str) -> str | None:
    """英文が上限を超えていれば答え直しの理由を、超えていなければ None を返す。"""
    lines = count_english_lines(text)
    if lines < ENGLISH_LINE_LIMIT:
        return None
    return (
        f"[cognizable フック] 回答に英文の行が {lines} 行ある（上限は {ENGLISH_LINE_LIMIT - 1} 行）。"
        "地の文を日本語に直して、回答を書き直す。コード、コマンド、識別子はそのままでよい。"
    )


# --- Gemini CLI: BeforeAgent、BeforeTool、AfterAgent ---


def on_gemini_before_agent(data: dict) -> dict:
    question = record_prompt(session_key(data), str(data.get("prompt", "")))
    return {
        "hookSpecificOutput": {
            "hookEventName": "BeforeAgent",
            "additionalContext": build_context(question),
        }
    }


def on_gemini_before_tool(data: dict) -> dict | None:
    if not edit_blocked(session_key(data), data.get("tool_name")):
        return None
    return {"decision": "deny", "reason": DENY_REASON}


def on_gemini_after_agent(data: dict) -> dict | None:
    if data.get("stop_hook_active"):
        return None
    reason = retry_reason(str(data.get("prompt_response") or ""))
    return None if reason is None else {"decision": "deny", "reason": reason}


# --- Antigravity CLI: PreInvocation、PreToolUse、Stop ---
# イベント名が入力にないため、hooks.json で `antigravity:イベント名` を引数に渡す。

# 応答を書いた主体とみなす、transcript の type、role、source の値に含まれる語。
ANTIGRAVITY_REPLY_ROLES = ("model", "assistant", "agent", "planner")


def on_antigravity_pre_invocation(data: dict) -> dict | None:
    # PreInvocation はモデルを呼ぶたびに動く。注入した指示は会話に残るため、
    # 依頼ごとの最初の呼び出し（invocationNum が 0）でだけ注入する。
    if (data.get("invocationNum") or 0) != 0:
        return None
    question = record_prompt(session_key(data), str(data.get("lastUserInput") or ""))
    return {"injectSteps": [{"systemMessage": {"systemMessage": build_context(question)}}]}


def on_antigravity_pre_tool_use(data: dict) -> dict | None:
    tool = (data.get("toolCall") or {}).get("name")
    if not edit_blocked(session_key(data), tool):
        return None
    return {"decision": "deny", "reason": DENY_REASON}


def _collect_reply_text(entry: object, out: list[str], in_reply: bool = False) -> None:
    if isinstance(entry, dict):
        role = " ".join(
            str(entry.get(k, "")) for k in ("type", "role", "source")
        ).lower()
        here = in_reply or (
            any(r in role for r in ANTIGRAVITY_REPLY_ROLES) and "tool" not in role
        )
        for key, value in entry.items():
            if here and key in ("text", "content", "response") and isinstance(value, str):
                out.append(value)
            else:
                _collect_reply_text(value, out, here)
    elif isinstance(entry, list):
        for item in entry:
            _collect_reply_text(item, out, in_reply)


def antigravity_reply_text(transcript_path: str, last_input: str) -> str:
    """最後の依頼より後の、エージェントの地の文を返す。

    Antigravity CLI は transcript の形式を公開していない。読めない形式なら空文字を返し、
    答え直しをさせない。
    """
    try:
        raw = Path(transcript_path).read_text(encoding="utf-8")
    except (OSError, TypeError):
        return ""
    texts: list[str] = []
    for line in raw.splitlines():
        if last_input and last_input in line:
            texts = []
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        _collect_reply_text(entry, texts)
    return "\n".join(texts)


def on_antigravity_stop(data: dict) -> dict | None:
    if not data.get("fullyIdle") or data.get("terminationReason") not in (None, "model_stop"):
        return None
    # Antigravity CLI には stop_hook_active に当たる値がない。同じ依頼で答え直させるのは
    # 1回だけにするため、答え直させた依頼を印として残す。
    last_input = str(data.get("lastUserInput") or "")
    mark = flag_path(session_key(data)).with_suffix(".retried")
    try:
        if mark.read_text(encoding="utf-8") == last_input:
            return None
    except OSError:
        pass
    text = antigravity_reply_text(str(data.get("transcriptPath") or ""), last_input)
    reason = retry_reason(text)
    if reason is None:
        return None
    try:
        mark.parent.mkdir(parents=True, exist_ok=True)
        mark.write_text(last_input, encoding="utf-8")
    except OSError:
        return None
    return {"decision": "continue", "reason": reason}


HANDLERS = {
    # Claude Code、Codex、Cursor（Cursor は Claude Code の設定を取り込む）
    "UserPromptSubmit": on_user_prompt_submit,
    "PreToolUse": on_pre_tool_use,
    "Stop": on_stop,
    # Gemini CLI
    "BeforeAgent": on_gemini_before_agent,
    "BeforeTool": on_gemini_before_tool,
    "AfterAgent": on_gemini_after_agent,
    # Antigravity CLI（引数で渡す）
    "antigravity:PreInvocation": on_antigravity_pre_invocation,
    "antigravity:PreToolUse": on_antigravity_pre_tool_use,
    "antigravity:Stop": on_antigravity_stop,
}


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(data, dict):
        return 0
    event = sys.argv[1] if len(sys.argv) > 1 else str(data.get("hook_event_name", ""))
    handler = HANDLERS.get(event)
    if handler is None:
        return 0
    result = handler(data)
    if result is not None:
        json.dump(result, sys.stdout, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
