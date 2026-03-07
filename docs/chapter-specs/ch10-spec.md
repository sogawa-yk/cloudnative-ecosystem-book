# 第10章 仕様書: Policy as Code ― OPA / Gatekeeper

## 章の概要

| 項目 | 内容 |
|------|------|
| **章番号** | 第10章 |
| **タイトル** | Policy as Code ― OPA / Gatekeeper |
| **所属** | Part 3: Security |
| **性質** | 概念 + 実践 |
| **ページ数（目安）** | 15p |
| **目的** | OPA/GatekeeperによるAdmission Controlの仕組みを理解し、セキュリティポリシーをコードとして管理・強制する手法を習得する |
| **依存する章** | Ch.1（サンプルアプリケーションの構築） |

## 前提知識

- 第1章で構築したサンプルアプリケーションが動作していること
- Kubernetesの基本リソースの理解
- Admission Controlの概念（第9章9.2節で導入済み。ただし本章から読み始めても理解できるよう再説明する）

## 節の構成

### 10.1 Policy as Code とは何か

**概要**: セキュリティポリシーやコンプライアンスルールをコードとして記述・管理するアプローチの意義を解説する。手動レビューとの比較で自動化のメリットを示す。

**図表**:
- 図10.1: 手動レビュー vs Policy as Code ― ポリシー適用フローの比較

**キーポイント**:
- 手動レビューの限界: 見落とし、属人化、スケールしない
- Policy as Code の利点: 宣言的、バージョン管理可能、自動テスト可能、一貫性
- Kubernetes における Policy as Code の実現手段: Admission Webhook

---

### 10.2 OPA と Gatekeeper のアーキテクチャ

**概要**: OPA（Open Policy Agent）の汎用ポリシーエンジンとしての位置づけと、GatekeeperがKubernetes専用のAdmission Controllerとして機能する仕組みを解説する。

**図表**:
- 図10.2: Gatekeeperのアーキテクチャ ― APIサーバー → Validating Admission Webhook → Gatekeeper → OPA → Rego評価

**キーポイント**:
- OPA: 汎用ポリシーエンジン。入力（JSON）に対してRegoでポリシーを評価し、判定を返す
- Gatekeeper: OPAをKubernetesネイティブに統合するプロジェクト。CRDでポリシーを管理
- ConstraintTemplate: ポリシーのテンプレート（Regoロジックを定義）
- Constraint: テンプレートのインスタンス化（適用対象・パラメータを指定）
- OKE環境へのGatekeeperインストール手順

---

### 10.3 Rego言語の基礎

**概要**: OPAのポリシー記述言語であるRegoの基本文法を、Kubernetesリソースの検証を題材に解説する。

**図表**:
- 表10.1: Rego の基本構文 ― ルール、パッケージ、入力参照、関数

**キーポイント**:
- パッケージとルールの構造
- 入力オブジェクト（`input`）の参照: Admission Review のJSON構造
- 否定条件（`not`）、集合操作、イテレーション
- `violation` ルールの書き方（Gatekeeper形式）
- テスト: `opa test` によるユニットテストの実行

---

### 10.4 実践 ― セキュリティポリシーの実装

**概要**: 実務で頻出するセキュリティポリシーをGatekeeperで実装する。ConstraintTemplateの作成からConstraintの適用、違反検出まで一連の流れを実践する。

**図表**:
- 図10.3: ConstraintTemplate → Constraint → 違反検出の流れ

**キーポイント**:
- ポリシー1: privilegedコンテナの禁止
- ポリシー2: 信頼レジストリ以外のイメージ使用禁止（OCIR等の指定レジストリのみ許可）
- ポリシー3: latest タグの使用禁止
- ポリシー4: リソースリクエスト/リミットの必須化
- 各ポリシーの段階的適用: dryrun → warn → deny
- Gatekeeperポリシーライブラリ（gatekeeper-library）の活用

---

### 10.5 ポリシーの運用と監査

**概要**: Gatekeeperのaudit機能による既存リソースの違反検出、ポリシーのバージョン管理、CI/CDとの連携など運用面を解説する。

**図表**:
- 図10.4: Gatekeeperの監査フロー ― 定期スキャン → 違反検出 → Status更新

**キーポイント**:
- Audit機能: 既に存在するリソースに対するポリシー違反のスキャン
- `kubectl get constraint` による違反ステータスの確認
- ポリシーのGit管理: ConstraintTemplate/ConstraintをKustomizeで管理
- dryrunモードでの段階的ロールアウト
- Gatekeeper Mutation: リソースの自動修正（MutatingWebhook）

---

### 10.6 まとめと次章への橋渡し

**概要**: 本章の内容を振り返り、Admission Controlでカバーできない「ビルド時のセキュリティ」（イメージの脆弱性・署名）の課題を提示して第11章へつなげる。

**キーポイント**:
- 本章のまとめ: Gatekeeperでデプロイ時にポリシーを自動強制する仕組みを構築した
- 残された課題: 「信頼レジストリのイメージ」であっても脆弱性を含む場合がある。イメージそのものの安全性を保証するにはサプライチェーンセキュリティが必要
- 次章予告: Trivy + Sigstoreでイメージスキャン・署名・検証を行い、Gatekeeperと連携して署名済みイメージのみデプロイ可能にする

## 図表リスト

| 番号 | 種類 | タイトル | 形式 |
|------|------|---------|------|
| 図10.1 | 図 | 手動レビュー vs Policy as Code のポリシー適用フロー比較 | Mermaid |
| 図10.2 | 図 | Gatekeeperのアーキテクチャ | Mermaid |
| 図10.3 | 図 | ConstraintTemplate → Constraint → 違反検出の流れ | Mermaid |
| 図10.4 | 図 | Gatekeeperの監査フロー | Mermaid |
| 表10.1 | 表 | Regoの基本構文 | Markdown表 |

## コード例

| 番号 | 内容 | 言語 | 概要 |
|------|------|------|------|
| コード10.1 | Gatekeeperインストール | bash | Helmを使ったGatekeeperのインストール手順 |
| コード10.2 | privileged禁止のConstraintTemplate | YAML + Rego | privilegedコンテナを検出するRegoロジック |
| コード10.3 | privileged禁止のConstraint | YAML | ConstraintTemplateを適用対象に紐づける定義 |
| コード10.4 | 信頼レジストリ制限のConstraintTemplate | YAML + Rego | 許可レジストリ一覧と照合するRegoロジック |
| コード10.5 | latestタグ禁止のConstraintTemplate | YAML + Rego | イメージタグがlatestでないことを検証 |
| コード10.6 | Regoユニットテスト | Rego | opa testで実行するテストケース |
| コード10.7 | Kustomizeでのポリシー管理 | YAML | ConstraintTemplate/ConstraintをKustomize構成で管理 |

## 章末の理解度チェック

1. **OPAとGatekeeperの関係**: OPA単体とGatekeeperの違いを説明し、Kubernetes環境でGatekeeperを使う利点を2つ挙げよ。
2. **ConstraintTemplateとConstraint**: ConstraintTemplateとConstraintの役割の違いを説明し、1つのConstraintTemplateから複数のConstraintを作成するユースケースを示せ。
3. **Rego**: 「コンテナイメージのタグが `latest` でないこと」を検証するRegoルールの概略を書け。
4. **段階的適用**: Gatekeeperのdryrun → warn → denyの段階的適用が重要である理由を述べよ。

## 章間の接続

### 前の章からの接続（Ch.9 → Ch.10）
- Ch.9ではRBAC・NetworkPolicy・PSAによるクラスタレベルのセキュリティを構築した
- Ch.9の9.2節で Admission Control の概念を導入しており、Ch.10ではその仕組みをOPA/Gatekeeperで本格的に実装する
- Ch.9で「手動で設定していたセキュリティポリシーを自動強制するにはどうするか」という課題を提示し、Ch.10がその解答となる

### 次の章への接続（Ch.10 → Ch.11）
- Ch.10の「信頼レジストリ制限」ポリシーは「どのレジストリからのイメージか」を検査するが、イメージの中身（脆弱性の有無、改ざんの有無）は検査できない
- Ch.11ではTrivyによるイメージ脆弱性スキャンとcosignによるイメージ署名を導入し、サプライチェーン全体のセキュリティを確保する
- Ch.11で作成した署名検証ポリシーをGatekeeper（Ch.10）と連携させる実践も含まれる
