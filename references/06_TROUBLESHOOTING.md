# Troubleshooting — 問題排解指南

> 常見問題的診斷和解決方案。

---

## 連線問題

### 401 Unauthorized

**症狀**: API 回傳 401 錯誤

**原因**:
- Token 過期
- Token 權限不足
- Token 被撤銷

**解決**:
1. 確認 MCP 連線設定中的 token 有效
2. 重新產生 API token（Atlassian Account Settings → Security → API Tokens）
3. 確認 token 有對應專案的存取權限

---

### 403 Forbidden

**症狀**: API 回傳 403 錯誤

**原因**:
- 用戶無該專案/issue 的權限
- IP 被封鎖
- 專案/issue 有額外權限限制

**解決**:
1. 確認用戶在 Jira 中有對應專案的存取權
2. 檢查專案權限設定（Project Settings → Permissions）
3. 確認 issue 沒有 security level 限制

---

### 連線逾時

**症狀**: 請求超時、無回應

**原因**:
- 網路問題
- Jira 伺服器負載過高
- 查詢太複雜/結果太多

**解決**:
1. 縮小查詢範圍（加 project、時間限制）
2. 減少 maxResults
3. 限制回傳的 fields
4. 稍後重試

---

## 查詢問題

### JQL Field Not Found

**錯誤訊息**: `Field 'xxx' does not exist or you do not have permission to view it`

**原因**:
- 欄位名稱拼寫錯誤
- Custom field 名稱不同
- 無該欄位的存取權

**解決**:
1. 確認欄位名稱（區分大小寫）
2. 查詢 03_FIELD_SCHEMA.md 確認正確名稱
3. Custom field 使用 `cf[XXXXX]` 格式
4. 用引號包住有空格的欄位名稱：`"Story Points"`

**範例**:
```jql
# 錯誤
storypoints > 0

# 正確
"Story Points" > 0
# 或
cf[10001] > 0
```

---

### JQL Value Not Found

**錯誤訊息**: `Value 'xxx' does not exist for field 'yyy'`

**原因**:
- 狀態/優先級名稱錯誤
- 該專案沒有此值

**解決**:
1. 確認狀態/優先級的正確名稱
2. 用 read_jira_issue 查看有效值
3. 使用 statusCategory 替代特定狀態

**範例**:
```jql
# 錯誤（狀態名可能因專案不同）
status = "In Dev"

# 更穩定
statusCategory = "In Progress"
```

---

### 查詢結果為空

**症狀**: 查詢執行成功但沒有結果

**檢查項目**:
1. JQL 條件是否太嚴格
2. 時間範圍是否正確
3. project key 是否正確
4. 用戶是否有存取權

**除錯方式**:
```jql
# 逐步放寬條件
# 第一步：只有 project
project = ABC

# 第二步：加一個條件
project = ABC AND statusCategory != Done

# 第三步：再加條件...
```

---

## 寫入問題

### Create Issue Failed

**錯誤訊息**: `Field 'xxx' is required`

**原因**:
- 缺少必填欄位

**解決**:
1. 確認 projectKey、issueType、summary 都有提供
2. 查詢專案的必填欄位設定
3. 某些專案可能有額外必填欄位

---

### Transition Failed

**錯誤訊息**: `Transition is not valid for this issue`

**原因**:
- Transition ID 錯誤
- 目前狀態無法執行該 transition
- 缺少 transition 的必填欄位

**解決**:
1. 先讀取 issue 取得可用 transitions
   ```python
   issue = read_jira_issue(issueKey="PROJ-123", expand="transitions")
   # 查看 issue.transitions 列表
   ```
2. 使用正確的 transition ID
3. 確認 transition 需要的欄位（如 resolution）

---

### Update Failed - Version Conflict

**錯誤訊息**: `version conflict` 或 `cannot update`

**原因**:
- 有人同時修改了 issue

**解決**:
1. 重新讀取 issue 取得最新版本
2. 重新執行更新
3. 考慮使用樂觀鎖或重試邏輯

---

## 效能問題

### 查詢太慢

**優化策略**:

```jql
# 1. 永遠指定 project
project = ABC AND ...

# 2. 加時間限制
project = ABC AND updated >= -30d

# 3. 使用索引欄位
# 好：project, status, assignee, reporter, created, updated
# 差：description, comment (文字搜尋慢)

# 4. 避免 OR 嵌套
# 差
(A OR B) AND (C OR D)
# 好：分成多次查詢

# 5. 限制結果數量
maxResults=20
```

---

### Token 用量過高

**優化策略**:

1. **使用壓縮腳本**
   ```bash
   # 不要直接貼 JSON
   python scripts/pack_issue.py issue.json > packed.md
   ```

2. **限制回傳欄位**
   ```python
   search_jira_issues(
       jql="...",
       fields="key,summary,status,assignee",  # 只要需要的欄位
       maxResults=20
   )
   ```

3. **兩段式查詢**
   ```python
   # 第一段：取 key 列表
   results = search_jira_issues(jql="...", fields="key", maxResults=50)

   # 第二段：詳讀少數 issues
   for key in selected_keys[:5]:
       issue = read_jira_issue(issueKey=key)
   ```

4. **快取 metadata**
   - Projects、issue types、fields 不常變，可以快取

---

## 常見錯誤訊息速查

| 錯誤訊息 | 可能原因 | 解決方向 |
|---------|---------|---------|
| 401 Unauthorized | Token 無效 | 重新設定認證 |
| 403 Forbidden | 權限不足 | 確認專案存取權 |
| 404 Not Found | Issue/Project 不存在 | 確認 key 正確 |
| 400 Bad Request | 請求格式錯誤 | 檢查參數格式 |
| Field does not exist | 欄位名錯誤 | 查 03_FIELD_SCHEMA |
| Value does not exist | 值不存在 | 確認有效值 |
| Transition not valid | 狀態流轉錯誤 | 查可用 transitions |
| Rate limit exceeded | 超過請求限制 | 等待或減少請求 |

---

## 除錯 Checklist

### 查詢不到預期結果
- [ ] project key 正確
- [ ] 欄位名稱正確（查 03_FIELD_SCHEMA）
- [ ] 值拼寫正確（狀態/優先級）
- [ ] 時間範圍合理
- [ ] 用戶有存取權

### 建立/更新失敗
- [ ] 必填欄位都有提供
- [ ] 欄位值格式正確
- [ ] 用戶有寫入權限
- [ ] Transition ID 正確（狀態變更）
- [ ] 無版本衝突

### 效能問題
- [ ] JQL 有 project 限制
- [ ] JQL 有時間限制
- [ ] maxResults 合理
- [ ] 只取需要的 fields
- [ ] 使用壓縮腳本

---

## 取得協助

### 自助診斷
1. 查本文件對應章節
2. 在 Jira 網頁 UI 測試同樣操作
3. 檢查 MCP 連線狀態

### 需要的資訊
回報問題時請提供：
- 錯誤訊息全文
- 使用的工具和參數
- 預期結果 vs 實際結果
- Jira 版本（Cloud/Server/Data Center）
