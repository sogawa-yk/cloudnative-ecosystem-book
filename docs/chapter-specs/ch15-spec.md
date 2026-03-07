# 第15章 仕様書: CIパイプライン — GitHub Actions

## 章の概要

| 項目 | 内容 |
|------|------|
| 章番号 | 第15章 |
| タイトル | CIパイプライン — GitHub Actions |
| 所属 | Part 4: CI/CD & GitOps |
| 性質 | 概念 + 実践 |
| ページ数（目安） | 15p |
| 依存する章 | Ch.1（サンプルアプリケーション）、Ch.11（Trivy + Sigstore） |
| 使用Namespace | `book-app`（サンプルアプリ）※CI自体はGitHub側で実行 |

### 目的

コンテナアプリケーションにおけるCI（継続的インテグレーション）のベストプラクティスを理解する。マルチステージビルドによる効率的なイメージ構築、キャッシュ戦略によるビルド高速化を学んだうえで、GitHub Actionsを用いてPRからビルド、Trivyによる脆弱性スキャン、cosignによるイメージ署名、コンテナレジストリへのPushまでの一連のCIパイプラインを構築する。

## 前提知識

- Dockerfileの基本的な記述方法
- コンテナイメージのビルド・Pushの経験
- Gitのブランチ戦略（feature branch, main）の基本理解
- Trivyによるイメージスキャンとcosignによる署名の概念（第11章）

## 節の構成

### 15.1 コンテナビルドのベストプラクティス

**概要**: 本番向けコンテナイメージを構築する際のベストプラクティスを解説する。マルチステージビルドによるイメージサイズの最小化、distrolessベースイメージの選択、レイヤーキャッシュを意識したDockerfileの記述方法を示す。

**図表**:
- 図15.1: マルチステージビルドの構造とレイヤー比較

**キーポイント**:
- マルチステージビルド: ビルドステージと実行ステージの分離
- ベースイメージの選択: distroless / Alpine / scratch の比較
- レイヤーキャッシュ: COPY go.mod → RUN go mod download → COPY . の順序
- .dockerignoreの活用
- 非rootユーザーでの実行

### 15.2 GitHub Actionsの基本構造

**概要**: GitHub Actionsのワークフロー構造（workflow, job, step）、トリガーイベント（push, pull_request）、ランナー環境を解説する。CIパイプラインの全体像を示し、各ステップの役割を概観する。

**図表**:
- 図15.2: CIパイプラインの全体フロー（PR → ビルド → テスト → スキャン → 署名 → Push）

**キーポイント**:
- ワークフローファイルの配置: `.github/workflows/ci.yaml`
- トリガー: pull_request（PR時）、push to main（マージ時）
- ジョブとステップの構造
- secrets / environment variablesの管理
- OIDC連携によるクラウドプロバイダーへの認証（OCIR等）

### 15.3 ビルドとキャッシュ戦略

**概要**: GitHub Actionsでのコンテナビルドの実践を行う。docker/build-push-actionによるビルド、GitHub Actions Cacheを活用したビルド高速化、マルチプラットフォームビルドの基本を解説する。

**図表**:
- 図15.3: キャッシュ戦略の比較（inline cache / GitHub Actions cache / registry cache）

**キーポイント**:
- docker/setup-buildx-action: BuildKitの有効化
- docker/build-push-action: ビルドとPushの一体化
- キャッシュ戦略: GitHub Actions cache（type=gha）の活用
- レジストリへのPush: OCIR（OKE環境）への認証とPush
- イメージタグ戦略: Git SHA、セマンティックバージョニング、latest

### 15.4 脆弱性スキャンの組み込み

**概要**: 第11章で学んだTrivyをCIパイプラインに組み込む。ビルド後のイメージに対してCRITICAL/HIGH脆弱性をスキャンし、検出された場合にパイプラインを失敗させる設定を行う。スキャン結果をGitHub Security Advisoriesに連携する方法も示す。

**図表**:
- 図15.4: CIパイプラインにおけるTrivyスキャンの位置づけ

**キーポイント**:
- aquasecurity/trivy-action: GitHub Actions用のTrivyアクション
- severity: CRITICAL,HIGH の指定
- exit-code: 1による失敗制御
- SARIF形式での結果出力とGitHub Security tabへのアップロード
- .trivyignore による既知の脆弱性の除外管理

### 15.5 イメージ署名の組み込み

**概要**: 第11章で学んだcosignをCIパイプラインに組み込む。Keyless署名（Sigstore/Fulcio）によるイメージ署名をCI内で自動実行し、署名済みイメージのみがデプロイ可能な状態を作る。

**図表**:
- 図15.5: Keyless署名のフローとOIDCトークンの流れ

**キーポイント**:
- sigstore/cosign-installer: cosignのセットアップ
- Keyless署名: GitHub ActionsのOIDCトークンをFulcioに提示して一時的な証明書を取得
- cosign sign によるイメージ署名
- cosign verify による署名検証の確認
- 署名メタデータ（SBOM等）のアタッチ

### 15.6 完成したCIワークフロー

**概要**: 15.1〜15.5の要素をすべて統合した完成版のCIワークフローファイルを示す。PR時とmainブランチPush時の動作の違い、条件分岐の設定、失敗時の通知設定を解説する。

**図表**:
- 図15.6: 完成版CIワークフローのジョブ依存関係

**キーポイント**:
- PR時: ビルド + テスト + スキャン（Pushはスキップ）
- mainマージ時: ビルド + テスト + スキャン + Push + 署名
- ジョブ分割: lint → build → scan → sign-and-push の依存関係
- 失敗時の通知（GitHub Actionsのstatus check）
- ブランチ保護ルールとの連携

## 図表リスト

| 図表番号 | タイトル | 形式 |
|----------|---------|------|
| 図15.1 | マルチステージビルドの構造とレイヤー比較 | テキスト図 |
| 図15.2 | CIパイプラインの全体フロー | Mermaid |
| 図15.3 | キャッシュ戦略の比較 | 表 |
| 図15.4 | CIパイプラインにおけるTrivyスキャンの位置づけ | Mermaid |
| 図15.5 | Keyless署名のフローとOIDCトークンの流れ | Mermaid |
| 図15.6 | 完成版CIワークフローのジョブ依存関係 | Mermaid |

## コード例

| コード番号 | 内容 | 言語 |
|-----------|------|------|
| コード15.1 | マルチステージビルドのDockerfile（Goアプリ） | Dockerfile |
| コード15.2 | .dockerignore | テキスト |
| コード15.3 | CIワークフロー: ビルドジョブ（キャッシュ付き） | YAML |
| コード15.4 | CIワークフロー: Trivyスキャンジョブ | YAML |
| コード15.5 | CIワークフロー: cosign署名ジョブ | YAML |
| コード15.6 | CIワークフロー: 完成版（全ジョブ統合） | YAML |
| コード15.7 | OCIR認証の設定（OKE環境向け） | YAML |

## 章末の理解度チェック

1. マルチステージビルドを使用する利点を、イメージサイズとセキュリティの観点から説明せよ。
2. GitHub ActionsにおけるKeyless署名の仕組みを、OIDCトークン・Fulcio・Rekorの役割を含めて説明せよ。
3. CIパイプラインでTrivyスキャンを実行する際、CRITICAL脆弱性が検出されたらビルドを失敗させるにはどのような設定が必要か。
4. PR時とmainブランチPush時でCIワークフローの動作を変える必要がある理由を説明し、GitHub Actionsでの実現方法を述べよ。

## 章間の接続

### 前の章からの接続（第14章 → 第15章）

第13章・第14章でCD側の仕組み（ArgoCD + Argo Rollouts）が整った。しかし、コードの変更からコンテナイメージが安全にレジストリに格納されるまでのCI部分が未整備である。本章ではGitHub ActionsによるCIパイプラインを構築し、第11章で学んだサプライチェーンセキュリティ（Trivyスキャン、cosign署名）を自動化する。

### 次の章への接続（第15章 → 第16章）

CI（GitHub Actions）とCD（ArgoCD + Argo Rollouts）が個別に構築された。しかし、CIでビルドされた新しいイメージが自動的にCDに反映される仕組みがない。第16章ではArgoCD Image Updaterによるイメージ更新の自動検知、環境プロモーション戦略を設計し、コードプッシュから本番Canaryデプロイまでの一気通貫パイプラインを完成させる。
