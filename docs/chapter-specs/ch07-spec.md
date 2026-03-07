# 第7章 仕様書: Cilium

## 章の概要

| 項目 | 内容 |
|------|------|
| **章番号** | 第7章 |
| **タイトル** | Cilium |
| **所属** | Part 2: Service Mesh |
| **性質** | 概念 + 実践 |
| **ページ数（目安）** | 25p |
| **依存する章** | Ch.1（サンプルアプリケーションの構築） |
| **Namespace** | book-mesh（Cilium関連）、book-app（ポリシー適用対象） |

### 目的

eBPF技術を活用したCiliumを導入し、サイドカーレスでService Meshの機能（L7ポリシー、mTLS、可観測性）を実現する。Istio（第6章）のサイドカーパターンとの違いを明確にし、eBPFアプローチの利点と制約を理解する。HubbleによるL3/L4/L7レベルの通信可視化を体験する。

### 前提知識

- 第1章: サンプルアプリケーションのデプロイとKustomizeの基本
- Kubernetesの基本リソース（Deployment, Service, Pod）
- Linuxカーネルの基本的な概念（カーネル空間とユーザー空間の違い）

---

## 節の構成

### 7.1 eBPFとは何か ― カーネルレベルのプログラマビリティ

**概要**: CiliumのコアテクノロジーであるeBPF（Extended Berkeley Packet Filter）の概念を解説する。Linuxカーネル内でサンドボックス化されたプログラムを実行する仕組み、従来のカーネルモジュールとの違い、ネットワーキングへの応用を説明する。

**図表**:
- 図7.1: eBPFプログラムの実行モデル（ユーザー空間 → カーネルフック → eBPFプログラム → マップ）

**キーポイント**:
- eBPFはカーネルを再コンパイルせずに、カーネル内で安全にプログラムを実行できる
- ネットワークパケット処理、セキュリティポリシー適用、可観測性データ収集をカーネルレベルで行える
- サイドカー（ユーザー空間プロキシ）を経由しないため、パフォーマンスオーバーヘッドが小さい

---

### 7.2 Ciliumのアーキテクチャ ― サイドカーレスの仕組み

**概要**: Ciliumのアーキテクチャを解説する。cilium-agentとcilium-operatorの役割、eBPFデータパスによるパケット処理、Istioのサイドカーパターンとの構造的な違いを図解する。

**図表**:
- 図7.2: Ciliumアーキテクチャ図（cilium-agent + eBPFデータパス + Hubble）
- 表7.1: IstioとCiliumのアーキテクチャ比較表

**キーポイント**:
- cilium-agentはDaemonSetとして各ノードに配置され、eBPFプログラムをカーネルにロードする
- サイドカーレスのため、Podあたりのリソース消費が抑えられる
- L3/L4の処理はeBPFで完結し、L7（HTTP等）の処理にはEnvoyプロキシを必要に応じて活用する
- サイドカーレスの制約: L7機能の一部はノード単位のプロキシに依存する

---

### 7.3 Ciliumのインストールとサンプルアプリへの導入

**概要**: OKE環境にCiliumをインストールし、サンプルアプリケーションに対してCiliumのネットワークポリシーが適用される状態を構築する。Helm / cilium CLIによるインストール、既存CNIとの関係、動作確認までをハンズオン形式で進める。

**図表**:
- 図7.3: Cilium導入後のクラスタ構成図（各ノードにcilium-agentが配置された状態）

**キーポイント**:
- Ciliumのインストール方法（Helm / cilium CLI）とOKE環境での設定
- CNI（Container Network Interface）としてのCiliumの位置づけと既存CNIとの共存
- cilium statusコマンドによる動作確認
- Kustomize overlayを使ったCilium関連マニフェストの管理

---

### 7.4 CiliumNetworkPolicy ― L7レベルのポリシー適用

**概要**: CiliumNetworkPolicy（CNP）を使い、HTTP メソッド・パスレベルの細粒度なネットワークポリシーを適用する。KubernetesネイティブのNetworkPolicyとの違いを明確にし、L7ポリシーの実用的なユースケースを示す。

**図表**:
- 図7.4: CiliumNetworkPolicyによるL7フィルタリングの概念図
- 表7.2: NetworkPolicyとCiliumNetworkPolicyの機能比較表

**キーポイント**:
- CiliumNetworkPolicyはKubernetes NetworkPolicyのスーパーセット
- L7ルール（HTTPメソッド、パス、ヘッダ）による細粒度なアクセス制御が可能
- サンプルアプリケーションで「注文サービスへのPOSTは許可、DELETEは拒否」のようなポリシーを実装
- ポリシー違反時の動作確認とトラブルシューティング

---

### 7.5 Hubble ― サービス間通信の可視化

**概要**: CiliumのObservabilityコンポーネントであるHubbleを導入し、サービス間通信のフローをリアルタイムで可視化する。Hubble CLIとHubble UIの両方を使い、L3/L4/L7レベルのフロー情報を確認する。

**図表**:
- 図7.5: Hubbleのアーキテクチャ図（Hubble Relay + Hubble UI + cilium-agentのフロー収集）
- 図7.6: Hubble UIのサービスマップ画面（サンプルアプリケーションの通信フロー表示）

**キーポイント**:
- HubbleはeBPFから収集したフロー情報を集約し、サービス間通信を可視化する
- hubble CLIでリアルタイムのフロー監視（hubble observe）とフィルタリングが可能
- Hubble UIはKialiと類似のサービスマップを提供する
- ポリシー適用状況（FORWARDED / DROPPED）をHubbleで確認できる

---

### 7.6 Cilium Service Mesh ― mTLSとL7トラフィック管理

**概要**: Ciliumが提供するService Mesh機能（mTLS、L7トラフィック管理）を設定する。WireGuardベースの暗号化やSPIFFEベースのIDによるmTLSの仕組みを解説し、IstioのmTLSとの違いを明確にする。

**図表**:
- 図7.7: CiliumのmTLS実装方式（WireGuard / SPIFFE）の概念図
- 表7.3: IstioとCiliumのmTLS実装比較表

**キーポイント**:
- CiliumはWireGuardによるノード間暗号化またはSPIFFEベースのPod単位mTLSを提供する
- ノード間暗号化はカーネルレベルで動作し、アプリケーションへの影響が最小限
- L7トラフィック管理にはCilium Envoy Configを使用する
- サイドカーレスのトレードオフ: L7機能の細かさはIstioに及ばない部分がある

---

### 7.7 本章のまとめと次章への橋渡し

**概要**: Ciliumで実現した機能を振り返り、IstioとCiliumの選定基準を整理する。次章（第8章）でService MeshのテレメトリをObservability基盤に統合する方法を予告する。

**図表**:
- 表7.4: IstioとCiliumの総合比較表（ユースケース別の推奨）

**キーポイント**:
- Ciliumはパフォーマンス重視・運用シンプルさ重視のユースケースに適する
- Istioは豊富なL7トラフィック制御や成熟したエコシステムが求められるユースケースに適する
- 次章ではIstio / Ciliumどちらの構成からでもObservability基盤と統合する方法を扱う

---

## 図表リスト

| 図表番号 | タイトル | 種類 | 節 |
|---------|---------|------|-----|
| 図7.1 | eBPFプログラムの実行モデル | Mermaid（フローチャート） | 7.1 |
| 図7.2 | Ciliumアーキテクチャ図 | Mermaid（アーキテクチャ図） | 7.2 |
| 表7.1 | IstioとCiliumのアーキテクチャ比較表 | 表 | 7.2 |
| 図7.3 | Cilium導入後のクラスタ構成図 | Mermaid（アーキテクチャ図） | 7.3 |
| 図7.4 | CiliumNetworkPolicyによるL7フィルタリング概念図 | Mermaid（フローチャート） | 7.4 |
| 表7.2 | NetworkPolicyとCiliumNetworkPolicyの機能比較表 | 表 | 7.4 |
| 図7.5 | Hubbleのアーキテクチャ図 | Mermaid（アーキテクチャ図） | 7.5 |
| 図7.6 | Hubble UIのサービスマップ画面 | テキスト図 / スクリーンショット | 7.5 |
| 図7.7 | CiliumのmTLS実装方式の概念図 | Mermaid（フローチャート） | 7.6 |
| 表7.3 | IstioとCiliumのmTLS実装比較表 | 表 | 7.6 |
| 表7.4 | IstioとCiliumの総合比較表 | 表 | 7.7 |

## コード例

| コード番号 | 内容 | 言語 | 節 |
|-----------|------|------|-----|
| コード7.1 | CiliumのHelmインストールコマンド | bash | 7.3 |
| コード7.2 | Cilium用Kustomize overlay | YAML | 7.3 |
| コード7.3 | cilium statusによる動作確認 | bash | 7.3 |
| コード7.4 | CiliumNetworkPolicy（L7 HTTPルール） | YAML | 7.4 |
| コード7.5 | CiliumNetworkPolicy（サービス間アクセス制御） | YAML | 7.4 |
| コード7.6 | Hubbleの有効化とHubble UIのインストール | bash / YAML | 7.5 |
| コード7.7 | hubble observeコマンドによるフロー監視 | bash | 7.5 |
| コード7.8 | WireGuard暗号化の有効化設定 | YAML | 7.6 |
| コード7.9 | Cilium Envoy Config（L7トラフィック管理） | YAML | 7.6 |

## 章末の理解度チェック

1. eBPFとは何か。従来のカーネルモジュールと比較した場合の利点を説明せよ。
2. サイドカーパターン（Istio）とサイドカーレス（Cilium）のトレードオフを3つ挙げて説明せよ。
3. CiliumNetworkPolicyがKubernetesネイティブのNetworkPolicyと比較して優れている点を、L7フィルタリングの具体例を含めて説明せよ。
4. Hubbleが収集するフロー情報にはどのようなものがあるか。L3/L4/L7それぞれのレベルで説明せよ。
5. Istioを選ぶべきユースケースとCiliumを選ぶべきユースケースをそれぞれ挙げ、その理由を述べよ。

## 章間の接続

### 前の章からの接続（Ch.1 → Ch.7）

第1章で構築したサンプルアプリケーションは、Kubernetesのネイティブネットワーキングのみでサービス間通信を行っている。本章では、eBPF技術を活用したCiliumを導入し、サイドカーを使わずにネットワークポリシーの適用と通信の可視化を実現する。第6章（Istio）とは独立して読むことが可能である。

### 次の章への接続（Ch.7 → Ch.8）

本章では、CiliumによるネットワークポリシーとHubbleによる可視化を構築した。しかし、CiliumやIstioが生成するテレメトリ（メトリクス、アクセスログ、トレース）はまだPart 1で構築したObservability基盤（Prometheus、Loki、Jaeger）に統合されていない。次章では、Service MeshのテレメトリをObservability基盤に流し込み、メッシュレイヤーとアプリケーションレイヤーの横断的な可観測性を実現する。
