#!/usr/bin/env python3
"""Format GitHub issues JSON into a readable markdown file for the agent."""

import json
import sys


def compute_net_score(reaction_groups):
    """Compute (upvotes, downvotes, net_score) from GitHub reaction groups."""
    if not reaction_groups:
        return (0, 0, 0)
    up = 0
    down = 0
    for group in reaction_groups:
        content = group.get("content", "")
        count = group.get("users", {}).get("totalCount", 0)
        if content in ("THUMBS_UP", "HEART", "HOORAY", "ROCKET"):
            up += count
        elif content in ("THUMBS_DOWN", "CONFUSED"):
            down += count
    return (up, down, up - down)


def format_issues(issues_file, sponsors_file, day):
    """Format issues into markdown."""
    with open(issues_file) as f:
        issues = json.load(f)

    sponsors = []
    try:
        with open(sponsors_file) as f:
            sponsors = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    if not issues:
        print("No community issues today.")
        return

    # Sort by net score descending
    issues.sort(key=lambda i: compute_net_score(i.get("reactionGroups"))[2], reverse=True)

    print(f"# Issues for Day {day}\n")
    for issue in issues:
        num = issue.get("number", "?")
        title = issue.get("title", "Untitled")
        body = issue.get("body", "")
        author = issue.get("author", {}).get("login", "unknown")
        up, down, net = compute_net_score(issue.get("reactionGroups"))

        # Truncate body to prevent prompt injection via extremely long issues
        if len(body) > 2000:
            body = body[:2000] + "\n...(truncated)"

        # Strip HTML comments (potential injection vector)
        import re
        body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)

        is_sponsor = author in sponsors
        sponsor_badge = " 💖 **Sponsor**" if is_sponsor else ""

        print(f"### Issue #{num}: {title}")
        print(f"**Author:** @{author}{sponsor_badge}")
        print(f"**Score:** 👍 {up} / 👎 {down} (net: {net})")
        print()
        print(body)
        print()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: format_issues.py <issues.json> <sponsors.json> <day>", file=sys.stderr)
        sys.exit(1)

    format_issues(sys.argv[1], sys.argv[2], sys.argv[3])
