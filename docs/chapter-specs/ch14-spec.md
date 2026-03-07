# 第14章 仕様書: Progressive Delivery — Argo Rollouts

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第14章 |
| タイトル | Progressive Delivery — Argo Rollouts |
| 所属 | Part 4: CI/CD & GitOps |
| 性質 | 概念 + 実践 |
| ページ数（目安） | 15p |
| 依存する章 | Ch.1（サンプルアプリケーション）、Ch.2（Prometheus） |
| 使用Namespace | `book-cicd`（Argo Rollouts Controller）、`book-app`（サンプルアプリ） |

### 目的

従来のDeploymentによる全トラフィック一括切り替えのリスクを理解し、Progressive Deliveryの概念と手法（Canary / Blue-Green）を学ぶ。Argo Rolloutsを導入し、サンプルアプリケーションでCanaryデプロイを実践する。さらに、第2章で構築したPrometheusのメトリクスをAnalysis Templateに組み込み、メトリクスに基づく自動昇格（Auto Promotion）を実現する。

## 前提知識

- Kubernetesの基本リソース（Deployment, Service, Ingress）の理解
- Kustomizeによるマニフェスト管理（第1章）
- Prometheusの基本概念とPromQLの初歩（第2章）
- Kubernetesのラベルセレクターによるトラフィックルーティングの仕組み

## 節の構成

### 14.1 Progressive Deliveryの概念

**概要**: デプロイ戦略の進化を振り返り（Recreate → RollingUpdate → Canary / Blue-Green）、Progressive Deliveryが解決する課題を説明する。各デプロイ戦略のトレードオフを比較し、実務での使い分け指針を示す。

**図表**:
- 図14.1: デプロイ戦略の比較（Recreate / RollingUpdate / Canary / Blue-Green）

**キーポイント**:
- Recreate: ダウンタイムあり、最もシンプル
- RollingUpdate: ゼロダウンタイムだが、ロールバック速度に難あり
- Canary: トラフィック比率を段階的に制御、メトリクスによる判定が可能
- Blue-Green: 即座の切り替えとロールバック、リソースコストが2倍

### 14.2 Argo Rolloutsのアーキテクチャ

**概要**: Argo Rolloutsの内部構成（Rollouts Controller、AnalysisRun Controller）と、Rollout CRDがKubernetes標準のDeploymentとどう異なるかを解説する。トラフィックルーティングの仕組み（Service切り替え / Ingress連携）を説明する。

**図表**:
- 図14.2: Argo RolloutsのアーキテクチャとCRD構成

**キーポイント**:
- Rollout CRD: Deploymentの拡張としての位置づけ
- AnalysisTemplate / AnalysisRun: メトリクスベースの判定メカニズム
- トラフィックルーティング: stable ServiceとCanary Serviceの切り替え
- kubectl argo rollouts プラグインによる操作

### 14.3 Argo Rolloutsのインストール

**概要**: Helmチャートによるインストール手順とArgo Rollouts kubectl pluginの導入、ダッシュボードの設定を示す。

**図表**:
- 図14.3: Argo Rolloutsインストール後のコンポーネント配置

**キーポイント**:
- `book-cicd` NamespaceへのHelmチャートによるインストール
- kubectl argo rollouts プラグインのインストール
- Argo Rollouts Dashboardの起動とアクセス
- Deploymentからの移行の容易さ

### 14.4 Canaryデプロイの実践

**概要**: サンプルアプリケーションのDeploymentをRollout CRDに書き換え、Canaryデプロイを実践する。ステップ定義（setWeight / pause）によるトラフィック制御と、手動昇格（promote）の操作を確認する。

**図表**:
- 図14.4: Canaryデプロイの段階的トラフィック移行フロー

**キーポイント**:
- DeploymentからRollout CRDへの移行: specの変更点
- strategy.canary.steps: setWeight（トラフィック比率設定）、pause（待機）
- stable ServiceとCanary Serviceの設定
- 実践: 新バージョンをデプロイし、段階的なトラフィック移行を確認
- kubectl argo rollouts promote / abort による手動制御

### 14.5 Analysis TemplateとAuto Promotion

**概要**: AnalysisTemplate CRDを使い、Prometheusメトリクス（エラー率、レイテンシ）に基づく自動昇格を設定する。Canaryステップにanalysisをインラインまたはバックグラウンドで組み込み、自動判定の動作を確認する。

**図表**:
- 図14.5: AnalysisTemplateによる自動判定フロー
- 表14.1: AnalysisTemplate主要フィールドの説明

**キーポイント**:
- AnalysisTemplate CRD: metrics（PromQLクエリ）、successCondition、failureLimit
- Prometheusをメトリクスプロバイダーとして設定
- インラインAnalysis: Canaryステップ内で特定タイミングに実行
- バックグラウンドAnalysis: Canary期間中に継続的にメトリクスを監視
- 実践: エラー率5%以下をsuccessConditionとし、正常時の自動昇格と異常時の自動ロールバックを確認

### 14.6 Blue-Greenデプロイ

**概要**: Blue-Greenデプロイの設定方法を解説する。activeServiceとpreviewServiceの概念、autoPromotionEnabledの設定、プレビュー環境での事前検証フローを示す。Canaryとの使い分け指針を提示する。

**図表**:
- 図14.6: Blue-Greenデプロイの切り替えフロー
- 表14.2: Canary vs Blue-Green の使い分け指針

**キーポイント**:
- strategy.blueGreen: activeService、previewService、autoPromotionEnabled
- プレビュー環境での手動検証 → promoteによる切り替え
- scaleDownDelaySeconds: 旧バージョンの保持期間
- Canaryとの使い分け: トラフィック量、検証要件、リソースコスト

## 図表リスト

| 図表番号 | タイトル | 形式 |
|----------|---------|------|
| 図14.1 | デプロイ戦略の比較（Recreate / RollingUpdate / Canary / Blue-Green） | Mermaid |
| 図14.2 | Argo RolloutsのアーキテクチャとCRD構成 | Mermaid |
| 図14.3 | Argo Rolloutsインストール後のコンポーネント配置 | Mermaid |
| 図14.4 | Canaryデプロイの段階的トラフィック移行フロー | Mermaid |
| 図14.5 | AnalysisTemplateによる自動判定フロー | Mermaid |
| 表14.1 | AnalysisTemplate主要フィールドの説明 | 表 |
| 図14.6 | Blue-Greenデプロイの切り替えフロー | Mermaid |
| 表14.2 | Canary vs Blue-Green の使い分け指針 | 表 |

## コード例

| コード番号 | 内容 | 言語 |
|-----------|------|------|
| コード14.1 | Argo Rollouts Helmインストールのvalues.yaml | YAML |
| コード14.2 | Rollout CRD（Canary戦略、サンプルアプリ用） | YAML |
| コード14.3 | stable Service / canary Serviceの定義 | YAML |
| コード14.4 | AnalysisTemplate（Prometheusエラー率チェック） | YAML |
| コード14.5 | AnalysisTemplate（Prometheusレイテンシチェック） | YAML |
| コード14.6 | Rollout CRD（Blue-Green戦略） | YAML |
| コード14.7 | kubectl argo rollouts操作コマンド集 | bash |

## 章末の理解度チェック

1. CanaryデプロイとBlue-Greenデプロイの違いを、トラフィック制御・リソースコスト・ロールバック速度の観点で比較せよ。
2. Argo RolloutsのRollout CRDは、Kubernetes標準のDeploymentと比較してどのような拡張を提供するか。既存のDeploymentからの移行手順を述べよ。
3. AnalysisTemplateでPrometheusメトリクスを使った自動昇格を設定する場合、successConditionとfailureLimitはそれぞれどのような役割を果たすか。
4. バックグラウンドAnalysisとインラインAnalysisの違いを説明し、それぞれの適切な使用場面を述べよ。

## 章間の接続

### 前の章からの接続（第13章 → 第14章）

第13章でArgoCDによるGitOps管理を確立した。しかし、ArgoCDのSync（同期）は新バージョンのマニフェストを一括で適用するため、問題のあるリリースが全ユーザーに即座に影響する。本章ではArgo Rolloutsを導入し、トラフィックを段階的に切り替えるProgressive Deliveryを実現する。第2章で構築したPrometheusのメトリクスを判定基準に組み込むことで、人手に頼らない自動的なリリース判定を可能にする。

### 次の章への接続（第14章 → 第15章）

CDの仕組み（ArgoCD + Argo Rollouts）が整った。しかし、コードの変更からコンテナイメージのビルド・テスト・脆弱性スキャン・署名までのCI（継続的インテグレーション）部分が未整備である。第15章ではGitHub Actionsを用いたCIパイプラインを構築し、第11章で学んだTrivyスキャンとcosign署名をパイプラインに組み込む。
