# 第16章 仕様書: 統合 — End-to-End デリバリーパイプライン

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第16章 |
| タイトル | 統合 — End-to-End デリバリーパイプライン |
| 所属 | Part 4: CI/CD & GitOps |
| 性質 | 統合 |
| ページ数（目安） | 20p |
| 依存する章 | Ch.13（ArgoCD）、Ch.14（Argo Rollouts）、Ch.15（GitHub Actions） |
| 使用Namespace | `book-cicd`（ArgoCD, Argo Rollouts, Image Updater）、`book-app`（サンプルアプリ） |

### 目的

第13章〜第15章で個別に構築したCI（GitHub Actions）とCD（ArgoCD + Argo Rollouts）を接続し、コードプッシュから本番Canaryデプロイ・Prometheusメトリクスによる自動判定までの一気通貫パイプラインを完成させる。ArgoCD Image Updaterによるイメージ更新の自動検知、環境プロモーション戦略（dev → staging → prod）を設計・実装し、Part 4の集大成として実務で運用可能なデリバリーパイプラインを構築する。

## 前提知識

- ArgoCDによるGitOps管理（第13章）
- Argo RolloutsによるCanaryデプロイとAnalysis Template（第14章）
- GitHub ActionsによるCI（ビルド、スキャン、署名、Push）（第15章）
- Prometheusメトリクスの基本（第2章）

## 節の構成

### 16.1 CI→CDの接続設計

**概要**: CIパイプライン（GitHub Actions）とCDパイプライン（ArgoCD）を接続する方法を比較する。イメージタグの更新をGitリポジトリに反映する3つのアプローチ（手動更新、CIからのgit push、Image Updater）のトレードオフを分析し、ArgoCD Image Updaterを推奨アプローチとして選定する理由を示す。

**図表**:
- 図16.1: CI→CD接続の3つのアプローチ比較
- 表16.1: CI→CD接続アプローチのトレードオフ比較

**キーポイント**:
- アプローチ1: CIからKustomize edit → git pushでマニフェスト更新（GitOps原則に準拠するが、CIにGit書き込み権限が必要）
- アプローチ2: ArgoCD Image Updaterによる自動検知（CIとCDの疎結合を維持）
- アプローチ3: Webhook通知による即座のSync（低レイテンシだがArgoCDへの直接アクセスが必要）
- 本書ではアプローチ2（Image Updater）を採用し、CIとCDの責務を明確に分離

### 16.2 ArgoCD Image Updaterの導入

**概要**: ArgoCD Image Updaterのインストールと設定を行う。コンテナレジストリ（OCIR）の監視設定、イメージ更新戦略（semver, latest, digest）の選択、Kustomizeとの連携方法を実践する。

**図表**:
- 図16.2: ArgoCD Image Updaterの動作フロー

**キーポイント**:
- Helmチャートによるインストール（`book-cicd` Namespace）
- レジストリ認証の設定（OCIR用のSecret）
- Applicationアノテーションによるイメージ更新設定
- 更新戦略: semver（セマンティックバージョニング）、latest（最新タグ）、digest（ダイジェスト指定）
- write-back方式: Git書き戻し vs ArgoCD parameter override

### 16.3 環境プロモーション戦略

**概要**: 開発（dev）→ ステージング（staging）→ 本番（prod）の環境プロモーション戦略を設計する。各環境の役割、プロモーションの判定基準、Kustomize overlaysによる環境別マニフェスト管理を示す。

**図表**:
- 図16.3: 環境プロモーションフロー（dev → staging → prod）

**キーポイント**:
- 3環境の役割: dev（自動デプロイ、開発者確認用）、staging（自動デプロイ + E2Eテスト）、prod（Canaryデプロイ + Auto Promotion）
- Kustomize overlaysによる環境差分管理
- ApplicationSetによるマルチ環境Application自動生成
- プロモーションのトリガー: dev/stagingは自動、prodはCanary + Analysis

### 16.4 E2Eパイプラインの構築

**概要**: 第13章〜第15章の全要素を統合し、コードプッシュから本番Canaryデプロイまでの完全なパイプラインを構築する。CI（GitHub Actions）→ イメージPush → Image Updater検知 → ArgoCD Sync → Argo Rollouts Canary → Prometheus Analysis → Auto Promotionの全フローを実装し、動作を確認する。

**図表**:
- 図16.4: E2Eデリバリーパイプラインの全体アーキテクチャ

**キーポイント**:
- 完全なフロー: git push → CI（ビルド・テスト・スキャン・署名・Push） → Image Updater（新イメージ検知） → ArgoCD（マニフェスト更新・Sync） → Argo Rollouts（Canary） → Prometheus（メトリクス分析） → Auto Promotion / Rollback
- 各コンポーネント間の接続ポイントの設定
- 実践: サンプルアプリのコードを変更し、E2Eでの自動デプロイを確認

### 16.5 ロールバックとインシデント対応

**概要**: パイプラインで問題が発生した場合のロールバック手順を整理する。CI失敗時、CD失敗時、Canary Analysis失敗時のそれぞれのロールバック方法と、GitOpsにおける「git revertによるロールバック」の原則を解説する。

**図表**:
- 図16.5: 障害発生ポイント別のロールバックフロー
- 表16.2: 障害パターンとロールバック手順の対応表

**キーポイント**:
- CI失敗: GitHub ActionsのStatus Checkにより自動ブロック
- Canary Analysis失敗: Argo Rolloutsによる自動ロールバック
- 本番障害: git revertによるGitOps準拠のロールバック
- ArgoCD Sync Historyによる変更履歴の追跡
- 緊急時の手動介入: argocd app sync --revision による特定リビジョンへの復旧

### 16.6 運用のベストプラクティス

**概要**: E2Eパイプラインの運用で考慮すべきポイントを整理する。通知設定、監査ログ、パイプラインのメトリクス（デプロイ頻度、リードタイム等）の収集、セキュリティ考慮事項をまとめる。

**図表**:
- 図16.6: デリバリーパイプラインの可観測性ダッシュボード構成
- 表16.3: DORA Four Keysとパイプラインメトリクスの対応

**キーポイント**:
- 通知: ArgoCD Notification / GitHub Actions通知のSlack連携
- DORA Four Keys: デプロイ頻度、変更リードタイム、変更失敗率、復旧時間
- 監査: GitログとArgoCD Sync Historyによる変更追跡
- セキュリティ: Secretの管理（Sealed Secrets / External Secrets）、最小権限の原則
- スケーラビリティ: Application数の増加に伴うArgoCD・Image Updaterのチューニング

### 16.7 Part 4のまとめ

**概要**: Part 4全体を振り返り、構築したデリバリーパイプラインの全体像を示す。Part 5（Platform Engineering）への橋渡しとして、「開発者がセルフサービスでパイプラインを利用できるようにするには何が必要か」という問いを提示する。

**図表**:
- 図16.7: Part 4で構築した全コンポーネントの関係図

**キーポイント**:
- Part 4の振り返り: GitOps（ArgoCD）+ Progressive Delivery（Argo Rollouts）+ CI（GitHub Actions）+ 統合（Image Updater + 環境プロモーション）
- 残る課題: 開発者が新サービスを追加する際に、CI/CDの設定を手動で作成する必要がある
- Part 5への伏線: BackstageのSoftware Templateでパイプライン設定を自動生成する可能性

## 図表リスト

| 図表番号 | タイトル | 形式 |
|----------|---------|------|
| 図16.1 | CI→CD接続の3つのアプローチ比較 | Mermaid |
| 表16.1 | CI→CD接続アプローチのトレードオフ比較 | 表 |
| 図16.2 | ArgoCD Image Updaterの動作フロー | Mermaid |
| 図16.3 | 環境プロモーションフロー（dev → staging → prod） | Mermaid |
| 図16.4 | E2Eデリバリーパイプラインの全体アーキテクチャ | Mermaid |
| 図16.5 | 障害発生ポイント別のロールバックフロー | Mermaid |
| 表16.2 | 障害パターンとロールバック手順の対応表 | 表 |
| 図16.6 | デリバリーパイプラインの可観測性ダッシュボード構成 | Mermaid |
| 表16.3 | DORA Four Keysとパイプラインメトリクスの対応 | 表 |
| 図16.7 | Part 4で構築した全コンポーネントの関係図 | Mermaid |

## コード例

| コード番号 | 内容 | 言語 |
|-----------|------|------|
| コード16.1 | ArgoCD Image Updater Helmインストールのvalues.yaml | YAML |
| コード16.2 | Applicationアノテーション（Image Updater設定） | YAML |
| コード16.3 | Kustomize overlays構成（dev / staging / prod） | YAML |
| コード16.4 | ApplicationSet（環境プロモーション用） | YAML |
| コード16.5 | prod環境のRollout CRD + AnalysisTemplate（統合版） | YAML |
| コード16.6 | ArgoCD Notification設定（Slack連携） | YAML |
| コード16.7 | Sealed Secretsによるシークレット管理 | YAML |
| コード16.8 | E2Eパイプライン動作確認コマンド集 | bash |

## 章末の理解度チェック

1. ArgoCD Image Updaterを使ったCI→CD接続と、CIからgit pushでマニフェストを更新するアプローチを比較し、それぞれの利点・欠点を述べよ。
2. dev → staging → prod の環境プロモーション戦略において、各環境でのデプロイ方法と判定基準をどのように差別化すべきか設計せよ。
3. E2Eパイプラインにおいて、Canary Analysisが失敗した場合のロールバックフローを、関与する各コンポーネント（Argo Rollouts, ArgoCD, GitHub Actions）の動作を含めて時系列で説明せよ。
4. DORA Four Keysの各指標を、本章で構築したパイプラインのどのメトリクスから計測できるか対応づけよ。
5. GitOps環境において、Secretをどのように安全に管理すべきか。Sealed SecretsとExternal Secrets Operatorの違いを説明せよ。

## 章間の接続

### 前の章からの接続（第15章 → 第16章）

第13章〜第15章でCI（GitHub Actions）とCD（ArgoCD + Argo Rollouts）を個別に構築した。しかし、CIでビルドされた新しいイメージがCDに自動反映される仕組みがなく、環境間のプロモーション戦略も未定義である。本章ではArgoCD Image Updaterで両者を接続し、環境プロモーション設計を加えることで、コードプッシュから本番Canaryデプロイまでの完全なE2Eパイプラインを完成させる。

### 次の章への接続（第16章 → 第17章）

Part 4でCI/CD & GitOpsの基盤が完成した。しかし、新しいサービスを追加する際には、Deployment/Rollout CRD、ArgoCD Application、GitHub Actionsワークフロー、環境overlay等を手動で作成する必要がある。Part 5ではPlatform Engineeringの観点から、Backstage（第17章）でサービスカタログとSoftware Templateを構築し、開発者がセルフサービスで新サービスを立ち上げられるInternal Developer Platformを実現する。
