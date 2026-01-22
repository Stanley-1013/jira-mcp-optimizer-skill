#!/usr/bin/env python3
"""
Git ↔ Jira 輔助腳本

Usage:
    python git_helpers.py validate "PROJ-123 feat: add feature"
    python git_helpers.py branch PROJ-123 "add user auth"
    python git_helpers.py mr-desc PROJ-123
    python git_helpers.py create-bug --title "Fix login" --mr-url "..."
"""

import re
import sys
import argparse
from typing import Optional, Tuple

# === Commit Validation ===

COMMIT_PATTERN = re.compile(
    r'^([A-Z]+-\d+)\s+(feat|fix|chore|docs|refactor|test|style|perf|ci|build|revert)(\([^)]+\))?:\s+.+'
)

JIRA_KEY_PATTERN = re.compile(r'^[A-Z]+-\d+')


def validate_commit(message: str) -> Tuple[bool, str]:
    """驗證 commit message 格式"""
    message = message.strip()

    # 檢查是否有 Jira key
    if not JIRA_KEY_PATTERN.match(message):
        return False, "Missing Jira key at start (e.g., PROJ-123)"

    # 檢查完整格式
    if not COMMIT_PATTERN.match(message):
        return False, "Invalid format. Expected: PROJ-123 type: description"

    return True, "Valid commit message"


def extract_jira_keys(text: str) -> list:
    """從文字中提取所有 Jira keys"""
    return re.findall(r'[A-Z]+-\d+', text)


# === Branch Name Generation ===

def generate_branch_name(jira_key: str, description: str, branch_type: str = "feature") -> str:
    """產生 branch 名稱"""
    # 清理 description
    clean_desc = re.sub(r'[^a-zA-Z0-9\s-]', '', description.lower())
    clean_desc = re.sub(r'\s+', '-', clean_desc.strip())
    clean_desc = clean_desc[:30]  # 限制長度

    return f"{branch_type}/{jira_key}-{clean_desc}"


# === MR Description Generation ===

MR_TEMPLATE = """## Jira
- **Issue**: [{key}](https://jira.example.com/browse/{key})
{epic_line}

## Summary
<!-- 這個 MR 做了什麼 -->

## Changes
-

## Test Plan
-

---
Closes {key}
"""


def generate_mr_description(jira_key: str, epic_key: Optional[str] = None) -> str:
    """產生 MR description"""
    epic_line = ""
    if epic_key:
        epic_line = f"- **Epic**: [{epic_key}](https://jira.example.com/browse/{epic_key})"

    return MR_TEMPLATE.format(key=jira_key, epic_line=epic_line)


# === Bug Creation (Stub) ===

def create_bug_stub(title: str, mr_url: str, auto_close: bool = False) -> dict:
    """
    建立 Bug 的 stub（實際需要連接 Jira MCP）

    Returns:
        dict: 準備好的 Jira API payload
    """
    return {
        "fields": {
            "project": {"key": "PROJ"},  # 需要替換
            "issuetype": {"name": "Bug"},
            "summary": f"[Auto] {title}",
            "description": f"Merged from: {mr_url}\n\nThis bug was discovered and fixed in a single MR.",
            "labels": ["auto-created", "fixed-in-mr"]
        },
        "transition_to_done": auto_close
    }


# === CLI ===

def main():
    parser = argparse.ArgumentParser(description="Git ↔ Jira 輔助工具")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # validate
    validate_parser = subparsers.add_parser("validate", help="驗證 commit message")
    validate_parser.add_argument("message", help="Commit message to validate")

    # branch
    branch_parser = subparsers.add_parser("branch", help="產生 branch 名稱")
    branch_parser.add_argument("jira_key", help="Jira issue key (e.g., PROJ-123)")
    branch_parser.add_argument("description", help="Short description")
    branch_parser.add_argument("--type", default="feature",
                               choices=["feature", "bugfix", "hotfix", "chore", "refactor"],
                               help="Branch type")

    # mr-desc
    mr_parser = subparsers.add_parser("mr-desc", help="產生 MR description")
    mr_parser.add_argument("jira_key", help="Jira issue key")
    mr_parser.add_argument("--epic", help="Epic key (optional)")

    # create-bug
    bug_parser = subparsers.add_parser("create-bug", help="產生建 Bug 的 payload")
    bug_parser.add_argument("--title", required=True, help="Bug title")
    bug_parser.add_argument("--mr-url", required=True, help="MR URL")
    bug_parser.add_argument("--auto-close", action="store_true", help="Auto transition to Done")

    # extract-keys
    extract_parser = subparsers.add_parser("extract-keys", help="從文字提取 Jira keys")
    extract_parser.add_argument("text", help="Text to extract from")

    args = parser.parse_args()

    if args.command == "validate":
        valid, msg = validate_commit(args.message)
        print(f"{'✓' if valid else '✗'} {msg}")
        sys.exit(0 if valid else 1)

    elif args.command == "branch":
        branch = generate_branch_name(args.jira_key, args.description, args.type)
        print(branch)

    elif args.command == "mr-desc":
        desc = generate_mr_description(args.jira_key, args.epic)
        print(desc)

    elif args.command == "create-bug":
        import json
        payload = create_bug_stub(args.title, args.mr_url, args.auto_close)
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    elif args.command == "extract-keys":
        keys = extract_jira_keys(args.text)
        print("\n".join(keys) if keys else "No Jira keys found")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
