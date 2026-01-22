# Issue Description Templates

> 標準化的 Issue 描述模板，確保資訊完整性和一致性。

---

## Bug Template

### 完整版

```markdown
## Summary
[一句話描述問題]

## Environment
| 項目 | 值 |
|------|-----|
| Platform | Web / iOS / Android / Desktop |
| Browser | Chrome / Safari / Firefox / Edge |
| Version | [App/Browser version] |
| OS | [Operating system] |
| User Role | [如適用] |

## Steps to Reproduce
1. [前置條件或狀態]
2. [操作步驟 1]
3. [操作步驟 2]
4. [觸發問題的動作]

## Expected Behavior
[描述預期應該發生什麼]

## Actual Behavior
[描述實際發生了什麼]

## Error Messages
```
[完整錯誤訊息，如有]
```

## Screenshots / Videos
[附件說明或 N/A]

## Logs
<details>
<summary>Console/Network Logs</summary>

```
[相關 log]
```
</details>

## Impact Assessment
- **Severity**: Critical / High / Medium / Low
- **Affected Users**: [估計影響範圍]
- **Workaround**: [有 / 無] - [描述替代方案]
- **Regression**: [是 / 否 / 不確定] - [如是，何時開始]

## Additional Context
[其他相關資訊、關聯 issues、相關 PR 等]
```

### 簡化版（資訊有限時）

```markdown
## Summary
[問題描述]

## Steps to Reproduce
1. [步驟]

## Expected vs Actual
- **Expected**: [預期]
- **Actual**: [實際]

## Severity
[Critical / High / Medium / Low]

## Needs Info
- [ ] 重現步驟需要更多細節
- [ ] 需要環境資訊
- [ ] 需要錯誤訊息/Log
- [ ] 需要截圖/影片
```

---

## Task Template

### 標準版

```markdown
## Objective
[這個任務要達成什麼目標]

## Context
[背景說明、為什麼需要做這個]

## Scope
### In Scope
- [包含項目 1]
- [包含項目 2]

### Out of Scope
- [不包含項目 1]
- [不包含項目 2]

## Requirements
- [ ] [需求 1]
- [ ] [需求 2]
- [ ] [需求 3]

## Technical Notes
[技術考量、實作方向、相關文件連結]

## Dependencies
- [依賴的其他 issues/tasks]
- [需要其他團隊協助的部分]

## Definition of Done
- [ ] [完成條件 1]
- [ ] [完成條件 2]
- [ ] Code reviewed
- [ ] Tests passed
- [ ] Documentation updated (if needed)
```

### 簡化版

```markdown
## Objective
[目標]

## Tasks
- [ ] [子任務 1]
- [ ] [子任務 2]
- [ ] [子任務 3]

## Notes
[相關資訊]
```

---

## Story Template

### User Story Format

```markdown
## User Story
**As a** [用戶角色]
**I want to** [功能/能力]
**So that** [價值/目的]

## Context
[背景說明、業務價值]

## Acceptance Criteria
- [ ] **Given** [前置條件] **When** [動作] **Then** [結果]
- [ ] **Given** [前置條件] **When** [動作] **Then** [結果]
- [ ] **Given** [前置條件] **When** [動作] **Then** [結果]

## UI/UX Notes
[設計稿連結、UI 規格、交互說明]

## Technical Considerations
[技術限制、相關 API、效能考量]

## Out of Scope
- [不包含的內容]

## Open Questions
- [ ] [待確認問題 1]
- [ ] [待確認問題 2]

## Related
- Epic: [EPIC-XXX]
- Design: [Figma link]
- API Doc: [link]
```

---

## Epic Template

```markdown
## Vision
[這個 Epic 要解決什麼問題、達成什麼目標]

## Background
[業務背景、市場需求、用戶痛點]

## Goals
- [ ] [目標 1]
- [ ] [目標 2]
- [ ] [目標 3]

## Success Metrics
| Metric | Current | Target |
|--------|---------|--------|
| [指標] | [現況] | [目標] |

## Scope
### MVP (Phase 1)
- [Story 1]
- [Story 2]

### Phase 2
- [Story 3]
- [Story 4]

### Future
- [可能的延伸]

## Stakeholders
| Role | Name | Responsibility |
|------|------|----------------|
| Product | [name] | Requirements |
| Engineering | [name] | Implementation |
| Design | [name] | UI/UX |

## Timeline
- Discovery: [date range]
- Development: [date range]
- Release: [target date]

## Risks & Dependencies
| Risk/Dependency | Impact | Mitigation |
|-----------------|--------|------------|
| [項目] | [影響] | [對策] |

## Related
- PRD: [link]
- Design: [link]
- Technical Spec: [link]
```

---

## Sub-task Template

```markdown
## Parent
[PARENT-XXX] - [Parent summary]

## Task
[具體要做什麼]

## Implementation Notes
[實作細節、程式碼位置、測試方式]

## Estimated
[時間估計，如適用]
```

---

## Quick Fill Guide

### 資訊對應表

| 輸入類型 | 建議模板 | 必填欄位 |
|---------|---------|---------|
| 用戶回報問題 | Bug | Summary, Steps, Expected/Actual |
| 開發任務 | Task | Objective, Scope, DoD |
| 新功能需求 | Story | User Story, AC |
| 大型專案 | Epic | Vision, Goals, Scope |
| 細項工作 | Sub-task | Parent, Task |

### 資訊不足時的處理

```markdown
## Needs Info
以下資訊需要補充：
- [ ] [缺少的資訊 1]
- [ ] [缺少的資訊 2]

@[相關人員] 請協助提供上述資訊
```
