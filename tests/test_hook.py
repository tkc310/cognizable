"""skills/cognizable/hooks/cognizable_hook.py のテスト。"""

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "skills" / "cognizable" / "hooks" / "cognizable_hook.py"
spec = importlib.util.spec_from_file_location("cognizable_hook", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


class QuestionTest(unittest.TestCase):
    def test_questions(self):
        for prompt in ("hooks について説明して", "質問です。R5 の上限は?", "これはどういう意味？", "説明してください"):
            self.assertTrue(hook.is_question(prompt), prompt)

    def test_change_requests(self):
        for prompt in ("README を修正して", "説明して、そのあと README に追加して", "テストを足して", "直せますか？修正をお願い", ""):
            self.assertFalse(hook.is_question(prompt), prompt)


class FlagTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["COGNIZABLE_HOOK_STATE_DIR"] = self.tmp.name

    def tearDown(self):
        del os.environ["COGNIZABLE_HOOK_STATE_DIR"]
        self.tmp.cleanup()

    def submit(self, prompt):
        return hook.on_user_prompt_submit({"session_id": "s", "prompt": prompt})

    def edit(self, tool="Edit"):
        return hook.on_pre_tool_use({"session_id": "s", "tool_name": tool})

    def test_context_always_points_to_skill(self):
        context = self.submit("README を修正して")["hookSpecificOutput"]["additionalContext"]
        self.assertIn(str(hook.SKILL_PATH), context)
        self.assertIn("日本語", context)
        self.assertNotIn("質問", context)

    def test_question_blocks_edits_until_next_prompt(self):
        context = self.submit("説明して")["hookSpecificOutput"]["additionalContext"]
        self.assertIn("質問", context)
        self.assertEqual(self.edit()["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIsNone(self.edit("Read"))
        self.assertEqual(self.edit("apply_patch")["hookSpecificOutput"]["permissionDecision"], "deny")
        self.submit("では修正して")
        self.assertIsNone(self.edit())

    def test_cursor_conversation_id(self):
        hook.on_user_prompt_submit({"conversation_id": "c", "prompt": "説明して"})
        result = hook.on_pre_tool_use({"conversation_id": "c", "tool_name": "Write"})
        self.assertEqual(result["hookSpecificOutput"]["permissionDecision"], "deny")


class EnglishTest(unittest.TestCase):
    def test_counts_only_prose_outside_code(self):
        text = "\n".join([
            "結論: 3つのフックを足した。",
            "This line is English prose.",
            "`scripts/check.py` を実行する。",
            "https://example.com/a/b/c",
            "```",
            "print('this is code and not counted')",
            "```",
            "Another English line here.",
        ])
        self.assertEqual(hook.count_english_lines(text), 2)

    def test_stop_blocks_three_lines_once(self):
        text = "One English line here.\nTwo English line here.\nThree English line here."
        result = hook.on_stop({"last_assistant_message": text})
        self.assertEqual(result["decision"], "block")
        self.assertIsNone(hook.on_stop({"last_assistant_message": text, "stop_hook_active": True}))
        self.assertIsNone(hook.on_stop({"last_assistant_message": text, "loop_count": 1}))
        self.assertIsNone(hook.on_stop({"last_assistant_message": "日本語だけの回答。"}))

    def test_reads_last_reply_from_transcript(self):
        entries = [
            {"type": "user", "message": {"content": "最初の質問"}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Old English reply line."}]}},
            {"type": "user", "message": {"content": "次の質問"}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read"}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "新しい回答。"}]}},
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write("\n".join(json.dumps(e, ensure_ascii=False) for e in entries))
        try:
            self.assertEqual(hook.last_reply_text(f.name), "新しい回答。")
        finally:
            os.unlink(f.name)


class OtherAgentsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["COGNIZABLE_HOOK_STATE_DIR"] = self.tmp.name

    def tearDown(self):
        del os.environ["COGNIZABLE_HOOK_STATE_DIR"]
        self.tmp.cleanup()

    ENGLISH = "One English line here.\nTwo English line here.\nThree English line here."

    def test_gemini(self):
        out = hook.on_gemini_before_agent({"session_id": "g", "prompt": "説明して"})
        self.assertIn("質問", out["hookSpecificOutput"]["additionalContext"])
        self.assertEqual(hook.on_gemini_before_tool({"session_id": "g", "tool_name": "write_file"})["decision"], "deny")
        self.assertEqual(hook.on_gemini_after_agent({"prompt_response": self.ENGLISH})["decision"], "deny")
        self.assertIsNone(hook.on_gemini_after_agent({"prompt_response": self.ENGLISH, "stop_hook_active": True}))

    def test_antigravity_injects_only_on_first_invocation(self):
        out = hook.on_antigravity_pre_invocation({"conversationId": "a", "invocationNum": 0, "lastUserInput": "説明して"})
        self.assertIn("質問", out["injectSteps"][0]["systemMessage"]["systemMessage"])
        self.assertIsNone(hook.on_antigravity_pre_invocation({"conversationId": "a", "invocationNum": 1}))
        denied = hook.on_antigravity_pre_tool_use({"conversationId": "a", "toolCall": {"name": "replace_file_content"}})
        self.assertEqual(denied["decision"], "deny")

    def test_antigravity_stop_retries_once_per_input(self):
        entries = [
            {"role": "user", "content": "質問です"},
            {"role": "tool", "content": self.ENGLISH},
            {"role": "model", "content": self.ENGLISH},
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            f.write("\n".join(json.dumps(e, ensure_ascii=False) for e in entries))
        data = {"conversationId": "a", "fullyIdle": True, "terminationReason": "model_stop",
                "lastUserInput": "質問です", "transcriptPath": f.name}
        try:
            self.assertEqual(hook.antigravity_reply_text(f.name, "質問です"), self.ENGLISH)
            self.assertEqual(hook.on_antigravity_stop(data)["decision"], "continue")
            self.assertIsNone(hook.on_antigravity_stop(data))
        finally:
            os.unlink(f.name)

    def test_unknown_transcript_does_nothing(self):
        data = {"conversationId": "b", "fullyIdle": True, "lastUserInput": "x", "transcriptPath": "/nonexistent"}
        self.assertIsNone(hook.on_antigravity_stop(data))


if __name__ == "__main__":
    unittest.main()
