# cognizable

ワーキングメモリが小さく、言語理解が高い読み手に合わせて、AI エージェントの出力を整形するスキル。使いながら、合わなかった出力を記録してルールを育てる。

削る対象は、同時に保持させる量と、本題に無関係な情報の2つ。語彙と論理のつながりは削らない。

## 何が変わるか

- 1行目に結論か次の行動が来る。
- 手順は番号付きで、1手順に1動作。
- 「上記」「それ」で前を読み返させない。
- 毎回「今どこまで進んだか」を書き直す。

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

## 使い方

1. `skills/` の中の5つのディレクトリを、使っているエージェントのスキル置き場にコピーする（Claude Code なら `~/.claude/skills/`）。`cog-` で始まる4つのスキルは `cognizable/SKILL.md` を読むため、`cognizable/` と同じ置き場に置く。
2. 会話の中で `/cognizable` と打つ。
3. 資料を変換するときは `/cognizable doc 対象` と打つ。
4. 止めるときは「cognizable 終了」と打つ。

## フック（Claude Code）

フックを登録すると、エージェントの回答が毎回 cognizable を経由する。`/cognizable` と打つ必要がなくなる。

| イベント | すること |
|----------|----------|
| UserPromptSubmit | 回答に cognizable のルール R1〜R19 を適用し、自然言語を日本語で書く指示を足す |
| PreToolUse | 「説明して」「質問です」などの質問の間は、ファイルを変更するツールを止める |
| Stop | 回答に英文の行が3行以上あれば、日本語に直して答え直させる |

登録の手順:

1. 「使い方」の手順1で、`skills/cognizable/` を `~/.claude/skills/` にコピーする。
2. [`skills/cognizable/hooks/settings.example.json`](skills/cognizable/hooks/settings.example.json) の `hooks` を、`~/.claude/settings.json` の `hooks` に足す。既にある `hooks` は消さずに、配列に足す。
3. Claude Code で `/hooks` を開き、3つのフックが並んでいるかを確かめる。

判定は機械的な目安で、外れることがある。

- 質問かどうかは語句で判定する。「説明して」「質問です」「教えて」「なぜ」、文末の「？」を質問とみなす。「修正して」「足して」など変更を頼む語句が一緒にあれば、変更の依頼とみなす。
- 英文の行は、日本語の文字を含まず、英単語が3つ以上ある行。コードブロック、インラインコード、URL、パスは数えない。
- PreToolUse は Bash によるファイルの変更を止めない。質問の印は、次の依頼で消える。
- Stop が答え直させるのは1回だけ。答え直しの後にもう一度止めると終わらなくなるため。

## Codex と Cursor で使う

スキルとフックの本体は `~/.claude/skills/` の1か所に置き、Codex と Cursor からはシンボリックリンクか設定の取り込みで参照する。ファイルを複製しない。

| 対象 | スキル | フック |
|------|--------|--------|
| Cursor | `~/.claude/skills/` をそのまま読む。設定は要らない | `~/.claude/settings.json` のフックをそのまま読む。設定は要らない |
| Codex | `~/.agents/skills/` に、5つのスキルのシンボリックリンクを置く | `~/.codex/hooks.json` に、登録の例へのシンボリックリンクを置く |

Cursor は、Cursor Settings の Agents にある Third-Party Imports が有効なとき（初期値は有効）に、Claude Code のスキルとフックを読む。

Codex の手順:

1. スキルのリンクを置く。

   ```sh
   mkdir -p ~/.agents/skills
   for s in cognizable cog-plan cog-ask cog-learn cog-review; do ln -s ~/.claude/skills/$s ~/.agents/skills/$s; done
   ```

2. フックのリンクを置く。`~/.codex/hooks.json` が既にあるときは、リンクを置かずに、登録の例の `hooks` を手で足す。

   ```sh
   ln -s ~/.claude/skills/cognizable/hooks/settings.example.json ~/.codex/hooks.json
   ```

3. Codex で `/hooks` を開き、3つのフックを信頼する。Codex は、信頼されていないフックを実行しない。

各スキルの `agents/openai.yaml` は、Codex がスキルを勝手に呼ばないための設定。Claude Code と Cursor の `disable-model-invocation: true` と同じ役割を持つ。

ツールによって、フックで効く範囲が違う。

| フック | Claude Code | Codex | Cursor |
|--------|-------------|-------|--------|
| cognizable の適用と日本語の指示 | 効く | 効く | 効かない。Cursor の依頼前のフックは、指示を足せない |
| 質問の間はファイルを変更しない | 効く | 効く（`apply_patch` を止める） | ファイルの変更は止まる。質問だという指示は届かない |
| 英文が3行以上なら答え直す | 効く | 効く | 効く |

## 育て方

読みにくい出力に出会ったら「読みにくい」と伝える。cognizable が書き直し、記録を1件出す。記録は [`feedback/log.md`](feedback/log.md) にためる。見直しと反映の手順は [`docs/growth.md`](docs/growth.md) にある。

読みにくくても言い出しにくい場面に備えて、cognizable は成果物を渡した直後に確認を1行だけ出す。

ルールの全体、ルールごとの根拠、読み手像への案内は、[`docs/growth.md`](docs/growth.md) の「関係する文書」にある。

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
