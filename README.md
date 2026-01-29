# Jira MCP Optimizer

讓 AI Agent 用最少 token、最少往返、最可靠的方式操作 Jira/Confluence。

---

## Prerequisites

### 1. Jira Cloud API Token

前往 [Atlassian API Token](https://id.atlassian.com/manage-profile/security/api-tokens) 建立 token。

### 2. 安裝 Jira MCP Server

此 Skill 依賴 Jira MCP Server 提供底層工具（`mcp__Jira__*`）。請先完成安裝：

```json
{
  "mcpServers": {
    "Jira": {
      "command": "npx",
      "args": ["-y", "jira-mcp-server"],
      "env": {
        "JIRA_BASE_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "you@example.com",
        "JIRA_API_TOKEN": "your-api-token",
        "CONFLUENCE_BASE_URL": "https://your-domain.atlassian.net/wiki"
      }
    }
  }
}
```

> MCP Server 名稱必須為 `Jira`，才能匹配 Skill 中的 `mcp__Jira__*` 工具模式。

---

## Installation

<details>
<summary><strong>Claude Code (CLI)</strong></summary>

```bash
# 全域安裝（所有專案可用）
git clone https://github.com/Stanley-1013/jira-mcp-optimizer-skill.git \
  ~/.claude/skills/jira-mcp-optimizer

# 或專案級安裝（僅限單一專案）
git clone https://github.com/Stanley-1013/jira-mcp-optimizer-skill.git \
  .claude/skills/jira-mcp-optimizer
```

MCP 設定檔位置：`~/.claude/settings.json`

</details>

<details>
<summary><strong>Cursor</strong></summary>

1. 將本 repo clone 到任意位置
2. 打開 Cursor Settings → Features → Rules
3. 新增 Rule，將 `SKILL.md` 內容貼入作為 System Prompt
4. MCP 設定：Settings → MCP Servers → 加入上方 JSON

</details>

<details>
<summary><strong>Windsurf</strong></summary>

1. Clone 本 repo
2. 將 `SKILL.md` 內容加入 `.windsurfrules` 或全域 Rules
3. MCP 設定：`~/.codeium/windsurf/mcp_config.json`

</details>

<details>
<summary><strong>Antigravity</strong></summary>

1. Clone 本 repo 到工作目錄
2. 在 Agent 設定中引用 `SKILL.md` 作為 System Instructions
3. MCP 設定依 Antigravity 文件加入 Jira Server

</details>

<details>
<summary><strong>其他平台（通用）</strong></summary>

核心檔案是 `SKILL.md`，任何支援 Custom Instructions + MCP 的 AI Agent 平台皆可使用：

1. 將 `SKILL.md` 內容作為 System Prompt / Instructions 載入
2. 設定 Jira MCP Server 連線
3. 確保 Agent 可存取 `references/` 和 `scripts/` 目錄

</details>

---

## What This Skill Does

### 核心能力

| 功能 | 說明 |
|------|------|
| 查票 | 自然語言 → JQL，限制範圍與欄位控制回應量 |
| 建票 | 結構化 Triage，自動套用模板與欄位驗證 |
| 改狀態 | 先讀後寫 + diff 確認，防止亂改 |
| Sprint 規劃 | Board/Sprint 操作，velocity 分析 |
| PRD 審核 | 解析需求文件，產出結構化回饋 |
| 文件導入 | PRD/需求批量轉 Jira Issues |
| 風險分析 | 時程/資源/品質/範圍四維預測 |
| Git ↔ Jira 同步 | 偵測 commit/branch/MR 中的 issue key，自動同步狀態 |
| 視覺化儀表板 | 專案進度 + 戰略風險分析 → 互動式 HTML Dashboard |

### 10 種角色

按任務場景自動切換專業角色：Decision Director、Work Organizer、PRD Guide、Work Item Planner、Readiness Checker、Progress Tracker、Bug Report Assistant、Import Validator、Risk Analyst、Dashboard Builder。

### 安全機制

- **寫入前確認**：所有 Jira 寫入操作需使用者確認
- **先讀再寫**：更新前必讀取現狀
- **最小變更**：一次只改必要欄位
- **資料摘要**：`scripts/pack_*.py` 結構化 Jira 資料供報告與多次引用（sub-agent 模式下可避免主 context 污染）

---

## Repo Structure

```
├── SKILL.md                  # 主設定（角色、流程、Guardrails）
├── references/
│   ├── 00_INDEX.md           # 全索引導航
│   ├── 01-06                 # 工具/JQL/欄位/流程/Prompt/除錯
│   ├── 07-13, 19-21          # Role 定義檔
│   ├── 14-18                 # Git Integration & Doc Import
│   └── templates/            # HTML 模板（Dashboard 等）
└── scripts/
    ├── pack_search.py        # 搜尋結果壓縮
    ├── pack_issue.py         # Issue 詳情壓縮
    ├── pack_dashboard.py     # Dashboard 數據彙整 + HTML 產出
    ├── normalize_fields.py   # 欄位正規化
    └── git_helpers.py        # Git ↔ Jira 輔助工具
```

---

## Quick Tips

- 提到 Jira 相關操作時，Agent 應自動載入此 Skill
- 如未自動載入，可手動輸入 `/jira-mcp-optimizer`
- 建議在 `CLAUDE.md` 加入：`涉及 Jira 操作時，必須先載入 jira-mcp-optimizer skill`

## License

MIT
