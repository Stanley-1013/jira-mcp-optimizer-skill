# Tool Map — Jira MCP 工具對照表

> 本文件將 Jira MCP 工具映射到概念動作，作為所有其他文件的基礎參考。

## 快速導覽

| 動作類型 | 工具數量 | 跳轉 |
|---------|----------|------|
| 讀取 Issue | 2 | [Read](#read-issue) |
| 搜尋 Issue | 4 | [Search](#search-issues) |
| 建立/修改 Issue | 2 | [Write](#write-issue) |
| Sprint/Agile | 5 | [Agile](#agile--sprint) |
| 用戶相關 | 6 | [User](#user-operations) |
| Confluence | 25+ | [Confluence](#confluence) |

---

## Read Issue

### read_jira_issue
**用途**: 讀取單一 issue 的完整資訊

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| issueKey | string | ✓ | Issue key (如 "PROJ-123") |
| expand | string | | 展開屬性，預設 "fields,transitions,changelog" |

**回傳**: Issue 完整物件，含 fields、transitions、changelog

**使用時機**:
- 更新前先讀取確認狀態
- 需要完整資訊（含 changelog、transitions）
- 檢查 issue 是否存在

**範例**:
```python
result = read_jira_issue(issueKey="PROJ-123", expand="fields,transitions")
```

---

## Search Issues

### search_jira_issues
**用途**: 使用 JQL 搜尋 issues

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| jql | string | ✓ | JQL 查詢語句 |
| fields | string | | 回傳欄位，預設 "*all" |
| maxResults | number | | 最多回傳數，預設 50，最大 100 |
| startAt | number | | 分頁起始位置，預設 0 |

**回傳**: `{ issues: [...], total: N, maxResults: M, startAt: S }`

**使用時機**:
- 按條件批次查詢
- 需要分頁處理大量結果
- 指定只回傳需要的欄位（省 token）

**最佳實踐**:
```python
# ✅ 好：限制欄位、限制數量
search_jira_issues(
    jql="project = ABC AND updated >= -7d",
    fields="key,summary,status,assignee",
    maxResults=20
)

# ❌ 差：無限制
search_jira_issues(jql="project = ABC")
```

### search_issues_by_user_involvement
**用途**: 按用戶參與度搜尋（assignee/reporter/creator/watcher）

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| searchType | enum | ✓ | "assignee", "reporter", "creator", "watcher", "all" |
| accountId | string | | 用戶 account ID |
| username | string | | 用戶名（可替代 accountId）|
| projectKeys | array | | 過濾專案 |
| issueType | string | | 過濾 issue 類型 |
| status | string | | 過濾狀態 |
| maxResults | number | | 最多 100 |

### list_issues_by_user_role
**用途**: 按用戶角色列出 issues，支援日期過濾

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| role | enum | ✓ | "assignee", "reporter", "creator" |
| accountId | string | | 用戶 account ID |
| startDate | string | | 開始日期 YYYY-MM-DD |
| endDate | string | | 結束日期 YYYY-MM-DD |

### get_my_unresolved_issues
**用途**: 取得我的未解決 issues

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| projectKeys | array | | 過濾專案列表 |
| maxResults | number | | 最多 100，預設 50 |

---

## Write Issue

### create_jira_issue
**用途**: 建立新 issue

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| projectKey | string | ✓ | 專案 key |
| issueType | string | ✓ | Issue 類型 ("Bug", "Task", "Story"...) |
| summary | string | ✓ | 標題 |
| description | string | | 描述 |
| priority | string | | 優先級 |
| assignee | string | | 指派人 account ID |
| labels | array | | 標籤列表 |
| components | array | | 元件列表 |
| customFields | object | | 自訂欄位 `{"customfield_10010": "value"}` |

**回傳**: 新建立的 issue key

**使用時機**:
- Triage 流程建立新票
- 自動化建票

### add_jira_comment
**用途**: 對 issue 添加評論

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| issueKey | string | ✓ | Issue key |
| body | string | ✓ | 評論內容 |
| visibility | object | | 可見性設定 `{type: "role"/"group", value: "..."}` |

---

## Agile / Sprint

### list_agile_boards
**用途**: 列出可存取的敏捷看板

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| projectKeyOrId | string | | 過濾特定專案 |
| type | enum | | "scrum" / "kanban" |
| maxResults | number | | 最多 50 |

### list_sprints_for_board
**用途**: 列出看板的 Sprints

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| boardId | number | ✓ | 看板 ID |
| state | enum | | "active", "closed", "future" |
| maxResults | number | | 最多 50 |

### get_sprint_details
**用途**: 取得 Sprint 詳細資訊及其所有 issues

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| sprintId | number | ✓ | Sprint ID |

### get_my_current_sprint_issues
**用途**: 取得我在當前 Sprint 的 issues

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| boardId | number | | 看板 ID（可選）|
| projectKey | string | | 專案 key（可選）|

---

## User Operations

### get_jira_current_user
**用途**: 取得當前認證用戶資訊

**回傳**: account ID, displayName, email, avatar URLs

### get_jira_user
**用途**: 查詢特定用戶

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| accountId | string | | 用戶 account ID |
| username | string | | 用戶名 |
| email | string | | Email |

### get_user_activity_history
**用途**: 取得用戶活動歷史

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| accountId | string | | 用戶 account ID |
| activityType | enum | | "comments", "transitions", "all" |
| days | number | | 回溯天數，預設 30，最大 365 |
| projectKeys | array | | 過濾專案 |

### get_user_time_tracking
**用途**: 取得用戶的工時記錄

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| accountId | string | | 用戶 account ID |
| startDate | string | | 開始日期 |
| endDate | string | | 結束日期 |
| projectKeys | array | | 過濾專案 |

---

## Meta / Project

### list_jira_projects
**用途**: 列出可存取的專案

**參數**:
| 參數 | 類型 | 必填 | 說明 |
|------|------|------|------|
| expand | string | | 展開屬性，預設 "description,lead,issueTypes" |

---

## Confluence

> Confluence 工具用於文檔管理，與 Jira 配合使用。

### 讀取

| 工具 | 用途 |
|------|------|
| read_confluence_page | 讀取單一頁面（支援 storage/markdown 格式）|
| search_confluence_pages | CQL 搜尋頁面 |
| list_confluence_spaces | 列出空間 |
| get_confluence_space | 取得空間詳情 |
| list_confluence_page_children | 列出子頁面 |
| list_confluence_page_ancestors | 取得頁面層級 |
| get_my_recent_confluence_pages | 我最近的頁面 |

### 寫入

| 工具 | 用途 |
|------|------|
| create_confluence_page | 建立頁面（支援 Markdown 輸入）|
| update_confluence_page | 更新頁面（需提供 version）|
| add_confluence_comment | 添加頁面評論 |
| add_confluence_page_label | 添加標籤 |

### 附件

| 工具 | 用途 |
|------|------|
| list_attachments_on_page | 列出頁面附件 |
| download_confluence_attachment | 下載附件（base64）|
| upload_confluence_attachment | 上傳附件 |
| get_page_with_attachments | 一次取得頁面內容與所有附件 |

### 用戶

| 工具 | 用途 |
|------|------|
| get_confluence_current_user | 當前用戶 |
| get_confluence_user | 查詢用戶 |
| find_confluence_users | 搜尋用戶 |
| search_pages_by_user_involvement | 按用戶參與搜尋 |
| list_pages_created_by_user | 用戶建立的頁面 |
| list_attachments_uploaded_by_user | 用戶上傳的附件 |

### 匯出

| 工具 | 用途 |
|------|------|
| export_confluence_page | 匯出頁面為 HTML/Markdown（圖片內嵌 base64）|

---

## Response Path Conventions

### Issue Object
```
issue.key                          # "PROJ-123"
issue.fields.summary               # "Issue title"
issue.fields.description           # 描述（可能是 string 或 ADF object）
issue.fields.status.name           # "In Progress"
issue.fields.issuetype.name        # "Bug"
issue.fields.priority.name         # "High"
issue.fields.assignee.displayName  # "John Doe"
issue.fields.assignee.accountId    # "5c1234..."
issue.fields.reporter.displayName  # "Jane Smith"
issue.fields.labels                # ["backend", "urgent"]
issue.fields.components[].name     # "API"
issue.fields.created               # "2024-01-15T10:30:00.000+0000"
issue.fields.updated               # "2024-01-16T14:20:00.000+0000"
issue.fields.comment.comments[]    # 評論列表
```

### Search Results
```
result.issues[]         # Issue 列表
result.total            # 總數
result.maxResults       # 本次最大數
result.startAt          # 起始位置
```

---

## Tool Selection Decision Tree

```
需要操作 Jira?
├── 讀取
│   ├── 單一 issue → read_jira_issue
│   ├── 批次查詢 → search_jira_issues
│   ├── 我的未完成 → get_my_unresolved_issues
│   └── Sprint 相關 → get_my_current_sprint_issues
├── 建立
│   └── 新 issue → create_jira_issue
├── 更新
│   ├── 加評論 → add_jira_comment
│   └── 改欄位 → (先 read → 再用對應更新工具)
└── Sprint/Agile
    ├── 列出看板 → list_agile_boards
    ├── 列出 Sprint → list_sprints_for_board
    └── Sprint 詳情 → get_sprint_details
```
