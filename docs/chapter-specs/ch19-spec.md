# 第19章 仕様書: 統合 ― すべてをプラットフォームとしてまとめる

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第19章 |
| タイトル | 統合 ― すべてをプラットフォームとしてまとめる |
| 所属する部 | Part 5: Platform Engineering |
| 性質 | 統合 |
| 目標ページ数 | 20p |
| 依存する章 | Ch.5（Observability統合）、Ch.8（Mesh統合）、Ch.12（Security統合）、Ch.16（CI/CD統合）、Ch.17（Backstage）、Ch.18（Crossplane） |
| 使用Namespace | `book-app`、`book-platform`、`book-observability`、`book-mesh`、`book-security`、`book-cicd` |

### 目的

本書の最終章として、Part 1〜4で個別に構築してきたObservability、Service Mesh、Security、CI/CD & GitOpsの全技術と、Part 5のBackstage・Crossplaneを統合し、開発者がGolden Pathに沿ってサービスを立ち上げるだけで、全ての基盤が自動的に適用される「完成されたInternal Developer Platform」を実現する。書籍全体の集大成として、CloudNativeエコシステムが一体のプラットフォームとして機能することを実証する。

## 前提知識

### 本書で習得済みであること

- サンプルアプリケーションのデプロイとKustomize（第1章）
- Prometheus + Loki + Jaeger + GrafanaによるObservability基盤（第2章〜第5章）
- IstioまたはCiliumによるService Mesh（第6章〜第8章）
- RBAC + NetworkPolicy + OPA/Gatekeeper + Trivy/Sigstoreによるセキュリティ基盤（第9章〜第12章）
- ArgoCD + Argo Rollouts + GitHub ActionsによるCI/CD & GitOps（第13章〜第16章）
- BackstageによるIDP構築（第17章）
- Crossplaneによるインフラ抽象化（第18章）

### 本章で新たに必要な知識

- なし（本章は既習技術の統合である）

## 節の構成

### 19.1 プラットフォームの全体像（4p）

#### 概要

Part 1〜5の全技術がIDPとしてどのように統合されるかの全体像を提示する。各レイヤー（アプリケーション、CI/CD、インフラ、Observability、Security、Service Mesh）がどのように連携し、開発者にどのような体験を提供するかを設計する。開発者体験（Developer Experience）の設計原則を解説する。

#### 図表

- **図19.1**: 統合プラットフォームの全体アーキテクチャ ― Backstage（入口）→ Software Template → GitHub Actions（CI）→ ArgoCD（CD）→ OKEクラスタ（Crossplaneインフラ + アプリケーション + Istio + Observability + Security）の全レイヤーを俯瞰する図。Part 1〜5の全コンポーネントの配置と相互関係を示す。
- **図19.2**: Golden Pathのフロー ― 開発者が新サービスを立ち上げてから本番トラフィックを受けるまでの全ステップを時系列で示すフロー図。

#### キーポイント

- 全6つのNamespace（book-app、book-platform、book-observability、book-mesh、book-security、book-cicd）の連携
- IDPの設計原則：セルフサービス、自動化、ガードレール
- 開発者体験の設計：認知負荷の最小化と透明性のバランス
- Part 1〜4の成果物が「プラットフォームの構成要素」として機能する視点

### 19.2 Golden Path テンプレートの構築（5p）

#### 概要

第17章のBackstage Software Templateを拡張し、新サービス作成時に以下がすべて自動で生成・設定されるGolden Pathテンプレートを構築する。

1. GitHubリポジトリ生成（Goサービスのスケルトン + Kustomize構成）
2. GitHub Actionsワークフロー（CI: テスト、Trivyスキャン、cosign署名、OCIRプッシュ）
3. ArgoCD Application定義（GitOpsリポジトリへの自動登録）
4. CrossplaneのClaim（データベース等のインフラ宣言）
5. Istioリソース（VirtualService、DestinationRule）
6. NetworkPolicy（デフォルトのネットワーク制限）
7. OPA/Gatekeeperの対象への自動組み込み
8. OpenTelemetry計装の設定
9. Grafanaダッシュボードのテンプレート

#### 図表

- **図19.3**: Golden Pathテンプレートが生成するリソース一覧 ― テンプレートから1クリックで生成される全リソースのマッピング図。各リソースがPart 1〜5のどの技術に対応するかを色分けで示す。
- **表19.1**: Golden Pathテンプレートのパラメータ ― 開発者が入力するパラメータ（サービス名、チーム、データベース要否、キャッシュ要否、トラフィック管理方式等）の一覧。

#### キーポイント

- テンプレートの設計：最小限の入力で最大限の自動化
- 条件分岐のあるテンプレート（データベース要否でClaimの生成を切り替え等）
- 生成されるGitOpsリポジトリの構造
- テンプレートのバージョニングと更新戦略

### 19.3 End-to-Endデモ：新サービスの立ち上げ（5p）

#### 概要

Golden Pathテンプレートを使い、実際に新しいマイクロサービスを立ち上げる一連の流れをEnd-to-Endでデモする。Backstage UIからのテンプレート選択に始まり、CI/CDパイプラインの自動実行、OKEへのデプロイ、Observability基盤での観測、Service Meshへの自動組み込み、セキュリティポリシーの自動適用までをステップバイステップで確認する。

#### 図表

- **図19.4**: End-to-Endデモのシーケンス図 ― 時系列で「開発者の操作」と「プラットフォームの自動処理」を対比するシーケンス図。各ステップでどのコンポーネント（Backstage、GitHub Actions、ArgoCD、Crossplane、Istio等）が動作するかを示す。
- **図19.5**: デモ後のGrafanaダッシュボード ― 新サービスのメトリクス、ログ、トレースが自動的にGrafanaで可視化されている状態のテキスト図。

#### キーポイント

- 開発者の操作はBackstage UIでのテンプレート選択とパラメータ入力のみ
- GitHub Actionsによる自動CI（ビルド、テスト、スキャン、署名、プッシュ）
- ArgoCDによるGitOpsデプロイの自動同期
- CrossplaneによるDB/キャッシュの自動プロビジョニング
- Istioサイドカーの自動注入とトラフィック管理
- Observability基盤（Prometheus、Loki、Jaeger）での自動メトリクス収集
- OPA/Gatekeeperによるポリシー自動適用の確認

### 19.4 プラットフォームの運用と進化（3p）

#### 概要

構築したIDPの日常的な運用と、プラットフォームの継続的な進化について解説する。テンプレートの更新戦略、既存サービスへの新技術の段階的ロールアウト、プラットフォームチームと開発チームのフィードバックループを扱う。

#### 図表

- **図19.6**: プラットフォームの進化サイクル ― プラットフォームチームがフィードバックを受けてテンプレート・Composition・ポリシーを更新し、開発チームに提供するサイクル図。

#### キーポイント

- テンプレートのバージョニングと後方互換性
- 新技術の段階的導入（既存サービスへの影響を最小化）
- プラットフォームチームのメトリクス（テンプレート利用率、デプロイ頻度等）
- フィードバックループの設計

### 19.5 本書のまとめと次のステップ（3p）

#### 概要

書籍全体を振り返り、Part 0〜5で構築したCloudNativeプラットフォームの全体像をまとめる。読者が本書の内容をベースに、さらに発展させていくための方向性を示す。

#### 図表

- **図19.7**: CloudNativeエコシステムの全体マップ ― 本書で扱った全技術（Prometheus、Loki、Jaeger、Grafana、Istio、Cilium、OPA/Gatekeeper、Trivy、cosign、ArgoCD、Argo Rollouts、GitHub Actions、Backstage、Crossplane）とCNCF Landscapeにおける位置づけ。
- **表19.2**: Part別の成果物サマリ ― 各Partで構築した成果物と、最終的なプラットフォームにおける役割の一覧。

#### キーポイント

- Part 0〜5の積み上げの振り返り
- 本書でカバーしなかった領域（Knative、Dapr、FinOps等）への道標
- CNCFエコシステムの継続的な進化とキャッチアップの方法
- 読者への最終メッセージ：「ツールの習得」から「プラットフォーム思考」へ

## 図表リスト

| 番号 | 種別 | タイトル | 節 | 形式 |
|------|------|---------|-----|------|
| 図19.1 | 図 | 統合プラットフォームの全体アーキテクチャ | 19.1 | Mermaid |
| 図19.2 | 図 | Golden Pathのフロー | 19.1 | Mermaid |
| 図19.3 | 図 | Golden Pathテンプレートが生成するリソース一覧 | 19.2 | Mermaid |
| 表19.1 | 表 | Golden Pathテンプレートのパラメータ | 19.2 | Markdown表 |
| 図19.4 | 図 | End-to-Endデモのシーケンス図 | 19.3 | Mermaid |
| 図19.5 | 図 | デモ後のGrafanaダッシュボード | 19.3 | テキスト図 |
| 図19.6 | 図 | プラットフォームの進化サイクル | 19.4 | Mermaid |
| 図19.7 | 図 | CloudNativeエコシステムの全体マップ | 19.5 | Mermaid |
| 表19.2 | 表 | Part別の成果物サマリ | 19.5 | Markdown表 |

## コード例

| 番号 | 内容 | 言語 | 節 |
|------|------|------|-----|
| コード19.1 | 統合Golden Pathテンプレート（template.yaml） | YAML | 19.2 |
| コード19.2 | テンプレートのスケルトン：GitHub Actionsワークフロー | YAML | 19.2 |
| コード19.3 | テンプレートのスケルトン：ArgoCD Application | YAML | 19.2 |
| コード19.4 | テンプレートのスケルトン：Crossplane Claim | YAML | 19.2 |
| コード19.5 | テンプレートのスケルトン：Istio VirtualService + DestinationRule | YAML | 19.2 |
| コード19.6 | テンプレートのスケルトン：NetworkPolicy | YAML | 19.2 |
| コード19.7 | テンプレートのスケルトン：OpenTelemetry計装設定 | YAML | 19.2 |
| コード19.8 | デモ：Backstageからのサービス作成（パラメータ例） | YAML | 19.3 |
| コード19.9 | デモ：生成されたリソースの確認コマンド群 | Bash | 19.3 |
| コード19.10 | デモ：ArgoCDの同期状態確認 | Bash | 19.3 |

## 章末の理解度チェック

1. **本書で構築したプラットフォームにおいて、開発者が新サービスを立ち上げる際に必要な操作を列挙せよ。** 手動操作と自動化された処理を区別して説明すること。
2. **Golden Pathテンプレートから生成されるリソースを、Part 1〜5の対応技術ごとに分類せよ。**
3. **Backstage Software Template、ArgoCD、Crossplaneの3つがGolden Pathにおいてそれぞれどの役割を担うか説明せよ。**
4. **プラットフォームの「ガードレール」と「自由度」のバランスについて考察せよ。** 本書で構築したプラットフォームにおいて、開発者に強制されるルールと選択可能な項目をそれぞれ挙げよ。
5. **本書の内容をベースに、さらにプラットフォームを発展させるとしたらどのような技術・機能を追加するか。** 2つ以上の具体例を挙げて説明せよ。

## 章間の接続

### 前の章からの接続

第17章でBackstageによるサービスカタログとSoftware Templateを、第18章でCrossplaneによるインフラの宣言的管理を個別に構築した。本章ではこれらに加え、Part 1のObservability基盤（Ch.5）、Part 2のService Mesh（Ch.8）、Part 3のセキュリティ監査基盤（Ch.12）、Part 4のEnd-to-Endデリバリーパイプライン（Ch.16）のすべてを統合する。各Partで「個別ツールとして構築してきたもの」が、本章で「プラットフォームの構成要素」として一つにまとまる。

### 次の章への接続

本章は書籍の最終章である。19.5節で本書全体を振り返り、読者が次に進むべき方向性（本書でカバーしなかったCNCFエコシステムの技術、プラットフォーム思考の深化、組織への導入戦略等）を提示して書籍を締めくくる。付録A〜Dは必要に応じて参照するリファレンスとして位置づける。
