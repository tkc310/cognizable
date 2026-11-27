# sharpen

ワーキングメモリが小さく、言語理解が高い読み手に合わせて、AI エージェントの出力を整形するスキル。使いながら、合わなかった出力を記録してルールを育てる。

削る対象は、同時に保持させる量と、本題に無関係な情報の2つ。語彙と論理のつながりは削らない。

## 何が変わるか

- 1行目に結論か次の行動が来る。
- 手順は番号付きで、1手順に1動作。
- 「上記」「それ」で前を読み返させない。
- 毎回「今どこまで進んだか」を書き直す。

ルールの全体は [`skills/sharpen/SKILL.md`](skills/sharpen/SKILL.md) にある。

## 3つのモード

| 起動 | すること |
|------|----------|
| `/sharpen` | 以降の応答を、ルール R1〜R16 で整形する |
| `/sharpen doc 対象` | 資料やソースコードを、4層の成果物（HTML の1ページ）に変換する |
| `/sharpen design 対象` | 既存のページや図の見た目を、デザイン規則 D1〜D13 で整える |

4層は次の順に深くなる。

| 層 | 役割 |
|----|------|
| L0 | 1画面の要約。結論、次の一手、全体の地図 |
| L1 | ブロックごとの概要。3〜4ブロック |
| L2 | 種類別の詳細。手順、参照、解説 |
| L3 | 原典へのリンク |

詳細は次のファイルにある。

- 変換の手順: [`references/transform.md`](skills/sharpen/references/transform.md)
- ソースコードの変換: [`references/code.md`](skills/sharpen/references/code.md)
- デザイン規則: [`references/design.md`](skills/sharpen/references/design.md)
- HTML のひな形: [`assets/template.html`](skills/sharpen/assets/template.html)

## 使い方

1. `skills/sharpen/` を、使っているエージェントのスキル置き場にコピーする（Claude Code なら `~/.claude/skills/sharpen/`）。
2. 会話の中で `/sharpen` と打つ。
3. 資料を変換するときは `/sharpen doc 対象` と打つ。
4. 止めるときは「sharpen 終了」と打つ。

pstack にも同じ名前の `/sharpen` スキルがある。両方を入れるとコマンド名が衝突するので、どちらかの置き場のディレクトリ名を変える。

## 育て方

読みにくい出力に出会ったら「読みにくい」と伝える。sharpen が書き直し、記録を1件出す。記録は [`feedback/log.md`](feedback/log.md) にためる。見直しと反映の手順は [`docs/growth.md`](docs/growth.md) にある。

読みにくくても言い出しにくい場面に備えて、sharpen は成果物を渡した直後に確認を1行だけ出す。

読み手像は [`docs/persona.md`](docs/persona.md)、ルールごとの根拠は [`docs/evidence.md`](docs/evidence.md) にある。

## 検査

```sh
python3 scripts/check.py
python3 scripts/check.py 成果物.html
python3 -m unittest discover -s tests -v
```

`scripts/check.py` は次を検査する。

- SKILL.md の frontmatter（`name` と `description`）
- ルール ID が R1 からの連番か、各ルールに悪い例と良い例があるか
- フィードバックログの各記録に必要な項目があり、指しているルール ID が実在するか
- SKILL.md が指す別ファイルとひな形が実在するか
- HTML の成果物が、デザイン規則と4層の構造を満たすか（行長、行の高さ、意味を持つ色の数、動き、L0 と L1 の項目数、地図に戻るリンクなど）

## 出典

ルールの構成は [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)（MIT License）を元にしている。ライセンス本文は [`skills/sharpen/LICENSE.i-have-adhd`](skills/sharpen/LICENSE.i-have-adhd) にある。
