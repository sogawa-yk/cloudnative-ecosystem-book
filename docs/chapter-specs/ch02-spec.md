# 第2章 仕様書: Metrics — Prometheus

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第2章 |
| タイトル | Metrics — Prometheus |
| 所属 | Part 1: Observability |
| 性質 | 概念 + 実践 |
| ページ数（目安） | 20p |
| 目的 | Pull型メトリクス収集の概念を理解し、サンプルアプリケーションにPrometheusを導入してカスタムメトリクスを収集・可視化・アラート設定ができるようになる |

## 前提知識

- 第1章の内容（サンプルアプリケーションがbook-app Namespaceで稼働していること）
- Kubernetesの基本リソース
- Helmチャートの基本的な利用方法

## 節の構成

### 2.1 なぜメトリクスが必要か — サンプルアプリの課題から

**概要**: 第1章で確立したサンプルアプリケーションを起点に、メトリクスがない状態で発生する具体的な問題を示す。「レスポンスが遅いがどのサービスが原因か分からない」「リソースの使用状況が見えない」といった課題を提示し、メトリクス収集の動機付けを行う。

**図表**:
- 図2.1: メトリクスなしの障害対応フロー vs メトリクスありの障害対応フロー

**キーポイント**:
- 障害発生時に手探りで原因を調査する非効率さ
- リソースのキャパシティプランニングが勘頼みになる問題
- メトリクスによる定量的な監視の必要性

### 2.2 Prometheusのアーキテクチャ

**概要**: Prometheusの全体アーキテクチャを解説する。Pull型のメトリクス収集モデル、Service Discoveryの仕組み、TSDBによるデータ保存、PromQLによるクエリ、Alertmanagerによるアラート通知の各コンポーネントの役割を説明する。

**図表**:
- 図2.2: Prometheusのアーキテクチャ全体図（Prometheus Server / Exporters / Service Discovery / Alertmanager / Grafana）
- 図2.3: Pull型 vs Push型メトリクス収集モデルの比較図

**キーポイント**:
- Pull型モデルの設計思想と利点（ターゲットの生死確認が自然にできる、中央集権的な設定管理）
- Service Discovery: Kubernetes SDによるPod / Serviceの自動検出
- TSDB: 時系列データの効率的な保存
- メトリクスの4つの型: Counter / Gauge / Histogram / Summary
- Push型との使い分け（Pushgatewayの用途）

### 2.3 Prometheusの導入 — Helmチャートによるデプロイ

**概要**: kube-prometheus-stack Helmチャートを使用してPrometheusをbook-observability Namespaceにデプロイする。Kustomize overlayと組み合わせた環境別の設定方法も示す。

**図表**:
- 図2.4: book-observability Namespaceのリソース配置図

**キーポイント**:
- kube-prometheus-stack Helmチャートの構成要素
- values.yamlのカスタマイズ（retention、storage、resource limits）
- Namespace `book-observability` の作成とデプロイ
- デプロイ後の動作確認（Prometheus UIへのアクセス）
- Service Discoveryでbook-app内のPodが自動検出されることの確認

### 2.4 サンプルアプリへのメトリクス計装

**概要**: サンプルアプリケーション（Go）にPrometheusクライアントライブラリを組み込み、カスタムメトリクスを公開する。`/metrics`エンドポイントの実装と、Prometheusのアノテーションによるスクレイプ設定を行う。

**図表**:
- 図2.5: メトリクス計装の全体フロー（アプリ → /metrics → Prometheus scrape）

**キーポイント**:
- Go用Prometheusクライアントライブラリ（`prometheus/client_golang`）の導入
- カスタムメトリクスの定義（HTTPリクエスト数、レスポンスタイム、アクティブコネクション数）
- `/metrics`エンドポイントの実装
- Podアノテーションによるスクレイプ設定（`prometheus.io/scrape`, `prometheus.io/port`, `prometheus.io/path`）
- ServiceMonitor CRDによるスクレイプ設定（kube-prometheus-stack利用時）

### 2.5 PromQLによるメトリクスのクエリ

**概要**: PromQLの基本構文を解説し、サンプルアプリのメトリクスに対して実用的なクエリを実行する。瞬時ベクトル、範囲ベクトル、集約関数、rate/increase関数などの基本操作を習得する。

**図表**:
- 表2.1: PromQLの基本関数一覧（rate, increase, sum, avg, histogram_quantile等）
- 図2.6: PromQLクエリの実行結果例（Prometheus UIのスクリーンショット相当のテキスト図）

**キーポイント**:
- セレクタとラベルマッチング
- 瞬時ベクトル（Instant Vector）と範囲ベクトル（Range Vector）
- rate() / increase() 関数によるCounter型メトリクスの変化率計算
- histogram_quantile() によるパーセンタイル算出（p50, p95, p99）
- 集約関数（sum, avg, max, min）とby / without句
- 実用クエリ例: リクエストレート、エラーレート、レイテンシパーセンタイル

### 2.6 アラート設計 — Alertmanager

**概要**: PrometheusのAlertmanagerを使ったアラート設計を解説する。アラートルールの定義方法、重要度の設計（critical / warning / info）、通知先のルーティング設定を行う。サンプルアプリに対する実用的なアラートルールを設定する。

**図表**:
- 図2.7: アラートの処理フロー（Prometheus → Alertmanager → 通知先）
- 表2.2: サンプルアプリ用アラートルール一覧

**キーポイント**:
- PrometheusRule CRDによるアラートルール定義
- for句によるアラートの持続時間指定（flapping防止）
- severity label（critical / warning / info）の設計指針
- Alertmanagerのルーティング設定（route / receiver / group_by）
- 実用アラート例: 高エラーレート、高レイテンシ、Pod再起動、ディスク使用率
- アラート疲れ（Alert Fatigue）を避けるための設計原則

## 図表リスト

| 図表番号 | タイトル | 種類 | 節 |
|----------|---------|------|-----|
| 図2.1 | メトリクスなし vs ありの障害対応フロー | テキスト図 | 2.1 |
| 図2.2 | Prometheusのアーキテクチャ全体図 | Mermaid | 2.2 |
| 図2.3 | Pull型 vs Push型メトリクス収集モデルの比較図 | Mermaid | 2.2 |
| 図2.4 | book-observability Namespaceのリソース配置図 | Mermaid | 2.3 |
| 図2.5 | メトリクス計装の全体フロー | Mermaid | 2.4 |
| 表2.1 | PromQLの基本関数一覧 | 表 | 2.5 |
| 図2.6 | PromQLクエリの実行結果例 | テキスト図 | 2.5 |
| 図2.7 | アラートの処理フロー | Mermaid | 2.6 |
| 表2.2 | サンプルアプリ用アラートルール一覧 | 表 | 2.6 |

## コード例

| コード番号 | 内容 | 言語 | 節 |
|-----------|------|------|-----|
| リスト2.1 | kube-prometheus-stack Helmインストールコマンド | Shell | 2.3 |
| リスト2.2 | values.yamlカスタマイズ（抜粋） | YAML | 2.3 |
| リスト2.3 | Goアプリへのメトリクス計装（main.go抜粋） | Go | 2.4 |
| リスト2.4 | カスタムメトリクスの定義と登録 | Go | 2.4 |
| リスト2.5 | ServiceMonitor CRDの定義 | YAML | 2.4 |
| リスト2.6 | PromQL実用クエリ集（リクエストレート、エラーレート、レイテンシ） | PromQL | 2.5 |
| リスト2.7 | PrometheusRule CRDによるアラートルール定義 | YAML | 2.6 |
| リスト2.8 | Alertmanagerのルーティング設定 | YAML | 2.6 |

## 章末の理解度チェック

1. PrometheusのPull型メトリクス収集モデルの利点を、Push型と比較して2つ挙げよ
2. メトリクスの4つの型（Counter / Gauge / Histogram / Summary）の違いを説明し、HTTPリクエスト数にはどの型が適切か理由とともに答えよ
3. `rate(http_requests_total[5m])` と `increase(http_requests_total[5m])` の違いを説明せよ
4. アラート疲れ（Alert Fatigue）を防ぐためのアラート設計の原則を3つ挙げよ
5. ServiceMonitor CRDとPodアノテーションによるスクレイプ設定の違いを説明せよ

## 章間の接続

### 前の章からの接続
- **第1章**: サンプルアプリケーションが`book-app` Namespaceで稼働している状態を前提とする。1.5節で明示した「パフォーマンスのボトルネックが見えない」「異常に気づけない」の課題を本章で解決する。

### 次の章への接続
- **第3章（Logs — Fluent Bit + Loki）**: メトリクスで「何が起きているか」は把握できるようになったが、「なぜ起きたか」の詳細はログが必要であることを示唆して接続する。
- **第4章（Traces — OpenTelemetry + Jaeger）**: 複数サービスにまたがるリクエストの因果関係はメトリクスだけでは追えないことを示唆して接続する。
- **第5章（統合 — Observability基盤）**: 本章で導入したPrometheusのメトリクスをGrafanaダッシュボードに統合し、ログ・トレースと相関分析する。
- **第14章（Progressive Delivery — Argo Rollouts）**: 本章で設定したメトリクスがCanaryデプロイの自動判定に利用される。
