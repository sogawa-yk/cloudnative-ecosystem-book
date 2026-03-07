# 要求内容

## 概要

サンプルアプリケーション（マイクロサービス構成）をKubernetes上にデプロイし、Kustomizeの基本を習得する。「素のK8s」のベースラインを確立し、以降の章で解決すべき課題を明示する。

## 対象

- **章番号**: 第1章
- **対象節**: 1.1 〜 1.5
- **章仕様書**: `docs/chapter-specs/ch01-spec.md`

## 執筆内容

### 1. 1.1 サンプルアプリケーションの全体像
- アーキテクチャ解説（フロントエンド、APIゲートウェイ、商品サービス、注文サービス、PostgreSQL）
- 図1.1: アーキテクチャ図、表1.1: サービス概要
- リスト1.1: APIゲートウェイのmain.go抜粋

### 2. 1.2 Kubernetesマニフェストの作成
- Deployment / Service / ConfigMap / Ingressの作成
- 図1.2: リソース構成図
- リスト1.2〜1.5: 各マニフェスト

### 3. 1.3 Kustomizeの基本 ― base + overlays
- Kustomizeの設計思想と基本概念
- 図1.3: base + overlays構造図、図1.4: 処理フロー
- リスト1.6〜1.8: kustomization.yaml

### 4. 1.4 サンプルアプリケーションのデプロイと動作確認
- デプロイ手順と確認コマンド
- 図1.5: kubectl出力例
- リスト1.9〜1.10: デプロイ・動作確認コマンド

### 5. 1.5 現状の課題 ― 「素のK8s」の限界
- 5領域の課題明示
- 図1.6: 課題マップ、表1.2: 課題一覧

## 図表リスト

| 図表番号 | 内容 | 種類 |
|---------|------|------|
| 図1.1 | サンプルアプリケーションのアーキテクチャ図 | Mermaid |
| 表1.1 | 各サービスの概要 | 表 |
| 図1.2 | Kubernetesリソースの構成図 | Mermaid |
| 図1.3 | Kustomizeのbase + overlays構造図 | Mermaid |
| 図1.4 | kustomization.yamlの処理フロー | Mermaid |
| 図1.5 | デプロイ後のkubectl出力例 | テキスト図 |
| 図1.6 | 現状の課題マップ | Mermaid |
| 表1.2 | 課題一覧と対応するPart | 表 |

## 前後の章との接続

### 前の章から
- 第0章で環境要件・Namespace設計・Kustomize overlay概要を説明済み
- 「概要→実践」への橋渡し

### 次の章へ
- 1.5節の課題がPart 1〜5の動機付けとなる
- 第2〜4章はそれぞれObservabilityの課題を解決

## 参照ドキュメント

- `docs/chapter-specs/ch01-spec.md`
- `docs/writing-guidelines.md`
- `docs/glossary.md`
- `docs/book-plan.md`

## 過去の章からの申し送り

- 第0章で示したKustomize overlay構造を詳細に解説すること（出典: 第0章のtasklist.md）
- Namespace `book-app` を使用すること（出典: 第0章のtasklist.md）

**今回の執筆でどう反映するか**:
- 1.3節でKustomize overlayの設計と実装を詳細に解説
- 全セクションで `book-app` Namespaceを一貫して使用
