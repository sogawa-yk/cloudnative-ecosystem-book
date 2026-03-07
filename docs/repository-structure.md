# リポジトリ構造定義書

## ディレクトリツリー

```
cloudnative-ecosystem-book/
├── CLAUDE.md                          # Claude Code設定
├── docs/                              # 永続的ドキュメント
│   ├── ideas/                         # 下書き・アイデア
│   │   └── book-concept.md
│   ├── book-plan.md                   # 書籍企画書
│   ├── book-architecture.md           # 書籍構成・章間依存関係図
│   ├── writing-guidelines.md          # 執筆ガイドライン
│   ├── glossary.md                    # 用語集
│   ├── figure-list.md                 # 図表一覧（全章横断）
│   ├── repository-structure.md        # 本ファイル
│   ├── chapter-specs/                 # 各章の仕様書
│   │   ├── ch00-spec.md
│   │   ├── ch01-spec.md
│   │   ├── ...
│   │   └── ch19-spec.md
│   └── feedbacks/                     # フィードバック
│       └── YYYY-MM-DD-chNN-topic.md
├── manuscript/                        # 原稿
│   ├── ch00/
│   │   ├── ch00.md                    # 本文
│   │   └── figures/                   # 図表ソース
│   ├── ch01/
│   │   ├── ch01.md
│   │   └── figures/
│   ├── ...
│   └── appendix/
│       ├── appendix-a.md
│       ├── appendix-b.md
│       ├── appendix-c.md
│       └── appendix-d.md
├── sample-app/                        # サンプルアプリケーション
│   ├── src/                           # アプリケーションソースコード
│   │   ├── frontend/
│   │   ├── api-gateway/
│   │   ├── product-service/
│   │   └── order-service/
│   ├── k8s/                           # Kubernetesマニフェスト
│   │   ├── base/                      # 環境共通マニフェスト
│   │   │   ├── kustomization.yaml
│   │   │   ├── namespace.yaml
│   │   │   ├── frontend/
│   │   │   ├── api-gateway/
│   │   │   ├── product-service/
│   │   │   └── order-service/
│   │   └── overlays/                  # 環境別カスタマイズ
│   │       ├── oke/                   # OKE（メイン）
│   │       │   ├── kustomization.yaml
│   │       │   ├── ingress.yaml
│   │       │   └── storage.yaml
│   │       └── kind/                  # kind
│   │           ├── kustomization.yaml
│   │           ├── ingress.yaml
│   │           └── storage.yaml
│   └── docker/                        # Dockerfile群
│       ├── frontend/Dockerfile
│       ├── api-gateway/Dockerfile
│       ├── product-service/Dockerfile
│       └── order-service/Dockerfile
├── manifests/                         # 各Part用のマニフェスト
│   ├── observability/                 # Part 1
│   │   ├── prometheus/
│   │   ├── fluent-bit/
│   │   ├── loki/
│   │   ├── jaeger/
│   │   ├── otel-collector/
│   │   └── grafana/
│   ├── mesh/                          # Part 2
│   │   ├── istio/
│   │   └── cilium/
│   ├── security/                      # Part 3
│   │   ├── rbac/
│   │   ├── network-policy/
│   │   ├── gatekeeper/
│   │   ├── trivy/
│   │   ├── cosign/
│   │   └── falco/
│   ├── cicd/                          # Part 4
│   │   ├── argocd/
│   │   ├── argo-rollouts/
│   │   └── github-actions/
│   └── platform/                      # Part 5
│       ├── backstage/
│       └── crossplane/
└── .steering/                         # 作業単位のドキュメント
    └── YYYYMMDD-chNN-section/
        ├── requirements.md
        ├── design.md
        └── tasklist.md
```

## ディレクトリの役割

### `docs/` — 永続的ドキュメント

書籍全体の「何を書くか」「どう書くか」を定義する。頻繁には変更しない。

### `manuscript/` — 原稿

書籍の本文。各章ごとにディレクトリを分け、本文と図表ソースを格納する。

### `sample-app/` — サンプルアプリケーション

Part 0で構築するサンプルアプリケーションのソースコードとマニフェスト。

- `src/`: 各サービスのGoソースコード
- `k8s/`: Kustomize形式のマニフェスト（base + overlays）
- `docker/`: 各サービスのDockerfile

### `manifests/` — 各Part用マニフェスト

Part 1〜5で導入するツール群のマニフェスト。Part別・ツール別に整理する。

### `.steering/` — 作業単位のドキュメント

特定の執筆作業に関する計画と進捗管理。作業ごとに新規作成し、履歴として保持する。

## Namespace対応

| ディレクトリ | Namespace | 用途 |
|-------------|-----------|------|
| `sample-app/k8s/` | `book-app` | サンプルアプリ本体 |
| `manifests/observability/` | `book-observability` | Observabilityツール群 |
| `manifests/mesh/` | `book-mesh` | Service Meshツール群 |
| `manifests/security/` | `book-security` | Securityツール群 |
| `manifests/cicd/` | `book-cicd` | CI/CDツール群 |
| `manifests/platform/` | `book-platform` | Platform Engineeringツール群 |
