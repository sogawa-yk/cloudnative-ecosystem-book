# 第9章 仕様書: クラスタセキュリティ ― RBAC + NetworkPolicy

## 章の概要

| 項目 | 内容 |
|------|------|
| **章番号** | 第9章 |
| **タイトル** | クラスタセキュリティ ― RBAC + NetworkPolicy |
| **所属** | Part 3: Security |
| **性質** | 概念 + 実践 |
| **ページ数（目安）** | 20p |
| **目的** | Kubernetesの認証・認可モデルとネットワーク分離の仕組みを理解し、サンプルアプリケーションに最小権限の原則を適用する |
| **依存する章** | Ch.1（サンプルアプリケーションの構築） |

## 前提知識

- 第1章で構築したサンプルアプリケーションが動作していること
- Kubernetesの基本リソース（Pod, Deployment, Service, Namespace）の理解
- kubectlの基本操作
- YAMLの読み書き

## 節の構成

### 9.1 Part 3 イントロダクション ― なぜセキュリティが必要か

**概要**: サンプルアプリケーションの現状のセキュリティ課題を洗い出し、Part 3全体で解決する領域（クラスタセキュリティ、ポリシー制御、サプライチェーンセキュリティ）の全体像を示す。

**図表**:
- 図9.1: Part 3のセキュリティ領域マップ ― クラスタ層・アドミッション層・サプライチェーン層の3層構造

**キーポイント**:
- サンプルアプリの現状: デフォルトServiceAccountで全Podが動作、Namespace間通信が無制限、privilegedコンテナの制約なし
- セキュリティは「後付け」ではなく「設計時から」組み込むべきである
- Part 3の3章（Ch.9〜11）は互いに独立して読める

---

### 9.2 Kubernetesの認証・認可モデル

**概要**: Kubernetes APIサーバーへのリクエストが認証（Authentication）、認可（Authorization）、Admission Controlの3段階で処理される仕組みを解説する。

**図表**:
- 図9.2: APIリクエストの処理フロー ― 認証 → 認可 → Admission Control → etcd

**キーポイント**:
- 認証: X.509証明書、Bearer Token、ServiceAccountトークン、OIDC
- 認可: RBAC（本書で採用）、ABAC、Webhook
- Admission Control: Mutating → Validating の2段階（Ch.10で詳述）
- OKE環境での認証設定の確認方法

---

### 9.3 RBAC ― ロールベースアクセス制御の設計

**概要**: RBAC（Role-Based Access Control）の4つのリソース（Role, ClusterRole, RoleBinding, ClusterRoleBinding）を解説し、サンプルアプリケーションに最小権限のRBAC設計を適用する。

**図表**:
- 図9.3: RBACリソースの関係図 ― Subject（User/Group/ServiceAccount）→ Binding → Role の紐づけ
- 表9.1: サンプルアプリの各サービスに割り当てるRole設計

**キーポイント**:
- Role vs ClusterRole: Namespace スコープとクラスタスコープの使い分け
- 最小権限の原則（Principle of Least Privilege）: 必要なリソース・操作のみ許可する
- デフォルトServiceAccountの危険性と、サービスごとのServiceAccount分離
- `kubectl auth can-i` による権限の確認方法
- 実践: サンプルアプリの各マイクロサービスに専用ServiceAccountとRoleを作成

---

### 9.4 NetworkPolicy ― Pod間通信の制御

**概要**: NetworkPolicyによるPod間ネットワーク通信のホワイトリスト制御を解説し、サンプルアプリケーションのサービス間通信を必要最小限に制限する。

**図表**:
- 図9.4: NetworkPolicy適用前後のトラフィックフロー比較図
- 図9.5: サンプルアプリの通信マトリクス ― 許可する通信パスの設計

**キーポイント**:
- NetworkPolicyの基本: podSelector、namespaceSelector、ipBlock
- Ingress（受信）ルールとEgress（送信）ルールの設計
- デフォルトDenyポリシー: まず全通信を拒否し、必要な通信のみ許可するアプローチ
- OKE環境でのCNI（Flannel / OCI VCN-Native Pod Networking）とNetworkPolicyのサポート状況
- 実践: サンプルアプリにデフォルトDeny + 個別Allow のNetworkPolicyを適用

---

### 9.5 SecurityContextとPod Security Standards

**概要**: Pod/コンテナレベルのセキュリティ設定（SecurityContext）と、Kubernetes標準のPod Security Standards（PSS）/ Pod Security Admission（PSA）を解説する。

**図表**:
- 表9.2: Pod Security Standardsの3つのレベル（Privileged / Baseline / Restricted）の比較

**キーポイント**:
- SecurityContext: runAsNonRoot、readOnlyRootFilesystem、allowPrivilegeEscalation、capabilities
- Pod Security Standards（PSS）: Privileged、Baseline、Restrictedの3レベル
- Pod Security Admission（PSA）: enforce、audit、warnの3モード
- 実践: book-appネームスペースにPSA labelsを設定し、Restrictedレベルを強制

---

### 9.6 ハンズオン ― サンプルアプリへのセキュリティ適用

**概要**: 9.3〜9.5の内容を統合し、サンプルアプリケーションに一貫したセキュリティ設計を適用する。Kustomizeのoverlayでセキュリティ設定を管理する。

**図表**:
- 図9.6: セキュリティ適用後のサンプルアプリアーキテクチャ図（RBAC + NetworkPolicy + PSA）

**キーポイント**:
- Kustomize overlayでのセキュリティマニフェスト管理
- 段階的な適用手順: ServiceAccount分離 → RBAC適用 → NetworkPolicy適用 → PSA強制
- 動作確認: 意図した通信は通り、意図しない通信はブロックされることを検証
- トラブルシューティング: NetworkPolicyで通信が遮断された場合のデバッグ手法

---

### 9.7 まとめと次章への橋渡し

**概要**: 本章で構築したクラスタセキュリティの内容を振り返り、RBAC・NetworkPolicy・PSAではカバーできない「ポリシーの自動強制」の課題を提示して第10章へつなげる。

**キーポイント**:
- 本章のまとめ: 認証・認可、ネットワーク分離、Podセキュリティの3層防御
- 残された課題: RBACとNetworkPolicyは「設定済みのリソースの制御」であり、「新たに作られるリソースがポリシーに違反していないか」を自動で検査する仕組みが必要
- 次章予告: OPA/Gatekeeperによる Policy as Code で Admission Control を実現する

## 図表リスト

| 番号 | 種類 | タイトル | 形式 |
|------|------|---------|------|
| 図9.1 | 図 | Part 3のセキュリティ領域マップ | Mermaid |
| 図9.2 | 図 | APIリクエストの処理フロー | Mermaid |
| 図9.3 | 図 | RBACリソースの関係図 | Mermaid |
| 図9.4 | 図 | NetworkPolicy適用前後のトラフィックフロー比較図 | Mermaid |
| 図9.5 | 図 | サンプルアプリの通信マトリクス | Mermaid |
| 図9.6 | 図 | セキュリティ適用後のサンプルアプリアーキテクチャ図 | Mermaid |
| 表9.1 | 表 | サンプルアプリの各サービスに割り当てるRole設計 | Markdown表 |
| 表9.2 | 表 | Pod Security Standardsの3つのレベル比較 | Markdown表 |

## コード例

| 番号 | 内容 | 言語 | 概要 |
|------|------|------|------|
| コード9.1 | ServiceAccountとRoleBindingの定義 | YAML | 各マイクロサービス用のServiceAccount・Role・RoleBinding |
| コード9.2 | デフォルトDeny NetworkPolicy | YAML | 全Ingress/Egressを拒否するベースポリシー |
| コード9.3 | サービス間Allow NetworkPolicy | YAML | フロントエンド→API→各サービスの通信許可ルール |
| コード9.4 | SecurityContextの設定 | YAML | runAsNonRoot、readOnlyRootFilesystem等の設定 |
| コード9.5 | PSA Namespace labels | YAML | Restrictedレベルのenforce/audit/warn設定 |
| コード9.6 | Kustomize overlayのセキュリティパッチ | YAML | セキュリティ設定をoverlayで管理する構成 |

## 章末の理解度チェック

1. **RBACの4リソース**: Role、ClusterRole、RoleBinding、ClusterRoleBindingの違いを説明し、Namespaceスコープのアクセス制御にはどの組み合わせを使うか答えよ。
2. **最小権限の原則**: デフォルトServiceAccountを各Podで共有することのリスクを2つ挙げ、それを回避する設計方法を述べよ。
3. **NetworkPolicy設計**: デフォルトDenyポリシーを適用した状態で、フロントエンドからAPIゲートウェイへの通信のみ許可するNetworkPolicyを書け。
4. **Pod Security Standards**: Restricted、Baseline、Privilegedの3レベルのうち、本番環境で推奨されるレベルとその理由を述べよ。
5. **トラブルシューティング**: NetworkPolicy適用後にサービス間通信が失敗した場合、原因を特定するための手順を3ステップで説明せよ。

## 章間の接続

### 前の章からの接続（Ch.8 → Ch.9）
- Ch.8（Service Mesh統合）ではサービス間通信の制御をService Meshレイヤーで実現した。Ch.9ではKubernetesネイティブのRBACとNetworkPolicyによるクラスタレベルのセキュリティを扱う
- Part 3はPart 2と独立しており、Ch.1のサンプルアプリから直接開始できる
- Part 3冒頭でサンプルアプリの「セキュリティが未設定」である現状を課題として提示し、Security領域の動機づけを行う

### 次の章への接続（Ch.9 → Ch.10）
- Ch.9のRBAC・NetworkPolicyは「既存リソースへのアクセス制御」であるが、「新規リソース作成時のポリシー違反チェック」はカバーできない
- Ch.10ではOPA/Gatekeeperを導入し、Admission Controlの段階でポリシーを自動強制する仕組みを構築する
- Ch.9で設計したセキュリティポリシー（privileged禁止、非rootユーザー強制等）を、Ch.10ではコードとして宣言的に管理する
