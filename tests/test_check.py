import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import check  # noqa: E402

SKILL_OK = """---
name: cognizable
description: 'テスト用の説明'
metadata:
  version: "0.1.0"
---

# cognizable

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
        problems, _ = check.check_skill("# cognizable\n")
        self.assertEqual(problems, ["SKILL.md: frontmatter がない"])

    def test_wrong_name(self):
        problems, _ = check.check_skill(SKILL_OK.replace("name: cognizable", "name: other"))
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


HTML_OK = """<!doctype html>
<html lang="ja"><head><style>
:root { --measure: 36em; --leading: 1.75; --sem-now: #00f; --sem-act: #0aa; }
@media (prefers-reduced-motion: no-preference) { html { scroll-behavior: smooth; } }
</style></head><body>
<nav><ol><li><a href="#map">地図</a></li><li>1</li><li>2</li><li>3</li><li>4</li><li>5</li></ol>
<button id="expand-all">開く</button><select></select></nav>
<section id="map" data-layer="0"><ol><li>a</li><li>b</li><li>c</li></ol><br></section>
<section data-layer="1"><a href="#map">地図に戻る</a>
<ul><li>a</li><li>b</li><li>c</li><li>d</li></ul>
<details data-layer="2"><summary>一覧</summary>
<ul><li>1</li><li>2</li><li>3</li><li>4</li><li>5</li><li>6</li></ul></details>
</section>
</body></html>
"""


class CheckHtmlTest(unittest.TestCase):
    def assert_problem(self, text, fragment):
        problems = check.check_html(text)
        self.assertTrue(any(fragment in p for p in problems), problems)

    def test_valid_html_has_no_problems(self):
        self.assertEqual(check.check_html(HTML_OK), [])

    def test_measure_too_wide(self):
        self.assert_problem(HTML_OK.replace("--measure: 36em", "--measure: 48em"), "D1")

    def test_measure_missing(self):
        self.assert_problem(HTML_OK.replace("--measure: 36em;", ""), "--measure")

    def test_leading_too_small(self):
        self.assert_problem(HTML_OK.replace("--leading: 1.75", "--leading: 1.2"), "D2")

    def test_too_many_semantic_colors(self):
        extra = "--sem-a: #111; --sem-b: #222; --sem-c: #333; --sem-now"
        self.assert_problem(HTML_OK.replace("--sem-now", extra, 1), "D5")

    def test_justify_is_forbidden(self):
        self.assert_problem(HTML_OK.replace("</style>", "p { text-align: justify; }</style>"), "両端揃え")

    def test_autoplay_is_forbidden(self):
        self.assert_problem(HTML_OK.replace("<br>", "<video autoplay></video>"), "autoplay")

    def test_motion_needs_reduced_motion(self):
        text = HTML_OK.replace("@media (prefers-reduced-motion: no-preference) ", "@media screen ")
        self.assert_problem(text, "prefers-reduced-motion")

    def test_layer0_is_required(self):
        self.assert_problem(HTML_OK.replace(' data-layer="0"', ""), "L0")

    def test_layer0_must_not_be_folded(self):
        text = HTML_OK.replace('<section id="map" data-layer="0">', '<details><summary>s</summary><section id="map" data-layer="0">')
        text = text.replace("<br></section>", "<br></section></details>")
        self.assert_problem(text, "L0 を折りたたみ")

    def test_too_many_l1_blocks(self):
        block = '<section data-layer="1"><a href="#map">戻る</a></section>'
        self.assert_problem(HTML_OK.replace("</body>", block * 4 + "</body>"), "L1 のブロック")

    def test_l1_needs_back_link(self):
        self.assert_problem(HTML_OK.replace('<a href="#map">地図に戻る</a>', ""), "地図に戻るリンク")

    def test_long_visible_list(self):
        self.assert_problem(HTML_OK.replace("<li>d</li>", "<li>d</li><li>e</li>"), "R5")

    def test_long_list_inside_details_is_allowed(self):
        self.assertEqual(check.check_html(HTML_OK.replace("<li>6</li>", "<li>6</li><li>7</li>")), [])

    def test_details_needs_summary(self):
        self.assert_problem(HTML_OK.replace("<summary>一覧</summary>", ""), "summary")

    def test_nav_is_required(self):
        text = HTML_OK.replace("<nav>", "<div>").replace("</nav>", "</div>")
        self.assert_problem(text, "D9")

    def test_expand_all_is_required(self):
        self.assert_problem(HTML_OK.replace(' id="expand-all"', ""), "expand-all")

    def test_too_many_settings(self):
        self.assert_problem(HTML_OK.replace("<select></select>", "<select></select>" * 5), "D13")


class CheckReferencesTest(unittest.TestCase):
    def test_missing_reference_in_skill_text(self):
        problems = check.check_references("references/transform.md だけを指す")
        self.assertTrue(any("references/design.md への参照がない" in p for p in problems))

    def test_missing_file(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            problems = check.check_references(" ".join(check.REFERENCES), Path(tmp))
        self.assertEqual(len(problems), len(check.REFERENCES))


COMPANION_OK = """---
name: cog-demo
description: 'テスト用の説明'
---

# cog-demo

出力には `cognizable/SKILL.md` の決まりを適用する。ひな形は `assets/page.html`。
"""


class CheckCompanionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "cog-demo"
        (self.dir / "assets").mkdir(parents=True)
        (self.dir / "assets" / "page.html").write_text("", encoding="utf-8")

    def test_valid_companion_has_no_problems(self):
        self.assertEqual(check.check_companion(COMPANION_OK, self.dir), [])

    def test_name_must_match_directory(self):
        problems = check.check_companion(COMPANION_OK.replace("name: cog-demo", "name: other"), self.dir)
        self.assertTrue(any("name" in p for p in problems))

    def test_must_apply_cognizable(self):
        problems = check.check_companion(COMPANION_OK.replace("cognizable/SKILL.md", "別の決まり"), self.dir)
        self.assertTrue(any("cognizable を適用する指定" in p for p in problems))

    def test_linked_file_must_exist(self):
        (self.dir / "assets" / "page.html").unlink()
        problems = check.check_companion(COMPANION_OK, self.dir)
        self.assertTrue(any("assets/page.html: ファイルがない" in p for p in problems))

    def test_companion_dirs_skip_cognizable(self):
        root = Path(self.tmp.name)
        (root / "cognizable").mkdir()
        self.assertEqual([d.name for d in check.companion_dirs(root)], ["cog-demo"])


class CheckDesignTest(unittest.TestCase):
    PAGE = "<style>:root { --measure: 36em; --leading: 1.75; }</style><main></main>"

    def test_page_without_layers_passes_design_check(self):
        self.assertEqual(check.check_design(self.PAGE), [])

    def test_page_without_layers_fails_structure_check(self):
        self.assertTrue(any("L0" in p for p in check.check_html(self.PAGE)))

    def test_design_check_catches_wide_measure(self):
        self.assertTrue(any("D1" in p for p in check.check_design(self.PAGE.replace("36em", "60em"))))


class MainTest(unittest.TestCase):
    def test_html_argument_checks_the_file(self):
        self.assertEqual(check.main([str(check.TEMPLATE_PATH)]), 0)

    def test_missing_html_file_fails(self):
        self.assertEqual(check.main(["no-such-file.html"]), 1)


class RepositoryTest(unittest.TestCase):
    """リポジトリにある実ファイルが検査を通ることを確かめる。"""

    def test_repository_files_pass(self):
        skill_text = check.SKILL_PATH.read_text(encoding="utf-8")
        problems, ids = check.check_skill(skill_text)
        problems += check.check_log(check.LOG_PATH.read_text(encoding="utf-8"), ids)
        problems += check.check_references(skill_text)
        problems += check.check_html(check.TEMPLATE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
