# sharpen

ワーキングメモリが小さい読み手に合わせて、AI エージェントの出力を整形するスキル。使いながら、合わなかった出力を記録してルールを育てる。

## 何が変わるか

- 1行目に結論か次の行動が来る。
- 手順は番号付きで、1手順に1動作。
- 「上記」「それ」で前を読み返させない。
- 毎回「今どこまで進んだか」を書き直す。

ルールの全体は [`skills/sharpen/SKILL.md`](skills/sharpen/SKILL.md) にある。

## 使い方

1. `skills/sharpen/` を、使っているエージェントのスキル置き場にコピーする（Claude Code なら `~/.claude/skills/sharpen/`）。
2. 会話の中で `/sharpen` と打つ。
3. 止めるときは「sharpen 終了」と打つ。

pstack にも同じ名前の `/sharpen` スキルがある。両方を入れるとコマンド名が衝突するので、どちらかの置き場のディレクトリ名を変える。

## 育て方

読みにくい出力に出会ったら「読みにくい」と伝える。sharpen が書き直し、記録を1件出す。記録は [`feedback/log.md`](feedback/log.md) にためる。見直しと反映の手順は [`docs/growth.md`](docs/growth.md) にある。

## 検査

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

`scripts/check.py` は次を検査する。

- SKILL.md の frontmatter（`name` と `description`）
- ルール ID が R1 からの連番か、各ルールに悪い例と良い例があるか
- フィードバックログの各記録に必要な項目があり、指しているルール ID が実在するか

## 出典

ルールの構成は [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd)（MIT License）を元にしている。ライセンス本文は [`skills/sharpen/LICENSE.i-have-adhd`](skills/sharpen/LICENSE.i-have-adhd) にある。
