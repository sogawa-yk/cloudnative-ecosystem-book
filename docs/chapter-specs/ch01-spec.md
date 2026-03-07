# 第1章 仕様書: サンプルアプリケーションの構築

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第1章 |
| タイトル | サンプルアプリケーションの構築 |
| 所属 | Part 0: 準備編 |
| 性質 | 実践（ベースライン構築 + Kustomize） |
| ページ数（目安） | 20p |
| 目的 | 本書全体を通して使用するサンプルアプリケーション（3〜4サービス構成のマイクロサービス）をKubernetes上にデプロイし、Kustomizeの基本を習得する。「素のK8s上で動くアプリ」のベースラインを確立し、以降の章で解決すべき課題を明示する |

## 前提知識

- Kubernetesの基本リソース（Pod, Deployment, Service, ConfigMap, Ingress, Namespace）
- kubectlの基本操作
- コンテナの基本概念
- YAMLの読み書き
- 第0章の内容（環境要件、Namespace設計）

## 節の構成

### 1.1 サンプルアプリケーションの全体像

**概要**: 本書で使用するサンプルアプリケーションのアーキテクチャを解説する。フロントエンド / APIゲートウェイ / 商品サービス / 注文サービス + PostgreSQLの構成を示し、各サービスの役割とサービス間通信のフローを説明する。アプリケーションはGoで実装されている。

**図表**:
- 図1.1: サンプルアプリケーションのアーキテクチャ図 — 各サービスの関係とリクエストフロー
- 表1.1: 各サービスの概要（名前、役割、言語、ポート）

**キーポイント**:
- フロントエンド: Webフロントエンド（React）
- APIゲートウェイ: リクエストルーティング（Go）
- 商品サービス: 商品情報のCRUD（Go）
- 注文サービス: 注文処理（Go）
- データベース: PostgreSQL
- サービス間はHTTP/RESTで通信

### 1.2 Kubernetesマニフェストの作成

**概要**: サンプルアプリケーションをKubernetesにデプロイするための基本マニフェストを作成する。Deployment / Service / ConfigMap / Ingressの4種類のリソースを使い、各サービスをbook-app Namespaceにデプロイする。

**図表**:
- 図1.2: Kubernetesリソースの構成図 — Deployment / Service / ConfigMap / Ingressの関係

**キーポイント**:
- Namespace: `book-app` の作成
- 各サービスのDeployment定義（replicas、コンテナイメージ、ポート、環境変数）
- Service定義（ClusterIP）
- ConfigMapによる設定の外出し（DB接続情報、サービス間エンドポイント）
- Ingressによる外部公開

### 1.3 Kustomizeの基本 — base + overlays

**概要**: Kustomizeの仕組みと設計思想を解説する。baseディレクトリに環境非依存のマニフェストを配置し、overlaysで環境固有の差分（Ingress、StorageClass、レジストリ）を上書きするパターンを学ぶ。

**図表**:
- 図1.3: Kustomizeのbase + overlays構造図
- 図1.4: kustomization.yamlの処理フロー（base → patch → 最終マニフェスト）

**キーポイント**:
- Kustomizeの基本概念: base / overlays / patches / kustomization.yaml
- ディレクトリ構造: `k8s/base/` と `k8s/overlays/oke/` `k8s/overlays/kind/`
- 環境間で差異が出るポイント: Ingress（OCI LB vs NGINX + NodePort）、StorageClass（OCI Block Volume CSI vs hostPath）、レジストリ（OCIR vs ローカルレジストリ）
- `kustomize build` と `kubectl apply -k` の使い方
- 読者が自身の環境用overlayを作成するための手順

### 1.4 サンプルアプリケーションのデプロイと動作確認

**概要**: 前節で作成したKustomize構成を使って、サンプルアプリケーションをOKE（またはkind）上にデプロイし、動作確認を行う。各サービスが正常に起動し、エンドツーエンドでリクエストが処理されることを確認する。

**図表**:
- 図1.5: デプロイ後のリソース状態を確認するkubectlコマンド出力例

**キーポイント**:
- `kubectl apply -k overlays/oke/` によるデプロイ
- `kubectl get pods -n book-app` によるPodの状態確認
- Ingress経由でのアクセス確認（curlによる疎通テスト）
- 商品の登録 → 注文作成のエンドツーエンド動作確認
- トラブルシューティングの基本（`kubectl describe`, `kubectl logs`）

### 1.5 現状の課題 — 「素のK8s」の限界

**概要**: デプロイしたサンプルアプリケーションが抱える課題を明示する。Observability、Service Mesh、Security、CI/CD & GitOps、Platform Engineeringの5つの領域で「何が足りないか」を具体的に示し、以降のPartで学ぶ内容への動機付けとする。

**図表**:
- 図1.6: 現状の課題マップ — 5つの領域と具体的な課題の対応図
- 表1.2: 課題一覧と対応するPart

**キーポイント**:
- Observabilityの課題: ログがバラバラ、障害時に何が起きたか分からない、パフォーマンスのボトルネックが見えない
- Service Meshの課題: サービス間通信が暗号化されていない、トラフィック制御ができない、サービス間の依存関係が見えない
- Securityの課題: Pod間の通信が制限されていない、コンテナイメージの脆弱性チェックがない、ポリシー適用が手動
- CI/CDの課題: デプロイが手動（kubectl apply）、ロールバックが煩雑、設定のドリフトに気づけない
- Platform Engineeringの課題: 新サービス追加の手順が属人的、インフラの状態管理が宣言的でない

## 図表リスト

| 図表番号 | タイトル | 種類 | 節 |
|----------|---------|------|-----|
| 図1.1 | サンプルアプリケーションのアーキテクチャ図 | Mermaid | 1.1 |
| 表1.1 | 各サービスの概要 | 表 | 1.1 |
| 図1.2 | Kubernetesリソースの構成図 | Mermaid | 1.2 |
| 図1.3 | Kustomizeのbase + overlays構造図 | Mermaid | 1.3 |
| 図1.4 | kustomization.yamlの処理フロー | Mermaid | 1.3 |
| 図1.5 | デプロイ後のkubectlコマンド出力例 | テキスト図 | 1.4 |
| 図1.6 | 現状の課題マップ | Mermaid | 1.5 |
| 表1.2 | 課題一覧と対応するPart | 表 | 1.5 |

## コード例

| コード番号 | 内容 | 言語 | 節 |
|-----------|------|------|-----|
| リスト1.1 | APIゲートウェイのmain.go（抜粋） | Go | 1.1 |
| リスト1.2 | Deployment マニフェスト（商品サービス） | YAML | 1.2 |
| リスト1.3 | Service マニフェスト | YAML | 1.2 |
| リスト1.4 | ConfigMap マニフェスト | YAML | 1.2 |
| リスト1.5 | Ingress マニフェスト | YAML | 1.2 |
| リスト1.6 | kustomization.yaml（base） | YAML | 1.3 |
| リスト1.7 | kustomization.yaml（OKE overlay） | YAML | 1.3 |
| リスト1.8 | kustomization.yaml（kind overlay） | YAML | 1.3 |
| リスト1.9 | デプロイと動作確認のコマンド一式 | Shell | 1.4 |
| リスト1.10 | curlによるエンドツーエンド動作確認 | Shell | 1.4 |

## 章末の理解度チェック

1. サンプルアプリケーションを構成する4つのサービスの役割をそれぞれ説明せよ
2. Kustomizeのbaseとoverlaysの関係を説明し、環境差分をoverlayで吸収する利点を述べよ
3. `kubectl apply -k` と `kustomize build | kubectl apply -f -` の違いを説明せよ
4. 現状の「素のK8s」環境において、Observabilityの観点で具体的にどのような課題があるか3つ挙げよ
5. 新しいクラウド環境用のoverlayを作成する場合、最低限変更が必要なリソースを3つ挙げよ

## 章間の接続

### 前の章からの接続
- **第0章**: 環境要件、Namespace設計（`book-app`）、Kustomize overlayの概要を受けて、実際にサンプルアプリケーションを構築する。第0章で示した「概要」を「実践」に移す。

### 次の章への接続
- **第2章（Metrics — Prometheus）**: 本章で確立した「素のK8sアプリ」に対し、1.5節で明示した「パフォーマンスのボトルネックが見えない」「異常に気づけない」という課題をメトリクス収集で解決する。サンプルアプリのDeploymentにPrometheusのアノテーションを追加する。
- **第3章（Logs — Fluent Bit + Loki）**: 1.5節で明示した「ログがバラバラ」の課題を、Fluent Bit + Lokiによるログ集約で解決する。
- **第4章（Traces — OpenTelemetry + Jaeger）**: 1.5節で明示した「障害時に何が起きたか分からない」の課題を、分散トレーシングで解決する。サンプルアプリにOTel SDKを組み込む。
- **以降の全章**: 本章で構築したサンプルアプリケーションが全Partのベースラインとなる。
