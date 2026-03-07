# 第12章 仕様書: 統合 ― セキュリティ監査基盤を構築する

## 章の概要

| 項目 | 内容 |
|------|------|
| **章番号** | 第12章 |
| **タイトル** | 統合 ― セキュリティ監査基盤を構築する |
| **所属** | Part 3: Security |
| **性質** | 統合 |
| **ページ数（目安）** | 20p |
| **目的** | Ch.9〜11の個別セキュリティ機能にFalcoのランタイム検知を加え、すべてのセキュリティイベントをObservability基盤と統合し、セキュリティ監査ダッシュボードを構築する |
| **依存する章** | Ch.5（Observability統合）、Ch.9（RBAC + NetworkPolicy）、Ch.10（OPA/Gatekeeper）、Ch.11（Trivy + Sigstore） |

## 前提知識

- 第5章で構築したObservability基盤（Prometheus + Grafana + Fluent Bit + Loki）が動作していること
- 第9章のRBAC・NetworkPolicy設定が適用済みであること
- 第10章のOPA/Gatekeeperが導入済みであること
- 第11章のTrivy・cosignの基本操作を理解していること

## 節の構成

### 12.1 セキュリティ監査基盤の設計

**概要**: Part 3で構築した個別セキュリティ機能を俯瞰し、統合監査基盤の全体アーキテクチャを設計する。各セキュリティイベントのデータフローを整理する。

**図表**:
- 図12.1: セキュリティ監査基盤の全体アーキテクチャ ― Falco / Gatekeeper / Trivy → Fluent Bit → Loki / Prometheus → Grafana

**キーポイント**:
- 監査基盤の目的: セキュリティイベントの一元可視化、リアルタイムアラート、コンプライアンスレポート
- データソースの整理: Falco（ランタイムイベント）、Gatekeeper（ポリシー違反）、Trivy（脆弱性スキャン結果）、Kubernetes Audit Log
- データフロー設計: ログ系 → Fluent Bit → Loki、メトリクス系 → Prometheus
- Namespace設計: book-security（セキュリティツール）、book-observability（Observability基盤）の連携

---

### 12.2 Falco ― ランタイムセキュリティ検知

**概要**: Falcoの概要とアーキテクチャを解説し、OKE環境にFalcoを導入してランタイムの異常検知を実現する。

**図表**:
- 図12.2: Falcoのアーキテクチャ ― カーネル（syscall） → Falcoエンジン → ルール評価 → アラート出力

**キーポイント**:
- Falcoの仕組み: システムコール（syscall）をカーネルレベルで捕捉し、ルールに基づいて異常を検知
- デフォルトルールセット: コンテナ内シェル起動、機密ファイルへのアクセス、予期しないネットワーク接続等
- OKE環境へのFalcoインストール（Helm）
- DaemonSetとしてのデプロイとノードレベルでの検知
- 実践: サンプルアプリのPodでシェルを起動し、Falcoがアラートを出すことを確認

---

### 12.3 Kubernetes Audit Log の活用

**概要**: Kubernetes APIサーバーのAudit Log（監査ログ）を取得・分析する仕組みを解説する。

**図表**:
- 図12.3: Audit Logのデータフロー ― APIサーバー → Audit Policy → Audit Backend → ログ収集

**キーポイント**:
- Audit Logとは: APIサーバーへのすべてのリクエスト（誰が、いつ、何を、どのリソースに対して行ったか）の記録
- Audit Policy: None / Metadata / Request / RequestResponseの4レベル
- OKE環境でのAudit Log取得方法
- セキュリティ上重要なイベント: Secretsへのアクセス、RBAC変更、Namespaceの作成・削除

---

### 12.4 Fluent Bit によるセキュリティログの集約

**概要**: Falcoのアラートログ、Gatekeeper違反ログ、Kubernetes Audit LogをFluent Bitで収集し、Lokiに送信する設定を行う。

**図表**:
- 図12.4: セキュリティログ集約パイプライン ― 各ソース → Fluent Bit（INPUT → FILTER → OUTPUT）→ Loki

**キーポイント**:
- Fluent BitのINPUT設定: Falcoログ（ファイル / stdout）、Gatekeeper Audit結果、Audit Log
- FILTER設定: ソースごとのラベル付与（`source=falco`, `source=gatekeeper`, `source=audit`）
- OUTPUT設定: Loki への送信（book-observabilityネームスペース）
- Ch.3（Fluent Bit + Loki）の構成を拡張する形で実装
- 実践: 各ソースからのログがLokiに到達していることをGrafana Exploreで確認

---

### 12.5 セキュリティメトリクスの収集

**概要**: Gatekeeper違反数、Trivyスキャン結果、Falcoアラート数をPrometheusメトリクスとして公開し、定量的なセキュリティモニタリングを実現する。

**図表**:
- 表12.1: セキュリティメトリクス一覧 ― メトリクス名、データソース、型、説明

**キーポイント**:
- Gatekeeper メトリクス: `gatekeeper_violations`（constraint別の違反数）
- Falco メトリクス: Falco Exporterを使ったPrometheus形式でのアラート公開
- Trivy メトリクス: Trivy Operatorによるクラスタ内スキャンとVulnerabilityReportのメトリクス化
- Prometheus ServiceMonitorの追加設定
- 実践: 各メトリクスがPrometheusに収集されていることをPromQLで確認

---

### 12.6 Grafana セキュリティダッシュボードの構築

**概要**: 収集したセキュリティログ・メトリクスを統合し、Grafanaでセキュリティ監査ダッシュボードを構築する。

**図表**:
- 図12.5: セキュリティダッシュボードのレイアウト設計（モックアップ）

**キーポイント**:
- ダッシュボードのセクション設計:
  - 概要パネル: 重大アラート数、未解決の脆弱性数、ポリシー違反数
  - Falcoパネル: ランタイムアラートのタイムライン、重大度別集計
  - Gatekeeperパネル: ポリシー違反のConstraint別内訳、dryrun vs deny
  - Trivyパネル: イメージ別脆弱性数、重大度分布、修正可能な脆弱性
  - Audit Logパネル: 重要なAPIリクエストのログビュー
- アラートルール: Criticalイベントに対するGrafanaアラートの設定
- 実践: ダッシュボードのJSON定義をConfigMapで管理しGrafanaにプロビジョニング

---

### 12.7 セキュリティイベントのシナリオテスト

**概要**: 構築したセキュリティ監査基盤の動作を検証するため、意図的にセキュリティ違反を発生させて検知・可視化の一連のフローを確認する。

**図表**:
- 図12.6: セキュリティイベントの検知フロー ― 違反発生 → 検知 → ログ/メトリクス → ダッシュボード → アラート

**キーポイント**:
- シナリオ1: privilegedコンテナのデプロイ試行 → Gatekeeper拒否 → ダッシュボードに違反記録
- シナリオ2: 署名なしイメージのデプロイ試行 → Gatekeeper拒否 → 違反メトリクス増加
- シナリオ3: Pod内でシェル起動 → Falcoアラート → Lokiにログ → ダッシュボード表示
- シナリオ4: 脆弱性を含むイメージのデプロイ → Trivy Operatorが検出 → ダッシュボード表示
- 各シナリオの期待される結果と確認手順

---

### 12.8 まとめとPart 3の振り返り

**概要**: Part 3全体の成果を振り返り、セキュリティ基盤の全体像を再確認する。Part 4（CI/CD & GitOps）への接続を示す。

**図表**:
- 図12.7: Part 3完成後のサンプルアプリ全体図 ― RBAC + NetworkPolicy + Gatekeeper + Trivy + cosign + Falco + セキュリティダッシュボード

**キーポイント**:
- Part 3のまとめ:
  - Ch.9: クラスタレベルのアクセス制御とネットワーク分離
  - Ch.10: Admission Controlによるポリシーの自動強制
  - Ch.11: サプライチェーンセキュリティ（脆弱性スキャン・署名・検証）
  - Ch.12: ランタイム検知とセキュリティ監査基盤の統合
- セキュリティの4層防御: クラスタ層 → アドミッション層 → サプライチェーン層 → ランタイム層
- Part 4への接続: CI/CDパイプラインにセキュリティチェック（Trivyスキャン、cosign署名）を組み込み、「Secure by Default」なデリバリーパイプラインを構築する

## 図表リスト

| 番号 | 種類 | タイトル | 形式 |
|------|------|---------|------|
| 図12.1 | 図 | セキュリティ監査基盤の全体アーキテクチャ | Mermaid |
| 図12.2 | 図 | Falcoのアーキテクチャ | Mermaid |
| 図12.3 | 図 | Audit Logのデータフロー | Mermaid |
| 図12.4 | 図 | セキュリティログ集約パイプライン | Mermaid |
| 図12.5 | 図 | セキュリティダッシュボードのレイアウト設計 | テキスト図 |
| 図12.6 | 図 | セキュリティイベントの検知フロー | Mermaid |
| 図12.7 | 図 | Part 3完成後のサンプルアプリ全体図 | Mermaid |
| 表12.1 | 表 | セキュリティメトリクス一覧 | Markdown表 |

## コード例

| 番号 | 内容 | 言語 | 概要 |
|------|------|------|------|
| コード12.1 | Falcoインストール | bash | HelmによるFalcoのインストール手順 |
| コード12.2 | Falcoカスタムルール | YAML | サンプルアプリ固有の検知ルール定義 |
| コード12.3 | Fluent Bitセキュリティログ設定 | YAML | Falco/Gatekeeper/Auditログの収集設定 |
| コード12.4 | Falco Exporterの設定 | YAML | FalcoアラートをPrometheusメトリクス化 |
| コード12.5 | Trivy Operatorインストール | bash | Trivy OperatorのHelm導入 |
| コード12.6 | Prometheus ServiceMonitor追加 | YAML | セキュリティメトリクス用ServiceMonitor |
| コード12.7 | Grafanaダッシュボード定義 | JSON | セキュリティダッシュボードのConfigMap |
| コード12.8 | Grafanaアラートルール | YAML | Criticalイベント用アラート設定 |
| コード12.9 | シナリオテスト用マニフェスト | YAML | 意図的な違反を発生させるPod定義 |

## 章末の理解度チェック

1. **Falcoの検知メカニズム**: Falcoがランタイムの異常を検知する仕組みを、システムコールの観点から説明せよ。
2. **セキュリティの4層防御**: Part 3で構築した4つのセキュリティ層（クラスタ、アドミッション、サプライチェーン、ランタイム）のそれぞれが「いつ」「何を」防御するか整理せよ。
3. **メトリクスとログの使い分け**: セキュリティイベントの監視において、Prometheusメトリクスによる監視とLokiログによる監視をどのように使い分けるべきか述べよ。
4. **ダッシュボード設計**: セキュリティダッシュボードに最低限含めるべきパネルを4つ挙げ、それぞれの役割を説明せよ。
5. **インシデント対応フロー**: Falcoが「コンテナ内でのシェル起動」を検知した場合、ダッシュボード上での確認から対応完了までの手順を述べよ。

## 章間の接続

### 前の章からの接続（Ch.11 → Ch.12）
- Ch.9〜11で構築した個別セキュリティ機能（RBAC、NetworkPolicy、Gatekeeper、Trivy、cosign）を統合する
- Ch.5のObservability基盤（Prometheus + Grafana + Fluent Bit + Loki）をセキュリティ領域に拡張する形で構築する
- Part 1の統合章（Ch.5）と同じ「ツールの統合」パターンを踏襲し、読者が統合のアプローチに馴染めるようにする

### 次の章への接続（Ch.12 → Ch.13）
- Part 3で確立したセキュリティ基盤は、Part 4のCI/CDパイプラインに組み込まれる
- 具体的には、Ch.15（GitHub Actions）でTrivyスキャンとcosign署名をCIパイプラインに統合する
- Ch.12のセキュリティダッシュボードは、Ch.16（統合）でCI/CDイベントとも連携する
- Part 4はPart 3と独立して開始できるが（Ch.13はCh.1のみに依存）、Security特化パスの読者にはPart 3の完了を推奨する
