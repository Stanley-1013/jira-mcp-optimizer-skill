# Git ↔ Jira Automation

> 狀態自動轉換設置

## 狀態流轉

```
To Do → In Progress → In Review → Done
         ↑              ↑           ↑
    Branch Created  MR Opened  MR Merged
```

## GitLab Integration 設置

1. Settings → Integrations → Jira
2. 啟用：
   - ✅ Enable comments
   - ✅ Enable Jira transitions
3. 設定 Done 的 Transition ID

## Jira Automation Rules

### Rule 1: Branch → In Progress
```
Trigger: Branch created
Action: Transition to "In Progress"
```

### Rule 2: MR → In Review
```
Trigger: Pull request created
Action: Transition to "In Review"
```

### Rule 3: Merged → Done
```
Trigger: Pull request merged
Action: Transition to "Done"
```

## Bug 修復無單

MR 加 label `bugfix-no-ticket`：
```bash
# CI 自動建單
python scripts/git_helpers.py create-bug \
  --title "$MR_TITLE" \
  --mr-url "$MR_URL" \
  --auto-close
```

---

**完整參考** → [14_WORKFLOW_GIT_INTEGRATION.md](14_WORKFLOW_GIT_INTEGRATION.md)
