# 書籍構成・章間依存関係図

## Part構成と依存関係

```mermaid
graph LR
    P0[Part 0: 準備編] --> P1[Part 1: Observability]
    P0 --> P2[Part 2: Service Mesh]
    P0 --> P3[Part 3: Security]
    P1 --> P4[Part 4: CI/CD & GitOps]
    P3 --> P4
    P1 --> P5[Part 5: Platform Engineering]
    P2 --> P5
    P3 --> P5
    P4 --> P5
```

## 章間依存関係

### Part 0: 準備編

```mermaid
graph TD
    Ch0[Ch.0 この本の歩き方] --> Ch1[Ch.1 サンプルアプリの構築]
```

- **Ch.0**: 前提なし。本書の読み方、環境要件を説明
- **Ch.1**: Ch.0のみ。サンプルアプリをK8s上にデプロイし、Kustomizeの基本を解説。以降すべての章の基盤

### Part 1: Observability

```mermaid
graph TD
    Ch1[Ch.1 サンプルアプリ] --> Ch2[Ch.2 Metrics — Prometheus]
    Ch1 --> Ch3[Ch.3 Logs — Fluent Bit + Loki]
    Ch1 --> Ch4[Ch.4 Traces — OTel + Jaeger]
    Ch2 --> Ch5[Ch.5 統合 — Observability基盤]
    Ch3 --> Ch5
    Ch4 --> Ch5
```

- **Ch.2**: Ch.1のみ。Prometheusの導入、メトリクス収集
- **Ch.3**: Ch.1のみ。Fluent Bit + Lokiによるログ集約
- **Ch.4**: Ch.1のみ。OpenTelemetry + Jaegerによる分散トレーシング
- **Ch.5**: Ch.2〜4すべて。Three Pillarsの統合、Grafanaダッシュボード、SLI/SLO

> **並列読書可能**: Ch.2, Ch.3, Ch.4は互いに独立しており、任意の順番で読める

### Part 2: Service Mesh

```mermaid
graph TD
    Ch1[Ch.1 サンプルアプリ] --> Ch6[Ch.6 Istio]
    Ch1 --> Ch7[Ch.7 Cilium]
    Ch6 --> Ch8[Ch.8 統合 — メッシュ + Observability]
    Ch7 --> Ch8
    Ch5[Ch.5 Observability統合] --> Ch8
```

- **Ch.6**: Ch.1のみ。Istioの導入、mTLS、トラフィック管理
- **Ch.7**: Ch.1のみ。CiliumのeBPFアプローチ、Hubble
- **Ch.8**: Ch.5〜7。メッシュのテレメトリをPart 1のObservability基盤に統合

> **選択読書可能**: Ch.6（Istio）とCh.7（Cilium）はどちらか一方だけでもCh.8に進める

### Part 3: Security

```mermaid
graph TD
    Ch1[Ch.1 サンプルアプリ] --> Ch9[Ch.9 RBAC + NetworkPolicy]
    Ch1 --> Ch10[Ch.10 OPA / Gatekeeper]
    Ch1 --> Ch11[Ch.11 Trivy + Sigstore]
    Ch9 --> Ch12[Ch.12 統合 — セキュリティ監査基盤]
    Ch10 --> Ch12
    Ch11 --> Ch12
    Ch5[Ch.5 Observability統合] --> Ch12
```

- **Ch.9**: Ch.1のみ。RBAC設計、NetworkPolicyによる通信制限
- **Ch.10**: Ch.1のみ。OPA/GatekeeperによるAdmission Control
- **Ch.11**: Ch.1のみ。イメージスキャン、署名と検証
- **Ch.12**: Ch.9〜11 + Ch.5。Falco + Observability基盤でセキュリティダッシュボード構築

> **並列読書可能**: Ch.9, Ch.10, Ch.11は互いに独立

### Part 4: CI/CD & GitOps

```mermaid
graph TD
    Ch1[Ch.1 サンプルアプリ] --> Ch13[Ch.13 ArgoCD]
    Ch1 --> Ch14[Ch.14 Argo Rollouts]
    Ch1 --> Ch15[Ch.15 GitHub Actions]
    Ch11[Ch.11 Trivy + Sigstore] --> Ch15
    Ch2[Ch.2 Prometheus] --> Ch14
    Ch13 --> Ch16[Ch.16 統合 — E2Eパイプライン]
    Ch14 --> Ch16
    Ch15 --> Ch16
```

- **Ch.13**: Ch.1のみ。ArgoCDによるGitOps管理
- **Ch.14**: Ch.1 + Ch.2（Prometheusメトリクスで自動判定）。Canary/Blue-Greenデプロイ
- **Ch.15**: Ch.1 + Ch.11（Trivyスキャン・cosign署名をCIに組み込む）。CIパイプライン構築
- **Ch.16**: Ch.13〜15すべて。CI→CD→Progressive Deliveryの一気通貫

### Part 5: Platform Engineering

```mermaid
graph TD
    Ch1[Ch.1 サンプルアプリ] --> Ch17[Ch.17 Backstage]
    Ch1 --> Ch18[Ch.18 Crossplane]
    Ch17 --> Ch19[Ch.19 統合 — プラットフォーム完成]
    Ch18 --> Ch19
    Ch5[Ch.5 Observability統合] --> Ch19
    Ch8[Ch.8 Mesh統合] --> Ch19
    Ch12[Ch.12 Security統合] --> Ch19
    Ch16[Ch.16 CI/CD統合] --> Ch19
```

- **Ch.17**: Ch.1のみ。Backstageでサービスカタログ構築
- **Ch.18**: Ch.1のみ。Crossplaneでインフラの宣言的管理
- **Ch.19**: 全統合章（Ch.5, Ch.8, Ch.12, Ch.16）+ Ch.17〜18。Golden Pathのデモ

## 全体依存関係図（サマリ）

```mermaid
graph TD
    Ch0[Ch.0 歩き方] --> Ch1[Ch.1 サンプルアプリ + Kustomize]

    Ch1 --> Ch2[Ch.2 Prometheus]
    Ch1 --> Ch3[Ch.3 Fluent Bit + Loki]
    Ch1 --> Ch4[Ch.4 OTel + Jaeger]
    Ch2 & Ch3 & Ch4 --> Ch5[Ch.5 Observability統合]

    Ch1 --> Ch6[Ch.6 Istio]
    Ch1 --> Ch7[Ch.7 Cilium]
    Ch5 & Ch6 & Ch7 --> Ch8[Ch.8 Mesh統合]

    Ch1 --> Ch9[Ch.9 RBAC + NP]
    Ch1 --> Ch10[Ch.10 OPA/GK]
    Ch1 --> Ch11[Ch.11 Trivy + Sigstore]
    Ch5 & Ch9 & Ch10 & Ch11 --> Ch12[Ch.12 Security統合]

    Ch1 --> Ch13[Ch.13 ArgoCD]
    Ch2 --> Ch14[Ch.14 Argo Rollouts]
    Ch11 --> Ch15[Ch.15 GitHub Actions]
    Ch13 & Ch14 & Ch15 --> Ch16[Ch.16 CI/CD統合]

    Ch1 --> Ch17[Ch.17 Backstage]
    Ch1 --> Ch18[Ch.18 Crossplane]
    Ch5 & Ch8 & Ch12 & Ch16 & Ch17 & Ch18 --> Ch19[Ch.19 プラットフォーム統合]

    style Ch5 fill:#4CAF50,color:#fff
    style Ch8 fill:#4CAF50,color:#fff
    style Ch12 fill:#4CAF50,color:#fff
    style Ch16 fill:#4CAF50,color:#fff
    style Ch19 fill:#FF9800,color:#fff
```

**凡例**: 緑 = 各Part統合章、オレンジ = 最終統合章

## 読書パス

### フルパス（推奨）
Ch.0 → Ch.1 → Part 1 → Part 2 → Part 3 → Part 4 → Part 5

### Observability特化パス
Ch.0 → Ch.1 → Ch.2 → Ch.3 → Ch.4 → Ch.5

### Security特化パス
Ch.0 → Ch.1 → Ch.9 → Ch.10 → Ch.11 → Ch.5（統合章でObservability基盤を参照するため） → Ch.12

### CI/CD特化パス
Ch.0 → Ch.1 → Ch.2（Prometheus、Rollouts用） → Ch.11（Trivy/cosign、CI用） → Ch.13 → Ch.14 → Ch.15 → Ch.16
