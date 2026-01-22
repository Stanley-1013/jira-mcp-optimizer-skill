# Comment Templates

> Jira 評論模板，用於標準化溝通和記錄。

---

## Status Updates

### Progress Update

```markdown
**Status Update** - [DATE]

**Summary**: [一句話描述目前狀態]

**Completed**:
- [x] [已完成項目 1]
- [x] [已完成項目 2]

**In Progress**:
- [ ] [進行中項目 1] - [進度 %]

**Blockers**: [無 / 描述阻擋因素]

**Next Steps**:
- [下一步 1]
- [下一步 2]

**ETA**: [預計完成日期，如適用]
```

### Sprint Update

```markdown
**Sprint Progress** - Sprint [N]

| Item | Status | Notes |
|------|--------|-------|
| [Feature A] | ✅ Done | Merged to main |
| [Feature B] | 🔄 In Progress | 70% complete |
| [Bug Fix C] | ⏳ Blocked | Waiting for API |

**Velocity**: [N] points completed of [M] committed

**Concerns**:
- [風險或需要注意的事項]
```

### Handoff

```markdown
**Handoff Notes** 🔄

**From**: [Your name]
**To**: [Recipient name]
**Reason**: [PTO / Role change / etc.]

**Current Status**: [狀態描述]

**Important Context**:
- [關鍵資訊 1]
- [關鍵資訊 2]

**Pending Actions**:
- [ ] [待完成項目 1]
- [ ] [待完成項目 2]

**Contacts**:
- [Stakeholder A] - [關於什麼問題]
- [Stakeholder B] - [關於什麼問題]

**Files/Links**:
- [相關文件連結]
```

---

## Questions & Clarifications

### Question

```markdown
**Question** ❓

**Topic**: [問題主題]

**Question**:
[具體問題內容]

**Context**:
[為什麼問這個問題 / 背景說明]

**My Understanding**:
[目前的理解，可能是錯的]

**Options I'm Considering**:
1. [選項 A] - [pros/cons]
2. [選項 B] - [pros/cons]

@[relevant person] Could you help clarify?

**Deadline**: [需要答覆的時間，如適用]
```

### Clarification Request

```markdown
**Clarification Needed** 🔍

Hi @[name],

關於 [主題/需求]，我需要確認以下幾點：

1. **[問題 1]**
   - 目前理解: [...]
   - 需要確認: [...]

2. **[問題 2]**
   - 目前理解: [...]
   - 需要確認: [...]

這些會影響 [影響範圍]，希望能在 [時間] 前得到答覆。

謝謝！
```

---

## Technical Notes

### Investigation

```markdown
**Investigation Notes** 🔍

**Date**: [DATE]
**Investigated by**: [Name]

**Summary**: [一句話總結]

**Findings**:
1. **[發現 1]**
   - Detail: [詳細說明]
   - Evidence: [證據/log/截圖]

2. **[發現 2]**
   - Detail: [詳細說明]
   - Evidence: [證據/log/截圖]

**Root Cause**:
[根本原因分析]

**Related Code**:
```
[相關程式碼片段或檔案路徑]
```

**Recommendations**:
- [建議 1]
- [建議 2]

**Next Steps**:
- [ ] [下一步行動]
```

### Technical Decision

```markdown
**Technical Decision** ⚙️

**Decision**: [決定摘要]

**Context**:
[背景說明]

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| A: [選項A] | [優點] | [缺點] |
| B: [選項B] | [優點] | [缺點] |

**Decision**: We will go with **[選項]**

**Rationale**:
[選擇原因]

**Trade-offs Accepted**:
- [接受的權衡 1]
- [接受的權衡 2]

**Decided by**: [Names]
**Date**: [Date]
```

### Code Review Feedback

```markdown
**Code Review** 📝

PR: [PR link]
Reviewer: [Name]

**Summary**: [整體評估 - Approve/Request Changes]

**Highlights** ✅:
- [做得好的地方]

**Suggestions** 💡:
- [ ] [建議 1] - [file:line]
- [ ] [建議 2] - [file:line]

**Required Changes** 🔴:
- [ ] [必須修改 1] - [原因]
- [ ] [必須修改 2] - [原因]

**Questions**:
- [程式碼相關問題]
```

---

## Resolution & Closure

### Bug Resolution

```markdown
**Resolution** ✅

**Root Cause**:
[根本原因說明]

**Fix Applied**:
[修復內容說明]

**Changes Made**:
- [變更 1] - [file/component]
- [變更 2] - [file/component]

**Verification**:
- [x] Unit tests added/updated
- [x] Manual testing completed
- [x] Regression testing passed
- [ ] [其他驗證項目]

**Affected Areas**:
- [受影響功能 1]
- [受影響功能 2]

**Related**:
- PR: [link]
- Commit: [hash]
- Tests: [link]

**Deployed to**: [env] on [date]
```

### Cannot Reproduce

```markdown
**Cannot Reproduce** 🔍

Attempted to reproduce on [DATE] by [Name].

**Environment Tested**:
- Platform: [...]
- Browser: [...]
- Version: [...]

**Steps Followed**:
1. [步驟 1]
2. [步驟 2]
3. [步驟 3]

**Result**: Unable to reproduce the issue

**Possible Reasons**:
- [可能原因 1]
- [可能原因 2]

**Next Steps**:
- [ ] Request more details from reporter
- [ ] Try different environment
- [ ] Monitor for recurrence

@[reporter] 能否提供更多資訊？
```

### Won't Fix

```markdown
**Decision: Won't Fix** ❌

**Reason**: [原因類別 - Design decision / Out of scope / Low priority / etc.]

**Explanation**:
[詳細說明為什麼不修復]

**Alternatives**:
- [替代方案 1]
- [替代方案 2]

**Related**:
- [相關決策文件/issue]

Decided by: [Name]
Date: [Date]
```

### Duplicate

```markdown
**Duplicate** 🔄

This issue is a duplicate of [ISSUE-XXX].

**Comparison**:
| This Issue | Original Issue |
|------------|----------------|
| [症狀] | [相同症狀] |
| [環境] | [相同/不同] |

Please follow [ISSUE-XXX] for updates.

Closing this issue.
```

---

## Collaboration

### Review Request

```markdown
**Review Request** 👀

Hi @[reviewer],

Could you please review [what needs review]?

**Context**:
[背景說明]

**What to Review**:
- [重點 1]
- [重點 2]

**Links**:
- PR: [link]
- Doc: [link]
- Design: [link]

**Timeline**: 希望能在 [時間] 前完成

謝謝！
```

### Blocking Notice

```markdown
**Blocking Notice** 🚫

This issue is **blocked** by:
- [BLOCKER-XXX] - [描述]

**Impact**:
- [受影響的工作]
- [時程影響]

**Unblocking Actions**:
- [ ] [需要做什麼來解除阻擋]

**Escalation**: [是否需要升級處理]

@[relevant team/person] 請協助處理
```

### Deployment Notice

```markdown
**Deployment Notice** 🚀

**Deployed to**: [Production / Staging / etc.]
**Date/Time**: [YYYY-MM-DD HH:MM TZ]
**Version**: [version/tag]

**Changes Included**:
- [ISSUE-XXX] - [描述]
- [ISSUE-YYY] - [描述]

**Rollback Plan**:
[如何回滾]

**Monitoring**:
- Dashboard: [link]
- Alerts: [status]

**Verification**:
- [x] Smoke tests passed
- [x] Key metrics normal
- [ ] [其他驗證]
```

---

## Quick Reference

| Situation | Template |
|-----------|----------|
| 定期更新狀態 | Progress Update |
| 交接工作 | Handoff |
| 需要澄清 | Question / Clarification Request |
| 調查結果 | Investigation |
| 技術決策 | Technical Decision |
| Code Review | Code Review Feedback |
| Bug 修復 | Bug Resolution |
| 無法重現 | Cannot Reproduce |
| 不修復 | Won't Fix |
| 重複 issue | Duplicate |
| 請求 review | Review Request |
| 被阻擋 | Blocking Notice |
| 部署通知 | Deployment Notice |
