# Jira MCP Optimizer — References Index

## Core Documents
| File | Description |
|------|-------------|
| 01_TOOL_MAP.md | MCP 工具對照表（最重要）- 把 MCP tool 名稱映射到概念動作 |
| 02_JQL_COOKBOOK.md | JQL 常用範本與除錯技巧 |
| 03_FIELD_SCHEMA.md | 欄位/狀態/transition/自訂欄位清單 |

## Workflows
| File | Description |
|------|-------------|
| 04_WORKFLOWS.md | Triage / Sprint planning / Bug→Task / PR→Issue / Release notes |
| 14_WORKFLOW_GIT_INTEGRATION.md | Git ↔ Jira 完整參考（全部內容）|
| 15_GIT_COMMIT.md | **輕量** - 只有 commit message 格式 |
| 16_GIT_MR.md | **輕量** - 只有 MR 模板 |
| 17_GIT_AUTOMATION.md | **輕量** - 只有自動化設置 |

## Prompts
| File | Description |
|------|-------------|
| 05_PROMPTS.md | 可直接貼給 agent 的 prompts（含輸入/輸出格式）|

## Operations
| File | Description |
|------|-------------|
| 06_TROUBLESHOOTING.md | 授權、權限、rate limit、常見錯誤處理 |

## Templates
| File | Description |
|------|-------------|
| templates/issue_description_templates.md | Issue 描述模板（Bug/Task/Story）|
| templates/acceptance_criteria_templates.md | 驗收標準模板 |
| templates/comment_templates.md | 評論模板（狀態更新/問題追蹤/Review 結果）|

## Roles
| File | Description |
|------|-------------|
| 07_ROLE_DECISION_DIRECTOR.md | 決策導演 - DACI 決策框架專家，協助在 Confluence 頁面上做出決策 |
| 08_ROLE_WORK_ORGANIZER.md | 工作組織者 - Issue 搜尋與組織助手，優先使用函數查詢 |
| 09_ROLE_PRD_GUIDE.md | PRD 專家 - 產品需求文檔創建與審核，直接權威的反饋風格 |
| 10_ROLE_WORK_ITEM_PLANNER.md | 工作規劃器 - 將 Epic/頁面分解為可執行任務 |
| 11_ROLE_READINESS_CHECKER.md | 就緒檢查器 - 評估 Issue 是否符合 Definition of Ready |
| 12_ROLE_PROGRESS_TRACKER.md | 進度追蹤器 - 產出週報和專案狀態報告 |
| 13_ROLE_BUG_REPORT_ASSISTANT.md | Bug 報告助手 - 審核 Bug 報告品質並提供改進建議 |

## Scripts
| Script | Description |
|--------|-------------|
| ../scripts/pack_issue.py | 把 Jira issue JSON 壓縮成最小上下文 Markdown |
| ../scripts/pack_search.py | 把搜尋結果列表壓成可掃描表格 |
| ../scripts/normalize_fields.py | 把 customfield 轉成友善名稱 |
| ../scripts/git_helpers.py | Git 輔助（validate/branch/mr-desc/create-bug）|

## Quick Navigation

### 我要查票
1. 看 02_JQL_COOKBOOK.md 找 JQL 模板
2. 搜尋後用 pack_search.py 壓縮結果
3. 需要詳情時讀單一 issue 並用 pack_issue.py 壓縮

### 我要建票
1. 看 03_FIELD_SCHEMA.md 確認必填欄位
2. 用 templates/issue_description_templates.md 產出內容
3. 看 01_TOOL_MAP.md 找對應的 create tool

### 我要改票
1. 先讀票確認目前狀態
2. 看 03_FIELD_SCHEMA.md 確認 transition ID
3. 執行更新並回讀確認

### 我要做 Sprint Planning
1. 看 04_WORKFLOWS.md 的 Sprint Planning workflow
2. 用 JQL 拉 backlog
3. 按 workflow 步驟執行

### 我要 Git ↔ Jira 連動

| 只需要... | 讀這個（輕量）| 腳本輔助 |
|----------|-------------|---------|
| Commit 格式 | 15_GIT_COMMIT.md | `git_helpers.py validate` |
| MR 模板 | 16_GIT_MR.md | `git_helpers.py mr-desc` |
| 自動化設置 | 17_GIT_AUTOMATION.md | - |
| 完整參考 | 14_WORKFLOW_GIT_INTEGRATION.md | - |

### 我要用特定 Role
| 場景 | Role |
|------|------|
| 團隊需要做決策 | 07_ROLE_DECISION_DIRECTOR.md (DACI) |
| 查找和組織工作項目 | 08_ROLE_WORK_ORGANIZER.md |
| 撰寫或審核 PRD | 09_ROLE_PRD_GUIDE.md |
| 分解大型 Epic 或頁面 | 10_ROLE_WORK_ITEM_PLANNER.md |
| 檢查 Issue 是否可開發 | 11_ROLE_READINESS_CHECKER.md |
| 產出週報或狀態報告 | 12_ROLE_PROGRESS_TRACKER.md |
| 審核 Bug 報告品質 | 13_ROLE_BUG_REPORT_ASSISTANT.md |
