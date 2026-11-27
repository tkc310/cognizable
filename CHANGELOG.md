# 変更履歴

## 0.3.1 (2026-11-28)

- SKILL.md と README から「出典」の節を消した。
- 同梱しているライセンス文のファイル名を `skills/cognizable/THIRD_PARTY_LICENSE` に変えた。

## 0.3.0 (2026-11-28)

- スキルの名前を sharpen から cognizable に変えた。リポジトリの名前に合わせた。
- 起動は `/cognizable`、`/cognizable doc 対象`、`/cognizable design 対象`。解除は「cognizable 終了」。
- スキルの置き場は `skills/cognizable/`。古い `skills/sharpen/` を入れている場合は、消してから入れ直す。
- HTML のひな形が設定を保存するキーを `cognizable-settings` に変えた。古い成果物で保存した設定は引き継がない。
- この履歴の 0.2.0 以前の項目も、新しい名前で書き直してある。

## 0.2.0 (2026-11-28)

調査を根拠に、ルールを改訂し、文書変換とデザインのモードを足した。根拠は `docs/evidence.md` にある。

- R2: 文を分けたら接続語を残す、を足した。
- R5: 覚えさせる項目は4つまで、見て探す一覧は5つずつ、に分けた。
- R6: 状態は1行で書く、と明記した。
- R7: 同じ概念に同じ語を使う、長い出力では主要な用語を冒頭にも置く、を足した。
- R11: 長い出力の冒頭の概要は残す、を足した。
- R12: 読み手に計算をさせない、を足した。
- R13〜R16 を足した。見出しは主張を述べる文、比喩と二重否定を使わない、手順と参照と解説を分ける、所要時間を先に示す。
- 読み手が言い出すのを待たず、成果物を渡した直後に確認を1行出す仕組みを足した。
- `/cognizable doc` を足した。資料とソースコードを4層の成果物に変換する（`references/transform.md`、`references/code.md`）。
- `/cognizable design` と、デザイン規則 D1〜D13 を足した（`references/design.md`）。
- HTML のひな形 `assets/template.html` を置いた。
- `scripts/check.py` が、別ファイルの参照と、HTML の成果物を検査するようになった。
- 読み手像 `docs/persona.md` を置いた。
- `docs/growth.md` に、調査を根拠にルールを足す手順を足した。

## 0.1.0 (2026-11-27)

- 最初の版。R1〜R12 の12ルールを置いた。
- フィードバックログ `feedback/log.md` と、改訂手順 `docs/growth.md` を置いた。
- 形式を検査する `scripts/check.py` を置いた。
