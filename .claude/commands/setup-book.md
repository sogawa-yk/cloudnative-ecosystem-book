---
description: 初回セットアップ: 永続ドキュメントをideas/book-concept.mdを元に作成する
---

# 初回書籍セットアップ

このコマンドは、書籍プロジェクトの永続ドキュメントを対話的に作成します。

## 実行方法

```bash
claude
> /setup-book
```

## 実行前の確認

`docs/ideas/` ディレクトリ内のファイルを確認します。

```
# 確認
ls docs/ideas/

# ファイルが存在する場合
✅ docs/ideas/book-concept.md が見つかりました
   この内容を元に書籍企画書を作成します

# ファイルが存在しない場合
⚠️  docs/ideas/ にファイルがありません
   対話形式で書籍企画書を作成します
```

## 手順

### ステップ0: インプットの読み込み

1. `docs/ideas/` 内のマークダウンファイルを全て読む
2. 内容を理解し、書籍企画書作成の参考にする

### ステップ1: 書籍企画書の作成

1. **book-planningスキル**をロード
2. `docs/ideas/book-concept.md`の内容を元に`docs/book-plan.md`を作成
3. コンセプトドキュメントを具体化：
   - 対象読者の詳細化
   - 到達目標の明確化
   - 全体構成とページ配分
   - 執筆方針
   - スコープ外の明示
4. ユーザーに確認を求め、**承認されるまで待機**

**以降のステップはbook-plan.mdの内容を元にするため、自動的に作成する**

### ステップ2: 書籍構成・依存関係の作成

1. `docs/book-plan.md`を読む
2. 章間の依存関係（前提知識の関係）を整理
3. `docs/book-architecture.md`を作成

### ステップ3: 執筆ガイドラインの作成

1. **writing-guidelinesスキル**をロード
2. 既存のドキュメントを読む
3. `docs/writing-guidelines.md`を作成

### ステップ4: 用語集の作成

1. **glossary-creationスキル**をロード
2. book-concept.mdとbook-plan.mdから用語を抽出
3. `docs/glossary.md`を作成

### ステップ5: リポジトリ構造定義書の作成

1. 既存のドキュメントを読む
2. `docs/repository-structure.md`を作成

### ステップ6: 各章の仕様書を作成

1. **chapter-spec-writingスキル**をロード
2. `docs/book-plan.md`の全体構成に基づき、全15章の仕様書を作成
3. 各仕様書を`docs/chapter-specs/chNN-spec.md`に保存
4. 仕様書には以下を含める：
   - 章の目的
   - 前提知識（依存する章）
   - 節の構成
   - 図表リスト
   - 章末の理解度チェック問題の方針
   - 前の章からの接続方法
   - 次の章への接続方法
   - 目標ページ数

### ステップ7: 図表一覧の作成

1. 全章の仕様書から図表情報を集約
2. `docs/figure-list.md`を作成

## 完了条件

- 全ての永続ドキュメントが作成されていること

完了時のメッセージ:
```
「初回セットアップが完了しました!

作成したドキュメント:
✅ docs/book-plan.md
✅ docs/book-architecture.md
✅ docs/writing-guidelines.md
✅ docs/glossary.md
✅ docs/repository-structure.md
✅ docs/chapter-specs/ch01-spec.md 〜 ch15-spec.md
✅ docs/figure-list.md

これで執筆を開始する準備が整いました。

今後の使い方:
- 章の執筆: /write-chapter [章番号]
  例: /write-chapter 1

- 章のレビュー: /review-chapter [章番号]
  例: /review-chapter 4

- ドキュメントの編集: 普通に会話で依頼してください
  例: 「用語集にA2Aの定義を追加して」
」
```
