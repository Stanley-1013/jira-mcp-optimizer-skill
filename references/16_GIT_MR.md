# Git MR/PR Workflow

> MR 標題、描述模板、自動關單

## MR Title

```
[PROJ-123] Short summary
```

或：
```
feat(PROJ-123): implement user authentication
```

## MR Description 模板

```markdown
## Jira
- **Issue**: [PROJ-123](https://jira.example.com/browse/PROJ-123)
- **Epic**: [EPIC-12](https://jira.example.com/browse/EPIC-12)

## Summary
<!-- 這個 MR 做了什麼 -->

## Changes
-

## Test Plan
-

---
Closes PROJ-123
```

## 自動關單關鍵字

| Keyword | Effect |
|---------|--------|
| `Closes PROJ-123` | Merge 後自動 close |
| `Fixes PROJ-123` | 同上 |
| `Resolves PROJ-123` | 同上 |

## 腳本輔助

```bash
# 從 Jira issue 產生 MR description
python scripts/git_helpers.py mr-desc PROJ-123

# 產生帶 Epic link 的完整模板
python scripts/git_helpers.py mr-desc PROJ-123 --with-epic
```

---

**完整參考** → [14_WORKFLOW_GIT_INTEGRATION.md](14_WORKFLOW_GIT_INTEGRATION.md)
