# ルールの根拠

cognizable のルールと規則が、どの知見に基づくかをまとめる。調査は2026年11月に行った。

## 読む前に知っておくこと

- ADHD と ASD を併発した成人を直接調べた研究は、ほぼ見つからなかった。
- ADHD や ASD の成人で、文章の形式を比べた実験は見つからなかった。
- そのため、根拠の多くは一般の読み手を対象にした研究と、専門家の合意からの外挿になる。
- 合わないルールは、フィードバックの記録で直す。手順は `docs/growth.md` にある。

証拠の強さは3段階で書く。

| 強さ | 意味 |
|------|------|
| 強 | メタ分析、標準、複数の再現がある |
| 中 | 個別の研究、または公的な指針 |
| 弱 | 実務者の通説、または推論 |

## 会話のルール（R1〜R19）

| ルール | 強さ | 根拠 |
|--------|------|------|
| R1 結論と次の行動を先頭に | 中 | 公用文作成の考え方、COGA 4.3.4。ADHD 児は文章の中心情報の再生が弱い（Miller 2013） |
| R2 1文に1情報、接続語を残す | 中 | 公用文作成の考え方、COGA 4.4.9。つながりを明示した文章は再生を高める（McNamara 1996） |
| R3 指示語で読み返させない | 中 | 公用文作成の考え方。処理と保持を同時に求めると理解が落ちる（Daneman & Merikle 1996） |
| R4 手順は番号付き、1手順1動作 | 中 | COGA の指示を分ける型。指示の遂行はワーキングメモリと関連する（Jaroslawska 2016） |
| R5 覚えさせる項目は4つまで | 強 | 注意に同時に保持できる量は4±1（Cowan 2001）。文書の読解での直接の検証はない |
| R6 状態を毎回書き直す | 中 | WCAG 3.3.7 の根拠、COGA 4.2.4 |
| R7 用語はその場で定義、先にも示す | 強 | 用語を先に教える原則 d=0.78（Mayer 2021）。語彙はワーキングメモリの弱さを補う（Peng 2018） |
| R8 比較は表にする | 中 | 図や表は探索の手間を減らす（Larkin & Simon 1987） |
| R9 脱線は最後に1行 | 強 | 無関係な内容を除く原則 d=0.86（Mayer 2021）。「1行」という形の根拠はない |
| R10 最後に次の一手を1つ | 弱 | 直接の根拠は見つからなかった。フィードバックで検証する |
| R11 前置きと挨拶を書かない、概要は残す | 強 | 無関係な内容を除く原則。見出しや要約の手がかりは保持を高める g=0.53（Schneider 2018） |
| R12 数字で書く、計算させない | 中 | 公用文作成の考え方、COGA 4.4.13 |
| R13 見出しは主張を述べる文 | 中 | 公用文作成の考え方、COGA。主張文の見出しは過程の理解を高める（Garner 2011） |
| R14 比喩、慣用句、二重否定を使わない | 中 | COGA 4.4.3〜4.4.4。言語能力が高ければ比喩理解の差は小さい（Kalandadze 2018）ため、目的は推論の手間を減らすこと |
| R15 手順、参照、解説に分ける | 弱 | Diátaxis、DITA。比較実験はない。初心者向けの支援は熟達者に無効か有害になりうる（Kalyuga 2003） |
| R16 所要時間と分量を先に示す | 中 | ADHD は時間の見積もりが不正確（Zheng 2022、小児中心）。不確実性への不耐性（Jenkinson 2020） |
| R17 主語と目的語を省略しない | 中 | 公用文作成の考え方（主語と述語の対応）、COGA 4.4.12（暗黙の内容を説明する）。処理と保持を同時に求めると理解が落ちる（Daneman & Merikle 1996）。日本語の省略を対象にした実験は確認していない |
| R18 推論の段を飛ばさない | 中 | つながりを明示した文章は再生を高める（McNamara 1996）。ADHD 児は一貫した心的表象を作りにくい（Miller 2013）。COGA 4.4.12 |
| R19 同じ種類の出力は同じ順番 | 中 | COGA 4.2.3（一貫した配置）。不確実性への不耐性（Jenkinson 2020）。出力の種類ごとの順番は推論 |

## 4層の構造（references/transform.md）

| 決めたこと | 強さ | 根拠 |
|------------|------|------|
| 概要を先に置く | 中 | 先行オーガナイザーの効果は小さいが正。ASD は全体の把握に時間がかかる（Van der Hallen 2015） |
| 分割して見せる | 強 | 分割の原則。56研究のメタ分析（Rey 2019） |
| 読む層は3つまで | 弱〜中 | 3層を超えると読み手が迷う（Nielsen 2006）。浅く広い構造のほうが探索が速い（Larson & Czerwinski 1998） |
| 地図に戻るリンクを置く | 中 | コードを読む人は、全体からの理解と細部からの理解を行き来する（von Mayrhauser & Vans 1995） |
| 図の型を絞る | 強 | ADHD と ASD は視空間のワーキングメモリが低い（Martinussen 2005、Habib 2019）。ノード数の値は推論 |

## デザイン規則（references/design.md）

| 規則 | 強さ | 根拠 |
|------|------|------|
| D1 行長は最大40字 | 強 | WCAG 1.4.8（日本語は40字以下）、jlreq-d 草案 |
| D2 文字と行間 | 強 | WCAG 1.4.12、jlreq-d 草案 |
| D3 専用書体を使わない | 強 | ディスレクシア用書体はメタ分析で効果なし g=−0.04（Azzarello 2026） |
| D4 コントラスト | 強 | WCAG 1.4.6、1.4.11 |
| D5 意味を持つ色は4色まで | 中 | WCAG 1.4.1、COGA 4.2.3。色数の上限は推論 |
| D6 ライトを既定 | 中 | 明るい背景のほうが読みの成績がよい（Budiu 2020） |
| D7 自動で動くものを置かない | 強 | WCAG 2.2.2、2.3.3 |
| D8 1カラム、周辺に装飾なし | 中 | 成人 ADHD は無関係な周辺画像による妨害が対照群の2倍以上（Forster 2014） |
| D9 現在地を常に表示 | 中 | WCAG 2.4.8、COGA 4.2.4。ワーキングメモリを補う効果は推論 |
| D10 折りたたむのは詳細だけ | 中 | 折りたたみの利点と害の調査（Wang 2023） |
| D11 定義をホバーだけにしない | 強 | WCAG 1.4.13 |
| D12 図は1枚に1つの主張 | 強 | 無関係な内容を除く原則、図と説明を近くに置く原則 d=0.85（Ginns 2006） |
| D13 設定は4つまで | 中 | 設定項目が多いと、設定の作業が注意を奪う（Zhu 2025、12名） |

## 出典

確認の深さを括弧に書く。「抄録」は抄録か公式の要約まで、「本文」はページを開いて確認、「書誌」は書誌情報だけの確認。

### 認知特性

- Wilson 2024, Cognitive Profile in Autism and ADHD: A Meta-Analysis of Performance on the WAIS-IV and WISC-V. doi:10.1093/arclin/acad073（抄録）
- Kofler et al. 2020, Working memory and short-term memory deficits in ADHD. doi:10.1037/neu0000641（抄録）
- Martinussen et al. 2005. doi:10.1097/01.chi.0000153228.72591.73（抄録）
- Habib et al. 2019. doi:10.1371/journal.pone.0216198（抄録）
- Daneman & Merikle 1996. doi:10.3758/bf03214546（抄録）
- Peng et al. 2018. doi:10.1037/bul0000124（抄録）
- Miller et al. 2013. doi:10.1007/s10802-012-9686-8（抄録）
- Jaroslawska et al. 2016. doi:10.3758/s13421-015-0579-2（抄録）
- Van der Hallen et al. 2015. doi:10.1037/bul0000004（抄録）
- Kalandadze et al. 2018. doi:10.1177/1362361316668652（抄録）
- Jenkinson et al. 2020. doi:10.1177/1362361320932437（抄録）
- Zheng et al. 2022. doi:10.1177/1087054720978557（抄録）
- Forster et al. 2014, Neuropsychology. PMC3906797（本文）

### 文書の構造

- W3C 2021, Making Content Usable for People with Cognitive and Learning Disabilities（COGA）. https://www.w3.org/TR/coga-usable/ （本文）
- 文化審議会 2022, 公用文作成の考え方（建議）. https://www.bunka.go.jp/seisaku/bunkashingikai/kokugo/hokoku/pdf/93731901_01.pdf （本文）
- Mayer 2021, Multimedia Learning 第3版（著者による要約で確認）
- Schneider et al. 2018, Educational Research Review 23:1–24（二次の要約）
- Rey et al. 2019. doi:10.1007/s10648-018-9456-4（抄録）
- Ginns 2006. doi:10.1016/j.learninstruc.2006.10.001（抄録）
- Cowan 2001. doi:10.1017/S0140525X01003922（書誌）
- Kalyuga et al. 2003, Educational Psychologist 38(1):23–31（抄録）
- McNamara et al. 1996, Cognition and Instruction 14(1)（二次の要約）
- Garner & Alley et al. 2011, ASEE AC 2011-900（本文）
- Larkin & Simon 1987, Cognitive Science 11:65–99（二次の要約）
- Larson & Czerwinski 1998. doi:10.1145/274644.274649（書誌）
- Nielsen 2006, Progressive Disclosure. https://www.nngroup.com/articles/progressive-disclosure/ （本文）
- von Mayrhauser & Vans 1995, IEEE Computer（本文）
- Procida, Diátaxis. https://diataxis.fr/ （本文）

### デザイン

- W3C 2023, WCAG 2.2. https://www.w3.org/TR/WCAG22/ （本文）
- W3C, 日本語組版処理の要件（JLReq）. https://www.w3.org/TR/jlreq/ （本文）。jlreq-d は専門家の草案
- Azzarello et al. 2026, Annals of Dyslexia（抄録）
- Budiu 2020, Dark Mode vs. Light Mode. https://www.nngroup.com/articles/dark-mode/ （本文）
- Wang 2023, Accordions on Desktop. Nielsen Norman Group（本文）
- Zhu, Chen & Zhao 2025, FocusView. arXiv:2507.13309（本文）
- Hannebauer et al. 2018. doi:10.1007/s10664-017-9579-0（抄録）
