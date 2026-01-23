---
name: jira-mcp-optimizer
description: |
  Jira/Confluence MCP 最佳化工具。用於查票、建票、改狀態、Sprint 規劃、PRD 審核、進度追蹤、風險分析、Git 整合。
  包含 9 種角色、Git ↔ Jira 自動化工作流、文件導入流程、和 token 壓縮腳本。
  Use when: 操作 Jira/Confluence、文件導入 Jira、風險分析、角色導向任務、或提到 jira。
  Auto-trigger: 當 agent 執行 git commit/push/pull/merge/checkout 且偵測到 Jira issue key（如 PROJ-123）時，
  必須自動載入此 skill 執行 Jira 同步（加 comment / 改狀態），無需使用者額外指示。
allowed-tools: Read, Glob, Grep, Bash, Write, mcp__Jira__*
# Read/Glob/Grep: 讀取 skill 內 references 和 templates
# Bash: 執行 scripts/*.py（壓縮/驗證/產生 payload）
# Write: Dashboard Builder (21) 產出 HTML 儀表板檔案
# mcp__Jira__*: 所有 Jira MCP 工具（查/建/改票、搜尋、comment、agile board 等）
---

# Jira MCP Optimizer

## Purpose
用 Jira MCP 進行：查票、建票、改狀態、寫 comment、規劃 sprint、整理需求。
優化重點：少 token、少往返、每一步可驗證、避免亂改票。

## When to use

### 主動載入（使用者明確要求）
- 需要**直接操作 Jira**（查/建/改/留言/指派/加標籤/改狀態）
- 需要**可追溯的工作流**（例如把 PR/bug 轉票、sprint 規劃、triage）
- 需要**大量查詢**（JQL、批次彙整、報表雛形）
- 需要**文件導入 Jira**（PRD/需求文件批量建票）
- 需要**風險分析**（時程/資源/品質/範圍風險預測）
- 需要**角色導向任務**（見 Roles 區塊）

### 自動觸發（Agent 偵測到即載入，無需使用者指示）
- 執行 `git commit/push/pull/merge/checkout -b` 且 **branch 名、commit msg、或 MR title 含 Jira issue key**（如 `PROJ-123`）
- 偵測到後：按 Git Integration SSOT 表執行對應 Jira 同步動作

## When NOT to use
- **即時互動式儀表板**：需要即時更新的線上儀表板 → 用 Jira Dashboard 或 BI 工具
  （靜態 HTML 儀表板可用 Dashboard Builder Role 21 產出）
- **即時通知**：需要 Slack/Teams 推播 → 用 Jira Automation 原生整合
- **權限管理**：需改 Jira 專案權限 → 用 Jira Admin UI
- **單純問 Jira 怎麼用**：概念說明 → 直接回答，不需載入 skill

## Inputs / Outputs

| 動作 | 輸入 | 輸出 |
|-----|------|------|
| 查票 | JQL / 自然語言 | Issue 清單（壓縮後） |
| 建票 | 描述 + project + type | Issue key + 確認連結 |
| 改票 | Issue key + 變更欄位 | diff + 回讀確認 |
| Git 連動 | commit msg / MR | 狀態更新 + comment |
| 文件導入 | PRD / 需求文件 | 導入報告 + Issue 清單 |
| 風險分析 | Sprint / Project 數據 | 風險報告 + 建議行動 |
| 儀表板 | Project key + 選項 | 自含式 HTML Dashboard（Chart.js）|

## Preconditions
1. 已完成 Jira MCP 連線與授權
2. 已知道：Jira base url、目標專案 key、常用 issue type、workflow 狀態
3. **首次使用健檢**：讀一張 issue 或 `list_jira_projects` 確認 200 OK 才繼續
4. **Meta 快取**：首次或 schema 變更時，執行 fields/transitions 查詢並更新 `references/03_FIELD_SCHEMA.md`
   - 以 projectKey 為單位；workflow/field 有改動或遇到 transition/欄位 mismatch 就重刷

## Guardrails (必遵守)
1. **先讀再寫**：任何 update 前必先讀取 issue 目前狀態/欄位。
2. **最小變更**：一次只改必要欄位；多欄位變更要分步並檢查結果。
3. **明確確認**：涉及狀態流轉、指派、刪除/關閉等不可逆操作，需在執行前列出變更摘要（diff）並等待明確指令。
4. **限制查詢範圍**：JQL 先小範圍（project + recent + limit），必要才擴大。
5. **避免幻想欄位**：所有欄位名稱、transition 名稱、customfield ID 一律以 `references/03_FIELD_SCHEMA.md` 與 `references/01_TOOL_MAP.md` 為準。
6. **停止條件**：
   - 403/401 → 停止寫入；可再讀一次 meta 確認權限缺口
   - issue 不存在 → 停止；回報 key 錯誤
   - transition 不存在 → 停止；列出可用 transitions 供選擇

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

### D) Git Integration：Git ↔ Jira 自動同步

**核心機制**：Agent 綁定工程師日常 git 操作，每次 git 動作後自動同步 Jira。無需額外 CI/CD。

**Issue Key 抽取優先序**：MR title → branch name → commit message → 手動指定

**原則：commit ≠ 完成，MR merged 才算 Done。**

**SSOT — 工程師 Git 操作 → Agent 自動 Jira 同步：**

| 工程師操作 | Agent 偵測 | Jira 動作 |
|-----------|-----------|-----------|
| `checkout -b feature/PROJ-123-*` | branch 名含 key | → In Progress |
| `commit -m "PROJ-123 ..."` | commit msg 含 key | 加 comment（狀態不變） |
| `push` + 開 MR | MR title 含 key | → In Review |
| 本地 `merge` | merge commit 含 key | → Done + 回讀確認 |
| `pull`（發現遠端已 merge） | 比對 MR 狀態 | 補轉 Done（若 Jira 仍 In Review） |
| MR 被 close（not merged） | MR 狀態 closed | → In Progress（打回） |

**輕量文件（按需讀取）：** 15_GIT_COMMIT.md / 16_GIT_MR.md / 17_GIT_AUTOMATION.md

**腳本輔助**：`scripts/git_helpers.py validate|branch|mr-desc|extract-keys|create-bug`

### E) Dashboard：產出專案視覺化儀表板
1) 確認專案 key 和 board ID
2) 收集數據（Sprint 歷史、Issues、風險信號、依賴連鎖）
3) 戰略分析（趨勢向量、交付機率、複合風險、行動建議）
4) 用 scripts/pack_dashboard.py 彙整 → 產出 HTML
5) 瀏覽器開啟確認

**Git E2E（最小驗證）：**
```
checkout -b feature/PROJ-123-add-auth → PROJ-123 轉 In Progress
commit "PROJ-123 feat: add auth"      → 加 comment（狀態不變）
push + open MR [PROJ-123]             → PROJ-123 轉 In Review
MR merged（本地或 pull 發現）           → PROJ-123 轉 Done（回讀確認）
```

## Roles (角色導向任務)

| 任務場景 | Role | 文件 |
|---------|------|------|
| 團隊需要做決策（DACI 框架）| Decision Director | references/07_ROLE_DECISION_DIRECTOR.md |
| 查找/組織工作項目 | Work Organizer | references/08_ROLE_WORK_ORGANIZER.md |
| 撰寫或審核 PRD | PRD Guide | references/09_ROLE_PRD_GUIDE.md |
| 分解 Epic/頁面為任務 | Work Item Planner | references/10_ROLE_WORK_ITEM_PLANNER.md |
| 檢查 Issue 是否可開發 | Readiness Checker | references/11_ROLE_READINESS_CHECKER.md |
| 產出週報/狀態報告 | Progress Tracker | references/12_ROLE_PROGRESS_TRACKER.md |
| 審核 Bug 報告品質 | Bug Report Assistant | references/13_ROLE_BUG_REPORT_ASSISTANT.md |
| 驗證導入結果完整性 | Import Validator | references/19_ROLE_IMPORT_VALIDATOR.md |
| 專案風險預測與預警 | Risk Analyst | references/20_ROLE_RISK_ANALYST.md |
| 專案儀表板（視覺化進度/風險）| Dashboard Builder | references/21_ROLE_DASHBOARD_BUILDER.md |

**使用原則**：識別任務類型 → 載入對應 Role 文件 → 遵循 Role 工作流 → 使用 Role 模板輸出

## E2E Example：從 PRD 到 Sprint Ready

```
用戶：「把這個 PRD 轉成 Jira tickets 並確認可以開發」

Step 1: 載入 PRD Guide (09) 解析文件結構
Step 2: 載入 Work Item Planner (10) 分解為 Epic/Story/Task
Step 3: 執行 Doc Import Workflow (18) 批量建票
Step 4: 載入 Import Validator (19) 驗證導入完整性
Step 5: 載入 Readiness Checker (11) 檢查每個 Issue 是否 Ready

輸出：
- 導入報告（X Epic, Y Stories, Z Tasks）
- 驗證結果（通過/需修正項目）
- Ready 檢查結果（可開發/需補資訊）
```

## Token Optimization

**核心原則**：
1. 永遠不要把 Jira 原始 JSON 直接餵給 agent → 用 `scripts/pack_*.py` 壓縮
2. 兩段式查詢：先用窄 JQL 找 top 10，再針對少數 keys 做詳讀
3. 變更前做 diff：agent 先輸出「要改什麼」給你看

## References

**Core**:
- references/00_INDEX.md
- references/01_TOOL_MAP.md
- references/02_JQL_COOKBOOK.md
- references/03_FIELD_SCHEMA.md

**Workflows**:
- references/04_WORKFLOWS.md
- references/14_WORKFLOW_GIT_INTEGRATION.md
- references/18_WORKFLOW_DOC_IMPORT.md

**Roles**: references/07-13, 19-20（見上表）

**Templates**: references/templates/

**Scripts**: scripts/pack_issue.py | pack_search.py | pack_dashboard.py | normalize_fields.py | git_helpers.py
