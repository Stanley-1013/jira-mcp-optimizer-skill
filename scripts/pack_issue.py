#!/usr/bin/env python3
"""Pack a Jira issue JSON into a compact markdown context.

Usage:
    python pack_issue.py issue.json > issue_packed.md
    cat issue.json | python pack_issue.py > issue_packed.md

Input: JSON from Jira (issue object)
Output: compact markdown to paste into LLM

This script extracts only the essential fields from a Jira issue,
reducing token usage by 70-90% compared to raw JSON.
"""

import json
import sys
from typing import Any, Dict, Optional

KEEP_FIELDS = [
    ("key", None),
    ("fields.summary", None),
    ("fields.status.name", None),
    ("fields.issuetype.name", None),
    ("fields.priority.name", None),
    ("fields.assignee.displayName", None),
    ("fields.reporter.displayName", None),
    ("fields.labels", []),
    ("fields.components", []),
    ("fields.created", None),
    ("fields.updated", None),
    ("fields.description", ""),
    ("fields.resolution.name", None),
    ("fields.fixVersions", []),
]


def get_path(obj: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Safely navigate nested dictionary using dot notation."""
    cur: Any = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def format_date(date_str: Optional[str]) -> str:
    """Format ISO date to readable format."""
    if not date_str:
        return ""
    # Take just the date part: 2024-01-15T10:30:00.000+0000 -> 2024-01-15
    return date_str[:10] if len(date_str) >= 10 else date_str


def truncate_text(text: str, max_length: int = 4000) -> str:
    """Truncate text with indication if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 20] + "\n\n...(truncated)"


def pack_issue(raw: Dict[str, Any]) -> str:
    """Convert raw Jira issue JSON to compact markdown."""
    out = []

    key = get_path(raw, "key", "(no-key)")
    summary = get_path(raw, "fields.summary", "(no summary)")
    out.append(f"# {key} — {summary}")
    out.append("")

    # Meta section
    status = get_path(raw, "fields.status.name", "")
    itype = get_path(raw, "fields.issuetype.name", "")
    prio = get_path(raw, "fields.priority.name", "")
    assignee = get_path(raw, "fields.assignee.displayName", "")
    reporter = get_path(raw, "fields.reporter.displayName", "")
    resolution = get_path(raw, "fields.resolution.name", "")
    created = format_date(get_path(raw, "fields.created", ""))
    updated = format_date(get_path(raw, "fields.updated", ""))

    out.append("## Meta")
    out.append(f"- **Type**: {itype}")
    out.append(f"- **Status**: {status}")
    if resolution:
        out.append(f"- **Resolution**: {resolution}")
    out.append(f"- **Priority**: {prio}")
    if assignee:
        out.append(f"- **Assignee**: {assignee}")
    if reporter:
        out.append(f"- **Reporter**: {reporter}")
    if created:
        out.append(f"- **Created**: {created}")
    if updated:
        out.append(f"- **Updated**: {updated}")

    # Labels
    labels = get_path(raw, "fields.labels", []) or []
    if labels:
        out.append(f"- **Labels**: {', '.join(labels)}")

    # Components
    comps = get_path(raw, "fields.components", []) or []
    if comps:
        names = [c.get("name", "") for c in comps if isinstance(c, dict)]
        names = [n for n in names if n]
        if names:
            out.append(f"- **Components**: {', '.join(names)}")

    # Fix Versions
    versions = get_path(raw, "fields.fixVersions", []) or []
    if versions:
        names = [v.get("name", "") for v in versions if isinstance(v, dict)]
        names = [n for n in names if n]
        if names:
            out.append(f"- **Fix Versions**: {', '.join(names)}")

    # Description
    out.append("")
    out.append("## Description")
    desc = get_path(raw, "fields.description", "") or ""

    if isinstance(desc, dict):
        # Atlassian Document Format (ADF) - extract text content
        out.append(_extract_adf_text(desc))
    else:
        desc = desc.strip()
        out.append(truncate_text(desc))

    # Comments (if present)
    comments = get_path(raw, "fields.comment.comments", [])
    if comments:
        out.append("")
        out.append("## Recent Comments")
        # Show last 3 comments only
        for comment in comments[-3:]:
            author = get_path(comment, "author.displayName", "Unknown")
            created = format_date(get_path(comment, "created", ""))
            body = get_path(comment, "body", "")
            if isinstance(body, dict):
                body = _extract_adf_text(body)
            body = truncate_text(body, 500)
            out.append(f"\n**{author}** ({created}):")
            out.append(body)

    return "\n".join(out) + "\n"


def _extract_adf_text(adf: Dict[str, Any], depth: int = 0) -> str:
    """Extract plain text from Atlassian Document Format."""
    if depth > 10:  # Prevent infinite recursion
        return ""

    result = []

    if adf.get("type") == "text":
        return adf.get("text", "")

    content = adf.get("content", [])
    for node in content:
        if isinstance(node, dict):
            node_type = node.get("type", "")

            if node_type == "text":
                result.append(node.get("text", ""))
            elif node_type == "paragraph":
                result.append(_extract_adf_text(node, depth + 1))
                result.append("\n")
            elif node_type == "bulletList":
                for item in node.get("content", []):
                    result.append("• " + _extract_adf_text(item, depth + 1).strip())
                    result.append("\n")
            elif node_type == "orderedList":
                for i, item in enumerate(node.get("content", []), 1):
                    result.append(f"{i}. " + _extract_adf_text(item, depth + 1).strip())
                    result.append("\n")
            elif node_type == "heading":
                level = node.get("attrs", {}).get("level", 1)
                result.append("#" * level + " " + _extract_adf_text(node, depth + 1).strip())
                result.append("\n")
            elif node_type == "codeBlock":
                result.append("```\n")
                result.append(_extract_adf_text(node, depth + 1))
                result.append("\n```\n")
            else:
                # Generic handling for other node types
                result.append(_extract_adf_text(node, depth + 1))

    return "".join(result)


def main() -> int:
    """Main entry point."""
    try:
        if len(sys.argv) > 1:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                raw = json.load(f)
        else:
            raw = json.load(sys.stdin)

        output = pack_issue(raw)
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
