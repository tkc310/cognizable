"""sharpen スキルとフィードバックログの形式を検査する。

使い方: python3 scripts/check.py
問題がなければ終了コード 0、あれば問題を1行ずつ出して終了コード 1 を返す。
"""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / "skills" / "sharpen" / "SKILL.md"
LOG_PATH = ROOT / "feedback" / "log.md"

DESCRIPTION_MAX = 1024
RULE_HEADING = re.compile(r"^### (R\d+)\. (.+)$", re.MULTILINE)
ENTRY_HEADING = re.compile(r"^## (\d{4}-\d{2}-\d{2}) (.+)$", re.MULTILINE)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FIELD_LINE = re.compile(r"^- ([^:：]+)[:：]\s*(.*)$")
REQUIRED_FIELDS = ("ルール", "場面", "困ったこと", "直した方向", "状態")
STATUSES = {"未対応", "反映済み", "見送り"}
NEW_RULE = "新規"


def parse_frontmatter(text: str) -> dict[str, str]:
    """先頭の --- で囲まれた部分から、トップレベルの key: value を取り出す。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter がない")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("frontmatter が閉じていない") from exc

    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if not line or line.startswith((" ", "\t")):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            continue
        fields[key.strip()] = value.strip().strip("'\"")
    return fields


def rule_sections(text: str) -> list[tuple[str, str]]:
    """(ルール ID, 本文) の組を、SKILL.md に出てくる順に返す。"""
    matches = list(RULE_HEADING.finditer(text))
    sections = []
    for i, match in enumerate(matches):
        start = match.end()
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            next_h2 = text.find("\n## ", start)
            end = next_h2 if next_h2 != -1 else len(text)
        sections.append((match.group(1), text[start:end]))
    return sections


def check_skill(text: str, dir_name: str = "sharpen") -> tuple[list[str], set[str]]:
    """SKILL.md を検査し、(問題の一覧, ルール ID の集合) を返す。"""
    problems: list[str] = []

    try:
        fm = parse_frontmatter(text)
    except ValueError as exc:
        return [f"SKILL.md: {exc}"], set()

    if fm.get("name") != dir_name:
        problems.append(f"SKILL.md: name が {dir_name!r} ではない（{fm.get('name')!r}）")
    description = fm.get("description", "")
    if not description:
        problems.append("SKILL.md: description がない")
    elif len(description) > DESCRIPTION_MAX:
        problems.append(f"SKILL.md: description が {DESCRIPTION_MAX} 文字を超えている（{len(description)} 文字）")
    if "<" in description or ">" in description:
        problems.append("SKILL.md: description に山かっこを使っている")

    sections = rule_sections(text)
    if not sections:
        problems.append("SKILL.md: ルール（### R1. 〜）が1つもない")

    ids = [rule_id for rule_id, _ in sections]
    expected = [f"R{n}" for n in range(1, len(ids) + 1)]
    if ids != expected:
        problems.append(f"SKILL.md: ルール ID が R1 からの連番になっていない（{', '.join(ids)}）")

    for rule_id, body in sections:
        for label in ("悪い例", "良い例"):
            if label not in body:
                problems.append(f"SKILL.md: {rule_id} に「{label}」がない")

    return problems, set(ids)


def check_log(text: str, rule_ids: set[str]) -> list[str]:
    """feedback/log.md の各記録を検査する。"""
    problems: list[str] = []
    text = HTML_COMMENT.sub("", text)
    matches = list(ENTRY_HEADING.finditer(text))

    for i, match in enumerate(matches):
        date_str, title = match.group(1), match.group(2)
        where = f"feedback/log.md「{date_str} {title}」"
        try:
            datetime.date.fromisoformat(date_str)
        except ValueError:
            problems.append(f"{where}: 日付が正しくない")

        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        fields: dict[str, str] = {}
        for line in text[match.end():end].splitlines():
            field = FIELD_LINE.match(line.strip())
            if field:
                fields[field.group(1).strip()] = field.group(2).strip()

        for name in REQUIRED_FIELDS:
            if not fields.get(name):
                problems.append(f"{where}: 「{name}」がない")

        rules = fields.get("ルール")
        if rules:
            for rule in re.split(r"[,、\s]+", rules):
                if rule and rule != NEW_RULE and rule not in rule_ids:
                    problems.append(f"{where}: ルール {rule} は SKILL.md にない")

        status = fields.get("状態")
        if status and status not in STATUSES:
            problems.append(f"{where}: 状態「{status}」は {'、'.join(sorted(STATUSES))} のどれでもない")

    return problems


def main() -> int:
    problems, rule_ids = check_skill(SKILL_PATH.read_text(encoding="utf-8"))
    problems += check_log(LOG_PATH.read_text(encoding="utf-8"), rule_ids)
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(f"OK: ルール {len(rule_ids)} 件、フィードバックログに問題なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())
