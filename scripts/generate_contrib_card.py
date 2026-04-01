#!/usr/bin/env python3
"""Generate an SVG card showcasing open source contributions."""

import os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "contributions.svg")

W = 1200
H = 520
R = 16

# Colors
BG = "#0D1117"
BG2 = "#161B22"
BG3 = "#1C2333"
BORDER = "#30363D"
ACCENT = "#58A6FF"
GREEN = "#3FB950"
PURPLE = "#D2A8FF"
ORANGE = "#F78166"
RED = "#FF7B72"
YELLOW = "#E3B341"
TEXT = "#E6EDF3"
DIM = "#8B949E"
MID = "#C9D1D9"

# Contribution data
CONTRIBUTIONS = [
    {
        "repo": "OpenClaw",
        "org": "openclaw",
        "stars": "260K",
        "color": ACCENT,
        "prs": [
            ("test: add unit tests for copilot-proxy, qwen-portal-auth, minimax extensions", "#27783", "open"),
            ("chore: migrate eslint-disable comments to oxlint-disable", "#27777", "open"),
        ],
        "desc": "AI gateway and agent platform",
        "logo_letter": "O",
    },
    {
        "repo": "LangChain",
        "org": "langchain-ai",
        "stars": "128K",
        "color": GREEN,
        "prs": [
            ("fix: RunnableRetry.batch/abatch corrupted outputs on retry", "#35556", "open"),
            ("fix: Streaming tool call empty args from SSE fragmentation", "#35528", "open"),
            ("fix: PydanticOutputParser for HuggingFace structured output", "#35484", "open"),
        ],
        "desc": "LLM application framework",
        "logo_letter": "L",
    },
    {
        "repo": "GraphRAG",
        "org": "microsoft",
        "stars": "31K",
        "color": PURPLE,
        "prs": [
            ("fix: Incorrect entity deduplication with same title different types", "#2262", "open"),
        ],
        "desc": "Graph-based RAG by Microsoft",
        "logo_letter": "G",
    },
    {
        "repo": "LangGraph",
        "org": "langchain-ai",
        "stars": "26K",
        "color": ORANGE,
        "prs": [
            ("fix: ToolNode ainvoke freezes on sse_read_timeout", "#7013", "open"),
        ],
        "desc": "Stateful multi-agent framework",
        "logo_letter": "G",
    },
    {
        "repo": "DeepEval",
        "org": "confident-ai",
        "stars": "14K",
        "color": YELLOW,
        "prs": [
            ("fix: Support popular benchmarks", "#2527", "open"),
        ],
        "desc": "LLM evaluation framework",
        "logo_letter": "D",
    },
    {
        "repo": "Cognee",
        "org": "topoteretes",
        "stars": "13K",
        "color": RED,
        "prs": [
            ("fix: Add usage frequency tracking for Kuzu adapter", "#2263", "open"),
        ],
        "desc": "Knowledge graph memory engine",
        "logo_letter": "C",
    },
]


def format_stars(s):
    return f"{s}"


def render_repo_row(item, x, y, idx):
    """Render a single repo contribution row."""
    color = item["color"]
    lines = []

    # Row background
    row_h = 68
    if idx % 2 == 0:
        lines.append(f'  <rect x="0" y="{y - 8}" width="{W}" height="{row_h}" fill="{BG2}" opacity="0.3"/>')

    # Logo circle
    lines.append(f'  <circle cx="{x + 22}" cy="{y + 20}" r="18" fill="{color}" opacity="0.12" stroke="{color}" stroke-width="1" stroke-opacity="0.3"/>')
    lines.append(
        f'  <text x="{x + 22}" y="{y + 26}" text-anchor="middle" '
        f'font-family="\'Segoe UI\',sans-serif" font-size="16" font-weight="700" fill="{color}">'
        f'{item["logo_letter"]}</text>'
    )

    # Repo name + org
    lines.append(
        f'  <text x="{x + 52}" y="{y + 14}" '
        f'font-family="\'Segoe UI\',sans-serif" font-size="15" font-weight="700" fill="{TEXT}">'
        f'{item["repo"]}</text>'
    )
    lines.append(
        f'  <text x="{x + 52}" y="{y + 30}" '
        f'font-family="\'Segoe UI\',sans-serif" font-size="10" fill="{DIM}">'
        f'{item["org"]} — {item["desc"]}</text>'
    )

    # Stars badge
    stars_x = x + 250
    lines.append(f'  <rect x="{stars_x}" y="{y + 2}" width="52" height="18" rx="9" fill="{YELLOW}" opacity="0.1" stroke="{YELLOW}" stroke-width="0.5" stroke-opacity="0.3"/>')
    # Star icon (simple)
    sx = stars_x + 10
    sy = y + 11
    lines.append(f'  <polygon points="{sx},{sy - 4} {sx + 1.5},{sy - 1} {sx + 4},{sy - 1} {sx + 2},{sy + 1} {sx + 3},{sy + 4} {sx},{sy + 2} {sx - 3},{sy + 4} {sx - 2},{sy + 1} {sx - 4},{sy - 1} {sx - 1.5},{sy - 1}" fill="{YELLOW}" opacity="0.8"/>')
    lines.append(
        f'  <text x="{stars_x + 35}" y="{y + 15}" text-anchor="middle" '
        f'font-family="\'Segoe UI\',sans-serif" font-size="9" font-weight="600" fill="{YELLOW}">'
        f'{item["stars"]}</text>'
    )

    # PR list
    pr_x = x + 320
    for pi, (title, num, state) in enumerate(item["prs"]):
        py = y + 6 + pi * 18

        # PR icon (merge/open)
        icon_color = GREEN if state == "merged" else ACCENT
        # Simple PR icon - circle with line
        lines.append(f'  <circle cx="{pr_x + 5}" cy="{py + 5}" r="4" fill="none" stroke="{icon_color}" stroke-width="1.2"/>')
        lines.append(f'  <circle cx="{pr_x + 5}" cy="{py + 5}" r="1.5" fill="{icon_color}"/>')

        # Truncate title
        display_title = title if len(title) <= 65 else title[:62] + "..."

        lines.append(
            f'  <text x="{pr_x + 14}" y="{py + 9}" '
            f'font-family="\'Segoe UI\',sans-serif" font-size="10" fill="{MID}">'
            f'{display_title}</text>'
        )

        # PR number
        num_x = pr_x + 14 + len(display_title) * 5.5 + 8
        if num_x > W - 60:
            num_x = W - 55
        lines.append(
            f'  <text x="{W - 35}" y="{py + 9}" text-anchor="end" '
            f'font-family="\'Segoe UI\',sans-serif" font-size="9" font-weight="600" fill="{icon_color}">'
            f'{num}</text>'
        )

    return "\n".join(lines)


def generate():
    # Header area
    header = f"""  <!-- Background -->
  <rect width="{W}" height="{H}" rx="{R}" fill="{BG}"/>

  <!-- Top accent line -->
  <defs>
    <linearGradient id="topLine" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{ACCENT}" stop-opacity="0"/>
      <stop offset="20%" stop-color="{ACCENT}" stop-opacity="0.5"/>
      <stop offset="50%" stop-color="{PURPLE}" stop-opacity="0.6"/>
      <stop offset="80%" stop-color="{GREEN}" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="{GREEN}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="{R}"/></clipPath>
  </defs>

  <g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect x="0" y="0" width="{W}" height="2" fill="url(#topLine)"/>

  <!-- Title row -->
  <text x="35" y="42" font-family="'Segoe UI',sans-serif" font-size="20" font-weight="700" fill="{TEXT}">Open Source Contributions</text>
  <text x="35" y="60" font-family="'Segoe UI',sans-serif" font-size="11" fill="{DIM}">Bug fixes, features, and tests contributed to major AI/ML projects</text>

  <!-- Summary badges -->
  <g transform="translate({W - 380}, 22)">
    <rect x="0" y="0" width="80" height="28" rx="6" fill="{ACCENT}" opacity="0.1" stroke="{ACCENT}" stroke-width="0.5" stroke-opacity="0.3"/>
    <text x="40" y="14" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="13" font-weight="700" fill="{ACCENT}">11</text>
    <text x="40" y="25" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="7" fill="{DIM}">PULL REQUESTS</text>

    <rect x="95" y="0" width="80" height="28" rx="6" fill="{GREEN}" opacity="0.1" stroke="{GREEN}" stroke-width="0.5" stroke-opacity="0.3"/>
    <text x="135" y="14" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="13" font-weight="700" fill="{GREEN}">6</text>
    <text x="135" y="25" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="7" fill="{DIM}">REPOSITORIES</text>

    <rect x="190" y="0" width="80" height="28" rx="6" fill="{YELLOW}" opacity="0.1" stroke="{YELLOW}" stroke-width="0.5" stroke-opacity="0.3"/>
    <text x="230" y="14" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="13" font-weight="700" fill="{YELLOW}">470K+</text>
    <text x="230" y="25" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="7" fill="{DIM}">COMBINED STARS</text>

    <rect x="285" y="0" width="80" height="28" rx="6" fill="{PURPLE}" opacity="0.1" stroke="{PURPLE}" stroke-width="0.5" stroke-opacity="0.3"/>
    <text x="325" y="14" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="13" font-weight="700" fill="{PURPLE}">AI/ML</text>
    <text x="325" y="25" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="7" fill="{DIM}">FOCUS AREA</text>
  </g>

  <!-- Column headers -->
  <line x1="25" y1="72" x2="{W - 25}" y2="72" stroke="{BORDER}" stroke-width="1"/>
  <text x="35" y="88" font-family="'Segoe UI',sans-serif" font-size="9" font-weight="600" fill="{DIM}" letter-spacing="1">PROJECT</text>
  <text x="285" y="88" font-family="'Segoe UI',sans-serif" font-size="9" font-weight="600" fill="{DIM}" letter-spacing="1">STARS</text>
  <text x="355" y="88" font-family="'Segoe UI',sans-serif" font-size="9" font-weight="600" fill="{DIM}" letter-spacing="1">CONTRIBUTIONS</text>
  <line x1="25" y1="94" x2="{W - 25}" y2="94" stroke="{BORDER}" stroke-width="0.5"/>"""

    # Render each repo
    rows = []
    y = 108
    for idx, item in enumerate(CONTRIBUTIONS):
        rows.append(render_repo_row(item, 25, y, idx))
        row_h = max(68, len(item["prs"]) * 18 + 32)
        y += row_h

    # Footer area
    footer = f"""
  <!-- Bottom accent -->
  <line x1="25" y1="{H - 40}" x2="{W - 25}" y2="{H - 40}" stroke="{BORDER}" stroke-width="0.5"/>
  <text x="{W / 2}" y="{H - 18}" text-anchor="middle" font-family="'Segoe UI',sans-serif" font-size="10" fill="{DIM}">
    Contributing to the AI/ML open source ecosystem — LangChain, Microsoft GraphRAG, OpenClaw, and more
  </text>
  </g>

  <!-- Border -->
  <rect width="{W}" height="{H}" rx="{R}" fill="none" stroke="{BORDER}" stroke-width="1"/>"""

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
{header}

{chr(10).join(rows)}

{footer}
</svg>"""

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write(svg)
    print(f"Generated {OUT}")


if __name__ == "__main__":
    generate()
