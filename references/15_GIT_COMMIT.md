# Git Commit Workflow

> 最小化：只管 commit message 格式

## Commit Message 格式

```
PROJ-123 type: short description
```

**Examples:**
```bash
PROJ-123 feat: add user authentication
PROJ-456 fix: resolve null pointer in payment
PROJ-789 chore: update dependencies
```

## Types

| Type | Use Case |
|------|----------|
| `feat` | 新功能 |
| `fix` | Bug 修復 |
| `chore` | 維護/依賴 |
| `docs` | 文檔 |
| `refactor` | 重構 |
| `test` | 測試 |

## Smart Commits（可選）

```bash
# 留言
PROJ-123 fix: resolve bug #comment fixed validation

# 記工時
PROJ-123 feat: add auth #time 2h

# 轉狀態
PROJ-123 fix: done #resolve
```

## 驗證腳本

```bash
# 快速驗證 commit message
python scripts/git_helpers.py validate "PROJ-123 feat: add feature"
```

---

**完整參考** → [14_WORKFLOW_GIT_INTEGRATION.md](14_WORKFLOW_GIT_INTEGRATION.md)
