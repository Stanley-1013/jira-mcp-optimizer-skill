# Field Schema — 欄位/狀態/Transition 參考

> ⚠️ **重要**：本文件的欄位名稱和 ID 需根據你的 Jira 實例調整。
> 第一次使用時，請執行「初始化」流程取得實際值。

## 初始化流程

### 1. 取得專案 Issue Types
```python
# 使用 list_jira_projects 取得專案資訊
result = list_jira_projects(expand="description,lead,issueTypes")

# 記錄下來：
# - projectKey
# - issueTypes[].name
```

### 2. 取得欄位定義
```python
# 讀取任一 issue 來取得欄位結構
issue = read_jira_issue(issueKey="PROJ-1", expand="fields")

# 提取 customfield 對應
# customfield_10001 = "Story Points"
# customfield_10002 = "Epic Link"
# ...
```

### 3. 取得 Transitions
```python
# 讀取 issue 的可用 transitions
issue = read_jira_issue(issueKey="PROJ-1", expand="transitions")

# 記錄：
# transitions[].id
# transitions[].name
# transitions[].to.name
```

---

## 標準欄位

### 必填欄位（建立 Issue）

| 欄位 | API 名稱 | 類型 | 說明 |
|------|----------|------|------|
| 專案 | project | object | `{key: "ABC"}` |
| Issue 類型 | issuetype | object | `{name: "Bug"}` |
| 標題 | summary | string | 必填，建議 <= 80 字元 |

### 常用欄位

| 欄位 | API 名稱 | 類型 | 範例值 |
|------|----------|------|--------|
| 描述 | description | string/ADF | Markdown 或 ADF 格式 |
| 優先級 | priority | object | `{name: "High"}` |
| 指派人 | assignee | object | `{accountId: "5c..."}` |
| 報告人 | reporter | object | `{accountId: "5c..."}` |
| 標籤 | labels | array | `["backend", "urgent"]` |
| 元件 | components | array | `[{name: "API"}]` |
| 修復版本 | fixVersions | array | `[{name: "1.0.0"}]` |
| 到期日 | duedate | string | `"2024-12-31"` |

### 唯讀欄位

| 欄位 | API 路徑 | 說明 |
|------|----------|------|
| Key | key | Issue key (PROJ-123) |
| 狀態 | fields.status.name | 目前狀態 |
| 解決狀態 | fields.resolution.name | 解決方式 |
| 建立時間 | fields.created | ISO 時間 |
| 更新時間 | fields.updated | ISO 時間 |
| 建立者 | fields.creator | 建立者資訊 |

---

## Issue Types

> 根據你的 Jira 實例填入

### 標準類型

| 類型 | 名稱 | 用途 |
|------|------|------|
| Epic | Epic | 大功能/主題 |
| Story | Story | 用戶故事 |
| Task | Task | 工作項目 |
| Bug | Bug | 缺陷 |
| Sub-task | Sub-task | 子任務 |

### 專案特定類型

```
# TODO: 從你的 Jira 取得並填入
# 使用 list_jira_projects(expand="issueTypes") 取得
```

---

## Priority

| 優先級 | 名稱 | JQL 用法 |
|--------|------|----------|
| 1 | Highest | `priority = Highest` |
| 2 | High | `priority = High` |
| 3 | Medium | `priority = Medium` |
| 4 | Low | `priority = Low` |
| 5 | Lowest | `priority = Lowest` |

---

## Status & Status Category

### Status Categories（通用）

| Category | 說明 | JQL |
|----------|------|-----|
| To Do | 待辦 | `statusCategory = "To Do"` |
| In Progress | 進行中 | `statusCategory = "In Progress"` |
| Done | 已完成 | `statusCategory = Done` |

### 常見 Status 對應

| Status | Category | 說明 |
|--------|----------|------|
| Open | To Do | 新開 |
| To Do | To Do | 待辦 |
| In Progress | In Progress | 進行中 |
| In Review | In Progress | 審查中 |
| Blocked | In Progress | 被阻擋 |
| Done | Done | 已完成 |
| Closed | Done | 已關閉 |
| Resolved | Done | 已解決 |

### 專案特定 Status

```
# TODO: 從你的 Jira 取得並填入
# 使用 read_jira_issue(expand="transitions") 查看可用狀態
```

---

## Transitions

> Transition 是狀態之間的流轉，每個有唯一 ID

### 取得 Transition ID

```python
# 讀取 issue 取得可用 transitions
issue = read_jira_issue(issueKey="PROJ-123", expand="transitions")

# 結果範例：
# issue.transitions = [
#   {id: "11", name: "Start Progress", to: {name: "In Progress"}},
#   {id: "21", name: "Done", to: {name: "Done"}},
#   {id: "31", name: "Close", to: {name: "Closed"}}
# ]
```

### 常見 Transition 模板

| 動作 | Transition 名稱 | 目標狀態 |
|------|----------------|----------|
| 開始處理 | Start Progress | In Progress |
| 提交審查 | Submit for Review | In Review |
| 核准 | Approve | Approved |
| 完成 | Done / Resolve | Done |
| 關閉 | Close | Closed |
| 重新開啟 | Reopen | Open |

### 專案特定 Transitions

```
# TODO: 執行取得後填入
# 格式：TransitionID | Transition名稱 | 從狀態 | 到狀態
```

---

## Custom Fields

> ⚠️ Custom Field ID 因 Jira 實例而異

### 如何找到 Custom Field ID

```python
# 方法 1: 從 issue 回應中找
issue = read_jira_issue(issueKey="PROJ-1")
# 觀察 fields 中的 customfield_XXXXX

# 方法 2: 使用 normalize_fields.py 產生映射
# python scripts/normalize_fields.py --generate-map issue.json > field_map.json
```

### 常見 Custom Fields 模板

| 用途 | 常見 ID | 名稱 | 值類型 |
|------|---------|------|--------|
| Sprint | customfield_10000 | Sprint | array |
| Story Points | customfield_10001 | Story Points | number |
| Epic Link | customfield_10002 | Epic Link | string (key) |
| Epic Name | customfield_10003 | Epic Name | string |
| Rank | customfield_10004 | Rank | string |
| Team | customfield_10005 | Team | object |
| 驗收標準 | customfield_10006 | Acceptance Criteria | string |
| 開始日期 | customfield_10007 | Start Date | date |

### 你的 Custom Fields

```
# TODO: 從你的 Jira 取得並填入
# customfield_XXXXX = "欄位名稱"
```

---

## Resolution

| Resolution | 說明 |
|------------|------|
| Fixed | 已修復 |
| Won't Fix | 不修復 |
| Duplicate | 重複 |
| Cannot Reproduce | 無法重現 |
| Done | 已完成 |
| Won't Do | 不處理 |

---

## 欄位格式參考

### Description (ADF 格式)

```json
{
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "paragraph",
      "content": [
        {"type": "text", "text": "This is a paragraph"}
      ]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [{"type": "text", "text": "Item 1"}]
            }
          ]
        }
      ]
    }
  ]
}
```

### Assignee

```json
{
  "accountId": "5c1234567890abcdef123456"
}
```

### Components

```json
[
  {"name": "API"},
  {"name": "Frontend"}
]
```

### Labels

```json
["backend", "urgent", "v2"]
```

---

## 快速參照表

### 建立 Issue 最小 Payload

```json
{
  "projectKey": "ABC",
  "issueType": "Task",
  "summary": "Task title"
}
```

### 建立 Bug 完整 Payload

```json
{
  "projectKey": "ABC",
  "issueType": "Bug",
  "summary": "Login fails with invalid credentials",
  "description": "## Steps to Reproduce\n1. ...\n\n## Expected\n...\n\n## Actual\n...",
  "priority": "High",
  "labels": ["login", "critical"],
  "components": ["Authentication"]
}
```

### Comment Payload

```json
{
  "body": "Investigation complete. Root cause identified."
}
```
