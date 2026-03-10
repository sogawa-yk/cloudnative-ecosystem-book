---
name: steering
description: 執筆作業毎の作業計画、タスクリストをドキュメントに記録するためのスキル。Galleyのsteeringスキルを書籍執筆用に適用。
allowed-tools: Read, Write, Edit
---

# Steering スキル

ステアリングファイル（`.steering/`）に基づいた執筆を支援し、tasklist.mdの進捗管理を確実に行うスキルです。

## スキルの目的

- ステアリングファイル（requirements.md, design.md, tasklist.md）の作成支援
- tasklist.mdに基づいた段階的な執筆管理
- **進捗の自動追跡とtasklist.md更新の強制**
- 執筆完了後の振り返り記録

## 使用タイミング

1. **作業計画時**: ステアリングファイルを作成する時
2. **執筆時**: tasklist.mdに従って執筆する時
3. **レビュー時**: 執筆完了後の振り返りを記録する時

## モード1: ステアリングファイル作成

Galleyのsteeringスキルと同じ手順。
ただしrequirements.mdには「執筆する節」「含めるべき図表」「前後の章との接続方法」を記載。

## モード2: 執筆（最重要）

### 🚨 重要な原則

**MUST（必須）**:
- tasklist.mdを常に参照しながら執筆
- タスク完了時に必ずEditツールで`[ ]`→`[x]`に更新
- **tasklist.mdの全タスクが完了するまで作業を継続する**

**NEVER（禁止）**:
- tasklist.mdを見ずに執筆を進める
- 「時間の都合により」「別タスクとして実施予定」などの理由でタスクをスキップする
- 未完了タスク（`[ ]`）を残したまま作業を終了する

### 🚨 タスク完全完了の原則

Galleyのsteeringスキルと同一のルール:
- 全タスクが`[x]`になるまで執筆を継続
- スキップが許可されるのは技術的な理由のみ
- タスクが大きすぎる場合はサブタスクに分割

## モード3: 振り返り

tasklist.mdに以下を記録:
- 執筆完了日
- 計画と実績の差分（予定ページ数 vs 実績）
- 執筆で発見した問題・改善点
- 次の章への申し送り事項

## テンプレート

ステアリングファイルのテンプレートは `./templates/` を参照:
- ./templates/requirements.md
- ./templates/design.md
- ./templates/tasklist.md
