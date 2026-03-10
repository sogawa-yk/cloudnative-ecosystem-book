---
name: glossary-creation
description: 書籍の用語集を作成するためのスキル。技術用語の日英対応と表記統一を管理。
allowed-tools: Read, Write
---

# 用語集作成スキル

## 前提条件

1. `docs/book-plan.md`（書籍企画書）
2. `docs/ideas/book-concept.md`（書籍コンセプト）

## 出力先

```
docs/glossary.md
```

## テンプレートの参照

用語集を作成する際は、次のテンプレートを使用してください: ./template.md

## 用語の分類

### ドメイン用語（マルチエージェント関連）
- エージェント、マルチエージェント、オーケストレーター等
- 協調パターン名（直列パイプライン、ファンアウト/ファンイン等）
- プロトコル名（MCP, A2A等）

### OCI用語
- OCI Generative AI Service
- OCI固有のサービス名
- 認証方式（Resource Principal等）

### 一般技術用語
- Function Calling, ReAct, RAG等
- Terraform, Kubernetes関連
