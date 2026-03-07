# 第13章 仕様書: GitOps — ArgoCD

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第13章 |
| タイトル | GitOps — ArgoCD |
| 所属 | Part 4: CI/CD & GitOps |
| 性質 | 概念 + 実践 |
| ページ数（目安） | 20p |
| 依存する章 | Ch.1（サンプルアプリケーションの構築） |
| 使用Namespace | `book-cicd`（ArgoCD）、`book-app`（サンプルアプリ） |

### 目的

Gitリポジトリを唯一の信頼できる情報源（Single Source of Truth）とし、宣言的な設定とReconciliation Loopによりアプリケーションを管理するGitOpsの原則を理解する。ArgoCDを導入し、第1章で構築したサンプルアプリケーションのマニフェストをGitOpsで管理する実践を通じて、自動同期と手動同期の使い分け、マルチ環境管理の設計力を身につける。

## 前提知識

- Kubernetesの基本リソース（Deployment, Service, Namespace）の理解
- Kustomizeによるbase/overlays方式の理解（第1章）
- Gitの基本操作（commit, push, branch）
- YAMLの読み書き

## 節の構成

### 13.1 GitOpsとは何か

**概要**: GitOpsの4原則（宣言的、バージョン管理、自動適用、自己修復）を解説し、従来のCI/CDパイプラインとの違いを明確にする。Push型デプロイとPull型デプロイの比較を通じて、GitOpsが解決する課題を示す。

**図表**:
- 図13.1: Push型デプロイとPull型（GitOps）デプロイの比較

**キーポイント**:
- GitOpsの4原則: 宣言的記述、Gitによるバージョン管理、自動適用、Reconciliation Loopによる自己修復
- Push型（CIツールがkubectl apply）とPull型（エージェントがGitを監視）の根本的な違い
- GitOpsにより得られる利点: 監査ログ、ロールバック、ドリフト検出

### 13.2 ArgoCDのアーキテクチャ

**概要**: ArgoCDの内部構成（API Server、Repo Server、Application Controller）と、それぞれの役割を解説する。CRD（Custom Resource Definition）としてのApplication、AppProject等の主要リソースを紹介する。

**図表**:
- 図13.2: ArgoCDのアーキテクチャと主要コンポーネント

**キーポイント**:
- API Server: Web UI・CLI・gRPC APIのエンドポイント
- Repo Server: Gitリポジトリからマニフェストを取得・レンダリング
- Application Controller: Reconciliation Loopを実行し、desired stateとlive stateを比較
- Redis: キャッシュとして使用

### 13.3 ArgoCDのインストールと初期設定

**概要**: HelmチャートによるArgoCDのインストール手順を示す。`book-cicd` Namespaceへのデプロイ、管理者パスワードの設定、argocd CLIの導入、Web UIへのアクセスまでを実践する。

**図表**:
- 図13.3: ArgoCDインストール後のリソース構成

**キーポイント**:
- Helmチャートのvalues.yamlで本番向け設定（HA構成、リソース制限）
- `book-cicd` Namespaceへのインストール
- 初期管理者パスワードの取得と変更
- Web UIへのアクセス方法（OKE環境: LoadBalancer / kind環境: port-forward）

### 13.4 Application CRDによるアプリケーション管理

**概要**: Application CRDの構造を詳細に解説する。repoURL、targetRevision、path、destination等の主要フィールドを説明し、第1章のサンプルアプリケーションをArgoCDで管理する最初のApplicationを作成する。

**図表**:
- 図13.4: Application CRDのフィールド構造とGitリポジトリとの対応

**キーポイント**:
- Application CRDの主要フィールド: source（repoURL, path, targetRevision）、destination（server, namespace）
- Kustomizeアプリケーションとの連携（source.kustomize設定）
- AppProjectによるアクセス制御（許可するリポジトリ、クラスタ、Namespace）
- 宣言的なApplication管理（App of Apps パターンの概要）

### 13.5 自動同期と手動同期の使い分け

**概要**: syncPolicy（自動同期 / 手動同期）の設定と、それぞれの適用場面を解説する。自動同期のオプション（selfHeal、prune）の動作を実際に確認し、本番環境では手動同期を推奨する理由を示す。

**図表**:
- 図13.5: Reconciliation Loopの動作フロー（自動同期 / 手動同期）
- 表13.1: 同期ポリシーの比較と推奨使用場面

**キーポイント**:
- `automated.selfHeal`: ドリフト（手動変更）を自動修正
- `automated.prune`: Gitから削除されたリソースをクラスタからも削除
- 手動同期: 本番環境での承認フロー、Sync Windowsとの組み合わせ
- 実践: Gitリポジトリのマニフェストを変更し、自動同期の動作を確認

### 13.6 Sync Waves・Hooks・ヘルスチェック

**概要**: 複数リソースのデプロイ順序制御（Sync Waves）、デプロイ前後のフック処理（Sync Hooks）、カスタムヘルスチェックの設定方法を解説する。

**図表**:
- 図13.6: Sync Wavesによるデプロイ順序制御の流れ

**キーポイント**:
- Sync Waves: アノテーション `argocd.argoproj.io/sync-wave` による順序制御
- Sync Hooks: PreSync（DB migration等）、PostSync（通知等）、SyncFail
- ヘルスチェック: Deploymentのロールアウト完了判定、カスタムヘルスチェックの定義
- 実践: サンプルアプリのDB migrationをPreSyncフックとして設定

### 13.7 マルチ環境管理とディレクトリ構成

**概要**: 開発・ステージング・本番等の複数環境をArgoCDで管理するためのリポジトリ構成パターンを解説する。Kustomize overlaysとの組み合わせ、ApplicationSetによる動的なApplication生成を紹介する。

**図表**:
- 図13.7: マルチ環境管理のディレクトリ構成パターン

**キーポイント**:
- モノレポ vs マルチレポのトレードオフ
- Kustomize overlaysとの連携: base + overlays/dev, overlays/staging, overlays/prod
- ApplicationSet: Gitディレクトリジェネレータによる動的Application生成
- 環境プロモーション戦略の概要（第16章への橋渡し）

## 図表リスト

| 図表番号 | タイトル | 形式 |
|----------|---------|------|
| 図13.1 | Push型デプロイとPull型（GitOps）デプロイの比較 | Mermaid |
| 図13.2 | ArgoCDのアーキテクチャと主要コンポーネント | Mermaid |
| 図13.3 | ArgoCDインストール後のリソース構成 | Mermaid |
| 図13.4 | Application CRDのフィールド構造とGitリポジトリとの対応 | Mermaid |
| 図13.5 | Reconciliation Loopの動作フロー（自動同期 / 手動同期） | Mermaid |
| 表13.1 | 同期ポリシーの比較と推奨使用場面 | 表 |
| 図13.6 | Sync Wavesによるデプロイ順序制御の流れ | Mermaid |
| 図13.7 | マルチ環境管理のディレクトリ構成パターン | テキスト図 |

## コード例

| コード番号 | 内容 | 言語 |
|-----------|------|------|
| コード13.1 | ArgoCD Helmインストールのvalues.yaml | YAML |
| コード13.2 | Application CRD（サンプルアプリ用） | YAML |
| コード13.3 | AppProject CRD（book-appプロジェクト） | YAML |
| コード13.4 | syncPolicy設定の各パターン | YAML |
| コード13.5 | Sync Wavesアノテーション付きマニフェスト | YAML |
| コード13.6 | PreSync Hookによるマイグレーションジョブ | YAML |
| コード13.7 | ApplicationSet（Gitディレクトリジェネレータ） | YAML |
| コード13.8 | argocd CLI基本操作コマンド集 | bash |

## 章末の理解度チェック

1. GitOpsの4原則を挙げ、従来のCI/CDパイプライン（Push型）との違いを説明せよ。
2. ArgoCDのReconciliation Loopにおいて、selfHealとpruneの動作の違いを説明し、それぞれを有効にすべき場面・無効にすべき場面を述べよ。
3. Application CRDのsource.pathとsource.kustomizeはどのような関係にあるか。Kustomize overlaysを使って複数環境を管理する場合のディレクトリ構成を図示せよ。
4. Sync Wavesを使ってデータベースマイグレーション → バックエンドデプロイ → フロントエンドデプロイの順序を制御するには、各リソースにどのようなアノテーションを付与すればよいか。
5. App of Appsパターンの利点と、ApplicationSetとの使い分けを説明せよ。

## 章間の接続

### 前の章からの接続（第12章 → 第13章）

第12章まででセキュリティ監査基盤の構築が完了した。Part 4ではCI/CD & GitOpsに焦点を移す。Part 4冒頭で「現状のサンプルアプリはkubectl applyによる手動デプロイであり、誰がいつ何を変更したか追跡できない」という課題を提示し、GitOpsの必要性を動機づける。

### 次の章への接続（第13章 → 第14章）

ArgoCDによるGitOps管理が確立された。しかし、新バージョンのデプロイは「全トラフィックを一度に切り替える」方式であり、問題のあるリリースが全ユーザーに影響する。第14章では、Argo Rolloutsを用いたProgressive Delivery（Canary / Blue-Green）により、段階的なトラフィック切り替えとメトリクスに基づく自動判定でデプロイリスクを最小化する手法を導入する。
