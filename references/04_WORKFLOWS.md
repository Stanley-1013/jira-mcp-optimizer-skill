# Workflows — 標準作業流程

> 每個 Workflow 定義輸入、輸出、步驟、品質關卡。
> 嚴格遵循可確保一致性和可追溯性。

---

## W1 — Triage：將描述轉成 Jira Issue

### 概述
把一段需求描述或 bug 報告轉成標準化的 Jira issue。

### 輸入
- 原始需求描述（自然語言）
- 專案 key（必須）
- Issue type 偏好（可選）

### 輸出
- 1 張標準化的 Jira issue
- Issue key 回報給用戶

### 步驟

```
1. 釐清資訊
   ├── 確認 projectKey
   ├── 判斷 issueType (Bug/Task/Story)
   ├── 評估 priority
   └── 識別 labels / components

2. 檢查重複
   └── search_jira_issues(jql="project = X AND text ~ '關鍵字' AND statusCategory != Done", maxResults=5)
       ├── 有重複 → 回報現有 issue，詢問是否要補充
       └── 無重複 → 繼續

3. 產生內容
   ├── 使用模板產出 summary（<= 80 字元）
   ├── 使用模板產出 description
   └── 使用模板產出 acceptance criteria（若適用）

4. 建立 Issue
   └── create_jira_issue(projectKey, issueType, summary, description, priority, labels)

5. 驗證
   └── read_jira_issue(issueKey) 確認建立成功

6. 後續
   ├── 需要指派 → add_jira_comment 說明
   └── 回報 issue key 給用戶
```

### 品質關卡
- [ ] Summary <= 80 字元，清楚描述問題
- [ ] Description 包含足夠上下文
- [ ] 若為 Bug，必須有重現步驟或標記 "needs-info"
- [ ] 若為 Story，必須有 AC
- [ ] 已檢查重複

### 範例

**輸入**:
> 用戶登入時如果密碼錯誤，系統只顯示 500 錯誤，沒有友善提示

**輸出**:
```json
{
  "projectKey": "AUTH",
  "issueType": "Bug",
  "summary": "Login shows 500 error instead of friendly message for wrong password",
  "description": "## Context\nUser authentication flow\n\n## Steps to Reproduce\n1. Go to login page\n2. Enter valid username\n3. Enter wrong password\n4. Click login\n\n## Expected\nShow friendly error message: \"Invalid credentials\"\n\n## Actual\nShows HTTP 500 error page\n\n## Impact\nPoor user experience, users may think system is broken",
  "priority": "High",
  "labels": ["login", "ux", "error-handling"]
}
```

---

## W2 — Search：用自然語言找票

### 概述
將用戶的自然語言查詢轉成 JQL 並執行搜尋。

### 輸入
- 自然語言查詢描述
- 專案範圍（可選）

### 輸出
- 搜尋結果摘要（壓縮格式）
- 若需詳情，提供 issue keys

### 步驟

```
1. 理解需求
   ├── 識別關鍵條件（專案、狀態、時間、人員）
   └── 確認排序需求

2. 轉換 JQL
   └── 參考 02_JQL_COOKBOOK.md 選擇模板

3. 執行搜尋
   └── search_jira_issues(jql, fields="key,summary,status,priority,assignee", maxResults=20)

4. 壓縮結果
   └── 使用 pack_search.py 或手動整理成表格

5. 呈現
   ├── 顯示總數和前 N 筆
   └── 若需詳情，提供 read_jira_issue 的選項
```

### JQL 轉換規則

| 用戶說 | JQL |
|-------|-----|
| "我的未完成" | `assignee = currentUser() AND statusCategory != Done` |
| "這週的 bug" | `issuetype = Bug AND created >= startOfWeek()` |
| "給 John 的高優先" | `assignee = "John" AND priority IN (Highest, High)` |
| "包含 login 的" | `text ~ "login"` |
| "當前 sprint" | `sprint IN openSprints()` |

### 品質關卡
- [ ] JQL 有加 project 限制（除非明確要跨專案）
- [ ] 結果數量合理（< 50）
- [ ] 若結果太多，建議縮小範圍

---

## W3 — Update：修改 Issue

### 概述
安全地更新 Jira issue 的欄位或狀態。

### 輸入
- Issue key
- 要修改的內容

### 輸出
- 修改確認
- 修改前後 diff

### 步驟

```
1. 讀取現況
   └── read_jira_issue(issueKey, expand="fields,transitions")
       └── 記錄目前值：status, assignee, 其他欄位

2. 分析變更
   └── 列出要改的欄位和目標值
       └── 產出 diff 格式：
           ```
           欄位      | 目前值      | 目標值
           --------- | ----------- | -------
           status    | Open        | In Progress
           assignee  | Unassigned  | John
           ```

3. 確認
   └── 呈現 diff 給用戶確認
       ├── 用戶確認 → 繼續
       └── 用戶取消 → 結束

4. 執行變更
   ├── 狀態變更 → 找對應 transition ID，執行 transition
   ├── 指派/欄位 → 使用對應更新工具
   └── 一次只改一個欄位（或有依賴關係的一組）

5. 驗證
   └── read_jira_issue(issueKey) 確認變更成功

6. 記錄
   └── 若需要，add_jira_comment 說明變更原因
```

### 品質關卡
- [ ] 先讀後寫（確認目前狀態）
- [ ] 產出 diff 並確認
- [ ] 驗證變更成功
- [ ] 不可逆操作需明確確認

### 注意事項
- 狀態流轉需使用正確的 transition ID
- 某些欄位可能有順序依賴（先改 A 才能改 B）
- 權限不足時會失敗，需處理錯誤

---

## W4 — Sprint Planning

### 概述
協助 Sprint 規劃，從 backlog 挑選 issues 進入 sprint。

### 輸入
- 專案 key
- Sprint 名稱或 ID
- 可選：容量限制

### 輸出
- Sprint 建議清單
- 總 story points 估算

### 步驟

```
1. 取得 Sprint 資訊
   ├── list_agile_boards(projectKeyOrId=X)
   └── list_sprints_for_board(boardId, state="active")
       或 list_sprints_for_board(boardId, state="future")

2. 取得 Backlog
   └── search_jira_issues(
         jql="project = X AND sprint IS EMPTY AND statusCategory != Done ORDER BY priority DESC, rank ASC",
         fields="key,summary,priority,customfield_XXXXX",  # Story Points
         maxResults=50
       )

3. 壓縮展示
   └── 使用 pack_search.py 產出表格

4. 分析建議
   ├── 依優先級排序
   ├── 計算總 story points
   └── 若有容量限制，標示建議範圍

5. 呈現選項
   └── 讓用戶選擇要加入的 issues

6. 執行（若用戶確認）
   └── 更新選中 issues 的 sprint 欄位
```

### 品質關卡
- [ ] 清楚列出 backlog 優先順序
- [ ] 計算 story points 總和
- [ ] 不超過 sprint 容量
- [ ] 用戶明確選擇後才執行

---

## W5 — Bug Report 標準化

### 概述
將 bug 報告標準化，確保包含所有必要資訊。

### 必要資訊

```markdown
## Summary
[一句話描述 bug]

## Environment
- Platform: [Web/iOS/Android]
- Browser: [Chrome/Safari/Firefox]
- Version: [App version or build]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[預期應該發生什麼]

## Actual Behavior
[實際發生什麼]

## Error Messages / Logs
```
[貼上錯誤訊息或日誌]
```

## Screenshots / Videos
[附件或連結]

## Impact
- Severity: [Critical/High/Medium/Low]
- Affected Users: [估計影響範圍]

## Additional Context
[其他相關資訊]
```

### 缺失資訊處理

| 缺失 | 處理 |
|------|------|
| 無重現步驟 | 標籤 "needs-repro-steps" |
| 環境不明 | 標籤 "needs-env-info" |
| 無法確認影響 | 標籤 "needs-impact-assessment" |
| 全部資訊充足 | 標籤 "ready-for-triage" |

---

## W6 — Daily Standup 支援

### 概述
快速取得個人工作狀態彙整。

### 步驟

```
1. 取得我的進行中
   └── search_jira_issues(
         jql="assignee = currentUser() AND status = 'In Progress'",
         maxResults=10
       )

2. 取得我昨天完成的
   └── search_jira_issues(
         jql="assignee = currentUser() AND status CHANGED TO Done AFTER -1d",
         maxResults=10
       )

3. 取得阻擋項目
   └── search_jira_issues(
         jql="assignee = currentUser() AND (status = Blocked OR labels = blocked)",
         maxResults=10
       )

4. 產出摘要
   └── 格式化成 standup 格式：
       - 昨天完成：...
       - 今天計劃：...
       - 阻擋：...
```

---

## Workflow 選擇指南

```
用戶需求
├── "建票" / "新增" / "triage"
│   └── W1 Triage
├── "找" / "搜尋" / "查詢"
│   └── W2 Search
├── "改" / "更新" / "移動狀態"
│   └── W3 Update
├── "sprint" / "規劃"
│   └── W4 Sprint Planning
├── "bug" / "回報問題"
│   └── W5 Bug Report
└── "standup" / "我的工作"
    └── W6 Daily Standup
```
