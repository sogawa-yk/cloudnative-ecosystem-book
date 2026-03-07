# 第4章 仕様書: Traces — OpenTelemetry + Jaeger

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第4章 |
| タイトル | Traces — OpenTelemetry + Jaeger |
| 所属 | Part 1: Observability |
| 性質 | 概念 + 実践 |
| ページ数（目安） | 20p |
| 目的 | 分散トレーシングの概念とOpenTelemetryのアーキテクチャを理解し、サンプルアプリケーションにOTel SDKを計装してJaegerでトレースを可視化・分析できるようになる |

## 前提知識

- 第1章の内容（サンプルアプリケーションがbook-app Namespaceで稼働していること）
- Kubernetesの基本リソース
- Helmチャートの基本的な利用方法
- HTTPヘッダーの基本概念

## 節の構成

### 4.1 なぜ分散トレーシングが必要か — サンプルアプリの課題から

**概要**: 第1章で確立したサンプルアプリケーションを起点に、マイクロサービス環境でリクエストの流れを追跡する困難さを具体的に示す。「フロントエンドからのリクエストが遅いが、APIゲートウェイ・商品サービス・注文サービス・DBのどこがボトルネックか分からない」という課題を提示する。

**図表**:
- 図4.1: マイクロサービス間のリクエストフロー — トレーシングなしでは因果関係が見えない問題

**キーポイント**:
- メトリクス（第2章）は「何が遅いか」を示すが「なぜ遅いか」のリクエスト単位の因果関係は示せない
- ログ（第3章）は各サービスの詳細を記録するが、サービス間の呼び出し関係を紐付けるのが困難
- 分散トレーシングによる解決: リクエスト全体のライフサイクルを1つのトレースとして可視化

### 4.2 分散トレーシングの基本概念

**概要**: 分散トレーシングの基本概念（Trace / Span / SpanContext / Propagation）を解説する。1つのリクエストがTraceとして表現され、各サービスでの処理がSpanとしてツリー構造を形成する仕組みを説明する。

**図表**:
- 図4.2: Trace / Span / SpanContextの関係図（ウォーターフォール図のテキスト表現）
- 図4.3: コンテキスト伝播（Context Propagation）の仕組み — HTTPヘッダーによるtrace IDの伝播

**キーポイント**:
- Trace: 1つのリクエストの全体を表す。一意のTrace IDで識別
- Span: Trace内の個々の処理単位。Span ID、親Span ID、開始/終了時間、タグ、ログを持つ
- SpanContext: Span間で伝播される最小限の情報（Trace ID, Span ID, Trace Flags）
- Context Propagation: HTTPヘッダー（W3C Trace Context: `traceparent`ヘッダー）による伝播
- Sampling: 全リクエストをトレースするとコストが膨大になるため、サンプリング戦略が必要

### 4.3 OpenTelemetryのアーキテクチャ

**概要**: OpenTelemetry（OTel）のアーキテクチャを解説する。API / SDK / Collector / Exporterの各レイヤーの役割と、ベンダーニュートラルなテレメトリ基盤としてのOTelの位置付けを説明する。OTelがTraces / Metrics / Logsの3つのシグナルを統一的に扱う設計であることを示す。

**図表**:
- 図4.4: OpenTelemetryのアーキテクチャ全体図（API / SDK / Collector / Backend）
- 図4.5: OTel Collectorの内部構造（Receiver → Processor → Exporter）

**キーポイント**:
- OTelの設計思想: ベンダーニュートラル、3つのシグナル（Traces / Metrics / Logs）の統一
- API層: 計装用のインタフェース定義（言語別SDK非依存）
- SDK層: APIの実装、サンプリング、バッチ処理
- OTel Collector: テレメトリデータの受信・加工・転送を行うエージェント/ゲートウェイ
  - Receiver: データの受信（OTLP, Jaeger, Zipkin等）
  - Processor: データの加工（バッチ処理、フィルタリング、属性追加）
  - Exporter: バックエンドへの転送（Jaeger, OTLP, Prometheus等）
- デプロイモデル: Agent（DaemonSet）+ Gateway（Deployment）パターン

### 4.4 サンプルアプリへのOTel SDK計装

**概要**: サンプルアプリケーション（Go）にOpenTelemetry SDKを組み込み、自動・手動計装を行う。HTTPクライアント/サーバーの自動計装と、ビジネスロジック固有のSpanを手動で追加する方法を実装する。

**図表**:
- 図4.6: サンプルアプリへの計装ポイントマップ — 各サービスのどこにSpanを追加するか

**キーポイント**:
- Go用OTel SDK（`go.opentelemetry.io/otel`）の導入
- TracerProviderの初期化とOTLP Exporterの設定
- 自動計装: `otelhttp`によるHTTPサーバー/クライアントの自動Span生成
- 手動計装: ビジネスロジック固有のSpan追加（DB操作、外部API呼び出し等）
- Span属性（Attributes）の追加: サービス名、リクエストパス、ユーザーID等
- Spanイベント（Events）の記録: エラー発生時の詳細情報
- Context Propagation: `otelhttp`による自動的なtraceparentヘッダーの注入/抽出

### 4.5 OTel Collectorのデプロイと設定

**概要**: OTel CollectorをHelmチャートでbook-observability Namespaceにデプロイする。Receiver / Processor / Exporterの設定を行い、サンプルアプリからのトレースデータをJaegerに転送するパイプラインを構築する。

**図表**:
- 図4.7: OTel Collectorのデプロイ構成図（サンプルアプリ → OTel Collector → Jaeger）

**キーポイント**:
- OTel Collector Helmチャートによるデプロイ
- Receiver設定: OTLP receiver（gRPC + HTTP）
- Processor設定: batch processor（パフォーマンス最適化）、memory_limiter（OOM防止）
- Exporter設定: OTLP exporter（Jaeger向け）
- Pipeline定義: traces パイプラインの構成
- サンプルアプリのOTLP Exporter接続先をCollectorのServiceに設定

### 4.6 Jaegerによるトレースの可視化と分析

**概要**: JaegerをHelmチャートでbook-observability Namespaceにデプロイし、収集したトレースデータを可視化・分析する。ウォーターフォール表示、サービス依存関係グラフ、パフォーマンスのボトルネック特定の方法を実習する。

**図表**:
- 図4.8: Jaeger UIのウォーターフォール表示例（テキスト図）
- 図4.9: Jaegerのサービス依存関係グラフ（DAG）

**キーポイント**:
- Jaeger Helmチャートによるデプロイ（all-in-oneモード）
- Jaeger UIでのトレース検索: サービス名、オペレーション名、タグ、期間によるフィルタリング
- ウォーターフォール表示の読み方: 各Spanの処理時間、親子関係、並列実行の把握
- サービス依存関係グラフ（DAG: Directed Acyclic Graph）の活用
- パフォーマンス分析: ボトルネックSpanの特定、遅延の原因調査
- サンプリング戦略の設定: Head-based sampling vs Tail-based sampling

## 図表リスト

| 図表番号 | タイトル | 種類 | 節 |
|----------|---------|------|-----|
| 図4.1 | トレーシングなしのリクエストフロー | テキスト図 | 4.1 |
| 図4.2 | Trace / Span / SpanContextの関係図 | テキスト図 | 4.2 |
| 図4.3 | コンテキスト伝播の仕組み | Mermaid | 4.2 |
| 図4.4 | OpenTelemetryのアーキテクチャ全体図 | Mermaid | 4.3 |
| 図4.5 | OTel Collectorの内部構造 | Mermaid | 4.3 |
| 図4.6 | サンプルアプリへの計装ポイントマップ | Mermaid | 4.4 |
| 図4.7 | OTel Collectorのデプロイ構成図 | Mermaid | 4.5 |
| 図4.8 | Jaeger UIのウォーターフォール表示例 | テキスト図 | 4.6 |
| 図4.9 | Jaegerのサービス依存関係グラフ | Mermaid | 4.6 |

## コード例

| コード番号 | 内容 | 言語 | 節 |
|-----------|------|------|-----|
| リスト4.1 | W3C Trace Context（traceparentヘッダー）の形式例 | Text | 4.2 |
| リスト4.2 | OTel SDK初期化（TracerProvider + OTLP Exporter） | Go | 4.4 |
| リスト4.3 | otelhttp による自動計装（HTTPサーバー） | Go | 4.4 |
| リスト4.4 | otelhttp による自動計装（HTTPクライアント） | Go | 4.4 |
| リスト4.5 | 手動計装によるカスタムSpanの追加 | Go | 4.4 |
| リスト4.6 | Span属性とイベントの設定 | Go | 4.4 |
| リスト4.7 | OTel Collector Helmインストールコマンド | Shell | 4.5 |
| リスト4.8 | OTel Collector設定（Receiver / Processor / Exporter / Pipeline） | YAML | 4.5 |
| リスト4.9 | Jaeger Helmインストールコマンド | Shell | 4.6 |
| リスト4.10 | サンプリング戦略の設定 | YAML | 4.6 |

## 章末の理解度チェック

1. Trace, Span, SpanContextの関係を説明し、1つのリクエストが4つのサービスを通過する場合のSpanの構造を図示せよ
2. W3C Trace Contextの`traceparent`ヘッダーが含む情報を列挙し、コンテキスト伝播が分散トレーシングにおいて果たす役割を説明せよ
3. OTel Collectorを挟む（アプリ → Collector → Jaeger）メリットを、アプリから直接Jaegerに送信する場合と比較して3つ挙げよ
4. 自動計装と手動計装の違いを説明し、それぞれが適するユースケースを挙げよ
5. Head-based samplingとTail-based samplingの違いを説明し、各方式のトレードオフを述べよ

## 章間の接続

### 前の章からの接続
- **第1章**: サンプルアプリケーションが`book-app` Namespaceで稼働している状態を前提とする。1.5節で明示した「障害時に何が起きたか分からない」の課題を本章で解決する。
- **第2章・第3章との関係**: 第2章（Prometheus）、第3章（Fluent Bit + Loki）とは独立しており、並列で読むことが可能。ただし、メトリクス（第2章）は「何が起きているか」を、ログ（第3章）は「各サービスで何が起きたか」を、トレース（本章）は「サービス間の因果関係」をそれぞれ補完する関係にあることを意識する。

### 次の章への接続
- **第5章（統合 — Observability基盤）**: 本章で導入したJaegerのトレースをGrafanaダッシュボードに統合し、メトリクス・ログと相関分析する。Trace IDをキーにした「メトリクス → トレース → ログ」のドリルダウン分析を実現する。第5章ではTrace IDによるログとの紐付け、Exemplarを使ったメトリクスとの紐付けを行い、Three Pillarsの真の統合を完成させる。
- **第8章（統合 — メッシュとObservability）**: Service Mesh（Istio / Cilium）が自動的に生成するトレースデータと、本章で設定したアプリケーション計装のトレースを統合する方法を扱う。
