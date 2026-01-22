---
name: jira-mcp-optimizer
description: |
  Jira/Confluence MCP 最佳化工具。用於查票、建票、改狀態、Sprint 規劃、PRD 審核、進度追蹤、Git 整合。
  包含 7 種角色（Decision Director/PRD Guide/Work Planner/Readiness Checker/Progress Tracker/Bug Assistant）、
  Git ↔ Jira 自動化工作流、和 token 壓縮腳本。
  Use when: 操作 Jira/Confluence、Git commit/MR 連動 Jira、角色導向任務、或提到 jira。
allowed-tools: Read, Glob, Grep
---

# Jira MCP Optimizer

## Purpose
用 Jira MCP 進行：查票、建票、改狀態、寫 comment、規劃 sprint、整理需求。
優化重點：少 token、少往返、每一步可驗證、避免亂改票。

## When to use
- 需要**直接操作 Jira**（查/建/改/留言/指派/加標籤/改狀態）
- 需要**可追溯的工作流**（例如把 PR/bug 轉票、sprint 規劃、triage）
- 需要**大量查詢**（JQL、批次彙整、報表雛形）
- 需要**Git ↔ Jira 連動**：
  - Commit/MR 帶 Jira key → 自動更新狀態
  - Bug 修復 → 更新或自動建立 Bug 單
  - Branch 命名規範 / MR 模板
- 需要**角色導向任務**：
  - 決策管理（DACI）→ Decision Director
  - PRD 撰寫/審核 → PRD Guide
  - Epic 分解 → Work Item Planner
  - Issue 就緒檢查 → Readiness Checker
  - 週報/進度追蹤 → Progress Tracker
  - Bug 報告審核 → Bug Report Assistant

## Preconditions
- 已完成 Jira MCP 連線與授權
- 已知道：Jira base url、目標專案 key、常用 issue type、workflow 狀態

## Guardrails (必遵守)
1. **先讀再寫**：任何 update 前必先讀取 issue 目前狀態/欄位。
2. **最小變更**：一次只改必要欄位；多欄位變更要分步並檢查結果。
3. **明確確認**：涉及狀態流轉、指派、刪除/關閉等不可逆操作，需在執行前列出變更摘要（diff）並等待明確指令。
4. **限制查詢範圍**：JQL 先小範圍（project + recent + limit），必要才擴大。
5. **避免幻想欄位**：所有欄位名稱、transition 名稱、customfield ID 一律以 `references/03_FIELD_SCHEMA.md` 與 `references/01_TOOL_MAP.md` 為準。

## Quickstart (最常用 4 個流程)

### A) Triage：把一段描述變成 Jira issue
1) 釐清：project / issue type / priority / assignee / labels
2) 用模板產出 description + acceptance criteria（見 references/templates）
3) 建票 → 回讀確認 → 補 comment / 補 labels

### B) Search：用自然語言找票
1) 轉成 JQL（見 references/02_JQL_COOKBOOK.md）
2) 搜尋（限制欄位、限制筆數）
3) 需要彙整時：用 scripts/pack_search.py 壓縮結果再摘要

### C) Update：改狀態/指派/補資訊
1) 讀 issue（含目前 status、assignee、必要欄位）
2) 列出將變更的欄位與目標值（diff）
3) 執行更新
4) 回讀確認

### D) Git Integration：Git ↔ Jira 自動化

**輕量文件（按需讀取）：**
| 只需要 | 讀這個 |
|-------|--------|
| Commit 格式 | references/15_GIT_COMMIT.md |
| MR 模板 | references/16_GIT_MR.md |
| 自動化設置 | references/17_GIT_AUTOMATION.md |
| 完整參考 | references/14_WORKFLOW_GIT_INTEGRATION.md |

**腳本輔助 `scripts/git_helpers.py`：**
```bash
# 驗證 commit message
python3 scripts/git_helpers.py validate "PROJ-123 feat: add feature"
# → ✓ Valid commit message

# 產生 branch 名稱
python3 scripts/git_helpers.py branch PROJ-123 "add user auth" --type feature
# → feature/PROJ-123-add-user-auth

# 產生 MR description（含 Epic）
python3 scripts/git_helpers.py mr-desc PROJ-123 --epic EPIC-45

# 從文字提取 Jira keys
python3 scripts/git_helpers.py extract-keys "Fixed PROJ-123 and BUG-456"
# → PROJ-123, BUG-456

# 產生建 Bug 的 payload（給 CI 用）
python3 scripts/git_helpers.py create-bug --title "Fix login" --mr-url "..." --auto-close
```

## Roles (角色導向任務)

根據任務類型選擇對應 Role，每個 Role 有專屬 system prompt 和工作流程：

| 任務場景 | Role | 文件 |
|---------|------|------|
| 團隊需要做決策（DACI 框架）| Decision Director | references/07_ROLE_DECISION_DIRECTOR.md |
| 查找/組織工作項目 | Work Organizer | references/08_ROLE_WORK_ORGANIZER.md |
| 撰寫或審核 PRD | PRD Guide | references/09_ROLE_PRD_GUIDE.md |
| 分解 Epic/頁面為任務 | Work Item Planner | references/10_ROLE_WORK_ITEM_PLANNER.md |
| 檢查 Issue 是否可開發 | Readiness Checker | references/11_ROLE_READINESS_CHECKER.md |
| 產出週報/狀態報告 | Progress Tracker | references/12_ROLE_PROGRESS_TRACKER.md |
| 審核 Bug 報告品質 | Bug Report Assistant | references/13_ROLE_BUG_REPORT_ASSISTANT.md |

### Role 使用原則
1. **識別任務類型**：先判斷用戶需求屬於哪種場景
2. **載入對應 Role**：讀取 Role 文件中的 System Prompt
3. **遵循 Role 工作流**：按 Role 定義的步驟執行
4. **使用 Role 模板**：輸出格式遵循 Role 的 Output Template

### 常見場景對應

```
用戶：「幫我整理這週做了什麼」
→ 使用 Progress Tracker (12)

用戶：「這個 issue 可以開始開發嗎？」
→ 使用 Readiness Checker (11)

用戶：「把這個 PRD 轉成 Jira tickets」
→ 使用 Work Item Planner (10)

用戶：「審核一下這個 PRD」
→ 使用 PRD Guide (09)

用戶：「這個 bug 報告寫得好嗎？」
→ 使用 Bug Report Assistant (13)

用戶：「團隊要決定用哪個方案」
→ 使用 Decision Director (07)
```

## Token Optimization

### 策略
1. **永遠不要把 Jira 原始 JSON 直接餵給 agent**：先跑 `scripts/pack_issue.py` / `scripts/pack_search.py`
2. **預先快取「不常變」的 meta**：projects / issue types / fields / transitions
3. **描述用模板**：description/AC/comment 使用固定模板
4. **兩段式查詢**：先用窄 JQL 找 top 10，再針對少數 keys 做詳讀
5. **變更前做 diff**：agent 先輸出「要改什麼」給你看

## Tooling Map
請先讀：references/01_TOOL_MAP.md

## References

### Core Documents
- Index: references/00_INDEX.md
- Tool Map: references/01_TOOL_MAP.md
- JQL Cookbook: references/02_JQL_COOKBOOK.md
- Field Schema: references/03_FIELD_SCHEMA.md
- Workflows: references/04_WORKFLOWS.md
- Prompts: references/05_PROMPTS.md
- Troubleshooting: references/06_TROUBLESHOOTING.md
- Git Integration: references/14_WORKFLOW_GIT_INTEGRATION.md

### Roles
- references/07_ROLE_DECISION_DIRECTOR.md
- references/08_ROLE_WORK_ORGANIZER.md
- references/09_ROLE_PRD_GUIDE.md
- references/10_ROLE_WORK_ITEM_PLANNER.md
- references/11_ROLE_READINESS_CHECKER.md
- references/12_ROLE_PROGRESS_TRACKER.md
- references/13_ROLE_BUG_REPORT_ASSISTANT.md

## Templates
- references/templates/issue_description_templates.md
- references/templates/acceptance_criteria_templates.md
- references/templates/comment_templates.md

## Scripts
- `scripts/pack_issue.py` - 壓縮單一 issue JSON
- `scripts/pack_search.py` - 壓縮搜尋結果列表
- `scripts/normalize_fields.py` - 轉換 customfield 為友善名稱
- `scripts/git_helpers.py` - Git 輔助（validate/branch/mr-desc/extract-keys/create-bug）
