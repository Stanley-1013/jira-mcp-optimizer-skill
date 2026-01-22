#!/usr/bin/env python3
"""Pack Jira search results into a compact markdown table.

Usage:
    python pack_search.py search.json > search_packed.md
    cat search.json | python pack_search.py > search_packed.md

Expected input JSON shape: { "issues": [ ... ], "total": N, "maxResults": M }

This script converts verbose Jira search results into a scannable table,
reducing token usage significantly while preserving key information.
"""

import json
import sys
from typing import Any, Dict, List, Optional


def get(d: Dict[str, Any], path: str, default: Any = "") -> Any:
    """Safely navigate nested dictionary using dot notation."""
    cur: Any = d
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return default
    return cur


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text with ellipsis."""
    text = str(text).replace("\n", " ").replace("|", "/").strip()
    if len(text) > max_len:
        return text[:max_len - 3] + "..."
    return text


def format_assignee(issue: Dict[str, Any]) -> str:
    """Format assignee display name or 'Unassigned'."""
    assignee = get(issue, "fields.assignee.displayName")
    if not assignee:
        return "Unassigned"
    # Shorten long names
    if len(assignee) > 15:
        parts = assignee.split()
        if len(parts) >= 2:
            return f"{parts[0]} {parts[-1][0]}."
    return assignee


def pack_search_results(data: Dict[str, Any], max_issues: int = 50) -> str:
    """Convert Jira search results to compact markdown table."""
    issues: List[Dict[str, Any]] = data.get("issues", []) if isinstance(data, dict) else []
    total = data.get("total", len(issues))
    start_at = data.get("startAt", 0)

    lines = []

    # Header with context
    lines.append(f"# Search Results")
    lines.append(f"")
    lines.append(f"Showing {len(issues[:max_issues])} of {total} issues (starting at {start_at})")
    lines.append("")

    # Table header
    lines.append("| Key | Type | Status | Priority | Assignee | Summary |")
    lines.append("|-----|------|--------|----------|----------|---------|")

    for issue in issues[:max_issues]:
        key = get(issue, "key")
        itype = get(issue, "fields.issuetype.name")
        status = get(issue, "fields.status.name")
        prio = get(issue, "fields.priority.name")
        assignee = format_assignee(issue)
        summary = truncate(get(issue, "fields.summary"), 50)

        lines.append(f"| {key} | {itype} | {status} | {prio} | {assignee} | {summary} |")

    # Footer with pagination hint
    if total > len(issues[:max_issues]):
        remaining = total - start_at - len(issues[:max_issues])
        if remaining > 0:
            lines.append("")
            lines.append(f"*{remaining} more issues not shown. Use pagination or refine JQL.*")

    return "\n".join(lines) + "\n"


def pack_search_detailed(data: Dict[str, Any], max_issues: int = 20) -> str:
    """Convert Jira search results to detailed list format."""
    issues: List[Dict[str, Any]] = data.get("issues", []) if isinstance(data, dict) else []
    total = data.get("total", len(issues))

    lines = []
    lines.append(f"# Search Results ({len(issues[:max_issues])} of {total})")
    lines.append("")

    for issue in issues[:max_issues]:
        key = get(issue, "key")
        summary = get(issue, "fields.summary")
        status = get(issue, "fields.status.name")
        itype = get(issue, "fields.issuetype.name")
        prio = get(issue, "fields.priority.name")
        assignee = format_assignee(issue)
        labels = get(issue, "fields.labels", [])
        updated = get(issue, "fields.updated", "")[:10]

        lines.append(f"## {key}: {truncate(summary, 60)}")
        lines.append(f"- **Type**: {itype} | **Status**: {status} | **Priority**: {prio}")
        lines.append(f"- **Assignee**: {assignee} | **Updated**: {updated}")
        if labels:
            lines.append(f"- **Labels**: {', '.join(labels[:5])}")
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pack Jira search results into compact markdown"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="JSON file to process (reads from stdin if not provided)"
    )
    parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="Output detailed list format instead of table"
    )
    parser.add_argument(
        "--max", "-m",
        type=int,
        default=50,
        help="Maximum number of issues to include (default: 50)"
    )

    args = parser.parse_args()

    try:
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)

        if args.detailed:
            output = pack_search_detailed(data, args.max)
        else:
            output = pack_search_results(data, args.max)

        sys.stdout.write(output)
        return 0

    except json.JSONDecodeError as e:
        sys.stderr.write(f"Error: Invalid JSON input - {e}\n")
        return 1
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: File not found - {e}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
