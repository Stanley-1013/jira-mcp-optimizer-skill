# Document Import Workflow

> 將 PRD/需求文件批量導入 Jira

## Overview

```
輸入：PRD / 需求文件 / Confluence 頁面
         ↓
    ┌────────────────┐
    │ Step 1: 解析   │ ← PRD Guide (09)
    │ 識別文件結構    │
    └────────────────┘
         ↓
    ┌────────────────┐
    │ Step 2: 映射   │ ← 本流程定義
    │ 結構 → Issue 類型│
    └────────────────┘
         ↓
    ┌────────────────┐
    │ Step 3: 分解   │ ← Work Item Planner (10)
    │ 細化為可執行任務 │
    └────────────────┘
         ↓
    ┌────────────────┐
    │ Step 4: 建票   │ ← create_jira_issue
    │ 批量建立 Issues │
    └────────────────┘
         ↓
    ┌────────────────┐
    │ Step 5: 驗證   │ ← Import Validator (19)
    │ 檢查完整性      │
    └────────────────┘
         ↓
輸出：導入報告 + Issue 清單
```

---

## Step 1: 解析文件結構

**使用 Role**: PRD Guide (09)

**目標**: 識別文件的層級結構和可建票項目

### 常見文件結構映射

| 文件元素 | Jira 映射 |
|---------|----------|
| 文件標題 / 專案名稱 | Epic |
| 大章節 (## 或 H2) | Story / Feature |
| 小節 (### 或 H3) | Task |
| 列表項目 (- 或 1.) | Sub-task |
| 驗收標準 / AC | Issue 的 Acceptance Criteria 欄位 |
| 備註 / Notes | Issue 的 Description 補充 |

### 解析輸出格式

```yaml
document_structure:
  title: "專案名稱"
  type: "PRD"  # PRD / 需求規格 / 功能清單 / 會議記錄
  sections:
    - level: 1
      title: "功能模組 A"
      suggested_type: "Story"
      children:
        - level: 2
          title: "子功能 A.1"
          suggested_type: "Task"
          acceptance_criteria:
            - "AC1: ..."
            - "AC2: ..."
```

---

## Step 2: 結構映射規則

### 預設映射規則

| 文件層級 | Issue Type | Labels |
|---------|-----------|--------|
| Level 0 (文件本身) | Epic | `imported`, `prd` |
| Level 1 (大章節) | Story | `imported` |
| Level 2 (小節) | Task | `imported` |
| Level 3+ (列表) | Sub-task | - |

### 自訂映射（詢問用戶）

```
Q: 這份文件要如何映射到 Jira？

選項：
A) 使用預設規則（文件→Epic, 章節→Story, 小節→Task）
B) 扁平化（全部建為 Task，用 labels 分類）
C) 自訂映射（請指定每層對應的 Issue Type）
```

### Issue 關聯設置

```yaml
relationships:
  epic_link: true        # Story/Task 連結到 Epic
  parent_link: true      # Sub-task 連結到 Parent
  blocks_link: false     # 預設不建立 blocks 關係
  labels_inherit: true   # 子項目繼承父項目 labels
```

---

## Step 3: 分解為可執行任務

**使用 Role**: Work Item Planner (10)

**輸入**: Step 2 的結構映射結果

**處理**:
1. 檢查每個 Task 是否足夠具體
2. 過大的 Task 進一步分解
3. 確保每個 Task 有明確的 Acceptance Criteria

### Task 大小檢查

```
✓ 好的 Task: "實作登入 API endpoint，支援 email/password"
✗ 過大: "完成用戶系統" → 應分解為多個 Task
✗ 過小: "加一個變數" → 應合併到上層 Task
```

---

## Step 4: 批量建票

### 建票順序

```
1. 先建 Epic（取得 Epic key）
2. 再建 Story（連結 Epic）
3. 再建 Task（連結 Story 或 Epic）
4. 最後建 Sub-task（連結 Parent Task）
```

### 建票 Payload 模板

```json
{
  "projectKey": "PROJ",
  "issueType": "Story",
  "summary": "功能模組 A",
  "description": "**來源文件**: PRD v1.2\n**來源章節**: 2.1 功能模組 A\n**導入時間**: 2024-01-15 14:30\n\n---\n\n### 原文內容\n\n[原始需求描述文字...]\n\n### 驗收標準\n\n- [ ] AC1: ...\n- [ ] AC2: ...",
  "labels": ["imported", "prd-v1.2", "section-2.1"],
  "epicKey": "PROJ-100"
}
```

**追溯欄位設計**（使用標準欄位，不依賴 customFields）：
- `description` 開頭：來源文件、章節、導入時間（結構化 Markdown）
- `labels`：`imported`（標記為導入）、`prd-v1.2`（版本）、`section-2.1`（章節）
- `created` 欄位：Jira 原生自動記錄創建時間

### 批量建票腳本

```bash
# 從 JSON 批量建票
python scripts/batch_import.py --input import_plan.json --dry-run
python scripts/batch_import.py --input import_plan.json --execute
```

---

## Step 5: 驗證

**使用 Role**: Import Validator (19)

**檢查項目**:
1. **完整性**: 原文件所有項目都有對應 Issue
2. **結構性**: Issue 階層關係正確
3. **內容性**: Summary/Description 正確反映原文
4. **連結性**: Epic Link / Parent Link 正確

**輸出**: 導入報告

---

## 導入報告模板

```markdown
# 導入報告

## 摘要
- 來源文件: PRD v1.2
- 導入時間: 2024-01-15 14:30
- 總計建立: 1 Epic, 5 Stories, 12 Tasks, 8 Sub-tasks

## Issue 清單
| Key | Type | Summary | Parent |
|-----|------|---------|--------|
| PROJ-100 | Epic | 專案名稱 | - |
| PROJ-101 | Story | 功能模組 A | PROJ-100 |
| PROJ-102 | Task | 子功能 A.1 | PROJ-101 |
| ... | ... | ... | ... |

## 驗證結果
- [x] 完整性檢查通過
- [x] 結構性檢查通過
- [ ] 內容性檢查：2 項需人工確認
  - PROJ-105: Summary 過長，已截斷
  - PROJ-108: AC 格式需調整

## 後續動作
1. 人工確認標記項目
2. 指派 Assignee
3. 設定 Sprint
```

---

## 常見文件類型處理

### PRD (Product Requirements Document)

```yaml
識別特徵:
  - 有「背景」「目標」「功能需求」「非功能需求」章節
  - 有用戶故事或場景描述

映射策略:
  - 文件 → Epic
  - 功能需求各項 → Story
  - 非功能需求 → Task (加 label: non-functional)
```

### 會議記錄 (Meeting Notes)

```yaml
識別特徵:
  - 有「討論事項」「決議」「待辦事項」

映射策略:
  - 跳過討論事項（不建票）
  - 決議 → 加到現有 Issue 的 comment
  - 待辦事項 → Task
```

### 技術規格 (Technical Spec)

```yaml
識別特徵:
  - 有 API 定義、資料結構、架構圖

映射策略:
  - 每個 API endpoint → Task
  - 資料模型變更 → Task
  - 架構變更 → Story
```

---

## Guardrails

1. **不要自動執行**: 批量建票前必須輸出計畫並等待確認
2. **保留來源追溯**: 每個 Issue 的 description 必須註明來源文件和章節
3. **使用 labels 標記**: 所有導入的 Issue 加上 `imported` label
4. **避免重複導入**: 建票前檢查是否已存在相同 Summary 的 Issue
5. **限制批量大小**: 單次最多建立 50 個 Issues，超過則分批

---

## Quick Reference

```
# 導入流程速查

1. 讀取文件
2. 執行 PRD Guide (09) 解析結構
3. 確認映射規則（問用戶）
4. 執行 Work Item Planner (10) 分解
5. 輸出建票計畫（dry-run）
6. 用戶確認後執行建票
7. 執行 Import Validator (19) 驗證
8. 輸出導入報告
```
