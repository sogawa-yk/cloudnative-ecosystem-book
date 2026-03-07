# 書籍企画書 (Book Plan)

## 書籍概要

### タイトル
**CloudNativeエコシステム実践ガイド** ― Kubernetesの「その先」を体系的に学ぶ

### 形態
- 判型: B5
- 想定ページ数: 約400ページ
- 配布形態: 技術書典 / 電子書籍

### コンセプト
- **積み上げ型の構成**: 1つのサンプルアプリケーションに各Partで技術を乗せていき、最終的にフル装備のCloudNativeアプリケーションが完成する
- **概念→実践→統合の3層構造**: 個別ツールの学習で終わらず、各Partの統合章で実務で必要な「組み合わせ方」まで踏み込む
- **ベンダーニュートラル**: ネイティブKubernetesを前提とし、どのクラウド・オンプレミス環境でも適用可能

### ビジョン
Kubernetes入門書は多数存在するが「K8sは分かった、で次は？」に答える日本語書籍はほとんどない。本書はその空白地帯を埋める。Observability、Service Mesh、Security、CI/CD & GitOps、Platform Engineeringの5つの領域を、1つのサンプルアプリケーションを通して体系的に学ぶことで、読者はCloudNativeエコシステム全体を俯瞰し、実務で技術選定・導入ができるようになる。

## 対象読者

### プライマリーペルソナ
- インフラエンジニア / SRE / プラットフォームエンジニア
- Kubernetesの基本リソース（Pod / Deployment / Service / ConfigMap / Ingress）を運用した経験がある
- YAML・Helmに抵抗がない
- 「K8sクラスタは作れるが、Observabilityやセキュリティ、CI/CDをどう組み合わせればいいか分からない」という課題を持つ

### 前提知識
読者が本書を読む前に理解していることを前提とする:
- Kubernetesの基本リソース（Pod, Deployment, Service, ConfigMap, Ingress, Namespace）
- kubectlの基本操作
- コンテナの基本概念（Docker / Podman等でのビルド・実行経験）
- YAMLの読み書き
- Helmチャートの基本的な利用方法
- Git / GitHubの基本操作

### 前提としない知識
本書で説明する:
- Prometheus / Grafana / Loki / Jaeger等のObservabilityツール
- Istio / Cilium等のService Mesh
- OPA / Gatekeeper / Trivy / Sigstore等のセキュリティツール
- ArgoCD / Argo Rollouts等のGitOps・Progressive Deliveryツール
- Backstage / Crossplane等のPlatform Engineeringツール
- OpenTelemetryの計装方法

## 到達目標

読了後、読者が以下をできるようになること:

1. Prometheus + Loki + Jaeger + GrafanaによるObservability基盤を構築し、Three Pillars（メトリクス・ログ・トレース）を統合的に運用できる
2. IstioまたはCiliumを用いたService Meshを導入し、サービス間通信の可視化・制御・セキュリティ強化ができる
3. RBAC / NetworkPolicy / OPA Gatekeeper / Trivy / Sigstoreを組み合わせたセキュリティ基盤を設計・構築できる
4. GitHub Actions + ArgoCD + Argo Rolloutsによるコードプッシュから本番デプロイまでの一気通貫パイプラインを構築できる
5. Backstage + Crossplaneを活用したInternal Developer Platformの概念を理解し、Golden Pathを設計できる
6. 各領域の技術を「組み合わせて」統合的なCloudNativeプラットフォームとして運用する設計力を身につける

## 全体構成

### 部構成

| 部 | タイトル | 概要 | ページ（目安） |
|----|---------|------|--------------|
| Part 0 | 準備編 | 本書の歩き方とサンプルアプリケーションの構築 | 約30p |
| Part 1 | Observability | メトリクス・ログ・トレースの収集と統合ダッシュボード | 約80p |
| Part 2 | Service Mesh | Istio / Ciliumによるサービス間通信の制御と可視化 | 約70p |
| Part 3 | Security | クラスタセキュリティからサプライチェーンセキュリティまで | 約70p |
| Part 4 | CI/CD & GitOps | GitOps・Progressive Delivery・CIパイプラインの構築 | 約70p |
| Part 5 | Platform Engineering | IDP構築とすべての技術の統合 | 約60p |
| 付録 | リファレンス | kubeadm構築、Helmチートシート、トラブルシューティング | 約20p |

### 章構成

| 章 | タイトル | ページ（目安） | 性質 |
|----|---------|--------------|------|
| 第0章 | この本の歩き方 | 10p | 導入 |
| 第1章 | サンプルアプリケーションの構築 | 20p | 実践（ベースライン構築 + Kustomize） |
| 第2章 | Metrics — Prometheus | 20p | 概念 + 実践 |
| 第3章 | Logs — Fluent Bit + Loki | 20p | 概念 + 実践 |
| 第4章 | Traces — OpenTelemetry + Jaeger | 20p | 概念 + 実践 |
| 第5章 | 統合 — Observability基盤を完成させる | 20p | 統合 |
| 第6章 | Istio | 25p | 概念 + 実践 |
| 第7章 | Cilium | 25p | 概念 + 実践 |
| 第8章 | 統合 — メッシュとObservabilityを連携する | 20p | 統合 |
| 第9章 | クラスタセキュリティ — RBAC + NetworkPolicy | 20p | 概念 + 実践 |
| 第10章 | Policy as Code — OPA / Gatekeeper | 15p | 概念 + 実践 |
| 第11章 | サプライチェーンセキュリティ — Trivy + Sigstore | 15p | 概念 + 実践 |
| 第12章 | 統合 — セキュリティ監査基盤を構築する | 20p | 統合 |
| 第13章 | GitOps — ArgoCD | 20p | 概念 + 実践 |
| 第14章 | Progressive Delivery — Argo Rollouts | 15p | 概念 + 実践 |
| 第15章 | CIパイプライン — GitHub Actions | 15p | 概念 + 実践 |
| 第16章 | 統合 — End-to-End デリバリーパイプライン | 20p | 統合 |
| 第17章 | Internal Developer Platform — Backstage | 20p | 概念 + 実践 |
| 第18章 | インフラ抽象化 — Crossplane | 20p | 概念 + 実践 |
| 第19章 | 統合 — すべてをプラットフォームとしてまとめる | 20p | 統合 |
| 付録A | kubeadmクラスタ構築リファレンス | 8p | リファレンス |
| 付録B | Helmチートシート | 4p | リファレンス |
| 付録C | 各ツールバージョン互換表 | 4p | リファレンス |
| 付録D | トラブルシューティング集 | 4p | リファレンス |

## サンプルアプリケーション

### 構成
3〜4サービス構成のマイクロサービスアプリケーション:
- **フロントエンド**: Webフロントエンド（React等）
- **APIゲートウェイ**: リクエストルーティング
- **商品サービス**: 商品情報の管理
- **注文サービス**: 注文処理
- **データベース**: PostgreSQL等

### 役割
- Part 0で「素のK8s上で動くアプリ」としてベースラインを確立
- 各Partで技術を積み上げ、最終的にフル装備のCloudNativeアプリケーションへ
- 現状の課題を各Partの冒頭で明示し、その技術の必要性を実感させる

## 実行環境

- **メイン環境**: OKE（Oracle Container Engine for Kubernetes）
- **代替環境**: kind / minikube / kubeadm / 他のマネージドK8s（EKS, GKE等）
- **環境差分の吸収**: Kustomizeのbase + overlays方式で対応（第1章で解説）
- **コード例の言語**: Go（サンプルアプリ）、Python（ユーティリティスクリプト）
- **検証済み環境**: OKE v1.34.2（3ノード、Oracle Linux 8.10、CRI-O）

### Kustomize overlay戦略

サンプルアプリケーションのマニフェストは以下の構造で管理する:

```
k8s/
  base/                  # 環境非依存の共通マニフェスト
    deployment.yaml
    service.yaml
    kustomization.yaml
  overlays/
    oke/                 # OKE固有の設定（メイン）
      ingress.yaml       # OCI Load Balancer
      storage.yaml       # OCI Block Volume CSI
      kustomization.yaml
    kind/                # kind固有の設定
      ingress.yaml       # NGINX Ingress + NodePort
      storage.yaml       # hostPath
      kustomization.yaml
```

環境間で差異が出るポイント:
- **Ingress**: OKE（OCI Load Balancer） / kind（NGINX Ingress + NodePort）
- **StorageClass**: OKE（OCI Block Volume CSI） / kind（hostPath）
- **レジストリ**: OKE（OCIR） / kind（ローカルレジストリ）

本書ではKustomizeの仕組みを第1章で解説し、読者が自身の環境用overlayを作成できるようにする。

### Namespace設計

書籍のハンズオンで使用するNamespaceは `book-` プレフィックスで統一する:

| Namespace | 用途 | 対応Part |
|-----------|------|---------|
| `book-app` | サンプルアプリケーション本体 | Part 0 |
| `book-observability` | Prometheus / Loki / Jaeger / Grafana等 | Part 1 |
| `book-mesh` | Service Mesh関連 | Part 2 |
| `book-security` | Security関連 | Part 3 |
| `book-cicd` | ArgoCD / Argo Rollouts等 | Part 4 |
| `book-platform` | Backstage / Crossplane等 | Part 5 |

## 執筆方針

- **実務指向**: 概念の説明だけでなく、実際に手を動かして動かせるハンズオン形式
- **課題起点**: 各Part冒頭で「今のサンプルアプリの何が問題か」を明示してから技術を導入する
- **段階的複雑化**: Part 0のシンプルなアプリから、Part 5の完全なCloudNativeプラットフォームまで段階的に複雑さを積み上げる
- **再利用と接続**: 統合章でPart間の技術を組み合わせ、読者が「技術の組み合わせ方」を体感できるようにする
- **概念→実践→統合**: 各Partは個別ツールの概念・実践と、Part全体の統合の3層構造を繰り返す

## スコープ外

明示的にスコープ外とする項目:
- Kubernetes自体の入門的な解説（前提知識として扱う）
- 特定クラウドプロバイダーのマネージドサービスへの深い依存
- Kubernetes以外のコンテナオーケストレーション（Docker Swarm, Nomad等）
- サーバーレス / FaaS（Knative等）
- データベース / メッセージキューの詳細な運用（アプリの一部として利用するのみ）
- ネットワーキングの低レイヤー（CNIの実装詳細等）
- Windows / macOS上でのKubernetesクラスタ構築の詳細手順

## 成功指標

- 読者がサンプルアプリを通じて全5領域の技術を実際に動かせること
- 各統合章が「個別ツールの寄せ集め」ではなく「統合基盤」として機能していること
- 「K8sの次に何を学べばいいか」の見取り図として繰り返し参照される本になること
