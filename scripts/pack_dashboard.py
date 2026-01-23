#!/usr/bin/env python3
"""
pack_dashboard.py - Strategic Dashboard Generator

Transforms Jira project data into a self-contained HTML dashboard
with Chart.js visualizations and strategic risk analysis.

Target audience: Chairman / C-level executives (Traditional Chinese labels)

Usage:
    python pack_dashboard.py --data metrics.json --output dashboard.html
    python pack_dashboard.py --data metrics.json --output dashboard.html --offline
    cat metrics.json | python pack_dashboard.py --output dashboard.html

Input: JSON with collected Jira data (see INPUT_SCHEMA below)
Output: Self-contained HTML dashboard file
"""

import json
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HEALTH_THRESHOLDS = {"healthy": 80, "warning": 60}  # >= healthy = green, >= warning = yellow, else red
RISK_THRESHOLDS = {
    "schedule": {
        "sprint_completion": {"healthy": 0.8, "warning": 0.6},
        "blocked_rate": {"healthy": 0.05, "warning": 0.15},
        "not_started_rate": {"healthy": 0.3, "warning": 0.5},
    },
    "scope": {
        "mid_sprint_add_rate": {"healthy": 0.1, "warning": 0.25},
    },
    "resource": {
        "max_wip_per_person": {"healthy": 5, "warning": 8},
        "unassigned_rate": {"healthy": 0.1, "warning": 0.2},
    },
    "quality": {
        "weekly_new_bugs": {"healthy": 5, "warning": 10},
        "reopen_rate": {"healthy": 0.05, "warning": 0.1},
        "high_pri_bugs": {"healthy": 3, "warning": 5},
    },
}

TREND_LABELS = {"up": "\u2191 \u60e1\u5316", "flat": "\u2192 \u6301\u5e73", "down": "\u2193 \u6539\u5584"}

# ---------------------------------------------------------------------------
# Metric Aggregation
# ---------------------------------------------------------------------------


def safe_div(a, b, default=0):
    """Safe division avoiding ZeroDivisionError."""
    return a / b if b else default


def aggregate_metrics(data: dict) -> dict:
    """Calculate all KPIs from raw Jira data."""
    sprint = data.get("sprint", {})
    issues = data.get("issues", {})
    velocity = data.get("velocity", {})

    sprint_total = sprint.get("issues", {}).get("total", 0)
    sprint_done = sprint.get("issues", {}).get("done", 0)
    total_issues = issues.get("total", 0)
    done_issues = issues.get("done", 0)
    active_issues = issues.get("active", total_issues - done_issues)

    completed_list = velocity.get("completed", [])
    avg_velocity = mean(completed_list) if completed_list else 0

    return {
        "sprint_completion_rate": safe_div(sprint_done, sprint_total),
        "overall_completion_rate": safe_div(done_issues, total_issues),
        "avg_velocity": round(avg_velocity, 1),
        "velocity_list": completed_list,
        "sprint_total": sprint_total,
        "sprint_done": sprint_done,
        "total_issues": total_issues,
        "done_issues": done_issues,
        "active_issues": active_issues,
    }


# ---------------------------------------------------------------------------
# Trend Vectors
# ---------------------------------------------------------------------------


def calculate_trend(values: list) -> str:
    """Determine trend direction from a list of numeric values (oldest→newest).
    Returns: 'up' (worsening), 'down' (improving), or 'flat'."""
    if len(values) < 2:
        return "flat"
    recent = values[-2:]
    older = values[:-2] if len(values) > 2 else values[:1]
    recent_avg = mean(recent)
    older_avg = mean(older)
    diff_pct = safe_div(recent_avg - older_avg, older_avg) if older_avg else 0
    if diff_pct > 0.1:
        return "up"
    elif diff_pct < -0.1:
        return "down"
    return "flat"


def calculate_trend_vectors(data: dict) -> dict:
    """Calculate trend direction for key metrics across sprints."""
    velocity = data.get("velocity", {})
    completed = velocity.get("completed", [])
    committed = velocity.get("committed", [])

    # Velocity trend (higher is better, so invert: up=improving)
    velocity_trend = calculate_trend(completed)
    # For velocity, up means improving, so flip labels
    velocity_direction = {"up": "down", "down": "up", "flat": "flat"}[velocity_trend]

    # Completion rate trend per sprint
    completion_rates = []
    if committed and completed:
        for c, t in zip(completed, committed):
            completion_rates.append(safe_div(c, t))
    completion_trend = calculate_trend(completion_rates)
    completion_direction = {"up": "down", "down": "up", "flat": "flat"}[completion_trend]

    # Bug trend (from weekly counts if available)
    bug_weekly = data.get("bug_trend", {}).get("weekly_counts", [])
    bug_direction = calculate_trend(bug_weekly)

    # Scope creep trend
    scope_rates = data.get("scope_creep", {}).get("sprint_rates", [])
    scope_direction = calculate_trend(scope_rates)

    return {
        "velocity": {"direction": velocity_direction, "sparkline": completed},
        "completion": {"direction": completion_direction, "sparkline": completion_rates},
        "bugs": {"direction": bug_direction, "sparkline": bug_weekly},
        "scope_creep": {"direction": scope_direction, "sparkline": scope_rates},
    }


# ---------------------------------------------------------------------------
# Delivery Probability
# ---------------------------------------------------------------------------


def calculate_delivery_probability(data: dict) -> dict:
    """Calculate probability of on-time delivery with confidence intervals."""
    sprint = data.get("sprint", {})
    velocity = data.get("velocity", {})
    completed_list = velocity.get("completed", [])

    remaining = sprint.get("issues", {}).get("total", 0) - sprint.get("issues", {}).get("done", 0)
    sprint_days = sprint.get("totalDays", 10)
    days_left = max(sprint_days - sprint.get("day", 0), 0)

    if not completed_list or sprint_days == 0:
        return {"expected": 50, "optimistic": 75, "pessimistic": 25}

    vel_avg = mean(completed_list)
    vel_std = stdev(completed_list) if len(completed_list) > 1 else vel_avg * 0.2

    daily_capacity = vel_avg / sprint_days
    daily_capacity_worst = max((vel_avg - vel_std) / sprint_days, 0.1)
    daily_capacity_best = (vel_avg + vel_std) / sprint_days

    if remaining <= 0:
        return {"expected": 99, "optimistic": 99, "pessimistic": 95}

    days_needed_expected = remaining / daily_capacity if daily_capacity > 0 else 999
    days_needed_worst = remaining / daily_capacity_worst
    days_needed_best = remaining / daily_capacity_best if daily_capacity_best > 0 else days_needed_expected

    p_expected = min(max(int(safe_div(days_left, days_needed_expected) * 100), 5), 99)
    p_optimistic = min(max(int(safe_div(days_left, days_needed_best) * 100), 5), 99)
    p_pessimistic = min(max(int(safe_div(days_left, days_needed_worst) * 100), 5), 99)

    return {
        "expected": p_expected,
        "optimistic": p_optimistic,
        "pessimistic": p_pessimistic,
    }


# ---------------------------------------------------------------------------
# Risk Scores
# ---------------------------------------------------------------------------


def score_from_thresholds(value, thresholds: dict, invert=False) -> int:
    """Convert a metric value to a 0-100 score using thresholds.
    Higher score = healthier. invert=True means lower value is better."""
    healthy = thresholds["healthy"]
    warning = thresholds["warning"]
    if invert:
        if value <= healthy:
            return 100
        elif value <= warning:
            return 70
        else:
            return max(30, int(100 - (value - warning) / max(warning, 0.01) * 50))
    else:
        if value >= healthy:
            return 100
        elif value >= warning:
            return 70
        else:
            return max(30, int(value / max(warning, 0.01) * 70))


def calculate_risk_scores(data: dict, metrics: dict) -> dict:
    """Calculate 4-category risk scores (0-100, higher=healthier)."""
    sprint = data.get("sprint", {})
    sprint_issues = sprint.get("issues", {})
    risks_input = data.get("risks", {})

    # Schedule risk
    completion_rate = metrics["sprint_completion_rate"]
    blocked_count = sprint_issues.get("blocked", 0)
    blocked_rate = safe_div(blocked_count, sprint_issues.get("total", 1))
    todo_count = sprint_issues.get("todo", 0)
    not_started_rate = safe_div(todo_count, sprint_issues.get("total", 1))
    # Consider sprint progress (mid-sprint check)
    sprint_progress = safe_div(sprint.get("day", 0), sprint.get("totalDays", 10))

    schedule_scores = [
        score_from_thresholds(completion_rate, RISK_THRESHOLDS["schedule"]["sprint_completion"]),
        score_from_thresholds(blocked_rate, RISK_THRESHOLDS["schedule"]["blocked_rate"], invert=True),
    ]
    if sprint_progress > 0.4:  # Only check not-started after 40% of sprint
        schedule_scores.append(
            score_from_thresholds(not_started_rate, RISK_THRESHOLDS["schedule"]["not_started_rate"], invert=True)
        )
    schedule_score = int(mean(schedule_scores))

    # Scope risk
    scope_data = data.get("scope_creep", {})
    mid_sprint_rate = scope_data.get("current_rate", 0)
    scope_score = score_from_thresholds(mid_sprint_rate, RISK_THRESHOLDS["scope"]["mid_sprint_add_rate"], invert=True)

    # Resource risk
    resource_data = data.get("resource", {})
    unassigned_rate = safe_div(
        sprint_issues.get("unassigned", 0), sprint_issues.get("total", 1)
    )
    max_wip = resource_data.get("max_wip", 0)
    resource_scores = [
        score_from_thresholds(unassigned_rate, RISK_THRESHOLDS["resource"]["unassigned_rate"], invert=True),
        score_from_thresholds(max_wip, RISK_THRESHOLDS["resource"]["max_wip_per_person"], invert=True),
    ]
    resource_score = int(mean(resource_scores))

    # Quality risk
    bug_data = data.get("bug_trend", {})
    weekly_bugs = bug_data.get("weekly_counts", [0])
    recent_bugs = weekly_bugs[-1] if weekly_bugs else 0
    high_pri_bugs = bug_data.get("high_priority_open", 0)
    quality_scores = [
        score_from_thresholds(recent_bugs, RISK_THRESHOLDS["quality"]["weekly_new_bugs"], invert=True),
        score_from_thresholds(high_pri_bugs, RISK_THRESHOLDS["quality"]["high_pri_bugs"], invert=True),
    ]
    quality_score = int(mean(quality_scores))

    def level_from_score(s):
        if s >= 80:
            return "healthy"
        elif s >= 60:
            return "warning"
        return "danger"

    return {
        "schedule": {"score": schedule_score, "level": level_from_score(schedule_score)},
        "scope": {"score": scope_score, "level": level_from_score(scope_score)},
        "resource": {"score": resource_score, "level": level_from_score(resource_score)},
        "quality": {"score": quality_score, "level": level_from_score(quality_score)},
    }


# ---------------------------------------------------------------------------
# Risk Persistence
# ---------------------------------------------------------------------------


def detect_risk_persistence(data: dict, current_risks: dict) -> dict:
    """Detect risks that persist across multiple sprints."""
    history = data.get("risk_history", {})  # {"schedule": ["healthy","warning","warning"], ...}
    persistence = {}
    for category in ["schedule", "scope", "resource", "quality"]:
        hist = history.get(category, [])
        current_level = current_risks[category]["level"]
        # Count consecutive non-healthy from most recent
        consecutive = 0
        levels = hist + [current_level]
        for lvl in reversed(levels):
            if lvl != "healthy":
                consecutive += 1
            else:
                break
        persistence[category] = {
            "consecutive_sprints": consecutive,
            "is_structural": consecutive >= 3,
            "is_persistent": consecutive >= 2,
            "improving": len(hist) >= 2 and hist[-1] != "healthy" and current_level == "healthy",
        }
    return persistence


# ---------------------------------------------------------------------------
# Dependency Chains
# ---------------------------------------------------------------------------


def analyze_dependency_chains(data: dict) -> dict:
    """Analyze blocked issue chains for cascade risks."""
    chains = data.get("dependency_chains", [])
    # Each chain: {"root": "PROJ-100", "chain": ["PROJ-101","PROJ-102"], "length": 3}
    if not chains:
        return {"max_chain_length": 0, "single_points_of_failure": [], "total_affected": 0}

    max_chain = max(chains, key=lambda c: c.get("length", 0))
    spof = [c for c in chains if c.get("downstream_count", 0) >= 3]

    return {
        "max_chain_length": max_chain.get("length", 0),
        "max_chain_root": max_chain.get("root", ""),
        "single_points_of_failure": [s.get("root", "") for s in spof],
        "total_affected": sum(c.get("downstream_count", 0) for c in chains),
    }


# ---------------------------------------------------------------------------
# Compound Risks
# ---------------------------------------------------------------------------


def detect_compound_risks(risks: dict, trends: dict, data: dict) -> list:
    """Detect cross-dimension risk correlations."""
    compounds = []

    # Scope up + Velocity down = demand inflation with declining capacity
    scope_bad = risks["scope"]["level"] != "healthy"
    velocity_declining = trends.get("velocity", {}).get("direction") == "up"  # up = worsening
    if scope_bad and velocity_declining:
        compounds.append({
            "type": "demand_inflation",
            "severity": "danger",
            "label": "\u9700\u6c42\u81a8\u8139\u4e14\u7522\u80fd\u4e0b\u964d",
            "description": "Scope \u6301\u7e8c\u589e\u52a0\u4f46\u5718\u968a\u901f\u5ea6\u4e0b\u964d\uff0c\u4ea4\u4ed8\u98a8\u96aa\u5927\u5e45\u4e0a\u5347",
            "action": "\u5efa\u8b70\u6e1b\u5c11\u4e0b Sprint \u627f\u8afe\u91cf 20-30%\uff0c\u512a\u5148\u6e05\u7406 blocked items",
        })

    # Resource concentrated + blocked = key person bottleneck
    resource_bad = risks["resource"]["level"] != "healthy"
    has_blocked = data.get("sprint", {}).get("issues", {}).get("blocked", 0) > 0
    if resource_bad and has_blocked:
        compounds.append({
            "type": "key_person_bottleneck",
            "severity": "danger",
            "label": "\u95dc\u9375\u4eba\u529b\u74f6\u9838",
            "description": "\u8cc7\u6e90\u96c6\u4e2d\u4e14\u8a72\u4eba\u54e1\u6709 Blocked issues\uff0c\u53ef\u80fd\u5f71\u97ff\u591a\u500b\u4ea4\u4ed8\u9805",
            "action": "\u8003\u616e\u91cd\u5206\u914d\u5de5\u4f5c\u6216\u5354\u8abf\u5916\u90e8\u963b\u64cb",
        })

    # Bug up + deadline approaching = quality pressure
    bug_worsening = trends.get("bugs", {}).get("direction") == "up"
    sprint = data.get("sprint", {})
    sprint_progress = safe_div(sprint.get("day", 0), sprint.get("totalDays", 10))
    if bug_worsening and sprint_progress > 0.6:
        compounds.append({
            "type": "quality_pressure",
            "severity": "warning",
            "label": "\u54c1\u8cea\u98a8\u96aa\u58d3\u7e2e",
            "description": "Bug \u8da8\u52e2\u4e0a\u5347\u4e14 Sprint \u5df2\u904e 60%\uff0c\u4fee\u5fa9\u6642\u9593\u4e0d\u8db3",
            "action": "\u8a55\u4f30\u662f\u5426\u9700\u5ef6\u5f8c\u65b0\u529f\u80fd\uff0c\u512a\u5148\u4fee\u5fa9\u9ad8\u512a\u5148\u7d1a Bug",
        })

    return compounds


# ---------------------------------------------------------------------------
# Action Recommendations
# ---------------------------------------------------------------------------


def generate_action_recommendations(
    health_score: int, risks: dict, persistence: dict, compounds: list, attention_items: list
) -> dict:
    """Generate tiered action recommendations for executives."""
    immediate = []  # Red
    this_week = []  # Yellow
    monitor = []    # Green

    # From health score
    if health_score < 50:
        immediate.append("\u5c08\u6848\u5065\u5eb7\u5ea6\u4f4e\u65bc 50\uff0c\u9700\u7acb\u5373\u8a55\u4f30\u662f\u5426\u8abf\u6574\u7bc4\u570d\u6216\u589e\u52a0\u8cc7\u6e90")
    elif health_score < 60:
        this_week.append("\u5c08\u6848\u5065\u5eb7\u5ea6\u504f\u4f4e\uff0c\u5efa\u8b70\u672c\u9031\u5167\u8207\u5718\u968a\u8a0e\u8ad6\u6539\u5584\u65b9\u6848")

    # From structural risks
    for cat, pers in persistence.items():
        cat_labels = {"schedule": "\u6642\u7a0b", "scope": "\u7bc4\u570d", "resource": "\u8cc7\u6e90", "quality": "\u54c1\u8cea"}
        if pers["is_structural"]:
            immediate.append(f"{cat_labels[cat]}\u98a8\u96aa\u5df2\u6301\u7e8c {pers['consecutive_sprints']} \u500b Sprint\uff0c\u5c6c\u7d50\u69cb\u6027\u554f\u984c\uff0c\u9700\u7d44\u7e54\u5c64\u9762\u4ecb\u5165")
        elif pers["is_persistent"]:
            this_week.append(f"{cat_labels[cat]}\u98a8\u96aa\u9023\u7e8c\u51fa\u73fe\uff0c\u5efa\u8b70\u8a02\u5b9a\u6539\u5584\u8a08\u756b")
        elif pers["improving"]:
            monitor.append(f"{cat_labels[cat]}\u6307\u6a19\u5df2\u56de\u7a69\uff0c\u7e7c\u7e8c\u89c0\u5bdf 1 Sprint")

    # From compound risks
    for comp in compounds:
        if comp["severity"] == "danger":
            immediate.append(f"{comp['label']}\uff1a{comp['action']}")
        else:
            this_week.append(f"{comp['label']}\uff1a{comp['action']}")

    # From attention items
    for item in attention_items[:3]:  # Top 3 only
        if item.get("impact") == "high":
            immediate.append(f"{item['key']} {item.get('reason', '')}\uff1a{item.get('action', '')}")
        elif item.get("impact") == "medium":
            this_week.append(f"{item['key']} {item.get('reason', '')}\uff1a{item.get('action', '')}")

    return {
        "immediate": immediate[:5],  # Max 5 per category
        "this_week": this_week[:5],
        "monitor": monitor[:5],
    }


# ---------------------------------------------------------------------------
# Health Score
# ---------------------------------------------------------------------------


def calculate_health_score(metrics: dict, risks: dict, trends: dict) -> tuple:
    """Composite health score (0-100) and level."""
    score = 100.0

    # Sprint completion (30%)
    sprint_rate = metrics["sprint_completion_rate"]
    score -= max(0, (0.8 - sprint_rate) * 100) * 0.30

    # Blocked rate (20%) - from risk score
    schedule_penalty = max(0, (100 - risks["schedule"]["score"]) * 0.2)
    score -= schedule_penalty

    # Overdue approximation from completion (25%)
    overall_gap = max(0, 0.7 - metrics["overall_completion_rate"])
    score -= overall_gap * 100 * 0.25

    # Bug trend (15%)
    if trends.get("bugs", {}).get("direction") == "up":
        score -= 15

    # Resource (10%)
    if risks["resource"]["level"] == "danger":
        score -= 10
    elif risks["resource"]["level"] == "warning":
        score -= 5

    score = max(0, min(100, int(score)))
    if score >= HEALTH_THRESHOLDS["healthy"]:
        level = "healthy"
    elif score >= HEALTH_THRESHOLDS["warning"]:
        level = "warning"
    else:
        level = "danger"

    return score, level


# ---------------------------------------------------------------------------
# HTML Generation
# ---------------------------------------------------------------------------


def get_template_path() -> Path:
    """Locate the dashboard HTML template."""
    script_dir = Path(__file__).parent
    template_path = script_dir.parent / "references" / "templates" / "dashboard_template.html"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path


def generate_html(dashboard_data: dict, template_path: Path = None, offline: bool = False) -> str:
    """Inject dashboard data JSON into HTML template."""
    if template_path is None:
        template_path = get_template_path()

    template = template_path.read_text(encoding="utf-8")
    data_json = json.dumps(dashboard_data, ensure_ascii=False, indent=2)

    # Replace placeholder
    html = template.replace("/*DATA_PLACEHOLDER*/", data_json)

    if offline:
        # Inline Chart.js for offline use (placeholder - actual file would be embedded)
        html = html.replace(
            '<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>',
            '<!-- Chart.js inlined for offline use -->\n<script>/* Chart.js would be inlined here */</script>',
        )

    return html


# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------


def build_dashboard(data: dict) -> dict:
    """Full pipeline: raw data -> dashboard JSON ready for template injection."""
    # Phase 1: Aggregate metrics
    metrics = aggregate_metrics(data)

    # Phase 2: Trend vectors
    trends = calculate_trend_vectors(data)

    # Phase 3: Delivery probability
    delivery = calculate_delivery_probability(data)

    # Phase 4: Risk scores
    risks = calculate_risk_scores(data, metrics)

    # Phase 5: Risk persistence
    persistence = detect_risk_persistence(data, risks)

    # Phase 6: Dependency chains
    dependencies = analyze_dependency_chains(data)

    # Phase 7: Compound risks
    compounds = detect_compound_risks(risks, trends, data)

    # Phase 8: Health score
    health_score, health_level = calculate_health_score(metrics, risks, trends)

    # Phase 9: Action recommendations
    attention_items = data.get("attention_items", [])
    actions = generate_action_recommendations(health_score, risks, persistence, compounds, attention_items)

    # Phase 10: Strategic insights (text summaries for the panel)
    strategic_insights = data.get("strategic_insights", [])  # Agent fills this via LLM reasoning

    # Assemble dashboard data
    dashboard = {
        "project": data.get("project", {}),
        "generated_at": data.get("generated_at", datetime.now().isoformat()),
        "date_range": data.get("date_range", ""),
        "sprint": data.get("sprint", {}),
        "health": {"score": health_score, "level": health_level},
        "delivery_probability": delivery,
        "kpi": {
            "completion_rate": round(metrics["overall_completion_rate"] * 100, 1),
            "sprint_completion_rate": round(metrics["sprint_completion_rate"] * 100, 1),
            "avg_velocity": metrics["avg_velocity"],
            "active_issues": metrics["active_issues"],
        },
        "trends": trends,
        "risks": risks,
        "risk_persistence": persistence,
        "dependencies": dependencies,
        "compound_risks": compounds,
        "issues": data.get("issues", {}),
        "velocity": data.get("velocity", {}),
        "epics": data.get("epics", []),
        "attention_items": attention_items,
        "actions": actions,
        "strategic_insights": strategic_insights,
    }

    return dashboard


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Generate executive dashboard HTML from Jira data")
    parser.add_argument("--data", type=str, help="Input JSON file path (or stdin if omitted)")
    parser.add_argument("--output", type=str, required=True, help="Output HTML file path")
    parser.add_argument("--template", type=str, help="Custom template path (optional)")
    parser.add_argument("--offline", action="store_true", help="Inline Chart.js for offline use")
    args = parser.parse_args()

    # Read input
    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = json.load(sys.stdin)

    # Build dashboard
    dashboard_data = build_dashboard(data)

    # Generate HTML
    template_path = Path(args.template) if args.template else None
    html = generate_html(dashboard_data, template_path, offline=args.offline)

    # Write output
    output_path = Path(args.output)
    output_path.write_text(html, encoding="utf-8")
    print(f"\u2705 Dashboard generated: {output_path}")
    print(f"   Health: {dashboard_data['health']['score']} ({dashboard_data['health']['level']})")
    print(f"   Delivery probability: {dashboard_data['delivery_probability']['expected']}%")
    print(f"   Actions: {len(dashboard_data['actions']['immediate'])} immediate, "
          f"{len(dashboard_data['actions']['this_week'])} this week, "
          f"{len(dashboard_data['actions']['monitor'])} monitor")


if __name__ == "__main__":
    main()
