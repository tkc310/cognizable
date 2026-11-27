# cognizable

ワーキングメモリが小さく、言語理解が高い読み手に合わせて、AI エージェントの出力を整形するスキル。使いながら、合わなかった出力を記録してルールを育てる。

削る対象は、同時に保持させる量と、本題に無関係な情報の2つ。語彙と論理のつながりは削らない。

## 何が変わるか

- 1行目に結論か次の行動が来る。
- 手順は番号付きで、1手順に1動作。
- 「上記」「それ」で前を読み返させない。
- 毎回「今どこまで進んだか」を書き直す。

ルールの全体は [`skills/cognizable/SKILL.md`](skills/cognizable/SKILL.md) にある。

## 3つのモード

| 起動 | すること |
|------|----------|
| `/cognizable` | 以降の応答を、ルール R1〜R19 で整形する |
| `/cognizable doc 対象` | 資料やソースコードを、4層の成果物（HTML の1ページ）に変換する |
| `/cognizable design 対象` | 既存のページや図の見た目を、デザイン規則 D1〜D13 で整える |

4層は次の順に深くなる。

| 層 | 役割 |
|----|------|
| L0 | 1画面の要約。結論、次の一手、全体の地図 |
| L1 | ブロックごとの概要。3〜4ブロック |
| L2 | 種類別の詳細。手順、参照、解説 |
| L3 | 原典へのリンク |

詳細は次のファイルにある。

- 変換の手順: [`references/transform.md`](skills/cognizable/references/transform.md)
- ソースコードの変換: [`references/code.md`](skills/cognizable/references/code.md)
- デザイン規則: [`references/design.md`](skills/cognizable/references/design.md)
- HTML のひな形: [`assets/template.html`](skills/cognizable/assets/template.html)

## 理解を助ける4つのスキル

AI と開発するときに、読み手が計画、設計、知識、変更を理解するためのスキル。4つとも、出力に cognizable のルール R1〜R19 を適用する。

| 順番 | 起動 | 役割 | 出力 |
|------|------|------|------|
| 1 | `/cog-plan 実装したい内容` | 実装の計画を、成果物とプロセスの流れ図にする | 流れ図と、人が決める判断の表 |
| 2 | `/cog-ask 設計したい内容` | 設計の判断を、推奨付きの問いにして1問ずつ聞く | 問いと、最後に決定の表 |
| 3 | `/cog-learn 分からないこと` | 理解が足りない箇所を、3ステップの短いレッスンで教える | 各ステップの説明と確認の問い |
| 4 | `/cog-review 対象` | 変更を、読む順番に並べ替えて案内する | 全体の地図、ステップごとの解説と確認点 |

4つは、順番どおりに使わなくてよい。どのスキルも単独で使える。

- `/cog-ask html 設計したい内容` と打つと、1画面に1問の HTML（[`wizard.html`](skills/cog-ask/assets/wizard.html)）で問いを出す。
- `/cog-review html 対象` と打つと、4層の HTML で変更を案内する。

各スキルの決まりは次のファイルにある。

- [`skills/cog-plan/SKILL.md`](skills/cog-plan/SKILL.md)
- [`skills/cog-ask/SKILL.md`](skills/cog-ask/SKILL.md)
- [`skills/cog-learn/SKILL.md`](skills/cog-learn/SKILL.md)
- [`skills/cog-review/SKILL.md`](skills/cog-review/SKILL.md)

## 使い方

1. `skills/` の中の5つのディレクトリを、使っているエージェントのスキル置き場にコピーする（Claude Code なら `~/.claude/skills/`）。`cog-` で始まる4つのスキルは `cognizable/SKILL.md` を読むため、`cognizable/` と同じ置き場に置く。
2. 会話の中で `/cognizable` と打つ。
3. 資料を変換するときは `/cognizable doc 対象` と打つ。
4. 止めるときは「cognizable 終了」と打つ。

## 育て方

読みにくい出力に出会ったら「読みにくい」と伝える。cognizable が書き直し、記録を1件出す。記録は [`feedback/log.md`](feedback/log.md) にためる。見直しと反映の手順は [`docs/growth.md`](docs/growth.md) にある。

読みにくくても言い出しにくい場面に備えて、cognizable は成果物を渡した直後に確認を1行だけ出す。

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
- `cog-` で始まるスキルが、出力に cognizable を適用する指定を持ち、指している別ファイルが実在するか
- `cog-` で始まるスキルの HTML のひな形が、デザイン規則（行長、行の高さ、意味を持つ色の数、動き）を満たすか
- HTML の成果物が、デザイン規則と4層の構造を満たすか（行長、行の高さ、意味を持つ色の数、動き、L0 と L1 の項目数、地図に戻るリンクなど）
