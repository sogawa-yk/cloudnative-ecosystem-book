---
name: chapter-writing
description: 章を執筆するための詳細ガイド。章の執筆時に使用。
allowed-tools: Read, Write, Edit
---

# 章執筆スキル

このスキルは、章仕様書に基づいて高品質な原稿を執筆するためのガイドです。

## 前提条件

### 必須ドキュメント
1. `docs/chapter-specs/chNN-spec.md`（該当章の仕様書）
2. `docs/writing-guidelines.md`（執筆ガイドライン）
3. `docs/glossary.md`（用語集）

### 推奨
4. 前の章の原稿（`manuscript/chNN-1/chNN-1.md`）
5. `docs/book-architecture.md`（章間の依存関係）

## 出力先

```
manuscript/chNN/chNN.md       # 本文
manuscript/chNN/figures/      # 図表ソース
```

## 執筆プロセス

### 図表ファーストの原則

**必ず図表を先に設計し、本文は図の解説として書く。**

1. chapter-specの図表リストを確認
2. 各図表をMermaid記法またはテキスト図で設計
3. 図表を`figures/`に配置
4. 本文で図表を参照しながら解説を書く

### 節の構成パターン

各節は以下の構造を基本とする:

```
## N.X [節タイトル]

[導入: 1-2段落。この節で何を学ぶか、なぜ重要か]

[図表の提示]

[概念の説明: 図表を参照しながら核心を解説]

[具体例: OCI上での例やユースケース]

[まとめ/次の節への橋渡し: 1段落]
```

### Mermaid図の記法

**必ず`Skill('figure-design')`の配色ルールに従うこと。**

グレー背景で見やすい配色を使用する。全てのMermaid図にテーマ設定とclassDefを適用する:

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4A90D9', 'primaryTextColor': '#FFFFFF', 'primaryBorderColor': '#2A6CB6', 'lineColor': '#333333', 'textColor': '#1A1A1A', 'background': 'transparent'}}}%%
graph TB
    A[コンポーネント]:::main --> B[コンポーネント]:::sub

    classDef main fill:#4A90D9,stroke:#2A6CB6,color:#FFFFFF
    classDef sub fill:#E8913A,stroke:#C47A2F,color:#FFFFFF
    classDef tool fill:#5BB870,stroke:#3D9A50,color:#FFFFFF
    classDef user fill:#5C6370,stroke:#3D4450,color:#FFFFFF
```

- ノード名は日本語でOK
- 矢印にはラベルを付ける
- 配色の詳細は `Skill('figure-design')` を参照

### コード例のルール

- 概念理解に必要な最小限のコードのみ
- 完全な実装は載せない
- 疑似コード風でもOK
- 必ずコメントを付ける

```python
# OCI GenAI Serviceでのチャット補完（疑似コード）
response = generative_ai_client.chat(
    model_id="cohere.command-r-plus",
    messages=[{"role": "user", "content": prompt}],
    tools=tool_definitions,  # Function Callingのツール定義
)
```

### 章の導入の書き方

- 前章の最後のトピックを軽く振り返る（1-2文）
- この章で扱うテーマを提示
- 読了後にわかるようになることを示す
- 長すぎないこと（半ページ以内）

### 章の結びの書き方

- この章で学んだことの要約（箇条書きではなく散文で）
- 次章のテーマへの自然な橋渡し
- 「次の章では〜を見ていく」のような明示的な接続

### 理解度チェック問題の書き方

章末に配置。**必ず以下の共通フォーマットに従うこと。**

```markdown
## 理解度チェック

### Q1. [問題タイトル]

**種類**: [概念の確認 / 判断問題 / 設計問題]

**難易度**: [基礎 / 応用]

**問題文**:
[問題文を記述。判断問題・設計問題の場合はシナリオを含める。]

**選択肢**（選択式の場合）:
- (a) [選択肢]
- (b) [選択肢]
- (c) [選択肢]
- (d) [選択肢]

<details>
<summary>解答と解説</summary>

**解答**: [解答]

**解説**: [なぜその解答になるか、関連する本文の節への参照を含める。]

**関連する節**: [N.X節]

</details>

---

### Q2. [問題タイトル]

（同じフォーマットで繰り返す）
```

**フォーマットのルール**:
- 問題数: 3〜5問
- 必ず「種類」「難易度」「問題文」「解答と解説」「関連する節」を含める
- 種類は3種混在を推奨（概念確認×1-2、判断問題×1-2、設計問題×0-1）
- 選択式でない問題（記述式・設計問題）は選択肢セクションを省略してよい
- 解説には必ず関連する節への参照を入れる（読者が復習できるように）

## セルフチェックリスト

執筆完了後、以下を確認:

- [ ] 各節に最低1つの図表があるか
- [ ] 図表番号が「図X.Y」形式で正しいか
- [ ] 図表にキャプションが付いているか
- [ ] 本文中で図表が参照されているか
- [ ] 用語がglossary.mdと一致しているか
- [ ] 常体（である調）で統一されているか
- [ ] 技術用語の初出表記（日本語（英語）形式）が守られているか
- [ ] 章の導入で前章とのつながりがあるか
- [ ] 章の結びで次章への橋渡しがあるか
- [ ] 理解度チェック問題が3〜5問含まれているか
- [ ] 理解度チェック問題が共通フォーマットに準拠しているか（種類・難易度・解答・解説・関連する節）
- [ ] 「一般的には〜」等の主張に情報ソース（脚注）が付いているか
- [ ] Mermaid図にテーマ設定とclassDefの配色が適用されているか
