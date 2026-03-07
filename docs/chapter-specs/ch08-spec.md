# 第8章 仕様書: 統合 ― メッシュとObservabilityを連携する

## 章の概要

| 項目 | 内容 |
|------|------|
| **章番号** | 第8章 |
| **タイトル** | 統合 ― メッシュとObservabilityを連携する |
| **所属** | Part 2: Service Mesh |
| **性質** | 統合 |
| **ページ数（目安）** | 20p |
| **依存する章** | Ch.5（Observability統合）、Ch.6（Istio）、Ch.7（Cilium） |
| **Namespace** | book-mesh、book-observability、book-app |

### 目的

Part 2で導入したService Mesh（Istio / Cilium）が生成するテレメトリ（メトリクス、アクセスログ、トレース）を、Part 1で構築したObservability基盤（Prometheus + Loki + Jaeger + Grafana）に統合する。メッシュレイヤーとアプリケーションレイヤーの横断的な可観測性を実現し、サービス間通信の状態をObservability基盤から一元的に監視できる構成を完成させる。

### 前提知識

- 第5章: Grafanaによる統合ダッシュボード、Exemplars、SLI/SLO
- 第6章: Istioのアーキテクチャ、VirtualService、mTLS（Istioルートの場合）
- 第7章: Ciliumのアーキテクチャ、Hubble、CiliumNetworkPolicy（Ciliumルートの場合）
- PrometheusのServiceMonitor / PodMonitorの基本（第2章で学習済み）

> **注意**: 本章はIstio（第6章）とCilium（第7章）のどちらか一方のみを完了していれば進められる構成となっている。両方を完了している場合は、それぞれの統合手順を実施できる。

---

## 節の構成

### 8.1 メッシュが生成するテレメトリ ― 何が得られるのか

**概要**: Service Mesh（Istio / Cilium）が自動的に生成するテレメトリの種類と内容を整理する。アプリケーションの計装なしに得られるメトリクス、アクセスログ、トレースの範囲を明確にし、アプリケーションレイヤーのテレメトリとの違いを対比する。

**図表**:
- 表8.1: メッシュが生成するテレメトリ一覧（Istio / Cilium比較）
- 図8.1: アプリケーションテレメトリとメッシュテレメトリのレイヤー図

**キーポイント**:
- メッシュはアプリケーションコードの変更なしにリクエストレベルのテレメトリを生成する
- Istioはenvoyのメトリクス、アクセスログ、トレーススパンを生成する
- CiliumはHubbleフロー、Prometheusメトリクス（L3/L4/L7）を生成する
- アプリケーションテレメトリ（ビジネスロジック内部）とメッシュテレメトリ（通信レイヤー）は補完関係にある

---

### 8.2 IstioメトリクスをPrometheusへ統合する

**概要**: Istioが生成するEnvoyメトリクスをPrometheusで収集する設定を行う。ServiceMonitorの作成、Istio標準メトリクス（istio_requests_total等）の解説、Grafanaダッシュボードへのパネル追加までを実践する。

**図表**:
- 図8.2: Istioメトリクス収集のデータフロー図（Envoy → Prometheus → Grafana）
- 表8.2: Istio標準メトリクス一覧（主要なもの）

**キーポイント**:
- Istioは`istio_requests_total`、`istio_request_duration_milliseconds`等の標準メトリクスを公開する
- ServiceMonitorでEnvoyサイドカーのメトリクスエンドポイントをスクレイプ対象に追加する
- 第5章で構築したGrafanaダッシュボードにメッシュレイヤーのパネルを追加する

---

### 8.3 CiliumメトリクスをPrometheusへ統合する

**概要**: Cilium / HubbleのメトリクスをPrometheusで収集する設定を行う。cilium-agentとHubbleが公開するメトリクスの解説、ServiceMonitorの作成、Grafanaダッシュボードへの統合を実践する。

**図表**:
- 図8.3: Ciliumメトリクス収集のデータフロー図（cilium-agent → Prometheus → Grafana）
- 表8.3: Cilium / Hubble標準メトリクス一覧（主要なもの）

**キーポイント**:
- cilium-agentは`cilium_forward_count_total`、`cilium_drop_count_total`等のメトリクスを公開する
- HubbleはL7レベルのHTTPメトリクス（hubble_http_requests_total等）を提供する
- ServiceMonitorでcilium-agentとHubbleのメトリクスエンドポイントを追加する
- GrafanaダッシュボードにネットワークポリシーのDROP/FORWARD可視化パネルを追加する

---

### 8.4 アクセスログをFluent Bitへ統合する

**概要**: Istioのenvoyアクセスログ、またはCiliumのHubbleフローログを、Fluent Bit経由でLokiへ収集する設定を行う。メッシュのアクセスログとアプリケーションログを統合的にLogQLで検索できる環境を構築する。

**図表**:
- 図8.4: アクセスログ収集のデータフロー図（Envoy/Hubble → Fluent Bit → Loki → Grafana）

**キーポイント**:
- IstioのEnvoyアクセスログは構造化JSON形式で出力でき、Fluent Bitのパーサーで処理する
- HubbleのフローログはHubble Exporterでファイル出力し、Fluent Bitで収集する
- Lokiのラベルにサービスメッシュのメタデータ（source/destination、response_code等）を付与する
- LogQLでアプリケーションログとメッシュアクセスログを横断的に検索する

---

### 8.5 トレースをOpenTelemetryへ統合する

**概要**: IstioのEnvoyが生成するトレーススパンをOpenTelemetry Collector経由でJaegerに送信する設定を行う。アプリケーションの計装で生成したスパンとメッシュが生成したスパンが1つのトレースとして結合される様子を確認する。

**図表**:
- 図8.5: トレース統合のデータフロー図（Envoy → OTel Collector → Jaeger）
- 図8.6: 統合トレースの表示例（アプリケーションスパン + メッシュスパンが結合された状態）

**キーポイント**:
- IstioのEnvoyはW3C Trace Context / Zipkin形式でスパンを生成する
- OTel Collectorをトレース収集のハブとして配置し、アプリケーションとメッシュのスパンを統合する
- メッシュスパンにより、アプリケーション間のネットワーク遅延が可視化される
- CiliumのL7プロキシも同様のトレースヘッダ伝播をサポートする

---

### 8.6 統合ダッシュボードの完成と検証

**概要**: メッシュテレメトリを統合したGrafanaダッシュボードを完成させ、障害シミュレーションで検証する。メッシュレイヤーの異常（mTLSエラー、ポリシー拒否、リトライ多発）をObservability基盤から検知・調査するフローを実践する。

**図表**:
- 図8.7: Part 2完成時の全体アーキテクチャ図（サンプルアプリ + Observability基盤 + Service Mesh）
- 表8.4: メッシュ関連の障害シナリオと検知方法

**キーポイント**:
- メッシュレイヤーの異常はメトリクス（エラー率増加）とアクセスログ（4xx/5xxレスポンス）で検知する
- トレースでメッシュスパンのレイテンシを確認し、ネットワーク遅延かアプリケーション遅延かを切り分ける
- ポリシー拒否はCiliumのDROPメトリクス / IstioのRBACログで特定する
- SLI/SLOにメッシュメトリクスを組み込み、通信品質も含めた信頼性管理を実現する

---

### 8.7 本章のまとめと次章への橋渡し

**概要**: Part 2で構築した Service Mesh + Observability統合基盤の全体像を振り返る。Part 3（Security）での活用を予告し、セキュリティイベントの可観測性がなぜ重要かを示す。

**図表**:
- 表8.5: Part 1〜2で構築した基盤のコンポーネント一覧

**キーポイント**:
- Part 2の成果: アプリケーションレイヤーとメッシュレイヤーの統合可観測性
- Service Meshのテレメトリにより、アプリケーション計装だけでは見えなかったネットワークレイヤーの問題を検知できるようになった
- Part 3ではセキュリティポリシーの適用と、セキュリティイベントのObservability基盤への統合を扱う

---

## 図表リスト

| 図表番号 | タイトル | 種類 | 節 |
|---------|---------|------|-----|
| 表8.1 | メッシュが生成するテレメトリ一覧（Istio / Cilium比較） | 表 | 8.1 |
| 図8.1 | アプリケーションテレメトリとメッシュテレメトリのレイヤー図 | Mermaid（レイヤー図） | 8.1 |
| 図8.2 | Istioメトリクス収集のデータフロー図 | Mermaid（フローチャート） | 8.2 |
| 表8.2 | Istio標準メトリクス一覧 | 表 | 8.2 |
| 図8.3 | Ciliumメトリクス収集のデータフロー図 | Mermaid（フローチャート） | 8.3 |
| 表8.3 | Cilium / Hubble標準メトリクス一覧 | 表 | 8.3 |
| 図8.4 | アクセスログ収集のデータフロー図 | Mermaid（フローチャート） | 8.4 |
| 図8.5 | トレース統合のデータフロー図 | Mermaid（フローチャート） | 8.5 |
| 図8.6 | 統合トレースの表示例 | テキスト図 | 8.5 |
| 図8.7 | Part 2完成時の全体アーキテクチャ図 | Mermaid（アーキテクチャ図） | 8.6 |
| 表8.4 | メッシュ関連の障害シナリオと検知方法 | 表 | 8.6 |
| 表8.5 | Part 1〜2で構築した基盤のコンポーネント一覧 | 表 | 8.7 |

## コード例

| コード番号 | 内容 | 言語 | 節 |
|-----------|------|------|-----|
| コード8.1 | ServiceMonitor（Istio Envoyメトリクス用） | YAML | 8.2 |
| コード8.2 | Grafanaダッシュボード（Istioメトリクスパネル）のProvisioning | YAML / JSON | 8.2 |
| コード8.3 | ServiceMonitor（Cilium / Hubbleメトリクス用） | YAML | 8.3 |
| コード8.4 | Grafanaダッシュボード（Ciliumメトリクスパネル）のProvisioning | YAML / JSON | 8.3 |
| コード8.5 | Fluent Bit設定（Envoyアクセスログのパース） | YAML | 8.4 |
| コード8.6 | Fluent Bit設定（Hubbleフローログの収集） | YAML | 8.4 |
| コード8.7 | IstioのトレースバックエンドをOTel Collectorに向ける設定 | YAML | 8.5 |
| コード8.8 | OTel Collectorのパイプライン設定（メッシュスパン受信） | YAML | 8.5 |
| コード8.9 | 統合ダッシュボード用Kustomize構成 | YAML | 8.6 |

## 章末の理解度チェック

1. Service Meshが自動生成するテレメトリと、アプリケーションの計装で得られるテレメトリの違いを説明せよ。両者が補完関係にある理由を述べよ。
2. IstioのEnvoyメトリクスをPrometheusで収集するために必要な設定を説明せよ。
3. メッシュのアクセスログをLokiに統合する際、ラベルとしてどのようなメタデータを付与すべきか。その理由とともに3つ以上挙げよ。
4. アプリケーションスパンとメッシュスパンが1つのトレースとして結合されるために必要な条件を説明せよ。

## 章間の接続

### 前の章からの接続（Ch.5〜7 → Ch.8）

第5章で構築したObservability基盤（Prometheus + Loki + Jaeger + Grafana）はアプリケーションレイヤーのテレメトリを収集しているが、サービス間のネットワーク通信の詳細は把握できていない。第6章（Istio）と第7章（Cilium）でService Meshを導入したことで、メッシュレイヤーのテレメトリが生成されるようになった。本章では、これらのメッシュテレメトリをObservability基盤に統合し、アプリケーションからネットワークまでの横断的な可観測性を実現する。

### 次の章への接続（Ch.8 → Ch.9）

Part 2でService MeshとObservabilityの統合基盤が完成した。サービス間通信の暗号化（mTLS）やネットワークポリシーによるアクセス制御も導入したが、これはService Meshレイヤーでの対策にとどまる。Part 3では、Kubernetesクラスタ全体のセキュリティを体系的に強化する。第9章ではRBACとNetworkPolicyによるクラスタレベルのアクセス制御、第10章ではPolicy as Codeによるガバナンス、第11章ではサプライチェーンセキュリティを扱い、第12章でこれらをObservability基盤と統合したセキュリティ監査基盤を構築する。
