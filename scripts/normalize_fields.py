#!/usr/bin/env python3
"""Normalize Jira custom field names to human-readable names.

Usage:
    python normalize_fields.py issue.json --map field_map.json > normalized.json
    python normalize_fields.py --generate-map issue.json > field_map.json

This script helps manage custom fields by:
1. Generating a mapping template from issue metadata
2. Applying mappings to convert customfield_XXXXX to readable names
"""

import json
import sys
import re
from typing import Any, Dict, List, Optional
from pathlib import Path


DEFAULT_FIELD_MAP = {
    # Common custom fields - update these for your Jira instance
    "customfield_10000": "sprint",
    "customfield_10001": "story_points",
    "customfield_10002": "epic_link",
    "customfield_10003": "epic_name",
    "customfield_10004": "rank",
    "customfield_10005": "flagged",
    "customfield_10006": "team",
    "customfield_10007": "acceptance_criteria",
    "customfield_10008": "start_date",
    "customfield_10009": "due_date",
    # Add your custom fields below
}


def load_field_map(map_file: Optional[str]) -> Dict[str, str]:
    """Load field mapping from JSON file or use defaults."""
    if map_file and Path(map_file).exists():
        with open(map_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_FIELD_MAP.copy()


def is_custom_field(field_name: str) -> bool:
    """Check if field name is a custom field."""
    return bool(re.match(r"customfield_\d+", field_name))


def normalize_field_name(field_name: str, field_map: Dict[str, str]) -> str:
    """Convert custom field ID to human-readable name."""
    if field_name in field_map:
        return field_map[field_name]
    return field_name


def normalize_issue(issue: Dict[str, Any], field_map: Dict[str, str]) -> Dict[str, Any]:
    """Normalize all custom fields in an issue."""
    result = {}

    for key, value in issue.items():
        if key == "fields" and isinstance(value, dict):
            # Normalize fields section
            normalized_fields = {}
            for field_key, field_value in value.items():
                new_key = normalize_field_name(field_key, field_map)
                normalized_fields[new_key] = field_value
            result[key] = normalized_fields
        else:
            result[key] = value

    return result


def generate_field_map(issues: List[Dict[str, Any]]) -> Dict[str, str]:
    """Generate a field mapping template from issue data."""
    custom_fields = set()

    for issue in issues:
        fields = issue.get("fields", {})
        for field_name in fields.keys():
            if is_custom_field(field_name):
                custom_fields.add(field_name)

    # Create mapping with placeholder values
    field_map = {}
    for cf in sorted(custom_fields):
        # Try to infer name from schema if available
        suggested_name = cf.replace("customfield_", "custom_")
        field_map[cf] = suggested_name

    return field_map


def extract_field_names_from_meta(create_meta: Dict[str, Any]) -> Dict[str, str]:
    """Extract field names from Jira createmeta response."""
    field_map = {}

    projects = create_meta.get("projects", [])
    for project in projects:
        issue_types = project.get("issuetypes", [])
        for issue_type in issue_types:
            fields = issue_type.get("fields", {})
            for field_id, field_info in fields.items():
                if is_custom_field(field_id):
                    name = field_info.get("name", "")
                    if name:
                        # Convert to snake_case
                        normalized = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower()).strip('_')
                        field_map[field_id] = normalized

    return field_map


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Normalize Jira custom field names"
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="JSON file to process (reads from stdin if not provided)"
    )
    parser.add_argument(
        "--map", "-m",
        dest="map_file",
        help="Path to field mapping JSON file"
    )
    parser.add_argument(
        "--generate-map", "-g",
        action="store_true",
        help="Generate field map template from input"
    )
    parser.add_argument(
        "--from-meta",
        action="store_true",
        help="Extract field names from createmeta response"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (defaults to stdout)"
    )

    args = parser.parse_args()

    try:
        # Read input
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = json.load(sys.stdin)

        # Process based on mode
        if args.generate_map:
            # Generate mapping template
            issues = data.get("issues", [data]) if isinstance(data, dict) else [data]
            result = generate_field_map(issues)
        elif args.from_meta:
            # Extract from createmeta
            result = extract_field_names_from_meta(data)
        else:
            # Normalize issue(s)
            field_map = load_field_map(args.map_file)

            if "issues" in data:
                # Search results
                data["issues"] = [normalize_issue(i, field_map) for i in data["issues"]]
                result = data
            else:
                # Single issue
                result = normalize_issue(data, field_map)

        # Output
        output = json.dumps(result, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output + "\n")
        else:
            sys.stdout.write(output + "\n")

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
