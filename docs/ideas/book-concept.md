# CloudNative エコシステム実践ガイド — 書籍企画書

## コンセプト

**K8s運用経験者が「次のステップ」として、CloudNativeエコシステムの各技術を体系的に学べる実践書。**

日本語書籍において、Kubernetes入門書は多数存在するが「K8sは分かった、で次は？」に答える本はほとんどない。本書はその空白地帯を埋める。

## 基本方針

| 項目 | 方針 |
|------|------|
| 想定読者 | K8s運用経験あり（Pod / Deployment / Service を理解済み）のエンジニア |
| 前提知識 | Kubernetesの基本リソースを扱える、YAML・Helmに抵抗がない |
| ページ数 | 300〜400ページ |
| 実行環境 | ネイティブKubernetes（kubeadm等）。ベンダーニュートラルだが、各マネージドK8s（OKE, EKS, GKE等）でも同様に動作する |
| クラウド依存 | なし（ベンダーニュートラル。kind等のローカル環境も一部利用可） |

## 構成フォーマット

各Partは以下の3層構造を繰り返す：

1. **概念** — なぜこの技術が必要か、アーキテクチャと設計思想を解説
2. **実践** — サンプルアプリに対して実際にツールを導入・設定するハンズオン
3. **統合** — Part内の個別ツールを組み合わせた統合構成の概念＋実践（各Partの最終章）

全編を通して **1つのサンプルアプリケーション** に技術を積み上げていく形式を取る。最終的にはフル装備のCloudNativeアプリケーションが完成する。

---

## 全体構成

### Part 0: 準備編（約30p）

#### Ch.0: この本の歩き方
- 前提知識、環境要件、本書のフォーマット（概念→実践→統合）

#### Ch.1: サンプルアプリケーションの構築
- 3〜4サービス構成のマイクロサービスアプリ（例：フロントエンド / APIゲートウェイ / 商品サービス / 注文サービス + DB）
- Deployment / Service / ConfigMap / Ingress でK8sにデプロイ
- 「素のK8s上で動くアプリ」をベースラインとして確立
- 現状の課題を明示：「ログがバラバラ」「障害時に何が起きたか分からない」「デプロイが手動」etc.

---

### Part 1: Observability（約80p）

#### Ch.2: Metrics — Prometheus
- **概念**: Pull型メトリクス収集、PromQL、アラート設計
- **実践**: サンプルアプリにPrometheusを導入、カスタムメトリクスをexpose、Alertmanager設定

#### Ch.3: Logs — Fluent Bit + Loki
- **概念**: ログ収集パイプラインの設計、構造化ログ、フィルタリング
- **実践**: Fluent BitをDaemonSetでデプロイ、サンプルアプリのログをLokiに集約

#### Ch.4: Traces — OpenTelemetry + Jaeger
- **概念**: 分散トレーシング、コンテキスト伝播、OpenTelemetryのアーキテクチャ
- **実践**: サンプルアプリにOTel SDKを計装、OTel Collector経由でJaegerにトレース送信

#### Ch.5: 統合 — Observability基盤を完成させる
- **概念**: Three Pillarsの相関、Grafanaによる統合ダッシュボード設計、SLI/SLO
- **実践**: Grafana上でPrometheus + Loki + Jaegerを統合、Exemplarsでメトリクスからトレースへドリルダウン、障害シミュレーションで全体を検証

---

### Part 2: Service Mesh（約70p）

#### Ch.6: Istio
- **概念**: サイドカーパターン、Envoyプロキシ、トラフィック管理の仕組み
- **実践**: サンプルアプリにIstio導入、mTLS有効化、トラフィック分割、タイムアウト/リトライ

#### Ch.7: Cilium
- **概念**: eBPFアプローチ、サイドカーレスの利点と制約、Hubble
- **実践**: CiliumでL7ポリシー適用、Hubbleでサービス間通信を可視化

#### Ch.8: 統合 — メッシュとObservabilityを連携する
- **概念**: メッシュが生成するテレメトリ、Observability基盤との接続設計
- **実践**: Istio/CiliumのメトリクスをPrometheusへ、アクセスログをFluent Bitへ、トレースをOTelへ流す統合構成。Part 1の基盤の上にメッシュの可視性を追加

---

### Part 3: Security（約70p）

#### Ch.9: クラスタセキュリティ — RBAC + NetworkPolicy
- **概念**: 認証・認可モデル、最小権限の原則、ネットワーク分離
- **実践**: サンプルアプリにRBAC設計適用、NetworkPolicyでサービス間通信を制限

#### Ch.10: Policy as Code — OPA / Gatekeeper
- **概念**: Admission Control、Rego言語、ポリシーライブラリ
- **実践**: 「privileged Podの禁止」「信頼レジストリ以外のイメージ禁止」などのポリシーを強制

#### Ch.11: サプライチェーンセキュリティ — Trivy + Sigstore
- **概念**: イメージ脆弱性、SBOM、署名と検証
- **実践**: Trivyでイメージ/マニフェストスキャン、cosignで署名、Gatekeeperで署名なしイメージの拒否

#### Ch.12: 統合 — セキュリティ監査基盤を構築する
- **概念**: セキュリティイベントの可視化、Audit Log、コンプライアンスダッシュボード
- **実践**: Falcoのランタイム検知 → Fluent Bitでログ集約 → Grafanaでセキュリティダッシュボード構築。OPA違反・Trivyスキャン結果もメトリクスとして統合

---

### Part 4: CI/CD & GitOps（約70p）

#### Ch.13: GitOps — ArgoCD
- **概念**: GitOpsの原則、Reconciliation Loop、Application CRD
- **実践**: サンプルアプリのマニフェストをGitOpsで管理、自動同期/手動同期の使い分け

#### Ch.14: Progressive Delivery — Argo Rollouts
- **概念**: Canary / Blue-Green / Analysis Template
- **実践**: サンプルアプリでCanaryデプロイ、Prometheusメトリクスを使ったAuto Promotion

#### Ch.15: CIパイプライン — GitHub Actions
- **概念**: コンテナビルドのベストプラクティス、マルチステージビルド、キャッシュ戦略
- **実践**: PR → ビルド → Trivyスキャン → cosign署名 → レジストリPush

#### Ch.16: 統合 — End-to-End デリバリーパイプライン
- **概念**: CI→CDの接続設計、Image Updater、環境プロモーション戦略
- **実践**: GitHub Actions（CI）→ イメージPush → ArgoCD Image Updater（CD）→ Argo Rollouts（Canary）→ Prometheusで自動判定。コードPushから本番デプロイまで全自動の一気通貫

---

### Part 5: Platform Engineering（約60p）

#### Ch.17: Internal Developer Platform — Backstage
- **概念**: Platform Engineeringの思想、サービスカタログ、Golden Path
- **実践**: Backstageでサンプルアプリのサービスカタログ構築、テンプレートからの新サービス作成

#### Ch.18: インフラ抽象化 — Crossplane
- **概念**: Control Plane of Control Planes、Composition、XRD
- **実践**: CrossplaneでDB/キャッシュなどのインフラをK8sマニフェストとして宣言的に管理

#### Ch.19: 統合 — すべてをプラットフォームとしてまとめる
- **概念**: Part 1〜4の全技術がIDPとしてどう統合されるか、開発者体験の設計
- **実践**: Backstageから新サービス作成 → 自動でGitOpsリポジトリ生成 → ArgoCD同期 → Observability / Mesh / Securityが自動適用される「Golden Path」のデモ

---

### 付録（約20p）

- kubeadmクラスタ構築リファレンス
- Helm チートシート
- 各ツールバージョン互換表
- トラブルシューティング集

---

## 本書の特徴

- **積み上げ型の構成**: Part 0で構築したサンプルアプリに各Partで技術を乗せていき、最終的にフル装備のCloudNativeアプリケーションが完成する
- **概念→実践→統合の3層構造**: 個別ツールの学習で終わらず、各Partの統合章で実務で必要な「組み合わせ方」まで踏み込む
- **Part間の橋渡し**: 統合章が次のPartへの自然な接続を担う（例：Part 4の統合章でPart 1のPrometheusやPart 3のTrivy/cosignの成果物を再利用）
- **ベンダーニュートラル**: ネイティブKubernetesを前提とし、どのクラウドやオンプレミス環境でも適用可能

## ページ配分サマリ

| Part | テーマ | 想定ページ数 |
|------|--------|-------------|
| Part 0 | 準備編（導入 + サンプルアプリ） | 約30p |
| Part 1 | Observability | 約80p |
| Part 2 | Service Mesh | 約70p |
| Part 3 | Security | 約70p |
| Part 4 | CI/CD & GitOps | 約70p |
| Part 5 | Platform Engineering | 約60p |
| 付録 | リファレンス | 約20p |
| **合計** | | **約400p** |
