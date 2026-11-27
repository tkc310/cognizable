"""sharpen スキル、フィードバックログ、HTML の成果物の形式を検査する。

使い方:
  python3 scripts/check.py              スキル、ログ、ひな形を検査する
  python3 scripts/check.py 成果物.html  HTML の成果物を、デザイン規則と4層の構造で検査する

問題がなければ終了コード 0、あれば問題を1行ずつ出して終了コード 1 を返す。
"""

from __future__ import annotations

import datetime
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_PATH = ROOT / "skills" / "sharpen" / "SKILL.md"
LOG_PATH = ROOT / "feedback" / "log.md"
SKILL_DIR = SKILL_PATH.parent
TEMPLATE_PATH = SKILL_DIR / "assets" / "template.html"
REFERENCES = ("references/transform.md", "references/design.md", "references/code.md", "assets/template.html")

# デザイン規則（references/design.md）の上限と下限
MEASURE_MAX_EM = 40.0  # D1
LEADING_MIN = 1.5  # D2
SEMANTIC_COLORS_MAX = 4  # D5
SETTINGS_MAX = 4  # D13
L1_BLOCKS_MAX = 4
VISIBLE_LIST_MAX = 4  # R5: 覚えさせる項目は4つまで
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
FORBIDDEN_HTML = (
    (re.compile(r"text-align\s*:\s*justify", re.I), "D2: 両端揃え（text-align: justify）を使っている"),
    (re.compile(r"font-style\s*:\s*italic", re.I), "D3: 斜体（font-style: italic）を使っている"),
    (re.compile(r"<\s*(marquee|blink)\b", re.I), "D7: marquee か blink を使っている"),
    (re.compile(r"\bautoplay\b", re.I), "D7: 自動再生（autoplay）を使っている"),
)
MOTION = re.compile(r"@keyframes|\banimation\s*:|\btransition\s*:|scroll-behavior\s*:\s*smooth", re.I)

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


def check_references(skill_text: str, skill_dir: Path = SKILL_DIR) -> list[str]:
    """SKILL.md が指す別ファイルが、実在し、SKILL.md から参照されているかを検査する。"""
    problems: list[str] = []
    for rel in REFERENCES:
        if not (skill_dir / rel).is_file():
            problems.append(f"skills/sharpen/{rel}: ファイルがない")
        if rel not in skill_text:
            problems.append(f"SKILL.md: {rel} への参照がない")
    return problems


class _Structure(HTMLParser):
    """4層の構造を数える。data-layer の付いた要素、折りたたみ、リストを追う。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict] = []
        self.layer_counts: dict[str, int] = {}
        self.layer0_in_details = False
        self.details_total = 0
        self.details_without_summary = 0
        self.long_lists: list[tuple[str, int]] = []
        self.l1_without_back = 0
        self.has_nav = False
        self.ids: set[str] = set()
        self.selects = 0

    def _inside(self, tag: str) -> bool:
        return any(node["tag"] == tag for node in self.stack)

    def _layer(self) -> str | None:
        for node in reversed(self.stack):
            if node["layer"] is not None:
                return node["layer"]
        return None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if attr.get("id"):
            self.ids.add(attr["id"])
        if tag == "nav":
            self.has_nav = True
        if tag == "select":
            self.selects += 1
        layer = attr.get("data-layer")
        if layer is not None:
            self.layer_counts[layer] = self.layer_counts.get(layer, 0) + 1
            if layer == "0" and (tag == "details" or self._inside("details")):
                self.layer0_in_details = True
        if tag == "details":
            self.details_total += 1
        if tag == "summary":
            for node in reversed(self.stack):
                if node["tag"] == "details":
                    node["summary"] = True
                    break
        if tag == "li" and self.stack and self.stack[-1]["tag"] in ("ul", "ol"):
            self.stack[-1]["items"] += 1
        if tag == "a" and attr.get("href") == "#map":
            for node in reversed(self.stack):
                if node["layer"] == "1":
                    node["back"] = True
                    break
        if tag in VOID_TAGS:
            return
        visible = (
            tag in ("ul", "ol")
            and self._layer() in ("0", "1")
            and not self._inside("details")
            and not self._inside("nav")
        )
        self.stack.append(
            {"tag": tag, "layer": layer, "items": 0, "summary": False, "back": False, "visible": visible}
        )

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_TAGS or not any(node["tag"] == tag for node in self.stack):
            return
        while self.stack:
            node = self.stack.pop()
            self._close(node)
            if node["tag"] == tag:
                break

    def _close(self, node: dict) -> None:
        if node["tag"] == "details" and not node["summary"]:
            self.details_without_summary += 1
        if node["visible"] and node["items"] > VISIBLE_LIST_MAX:
            self.long_lists.append((node["tag"], node["items"]))
        if node["layer"] == "1" and not node["back"]:
            self.l1_without_back += 1

    def close(self) -> None:
        super().close()
        while self.stack:
            self._close(self.stack.pop())


def check_html(text: str, where: str = "HTML") -> list[str]:
    """HTML の成果物を、デザイン規則（D1〜D13）と4層の構造で検査する。"""
    problems: list[str] = []

    measure = re.search(r"--measure\s*:\s*([\d.]+)em", text)
    if not measure:
        problems.append(f"{where}: D1: 行長の変数 --measure（em）がない")
    elif float(measure.group(1)) > MEASURE_MAX_EM:
        problems.append(f"{where}: D1: 行長が {MEASURE_MAX_EM:g}em を超えている（{measure.group(1)}em）")

    leading = re.search(r"--leading\s*:\s*([\d.]+)\s*;", text)
    if not leading:
        problems.append(f"{where}: D2: 行の高さの変数 --leading がない")
    elif float(leading.group(1)) < LEADING_MIN:
        problems.append(f"{where}: D2: 行の高さが {LEADING_MIN:g} より小さい（{leading.group(1)}）")

    semantic = set(re.findall(r"(--sem-[\w-]+)\s*:", text))
    if len(semantic) > SEMANTIC_COLORS_MAX:
        problems.append(
            f"{where}: D5: 意味を持つ色が {SEMANTIC_COLORS_MAX} 色を超えている（{'、'.join(sorted(semantic))}）"
        )

    for pattern, message in FORBIDDEN_HTML:
        if pattern.search(text):
            problems.append(f"{where}: {message}")
    if MOTION.search(text) and "prefers-reduced-motion" not in text:
        problems.append(f"{where}: D7: 動きがあるのに prefers-reduced-motion の指定がない")

    parser = _Structure()
    parser.feed(text)
    parser.close()

    if parser.layer_counts.get("0", 0) != 1:
        problems.append(f"{where}: L0（data-layer=\"0\"）が1つではない（{parser.layer_counts.get('0', 0)} 個）")
    if parser.layer0_in_details:
        problems.append(f"{where}: D10: L0 を折りたたみの中に置いている")
    l1 = parser.layer_counts.get("1", 0)
    if l1 < 1:
        problems.append(f"{where}: L1（data-layer=\"1\"）がない")
    elif l1 > L1_BLOCKS_MAX:
        problems.append(f"{where}: L1 のブロックが {L1_BLOCKS_MAX} 個を超えている（{l1} 個）")
    if parser.l1_without_back:
        problems.append(f"{where}: 地図に戻るリンク（href=\"#map\"）がない L1 が {parser.l1_without_back} 個ある")
    if "map" not in parser.ids:
        problems.append(f"{where}: 地図（id=\"map\"）がない")
    for tag, count in parser.long_lists:
        problems.append(
            f"{where}: R5: L0 か L1 に、{VISIBLE_LIST_MAX} 項目を超えるリストがある（{tag}、{count} 項目）"
        )
    if parser.details_without_summary:
        problems.append(f"{where}: D10: summary のない details が {parser.details_without_summary} 個ある")
    if not parser.has_nav:
        problems.append(f"{where}: D9: 目次（nav）がない")
    if parser.details_total and "expand-all" not in parser.ids:
        problems.append(f"{where}: D10: 「すべて開く」の操作（id=\"expand-all\"）がない")
    if parser.selects > SETTINGS_MAX:
        problems.append(f"{where}: D13: 設定が {SETTINGS_MAX} つを超えている（{parser.selects} 個）")

    return problems


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args:
        problems = []
        for name in args:
            path = Path(name)
            if not path.is_file():
                problems.append(f"{name}: ファイルがない")
                continue
            problems += check_html(path.read_text(encoding="utf-8"), where=name)
        for problem in problems:
            print(problem)
        if problems:
            return 1
        print(f"OK: HTML {len(args)} 件に問題なし")
        return 0

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    problems, rule_ids = check_skill(skill_text)
    problems += check_log(LOG_PATH.read_text(encoding="utf-8"), rule_ids)
    problems += check_references(skill_text)
    if TEMPLATE_PATH.is_file():
        problems += check_html(TEMPLATE_PATH.read_text(encoding="utf-8"), where="assets/template.html")
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print(f"OK: ルール {len(rule_ids)} 件、フィードバックログ、別ファイルの参照、ひな形に問題なし")
    return 0


if __name__ == "__main__":
    sys.exit(main())
