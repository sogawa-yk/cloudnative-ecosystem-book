# 第17章 仕様書: Internal Developer Platform ― Backstage

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第17章 |
| タイトル | Internal Developer Platform ― Backstage |
| 所属する部 | Part 5: Platform Engineering |
| 性質 | 概念 + 実践 |
| 目標ページ数 | 20p |
| 依存する章 | Ch.1（サンプルアプリケーションの構築） |
| 使用Namespace | `book-platform` |

### 目的

Platform Engineeringの思想とIDP（Internal Developer Platform）の必要性を理解し、Backstageを用いてサービスカタログの構築とSoftware Templateによる新サービス作成を実践する。読者がPart 1〜4で個別に導入してきた技術群を「開発者に提供するプラットフォーム」として捉え直す視点を獲得することを目指す。

## 前提知識

### 本書で習得済みであること

- Kubernetesの基本リソースとkubectl操作（第0章〜第1章）
- サンプルアプリケーションのデプロイとKustomizeの基本（第1章）

### 本章で新たに必要な知識

- Node.js / TypeScriptの基礎的な読解力（Backstageプラグイン開発で使用）
- YAMLの読み書き（catalog-info.yaml、テンプレート定義）

## 節の構成

### 17.1 Platform Engineeringとは何か（4p）

#### 概要

Platform Engineeringの背景と思想を解説する。DevOpsの「You build it, you run it」がもたらした認知負荷の問題、Team Topologiesにおけるプラットフォームチームの役割、IDPの概念を説明する。

#### 図表

- **図17.1**: Platform Engineeringの全体像 ― プラットフォームチームと開発チームの関係を示す。プラットフォームチームがGolden Pathを提供し、開発チームがセルフサービスで利用する構図。
- **図17.2**: 認知負荷の変化 ― DevOps以前（サイロ）→ DevOps（全責任）→ Platform Engineering（抽象化による負荷軽減）の3段階の比較図。

#### キーポイント

- DevOpsの進化形としてのPlatform Engineering
- 認知負荷（Cognitive Load）の削減がPlatform Engineeringの核心
- IDPの三要素：セルフサービス、Golden Path、自動化
- Team Topologiesのプラットフォームチーム概念

### 17.2 Backstageの概要とアーキテクチャ（4p）

#### 概要

Backstageの起源（Spotify）、CNCFプロジェクトとしての位置づけ、コア機能（Service Catalog、Software Templates、TechDocs、プラグインシステム）を解説する。Backstageのアーキテクチャ（フロントエンド + バックエンド + データベース）を説明する。

#### 図表

- **図17.3**: Backstageのアーキテクチャ ― フロントエンド（React）、バックエンド（Node.js）、PostgreSQLデータベース、プラグインシステムの関係図。
- **表17.1**: Backstageのコア機能一覧 ― Service Catalog、Software Templates、TechDocs、Search、Kubernetes Pluginの概要と用途。

#### キーポイント

- Backstageの4つのコア機能
- プラグインベースのアーキテクチャ（拡張性の高さ）
- Entity（エンティティ）とcatalog-info.yamlの概念
- CNCFにおけるBackstageの位置づけ（Incubatingプロジェクト）

### 17.3 Backstageのデプロイ（4p）

#### 概要

OKE上にBackstageをデプロイする手順を示す。Helmチャートを使用したデプロイ、PostgreSQLの設定、Backstageのapp-config.yamlによる設定を解説する。

#### 図表

- **図17.4**: Backstageのデプロイ構成 ― book-platform Namespace内のBackstage Pod、PostgreSQL Pod、Ingressの構成図。

#### キーポイント

- Helm chartによるBackstageのインストール
- app-config.yamlの主要設定項目（baseUrl、データベース接続、認証）
- Kubernetes環境でのBackstage運用上の考慮事項
- book-platform Namespaceへのデプロイ

### 17.4 サービスカタログの構築（4p）

#### 概要

サンプルアプリケーション（フロントエンド、APIゲートウェイ、商品サービス、注文サービス）をBackstageのサービスカタログに登録する。catalog-info.yamlの記述方法、Entity間の依存関係の定義、オーナーシップの設定を実践する。

#### 図表

- **図17.5**: サービスカタログの依存関係グラフ ― Backstage上でサンプルアプリの4サービス + データベースの依存関係が可視化される画面イメージ（テキスト図）。
- **表17.2**: catalog-info.yamlの主要フィールド ― apiVersion、kind、metadata、spec.type、spec.owner、spec.dependsOn等の説明。

#### キーポイント

- catalog-info.yamlの記述パターン（Component、API、Resource）
- Entity間のリレーション（dependsOn、providesApi、consumesApi）
- オーナーシップの設計（Group、User）
- カタログの自動検出（GitHub Discovery）

### 17.5 Software Templateによる新サービス作成（4p）

#### 概要

Backstage Software Templateを使って、Golden Pathとして新しいマイクロサービスをテンプレートから生成する仕組みを構築する。テンプレートにはKustomize構成、Dockerfile、基本的なGoのサービスコード、catalog-info.yamlが含まれる。

#### 図表

- **図17.6**: Software Templateのワークフロー ― 開発者がBackstage UIからテンプレートを選択 → パラメータ入力 → GitHubリポジトリ生成 → catalog-info.yaml自動登録の流れ。
- **表17.3**: テンプレートに含まれるファイル一覧 ― 生成されるリポジトリのディレクトリ構成と各ファイルの役割。

#### キーポイント

- template.yamlの構造（parameters、steps、output）
- Scaffolder（足場生成）の仕組み
- テンプレートからGitHubリポジトリを自動生成するステップ
- Golden Pathの設計思想：自由度と標準化のバランス

## 図表リスト

| 番号 | 種別 | タイトル | 節 | 形式 |
|------|------|---------|-----|------|
| 図17.1 | 図 | Platform Engineeringの全体像 | 17.1 | Mermaid |
| 図17.2 | 図 | 認知負荷の変化（DevOps → Platform Engineering） | 17.1 | Mermaid |
| 図17.3 | 図 | Backstageのアーキテクチャ | 17.2 | Mermaid |
| 表17.1 | 表 | Backstageのコア機能一覧 | 17.2 | Markdown表 |
| 図17.4 | 図 | Backstageのデプロイ構成 | 17.3 | Mermaid |
| 図17.5 | 図 | サービスカタログの依存関係グラフ | 17.4 | テキスト図 |
| 表17.2 | 表 | catalog-info.yamlの主要フィールド | 17.4 | Markdown表 |
| 図17.6 | 図 | Software Templateのワークフロー | 17.5 | Mermaid |
| 表17.3 | 表 | テンプレートに含まれるファイル一覧 | 17.5 | Markdown表 |

## コード例

| 番号 | 内容 | 言語 | 節 |
|------|------|------|-----|
| コード17.1 | Backstage Helm valuesの主要設定 | YAML | 17.3 |
| コード17.2 | app-config.yamlの設定例 | YAML | 17.3 |
| コード17.3 | catalog-info.yaml（Componentの定義例） | YAML | 17.4 |
| コード17.4 | catalog-info.yaml（API定義とリレーション） | YAML | 17.4 |
| コード17.5 | template.yaml（Software Template定義） | YAML | 17.5 |
| コード17.6 | テンプレートのスケルトン（Goサービス） | Go | 17.5 |
| コード17.7 | テンプレートのKustomization.yaml | YAML | 17.5 |

## 章末の理解度チェック

1. **Platform Engineeringが解決する課題は何か。** DevOpsにおける認知負荷の問題と、IDPによるセルフサービス化の関係を説明せよ。
2. **Backstageのcatalog-info.yamlで定義できるEntityの種類（kind）を3つ挙げ、それぞれの用途を説明せよ。**
3. **Software Templateのtemplate.yamlにおいて、parametersセクションとstepsセクションはそれぞれ何を定義するか。**
4. **Golden Pathの設計において、「自由度」と「標準化」のバランスをどのように取るべきか。** 本章の内容を踏まえて考察せよ。

## 章間の接続

### 前の章からの接続

第16章（統合 ― End-to-End デリバリーパイプライン）でCI/CDの一気通貫パイプラインが完成した。しかし、新しいサービスを追加する際には、手動で多くの設定（リポジトリ作成、マニフェスト作成、ArgoCD Application登録、Observability設定等）を行う必要がある。本章ではこの「新サービス立ち上げの認知負荷」を課題として提示し、Platform Engineeringの思想とBackstageによるIDP構築を導入する。

### 次の章への接続

本章で構築したBackstageのSoftware Templateは、現時点ではGitHubリポジトリの生成までを行う。第18章ではCrossplaneによるインフラの宣言的管理を学び、第19章でBackstageテンプレートとCrossplane、ArgoCD、Observability、Service Mesh、Securityの全技術を統合したGolden Pathを完成させる。
