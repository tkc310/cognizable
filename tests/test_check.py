import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check  # noqa: E402

SKILL_OK = """---
name: sharpen
description: 'テスト用の説明'
metadata:
  version: "0.1.0"
---

# sharpen

## ルール

### R1. 一つ目

- 悪い例: あ
- 良い例: い

### R2. 二つ目

- 悪い例: う
- 良い例: え

## 次の節

悪い例も良い例もここには書かない。
"""

ENTRY_OK = """# ログ

## 2026-11-27 見出し

- ルール: R1, 新規
- 場面: 場面の説明
- 困ったこと: 困ったこと
- 直した方向: 直した方向
- 状態: 未対応
"""


class CheckSkillTest(unittest.TestCase):
    def test_valid_skill_has_no_problems(self):
        problems, ids = check.check_skill(SKILL_OK)
        self.assertEqual(problems, [])
        self.assertEqual(ids, {"R1", "R2"})

    def test_missing_frontmatter(self):
        problems, _ = check.check_skill("# sharpen\n")
        self.assertEqual(problems, ["SKILL.md: frontmatter がない"])

    def test_wrong_name(self):
        problems, _ = check.check_skill(SKILL_OK.replace("name: sharpen", "name: other"))
        self.assertTrue(any("name" in p for p in problems))

    def test_description_too_long(self):
        text = SKILL_OK.replace("テスト用の説明", "あ" * (check.DESCRIPTION_MAX + 1))
        problems, _ = check.check_skill(text)
        self.assertTrue(any("文字を超えている" in p for p in problems))

    def test_rule_ids_must_be_sequential(self):
        problems, _ = check.check_skill(SKILL_OK.replace("### R2.", "### R3."))
        self.assertTrue(any("連番" in p for p in problems))

    def test_rule_needs_examples(self):
        text = SKILL_OK.replace("- 悪い例: う\n", "")
        problems, _ = check.check_skill(text)
        self.assertEqual(problems, ["SKILL.md: R2 に「悪い例」がない"])

    def test_last_rule_does_not_borrow_examples_from_next_section(self):
        text = SKILL_OK.replace("- 悪い例: う\n- 良い例: え\n", "")
        problems, _ = check.check_skill(text)
        self.assertIn("SKILL.md: R2 に「悪い例」がない", problems)
        self.assertIn("SKILL.md: R2 に「良い例」がない", problems)


class CheckLogTest(unittest.TestCase):
    ids = {"R1", "R2"}

    def test_valid_entry(self):
        self.assertEqual(check.check_log(ENTRY_OK, self.ids), [])

    def test_empty_log(self):
        self.assertEqual(check.check_log("# ログ\n", self.ids), [])

    def test_commented_example_is_ignored(self):
        text = "# ログ\n<!--\n## 2026-11-27 例\n\n- ルール: R99\n-->\n"
        self.assertEqual(check.check_log(text, self.ids), [])

    def test_missing_field(self):
        problems = check.check_log(ENTRY_OK.replace("- 場面: 場面の説明\n", ""), self.ids)
        self.assertEqual(len(problems), 1)
        self.assertIn("「場面」がない", problems[0])

    def test_unknown_rule(self):
        problems = check.check_log(ENTRY_OK.replace("R1, 新規", "R9"), self.ids)
        self.assertEqual(len(problems), 1)
        self.assertIn("R9", problems[0])

    def test_unknown_status(self):
        problems = check.check_log(ENTRY_OK.replace("未対応", "完了"), self.ids)
        self.assertEqual(len(problems), 1)
        self.assertIn("完了", problems[0])

    def test_invalid_date(self):
        problems = check.check_log(ENTRY_OK.replace("2026-11-27", "2026-13-01"), self.ids)
        self.assertEqual(len(problems), 1)
        self.assertIn("日付", problems[0])

    def test_full_width_colon_is_accepted(self):
        text = ENTRY_OK.replace("- 状態: 未対応", "- 状態：未対応")
        self.assertEqual(check.check_log(text, self.ids), [])


class RepositoryTest(unittest.TestCase):
    """リポジトリにある実ファイルが検査を通ることを確かめる。"""

    def test_repository_files_pass(self):
        skill_text = check.SKILL_PATH.read_text(encoding="utf-8")
        problems, ids = check.check_skill(skill_text)
        problems += check.check_log(check.LOG_PATH.read_text(encoding="utf-8"), ids)
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
