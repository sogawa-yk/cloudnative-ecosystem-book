# 第18章 仕様書: インフラ抽象化 ― Crossplane

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第18章 |
| タイトル | インフラ抽象化 ― Crossplane |
| 所属する部 | Part 5: Platform Engineering |
| 性質 | 概念 + 実践 |
| 目標ページ数 | 20p |
| 依存する章 | Ch.1（サンプルアプリケーションの構築） |
| 使用Namespace | `book-platform` |

### 目的

Crossplaneの「Control Plane of Control Planes」という思想を理解し、Kubernetesマニフェストによるインフラの宣言的管理を実践する。XRD（Composite Resource Definition）とCompositionを用いてインフラリソースを抽象化し、開発者がKubernetesネイティブなインターフェースでデータベースやキャッシュ等のインフラを自己プロビジョニングできる仕組みを構築する。

## 前提知識

### 本書で習得済みであること

- Kubernetesの基本リソースとkubectl操作（第0章〜第1章）
- サンプルアプリケーションのデプロイとKustomizeの基本（第1章）
- CRD（Custom Resource Definition）の概念（第13章で初出だが、本章でも改めて説明する）

### 本章で新たに必要な知識

- なし（Crossplane固有の概念は本章で解説する）

## 節の構成

### 18.1 インフラ管理の課題とCrossplaneの思想（4p）

#### 概要

従来のインフラ管理（手動プロビジョニング、Terraform等のIaCツール）の課題を整理し、Crossplaneが提唱する「Control Plane of Control Planes」の思想を解説する。KubernetesのReconciliation Loopをインフラ管理に拡張するというアプローチの意義を説明する。

#### 図表

- **図18.1**: インフラ管理アプローチの比較 ― 手動プロビジョニング、Terraform（命令的IaC）、Crossplane（宣言的・Reconciliation Loop）の3つのアプローチを比較する図。
- **図18.2**: Control Plane of Control Planes ― Kubernetes API Serverを統一的なコントロールプレーンとして、クラウドプロバイダーのAPIを抽象化する構図。

#### キーポイント

- Terraformとの違い：宣言的 + Reconciliation Loop（ドリフト検出と自動修復）
- Kubernetes APIをインフラ管理のインターフェースとして使う利点
- CRDによるKubernetes APIの拡張
- GitOps（ArgoCD）との親和性

### 18.2 Crossplaneのアーキテクチャ（4p）

#### 概要

Crossplaneのアーキテクチャを解説する。Provider、Managed Resource、XRD、Composition、Composite Resource（XR）、Claimの各概念と関係性を図示し、抽象化レイヤーの仕組みを説明する。

#### 図表

- **図18.3**: Crossplaneのコンポーネント階層 ― Provider → Managed Resource → Composition → XRD → Claim の階層関係を示す図。
- **表18.1**: Crossplaneの主要概念一覧 ― Provider、Managed Resource、XRD、Composition、Composite Resource（XR）、Claimの定義と役割。

#### キーポイント

- Provider：クラウドプロバイダーやサービスへの接続アダプタ
- Managed Resource：クラウドリソースの1:1マッピング
- XRDとComposition：抽象化レイヤーの核心
- Claim：開発者向けの簡潔なインターフェース

### 18.3 Crossplaneのインストールとプロバイダー設定（3p）

#### 概要

OKE上にCrossplaneをHelmチャートでインストールし、Providerの設定を行う。本章ではProvider-Kubernetes（Kubernetes内リソースのプロビジョニング）とProvider-Helm（Helmリリースの管理）を使用する。

#### 図表

- **図18.4**: Crossplaneのデプロイ構成 ― book-platform Namespace内のCrossplane Pod、Provider Pod、CRDの関係図。

#### キーポイント

- Helm chartによるCrossplaneのインストール
- Provider-KubernetesとProvider-Helmの導入
- ProviderConfigによる認証設定
- Crossplaneが生成するCRDの確認

### 18.4 XRDとCompositionによるインフラ抽象化（5p）

#### 概要

XRD（Composite Resource Definition）とCompositionを定義して、「データベース」と「キャッシュ」のインフラをKubernetesマニフェストとして宣言的に管理する仕組みを構築する。開発者はClaimを投入するだけでPostgreSQLインスタンスやRedisインスタンスがプロビジョニングされる。

#### 図表

- **図18.5**: XRD・Composition・Claimの関係 ― 開発者がClaim（例: `DatabaseClaim`）を作成 → XRDがスキーマを検証 → Compositionが具体的なManaged Resourceを生成する流れ。
- **図18.6**: データベース抽象化の具体例 ― `DatabaseClaim`から生成されるリソース群（Deployment、Service、PVC、ConfigMap）のマッピング図。

#### キーポイント

- XRDの定義：spec.versions、spec.claimNames、openAPIV3Schema
- Compositionの定義：resources配列、patches、base
- 抽象化の設計原則：開発者に公開するパラメータの選定
- パッチ（patches）によるパラメータのマッピング

### 18.5 Claimによるセルフサービスプロビジョニング（4p）

#### 概要

構築したXRD/Compositionを使って、開発者がClaimを投入してインフラをプロビジョニングする体験を実践する。データベースClaimとキャッシュClaimを作成し、サンプルアプリケーションから利用する。ドリフト検出と自動修復の動作も確認する。

#### 図表

- **表18.2**: DatabaseClaim / CacheClaim のパラメータ一覧 ― 開発者が指定するパラメータ（size、version、storageSize等）の説明。
- **図18.7**: ドリフト検出と自動修復 ― 手動でリソースを変更 → Crossplaneが差分を検出 → 宣言された状態に自動修復する流れ。

#### キーポイント

- Claimの作成と状態確認（kubectl get claim）
- プロビジョニングされたリソースの確認
- ドリフト検出と自動修復のデモ
- GitOps（ArgoCD）との組み合わせ：ClaimをGitで管理する

## 図表リスト

| 番号 | 種別 | タイトル | 節 | 形式 |
|------|------|---------|-----|------|
| 図18.1 | 図 | インフラ管理アプローチの比較 | 18.1 | Mermaid |
| 図18.2 | 図 | Control Plane of Control Planes | 18.1 | Mermaid |
| 図18.3 | 図 | Crossplaneのコンポーネント階層 | 18.2 | Mermaid |
| 表18.1 | 表 | Crossplaneの主要概念一覧 | 18.2 | Markdown表 |
| 図18.4 | 図 | Crossplaneのデプロイ構成 | 18.3 | Mermaid |
| 図18.5 | 図 | XRD・Composition・Claimの関係 | 18.4 | Mermaid |
| 図18.6 | 図 | データベース抽象化の具体例 | 18.4 | Mermaid |
| 表18.2 | 表 | DatabaseClaim / CacheClaimのパラメータ一覧 | 18.5 | Markdown表 |
| 図18.7 | 図 | ドリフト検出と自動修復 | 18.5 | Mermaid |

## コード例

| 番号 | 内容 | 言語 | 節 |
|------|------|------|-----|
| コード18.1 | Crossplane Helm valuesの主要設定 | YAML | 18.3 |
| コード18.2 | Provider-KubernetesのProviderConfig | YAML | 18.3 |
| コード18.3 | XRD定義（DatabaseCompositeResource） | YAML | 18.4 |
| コード18.4 | Composition定義（PostgreSQLのプロビジョニング） | YAML | 18.4 |
| コード18.5 | XRD定義（CacheCompositeResource） | YAML | 18.4 |
| コード18.6 | DatabaseClaim（開発者が投入するClaim） | YAML | 18.5 |
| コード18.7 | CacheClaim（開発者が投入するClaim） | YAML | 18.5 |
| コード18.8 | Claimの状態確認コマンド | Bash | 18.5 |

## 章末の理解度チェック

1. **CrossplaneとTerraformの違いを説明せよ。** 特にReconciliation Loopの観点から、インフラのドリフト検出・修復の仕組みを比較せよ。
2. **XRD、Composition、Claimの3つの概念の関係を説明せよ。** それぞれがインフラ抽象化のどのレイヤーに対応するか述べよ。
3. **Crossplaneの「Control Plane of Control Planes」とはどのような概念か。** Kubernetes APIをインフラ管理に拡張することの利点を2つ挙げよ。
4. **XRDの設計において、開発者に公開するパラメータをどのような基準で選定すべきか。** 抽象化の粒度に関する考慮事項を述べよ。
5. **CrossplaneのClaimをGitリポジトリで管理し、ArgoCDで同期する利点を説明せよ。**

## 章間の接続

### 前の章からの接続

第17章でBackstageによるサービスカタログとSoftware Templateを構築した。Software Templateで新サービスのリポジトリを生成できるようになったが、サービスが必要とするインフラ（データベース、キャッシュ等）のプロビジョニングは手動のままである。本章ではこの課題を起点に、Crossplaneによるインフラの宣言的管理と開発者セルフサービスを導入する。

### 次の章への接続

本章で構築したCrossplaneのClaim機構と、第17章のBackstage Software Templateを組み合わせることで、第19章ではテンプレートからのサービス作成時にインフラのClaimも自動生成されるGolden Pathを実現する。さらにArgoCD、Observability、Service Mesh、Securityの全技術と統合し、書籍全体の集大成となるフルスタックプラットフォームを完成させる。
