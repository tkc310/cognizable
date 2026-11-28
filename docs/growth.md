# cognizable の育て方

cognizable は、使って合わなかった出力を記録し、記録がたまったらルールを直す。この文書はその手順を決める。

## 関係する文書

| 文書 | 内容 |
|------|------|
| [`skills/cognizable/SKILL.md`](../skills/cognizable/SKILL.md) | 会話のルール R1〜R19 の全体 |
| [`skills/cognizable/references/design.md`](../skills/cognizable/references/design.md) | デザイン規則 D1〜D13 の全体 |
| [`skills/cognizable/references/transform.md`](../skills/cognizable/references/transform.md) | 資料を4層の成果物に変換する手順 |
| [`skills/cognizable/references/code.md`](../skills/cognizable/references/code.md) | ソースコードを変換する手順 |
| [`docs/research/evidence.md`](research/evidence.md) | ルールと規則ごとの根拠と、証拠の強さ |
| [`docs/persona.md`](persona.md) | cognizable が想定する読み手像 |
| [`docs/trials/`](trials/) | スキルを実際の題材で試したときに、エージェントが気づいた点の記録 |

## 1. 記録する

読みにくい出力に出会ったら、その場で cognizable に「読みにくい」「cognizable: 〜」と伝える。cognizable は出力を書き直し、フィードバック記録を1件出す。

記録は `feedback/log.md` の末尾に追記する。cognizable がリポジトリに書き込めない環境では、出てきたコードブロックを手で貼る。

記録した時点の「状態」は `未対応` にする。

## 2. 見直す

`未対応` の記録が5件たまったら、見直しの作業を1回行う。5件に満たなくても、月に1回は見直す。

見直しでは、記録ごとに次のどれかを選ぶ。

| 判断 | 当てはまるとき | すること |
|------|----------------|----------|
| 既存ルールを直す | 指したルールの書き方が弱い、または例が足りない | SKILL.md の該当ルールの本文か例を直す |
| ルールを足す | 「ルール: 新規」で、同じ困りごとが2件以上ある | SKILL.md の末尾に次の番号でルールを足す |
| 見送る | 1回限りの状況、または他のルールと衝突する | 何もしない |

1件だけの `新規` は、すぐにはルールにしない。2件目が出るまで `未対応` のまま残す。

### 調査を根拠にルールを足すとき

研究や公的な指針を根拠にするときは、同じ困りごとが2件たまるのを待たずにルールを足してよい。条件は次の2つ。

1. `docs/research/evidence.md` に、ルールの ID、証拠の強さ、出典を1行で書く。
2. 証拠の強さが「弱」のルールは、合わないという記録が1件出た時点で見直す。

デザイン規則（`skills/cognizable/references/design.md` の D1 から）も同じ手順で直す。

## 3. 反映する

1. SKILL.md を直す。
2. 反映した記録の「状態」を `反映済み` に、見送った記録を `見送り` に書き換える。
3. SKILL.md の `metadata.version` を上げる。ルールを足したら2桁目、文言や例だけ直したら3桁目を上げる。
4. `CHANGELOG.md` に、どのルールをどう直したかを1行ずつ書く。
5. `python3 scripts/check.py` と `python3 -m unittest discover -s tests` を通す。
6. PR を出す。

## ルール ID の決まり

- ID は `R1` からの連番にする。`scripts/check.py` が連番かどうかを検査する。
- ルールを削除したときは、後ろのルールの番号を詰める。詰めた番号を指している記録があれば、記録の「ルール」も新しい番号に書き換える。
- 記録の「ルール」が SKILL.md にない ID を指していると、`scripts/check.py` が失敗する。
- デザイン規則の ID は `D1` からの連番にする。記録の「ルール」にデザイン規則を書くときは、`新規` と書き、「場面」に `D5` のように ID を書く。
