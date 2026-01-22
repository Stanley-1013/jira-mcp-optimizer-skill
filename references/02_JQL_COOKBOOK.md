# JQL Cookbook — 常用查詢範本

> JQL (Jira Query Language) 是 Jira 的查詢語言。本文件提供經過測試的常用範本。

## 基礎語法速查

### 運算子
| 運算子 | 說明 | 範例 |
|--------|------|------|
| = | 等於 | `status = "In Progress"` |
| != | 不等於 | `status != Done` |
| ~ | 包含（文字搜尋）| `summary ~ "login"` |
| !~ | 不包含 | `summary !~ "test"` |
| IN | 在列表中 | `status IN ("Open", "In Progress")` |
| NOT IN | 不在列表中 | `status NOT IN (Done, Closed)` |
| IS | 空值檢查 | `assignee IS EMPTY` |
| IS NOT | 非空值檢查 | `assignee IS NOT EMPTY` |
| >= <= > < | 比較（日期/數字）| `created >= -7d` |

### 邏輯運算
| 運算子 | 說明 |
|--------|------|
| AND | 且 |
| OR | 或 |
| NOT | 非 |
| () | 群組優先 |

### 時間表達式
| 表達式 | 說明 |
|--------|------|
| -7d | 過去 7 天 |
| -2w | 過去 2 週 |
| -1M | 過去 1 個月 |
| startOfDay() | 今天開始 |
| endOfDay() | 今天結束 |
| startOfWeek() | 本週開始 |
| startOfMonth() | 本月開始 |

---

## 最常用查詢（複製即用）

### 我的工作

```jql
# 指派給我的未完成工作
assignee = currentUser() AND statusCategory != Done ORDER BY priority DESC, updated DESC

# 我的待辦（高優先級）
assignee = currentUser() AND statusCategory != Done AND priority IN (Highest, High) ORDER BY priority DESC

# 我報告的 bug
reporter = currentUser() AND issuetype = Bug ORDER BY created DESC

# 我最近更新的
assignee = currentUser() AND updated >= -7d ORDER BY updated DESC
```

### 專案總覽

```jql
# 專案最近 7 天更新
project = ABC AND updated >= -7d ORDER BY updated DESC

# 專案未完成工作
project = ABC AND statusCategory != Done ORDER BY priority DESC, created ASC

# 專案本週新建
project = ABC AND created >= startOfWeek() ORDER BY created DESC

# 專案 bug 統計
project = ABC AND issuetype = Bug AND statusCategory != Done ORDER BY priority DESC
```

### Sprint / Backlog

```jql
# 當前 Sprint 的所有 issues
project = ABC AND sprint IN openSprints() ORDER BY rank ASC

# 當前 Sprint 未完成
project = ABC AND sprint IN openSprints() AND statusCategory != Done ORDER BY rank ASC

# Backlog（未排入 Sprint）
project = ABC AND sprint IS EMPTY AND statusCategory != Done ORDER BY priority DESC, created ASC

# 特定 Sprint
sprint = "Sprint 42" ORDER BY rank ASC
```

### Bug Triage

```jql
# 新 bug、尚未指派
project = ABC AND issuetype = Bug AND assignee IS EMPTY AND created >= -14d ORDER BY priority DESC, created DESC

# 高優先級 bug 未修
project = ABC AND issuetype = Bug AND priority IN (Highest, High) AND statusCategory != Done ORDER BY priority DESC

# 長期未處理的 bug（超過 30 天）
project = ABC AND issuetype = Bug AND statusCategory != Done AND created <= -30d ORDER BY created ASC

# 已解決但待驗證
project = ABC AND issuetype = Bug AND status = "Resolved" ORDER BY updated DESC
```

### 狀態追蹤

```jql
# 卡在「In Progress」超過 7 天
project = ABC AND status = "In Progress" AND updated <= -7d ORDER BY updated ASC

# 最近變成 Done
project = ABC AND status CHANGED TO Done AFTER -7d ORDER BY updated DESC

# 被 Reopen 的 issues
project = ABC AND status CHANGED FROM Done TO "Open" AFTER -30d ORDER BY updated DESC

# 狀態變更歷史
project = ABC AND status CHANGED DURING (startOfWeek(), endOfWeek()) ORDER BY updated DESC
```

### 標籤 / 元件

```jql
# 特定標籤
project = ABC AND labels = "urgent" ORDER BY priority DESC

# 多標籤（或）
project = ABC AND labels IN ("backend", "api") ORDER BY priority DESC

# 多標籤（且）
project = ABC AND labels = "backend" AND labels = "urgent" ORDER BY priority DESC

# 特定元件
project = ABC AND component = "API" AND statusCategory != Done ORDER BY priority DESC

# 無標籤的 issues
project = ABC AND labels IS EMPTY AND statusCategory != Done ORDER BY created DESC
```

### 跨專案

```jql
# 多專案查詢
project IN (ABC, XYZ) AND statusCategory != Done ORDER BY project ASC, priority DESC

# 全站高優先級
priority = Highest AND statusCategory != Done ORDER BY project ASC, updated DESC
```

---

## 進階技巧

### 文字搜尋優化

```jql
# 標題包含關鍵字（模糊）
summary ~ "login"

# 標題或描述包含
text ~ "authentication"

# 精確匹配（用引號）
summary ~ "\"user login\""

# 排除特定詞
summary ~ "login" AND summary !~ "test"
```

### 日期範圍

```jql
# 特定日期範圍
created >= "2024-01-01" AND created <= "2024-01-31"

# 上週
created >= startOfWeek(-1) AND created < startOfWeek()

# 上個月
created >= startOfMonth(-1) AND created < startOfMonth()

# 過去 N 個工作日（約略）
updated >= -5d AND updated <= now()
```

### 欄位存在性

```jql
# 有填 Story Points
"Story Points" IS NOT EMPTY

# 沒有 Due Date
duedate IS EMPTY

# 有 Epic Link
"Epic Link" IS NOT EMPTY
```

### 排序技巧

```jql
# 多欄位排序
ORDER BY priority DESC, created ASC

# 按 Rank（Scrum 看板順序）
ORDER BY rank ASC

# 按最後更新
ORDER BY updated DESC

# 按 Due Date（空的排最後）
ORDER BY duedate ASC NULLS LAST
```

---

## 效能最佳實踐

### ✅ 好的查詢習慣

```jql
# 1. 永遠指定 project
project = ABC AND status = "Open"

# 2. 限制時間範圍
project = ABC AND updated >= -30d

# 3. 使用 statusCategory 而非列舉所有狀態
statusCategory != Done  # 比 status NOT IN ("Done", "Closed", "Resolved") 好

# 4. 先窄後寬
project = ABC AND updated >= -7d AND assignee = currentUser()
```

### ❌ 避免的查詢

```jql
# 1. 無限制的全站搜尋
status = "Open"  # 沒有 project 限制

# 2. 過度使用文字搜尋
text ~ "a"  # 太廣泛

# 3. 複雜的 OR 嵌套
(A OR B) AND (C OR D) AND (E OR F)  # 改用多次查詢
```

---

## 除錯指南

### 常見錯誤

| 錯誤訊息 | 原因 | 解決方案 |
|---------|------|---------|
| `Field 'xxx' does not exist` | 欄位名稱錯誤 | 查 03_FIELD_SCHEMA.md |
| `Value 'xxx' does not exist` | 值不存在 | 確認狀態/優先級名稱 |
| `Function 'xxx' does not exist` | 函數名錯誤 | 檢查拼寫和括號 |
| `Unable to find JQL function` | 外掛函數不存在 | 使用標準函數 |
| 查詢 timeout | 太複雜/太廣 | 加 project + 時間限制 |

### 欄位名稱對照

| 常用名稱 | JQL 欄位名 |
|---------|-----------|
| Story Points | `"Story Points"` 或 `cf[10001]` |
| Sprint | `sprint` |
| Epic Link | `"Epic Link"` 或 `cf[10002]` |
| Team | `"Team"` 或對應的 customfield |

### 快速驗證

```jql
# 測試欄位是否存在
project = ABC AND "Your Field Name" IS NOT EMPTY LIMIT 1

# 測試值是否有效
project = ABC AND status = "Your Status" LIMIT 1
```

---

## 模板生成規則

當用戶描述需求時，使用以下規則轉換：

| 用戶說 | JQL 轉換 |
|-------|----------|
| "我的" / "給我的" | `assignee = currentUser()` |
| "未完成" / "還沒做" | `statusCategory != Done` |
| "最近" / "這週" | `updated >= -7d` 或 `updated >= startOfWeek()` |
| "bug" | `issuetype = Bug` |
| "高優先" | `priority IN (Highest, High)` |
| "沒人處理" | `assignee IS EMPTY` |
| "包含 XXX" | `summary ~ "XXX"` 或 `text ~ "XXX"` |
| "某專案" | `project = XXX` |
| "當前 sprint" | `sprint IN openSprints()` |
