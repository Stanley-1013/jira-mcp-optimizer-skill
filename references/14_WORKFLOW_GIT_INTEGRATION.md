# Git ↔ Jira Integration Workflow

> 把 Jira issue key 當成 Git ↔ Jira 的 join key，用命名規範 + MR 模板 + 自動 transition 實現專案管理自動化。

## Core Principle

**每一段 Git 活動都要能對到 Jira key**

不管是 GitLab Jira integration 還是 Jira Automation triggers，都依賴「能從 branch / commit / MR 找到 Jira issue key」。

---

## 1. Git 命名規範

### A. Branch 命名（強制帶 Story/Bug key）

```
feature/PROJ-123-short-desc
bugfix/PROJ-456-null-pointer
chore/PROJ-789-deps-bump
hotfix/PROJ-101-critical-fix
```

| Prefix | Use Case | Example |
|--------|----------|---------|
| `feature/` | 新功能開發 | `feature/PROJ-123-user-auth` |
| `bugfix/` | Bug 修復 | `bugfix/PROJ-456-login-error` |
| `hotfix/` | 緊急修復 | `hotfix/PROJ-789-prod-crash` |
| `chore/` | 維護/依賴更新 | `chore/PROJ-101-upgrade-deps` |
| `refactor/` | 重構 | `refactor/PROJ-202-cleanup-api` |

### B. Commit Message 格式

**基本格式（Conventional Commits + Jira key）：**

```
PROJ-123 feat: add user authentication

PROJ-456 fix: handle null pointer in payment module

PROJ-789 chore: update dependencies
```

**帶 scope：**

```
PROJ-123 feat(auth): implement OAuth2 login
PROJ-456 fix(payment): validate card number before submit
```

### C. Smart Commits（直接從 commit 操作 Jira）

> 需要啟用 Jira + GitLab/GitHub integration

| Action | Syntax | Example |
|--------|--------|---------|
| 留言 | `#comment <text>` | `PROJ-123 #comment fixed validation logic` |
| 記工時 | `#time <duration>` | `PROJ-123 #time 2h 30m Investigation` |
| 轉狀態 | `#<transition-name>` | `PROJ-123 #start-review` |
| 組合 | 多個指令同一行 | `PROJ-123 #time 1h #comment done #resolve` |

**注意：**
- Transition 名稱遇到空白用 `-` 連接（如 `#start-review`）
- 若 workflow transition 有必填欄位，Smart Commit 可能「無聲失敗」

---

## 2. MR/PR 模板

### MR Title 格式

```
[PROJ-123] Short summary of changes
```

或使用 Conventional Commits 風格：

```
feat(PROJ-123): implement user authentication
fix(PROJ-456): resolve null pointer exception
```

### MR Description 模板

```markdown
## Jira

- **Story/Task**: [PROJ-123](https://your-jira.atlassian.net/browse/PROJ-123)
- **Epic**: [EPIC-12](https://your-jira.atlassian.net/browse/EPIC-12)

## Summary

<!-- 簡述這個 MR 做了什麼 -->

## Changes

- [ ] Change 1
- [ ] Change 2

## Test Plan

<!-- 測試步驟 -->

## Rollback Plan

<!-- 回滾步驟（如適用）-->

---

Closes PROJ-123
```

**關鍵字效果：**

| Keyword | Effect (GitLab) | Effect (GitHub) |
|---------|-----------------|-----------------|
| `Closes PROJ-123` | Merge 後自動 close | Merge 後自動 close |
| `Fixes PROJ-123` | 同上 | 同上 |
| `Resolves PROJ-123` | 同上 | 同上 |

---

## 3. 狀態自動轉換

### 路線 1：GitLab Jira Integration

**設置：**
1. GitLab → Settings → Integrations → Jira
2. 啟用：
   - Enable comments（自動在 Jira 加評論）
   - Enable Jira transitions（自動轉狀態）
   - 設定 Transition ID（或用 Done category）

**效果：**
- Commit/MR 提到 `PROJ-123` → Jira 自動加 cross-reference comment
- MR merged → Jira issue 自動轉到 Done

### 路線 2：Jira Automation（DevOps Triggers）

**觸發事件：**

| Event | Jira Automation Trigger | Suggested Action |
|-------|------------------------|------------------|
| Branch created | `Branch created` | → Transition to "In Progress" |
| PR/MR opened | `Pull request created` | → Transition to "In Review" |
| PR/MR merged | `Pull request merged` | → Transition to "Done" |
| Build success | `Build successful` | → Add comment |
| Deploy to prod | `Deployment successful` | → Transition to "Deployed" |

**範例 Automation Rule：**

```yaml
# PR Merged → Done
trigger: Pull request merged
condition:
  - issue.type in ["Story", "Task", "Bug"]
action:
  - Transition issue to "Done"
  - Add comment: "Merged via {{pullRequest.url}}"
```

### 推薦狀態流轉

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   To Do     │ ──► │ In Progress │ ──► │  In Review  │ ──► │    Done     │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   ▲                   ▲                   ▲
       │                   │                   │                   │
       │            Branch Created       MR Opened           MR Merged
       │                                                          │
       └──────────────────────────────────────────────────────────┘
                              (Manual: Reopen)
```

---

## 4. Bug 修復工作流

### A. 已有 Bug 單（推薦）

```bash
# 1. 建立 bugfix branch
git checkout -b bugfix/BUG-123-fix-login-error

# 2. 修復並 commit（帶 Jira key）
git commit -m "BUG-123 fix: resolve login validation error"

# 3. 開 MR 並在 description 加上
# Closes BUG-123
# 修復說明：...

# 4. Merge 後 Jira 自動：
#    - 加上 MR link 評論
#    - 轉狀態到 Done/Resolved
```

### B. 沒有 Bug 單（自動補建）

**方案 B1：CI Job 自動建單（推薦）**

1. 開發者在 MR 加 label：`bugfix-no-ticket`
2. 或在 MR description 寫：`CreateBug: <bug title>`
3. CI job 偵測後：
   - 用 Jira API 建立 Bug
   - 自動填入 MR link、修復說明
   - 立刻 transition 到 Done
   - 在 MR 回貼「已建立 BUG-xxx」

**CI Script 範例（GitLab CI）：**

```yaml
create-bug-ticket:
  stage: post-merge
  rules:
    - if: $CI_MERGE_REQUEST_LABELS =~ /bugfix-no-ticket/
  script:
    - |
      # 使用 Jira MCP 或 REST API 建立 Bug
      python scripts/create_bug_from_mr.py \
        --title "$CI_MERGE_REQUEST_TITLE" \
        --description "$CI_MERGE_REQUEST_DESCRIPTION" \
        --mr-url "$CI_MERGE_REQUEST_URL" \
        --project "PROJ" \
        --transition-to "Done"
```

**方案 B2：強制先建單**

用 GitLab merge check 擋掉沒有 Jira key 的 MR：
- Settings → Merge requests → Require an associated Jira issue

---

## 5. Integration with Jira MCP

### 相關工具

| Tool | Use Case |
|------|----------|
| `create_jira_issue` | 從 MR/commit 建立 Bug/Task |
| `read_jira_issue` | 讀取 issue 狀態 |
| `add_jira_comment` | 自動添加 Git 活動評論 |
| `search_jira_issues` | 查找相關 issue |

### Workflow: Commit 時更新 Jira

```python
# scripts/update_jira_from_commit.py
import re
import subprocess
from jira_mcp import add_jira_comment

def get_jira_keys_from_commit(commit_msg):
    """從 commit message 提取 Jira keys"""
    pattern = r'([A-Z]+-\d+)'
    return re.findall(pattern, commit_msg)

def update_jira_from_commit():
    # 獲取最新 commit message
    commit_msg = subprocess.check_output(
        ['git', 'log', '-1', '--format=%s%n%b']
    ).decode().strip()

    # 提取 Jira keys
    keys = get_jira_keys_from_commit(commit_msg)

    for key in keys:
        # 在 Jira 添加評論
        add_jira_comment(
            issueKey=key,
            body=f"Commit: {commit_msg}\nBranch: {get_current_branch()}"
        )
```

### Workflow: MR Merged 時自動建/更新 Bug

```python
# scripts/create_bug_from_mr.py
from jira_mcp import create_jira_issue, read_jira_issue

def create_bug_from_mr(title, description, mr_url, project):
    """從 MR 建立已完成的 Bug"""

    # 建立 Bug
    issue = create_jira_issue(
        projectKey=project,
        issueType="Bug",
        summary=f"[Auto] {title}",
        description=f"""
## Source
Merged from: {mr_url}

## Fix Description
{description}

## Status
This bug was discovered and fixed in a single MR.
Auto-created and marked as Done.
        """,
        labels=["auto-created", "fixed-in-mr"]
    )

    # TODO: Transition to Done
    # (需要根據專案 workflow 設定 transition ID)

    return issue['key']
```

---

## 6. MVP 設置清單

### Phase 1：命名規範（立即可做）

- [ ] 統一 branch 命名：`<type>/PROJ-123-desc`
- [ ] Commit message 帶 Jira key
- [ ] MR description 固定模板

### Phase 2：GitLab Integration（需設置）

- [ ] 啟用 GitLab Jira integration
- [ ] Enable comments
- [ ] Enable Jira transitions
- [ ] 設定 merge check（require Jira issue）

### Phase 3：Jira Automation（進階）

- [ ] 設定 DevOps triggers
- [ ] Branch created → In Progress
- [ ] MR merged → Done
- [ ] Deploy success → Deployed

### Phase 4：自動建單（可選）

- [ ] 設定 CI job 偵測 `bugfix-no-ticket`
- [ ] 實作 `create_bug_from_mr.py`
- [ ] 測試完整流程

---

## 7. Troubleshooting

### Smart Commits 不生效

| 問題 | 可能原因 | 解決 |
|------|---------|------|
| Transition 失敗 | Workflow 有必填欄位 | 移除必填或用 Automation |
| 沒有 comment | Integration 未啟用 | 檢查 GitLab/GitHub integration |
| Key 沒被識別 | 格式不對 | 確認是大寫 + 正確格式 |

### Jira Automation 不觸發

| 問題 | 可能原因 | 解決 |
|------|---------|------|
| PR merged 沒反應 | Integration 未連接 | 重新設定 GitLab for Jira app |
| 觸發但沒動作 | Condition 不符 | 檢查 issue type/project filter |
| 部分 issue 沒動 | 權限問題 | 確認 automation 有 transition 權限 |

---

## 8. Templates

### Git Commit Template

```
# .gitmessage
# Format: PROJ-123 type(scope): subject
#
# Types: feat, fix, chore, docs, style, refactor, test
# Smart Commits: #comment, #time, #transition-name

```

### Pre-commit Hook（驗證 Jira key）

```bash
#!/bin/sh
# .git/hooks/commit-msg

commit_msg=$(cat "$1")
jira_pattern="^[A-Z]+-[0-9]+"

if ! echo "$commit_msg" | grep -qE "$jira_pattern"; then
    echo "ERROR: Commit message must start with Jira issue key (e.g., PROJ-123)"
    exit 1
fi
```

### GitLab MR Template

```markdown
<!-- .gitlab/merge_request_templates/Default.md -->

## Jira

- **Issue**: <!-- PROJ-123 -->
- **Epic**: <!-- EPIC-12 (if applicable) -->

## Summary

<!-- What does this MR do? -->

## Changes

-

## Test Plan

-

## Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Jira issue linked

---

Closes <!-- PROJ-123 -->
```
