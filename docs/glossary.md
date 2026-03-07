# 用語集 (Glossary)

**更新日**: 2026-03-07

## 凡例

- **表記**: 本書での統一表記
- **英語**: 英語表記（初出時に併記）
- **定義**: 本書における定義
- **初出**: 最初に登場する章

---

## Observability関連

### メトリクス (Metrics)
**定義**: システムの状態を数値で表現する時系列データ。CPU使用率、リクエストレート、エラー率など。
**初出**: 第2章

### PromQL (Prometheus Query Language)
**定義**: Prometheusに格納されたメトリクスを問い合わせるための専用クエリ言語。
**初出**: 第2章

### 構造化ログ (Structured Logging)
**定義**: キーバリュー形式（JSON等）で出力されるログ。機械的なパース・フィルタリングが容易。
**初出**: 第3章

### 分散トレーシング (Distributed Tracing)
**定義**: マイクロサービス間をまたがるリクエストの流れを追跡する手法。各サービスでのスパンを結合してトレースを構成する。
**初出**: 第4章

### スパン (Span)
**定義**: 分散トレースにおける1つの処理単位。開始時刻、終了時刻、メタデータを持つ。
**初出**: 第4章

### コンテキスト伝播 (Context Propagation)
**定義**: サービス間の呼び出し時にトレースIDやスパンIDなどのコンテキスト情報をHTTPヘッダ等で伝達する仕組み。
**初出**: 第4章

### Three Pillars
**定義**: Observabilityの三本柱。メトリクス、ログ、トレースの3つを指す。
**初出**: 第5章

### SLI (Service Level Indicator)
**定義**: サービスの品質を測定する具体的な指標。レイテンシ、エラー率、スループット等。
**初出**: 第5章

### SLO (Service Level Objective)
**定義**: SLIに対する目標値。例: 「99.9%のリクエストが200ms以内に応答する」。
**初出**: 第5章

### Exemplars
**定義**: メトリクスデータポイントにトレースIDを紐づける仕組み。メトリクスからトレースへのドリルダウンを可能にする。
**初出**: 第5章

## Service Mesh関連

### サービスメッシュ (Service Mesh)
**定義**: マイクロサービス間の通信を制御・観測するためのインフラストラクチャレイヤー。アプリケーションコードを変更せずにトラフィック管理、セキュリティ、可観測性を提供する。
**初出**: 第6章

### サイドカー (Sidecar)
**定義**: アプリケーションコンテナと同じPod内で動作する補助コンテナ。Service Meshではプロキシとして通信を仲介する。
**初出**: 第6章

### mTLS (Mutual TLS)
**定義**: サーバーとクライアントの双方が証明書を提示して相互認証を行うTLS通信。Service Meshでサービス間通信の暗号化と認証に使用。
**初出**: 第6章

### eBPF (Extended Berkeley Packet Filter)
**定義**: Linuxカーネル内でサンドボックス化されたプログラムを実行する技術。Ciliumがサイドカーなしでネットワーク制御を実現するために使用する。
**初出**: 第7章

## Security関連

### RBAC (Role-Based Access Control)
**定義**: ロール（役割）に基づいてKubernetesリソースへのアクセスを制御する認可機構。
**初出**: 第9章

### NetworkPolicy
**定義**: KubernetesにおけるPod間のネットワーク通信を制御するリソース。許可する通信をホワイトリスト形式で定義する。
**初出**: 第9章

### Admission Control
**定義**: Kubernetes APIサーバーがリソースの作成・変更リクエストを受け付ける前に、ポリシーに基づいて許可・拒否する仕組み。
**初出**: 第10章

### Policy as Code
**定義**: セキュリティポリシーやコンプライアンスルールをコードとして記述・管理するアプローチ。OPA/Gatekeeperが代表的。
**初出**: 第10章

### SBOM (Software Bill of Materials)
**定義**: ソフトウェアに含まれるコンポーネント（ライブラリ、依存関係）の一覧。サプライチェーンセキュリティの基盤。
**初出**: 第11章

### コンテナイメージ署名 (Container Image Signing)
**定義**: コンテナイメージにデジタル署名を付与し、改ざんされていないことを検証可能にする仕組み。cosign等で実装する。
**初出**: 第11章

## CI/CD・GitOps関連

### GitOps
**定義**: Gitリポジトリを唯一の信頼できる情報源（Single Source of Truth）とし、宣言的な設定とReconciliation Loopによりインフラ・アプリケーションを管理するプラクティス。
**初出**: 第13章

### Reconciliation Loop
**定義**: Gitリポジトリの宣言的な状態と実際のクラスタ状態を定期的に比較し、差分があれば自動的に修正するループ処理。
**初出**: 第13章

### Progressive Delivery
**定義**: Canaryデプロイやブルーグリーンデプロイなど、段階的にトラフィックを切り替えてリスクを最小化するデプロイ手法の総称。
**初出**: 第14章

### Canaryデプロイ (Canary Deployment)
**定義**: 新バージョンに少量のトラフィックを流し、メトリクスを監視しながら段階的にトラフィック比率を上げるデプロイ手法。
**初出**: 第14章

### Auto Promotion
**定義**: Canaryデプロイにおいて、メトリクス分析の結果が基準を満たした場合に自動的に次のステップに進める機能。
**初出**: 第14章

## Platform Engineering関連

### IDP (Internal Developer Platform)
**定義**: 開発者がセルフサービスでインフラやアプリケーションを管理するための社内プラットフォーム。
**初出**: 第17章

### サービスカタログ (Service Catalog)
**定義**: 組織内のすべてのサービス、API、インフラリソースを一覧化し、オーナーシップやドキュメントを紐づけたカタログ。
**初出**: 第17章

### Golden Path
**定義**: プラットフォームチームが提供する、推奨されるサービス構築・デプロイの標準パス。開発者が「正しい道」を迷わず進めるようにする。
**初出**: 第17章

### XRD (Composite Resource Definition)
**定義**: Crossplaneにおいて、複数のインフラリソースを抽象化した独自のAPIを定義するためのリソース。
**初出**: 第18章

## Kubernetes基本用語

### Kustomize
**定義**: Kubernetesマニフェストをテンプレートなしでカスタマイズする仕組み。base（共通）とoverlays（環境別）の構造でマニフェストの差分を管理する。
**初出**: 第1章

### DaemonSet
**定義**: クラスタ内の全ノード（または指定ノード）に1つずつPodを配置するKubernetesリソース。ログ収集エージェント等に使用。
**初出**: 第3章

### CRD (Custom Resource Definition)
**定義**: Kubernetesに独自のリソースタイプを追加する仕組み。ArgoCD、Crossplane等多くのツールがCRDでAPIを拡張する。
**初出**: 第13章

## ツール名表記

本書では以下の表記で統一する:

| 表記 | 備考 |
|------|------|
| Prometheus | |
| Grafana | |
| Fluent Bit | スペースあり、Bは大文字 |
| Loki | Grafana Lokiの略称 |
| OpenTelemetry | 略称はOTel |
| Jaeger | |
| Istio | |
| Cilium | |
| Hubble | Ciliumの可観測性コンポーネント |
| Envoy | Envoy Proxy |
| OPA | Open Policy Agent |
| Gatekeeper | OPA Gatekeeper |
| Trivy | |
| cosign | 小文字始まり |
| Sigstore | |
| Falco | |
| ArgoCD | Argo CDではなくArgoCDで統一 |
| Argo Rollouts | スペースあり |
| GitHub Actions | |
| Backstage | |
| Crossplane | |
| Kustomize | |
| Helm | |
| OKE | Oracle Container Engine for Kubernetes |
| OCIR | Oracle Cloud Infrastructure Registry |

---

## 索引（五十音順）

### あ行

### か行
- [コンテキスト伝播](#コンテキスト伝播-context-propagation)
- [コンテナイメージ署名](#コンテナイメージ署名-container-image-signing)
- [構造化ログ](#構造化ログ-structured-logging)

### さ行
- [サービスカタログ](#サービスカタログ-service-catalog)
- [サービスメッシュ](#サービスメッシュ-service-mesh)
- [サイドカー](#サイドカー-sidecar)
- [スパン](#スパン-span)

### た行

### な行

### は行
- [分散トレーシング](#分散トレーシング-distributed-tracing)

### ま行
- [メトリクス](#メトリクス-metrics)

### や行

### ら行

### わ行

### A-Z
- [Admission Control](#admission-control)
- [Auto Promotion](#auto-promotion)
- [Canaryデプロイ](#canaryデプロイ-canary-deployment)
- [CRD](#crd-custom-resource-definition)
- [DaemonSet](#daemonset)
- [eBPF](#ebpf-extended-berkeley-packet-filter)
- [Exemplars](#exemplars)
- [GitOps](#gitops)
- [Golden Path](#golden-path)
- [IDP](#idp-internal-developer-platform)
- [Kustomize](#kustomize)
- [mTLS](#mtls-mutual-tls)
- [NetworkPolicy](#networkpolicy)
- [Policy as Code](#policy-as-code)
- [Progressive Delivery](#progressive-delivery)
- [PromQL](#promql-prometheus-query-language)
- [RBAC](#rbac-role-based-access-control)
- [Reconciliation Loop](#reconciliation-loop)
- [SBOM](#sbom-software-bill-of-materials)
- [SLI](#sli-service-level-indicator)
- [SLO](#slo-service-level-objective)
- [Three Pillars](#three-pillars)
- [XRD](#xrd-composite-resource-definition)
