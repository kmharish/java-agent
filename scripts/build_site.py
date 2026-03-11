#!/usr/bin/env python3
"""Build a GitHub Pages site from JOURNAL.md and LEARNINGS.md."""

import os
import re
import html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, "..")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")


def read_file(path):
    """Read a file, return empty string if missing."""
    try:
        with open(os.path.join(PROJECT_ROOT, path)) as f:
            return f.read()
    except FileNotFoundError:
        return ""


def md_to_html(md_text):
    """Simple markdown to HTML conversion (no dependencies)."""
    lines = md_text.split("\n")
    html_lines = []
    in_code = False
    in_list = False

    for line in lines:
        # Code blocks
        if line.strip().startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                lang = line.strip()[3:].strip()
                cls = f' class="language-{lang}"' if lang else ""
                html_lines.append(f"<pre><code{cls}>")
                in_code = True
            continue

        if in_code:
            html_lines.append(html.escape(line))
            continue

        # Close list if needed
        if in_list and not line.strip().startswith("- ") and not line.strip().startswith("* "):
            html_lines.append("</ul>")
            in_list = False

        stripped = line.strip()

        # Headings
        if stripped.startswith("## "):
            text = html.escape(stripped[3:])
            # Create anchor from heading text
            anchor = re.sub(r"[^a-z0-9-]", "", stripped[3:].lower().replace(" ", "-").replace("—", "-"))
            html_lines.append(f'<h2 id="{anchor}">{text}</h2>')
            continue
        if stripped.startswith("# "):
            text = html.escape(stripped[2:])
            html_lines.append(f"<h1>{text}</h1>")
            continue

        # List items
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            text = inline_md(stripped[2:])
            html_lines.append(f"<li>{text}</li>")
            continue

        # Empty lines
        if not stripped:
            html_lines.append("")
            continue

        # Regular paragraphs
        html_lines.append(f"<p>{inline_md(stripped)}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_code:
        html_lines.append("</code></pre>")

    return "\n".join(html_lines)


def inline_md(text):
    """Convert inline markdown: **bold**, *italic*, `code`, [link](url)."""
    text = html.escape(text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    # Code
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Links
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def count_entries(journal_text):
    """Count journal entries (lines starting with ## Day)."""
    return len(re.findall(r"^## Day", journal_text, re.MULTILINE))


def build_site():
    """Generate the docs/ directory for GitHub Pages."""
    os.makedirs(DOCS_DIR, exist_ok=True)

    journal = read_file("JOURNAL.md")
    learnings = read_file("LEARNINGS.md")
    day_count = read_file("DAY_COUNT").strip() or "0"

    journal_html = md_to_html(journal)
    learnings_html = md_to_html(learnings)
    entry_count = count_entries(journal)

    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>java-agent — Evolution Journal</title>
    <style>
        :root {{
            --bg: #0d1117;
            --fg: #c9d1d9;
            --accent: #58a6ff;
            --accent2: #f0883e;
            --muted: #8b949e;
            --surface: #161b22;
            --border: #30363d;
            --green: #3fb950;
            --red: #f85149;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--fg);
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}
        header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid var(--border);
        }}
        header h1 {{
            font-size: 2rem;
            color: var(--accent);
            margin-bottom: 0.5rem;
        }}
        header h1 .icon {{ font-size: 1.5rem; }}
        header .subtitle {{
            color: var(--muted);
            font-size: 1rem;
        }}
        .stats {{
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-top: 1rem;
        }}
        .stat {{
            text-align: center;
        }}
        .stat .number {{
            font-size: 1.5rem;
            font-weight: bold;
            color: var(--accent2);
        }}
        .stat .label {{
            font-size: 0.8rem;
            color: var(--muted);
            text-transform: uppercase;
        }}
        nav {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-bottom: 2rem;
        }}
        nav a {{
            color: var(--accent);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.9rem;
        }}
        nav a:hover, nav a.active {{
            background: var(--surface);
            border-color: var(--accent);
        }}
        .section {{ display: none; }}
        .section.active {{ display: block; }}
        h1 {{ font-size: 1.5rem; color: var(--accent); margin-bottom: 1rem; }}
        h2 {{
            font-size: 1.2rem;
            color: var(--fg);
            margin-top: 2rem;
            margin-bottom: 0.5rem;
            padding-bottom: 0.3rem;
            border-bottom: 1px solid var(--border);
        }}
        p {{ margin: 0.5rem 0; }}
        ul {{ margin: 0.5rem 0 0.5rem 1.5rem; }}
        li {{ margin: 0.3rem 0; }}
        strong {{ color: var(--accent2); }}
        code {{
            background: var(--surface);
            padding: 0.15rem 0.4rem;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        pre {{
            background: var(--surface);
            padding: 1rem;
            border-radius: 6px;
            overflow-x: auto;
            margin: 0.5rem 0;
            border: 1px solid var(--border);
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
        a {{ color: var(--accent); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        footer {{
            margin-top: 3rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            text-align: center;
            color: var(--muted);
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <header>
        <h1><span class="icon">☕</span> java-agent</h1>
        <p class="subtitle">A self-evolving AI agent for Java/Spring Boot development</p>
        <div class="stats">
            <div class="stat">
                <div class="number">{day_count}</div>
                <div class="label">Days Alive</div>
            </div>
            <div class="stat">
                <div class="number">{entry_count}</div>
                <div class="label">Journal Entries</div>
            </div>
        </div>
    </header>

    <nav>
        <a href="#" class="active" onclick="showSection('journal', this)">Journal</a>
        <a href="#" onclick="showSection('learnings', this)">Learnings</a>
        <a href="https://github.com/kmharish/java-agent" target="_blank">GitHub</a>
    </nav>

    <div id="journal" class="section active">
        {journal_html}
    </div>

    <div id="learnings" class="section">
        {learnings_html}
    </div>

    <footer>
        <p>Powered by Claude Code. Evolving every 8 hours.</p>
        <p><a href="https://github.com/kmharish/java-agent">View source on GitHub</a></p>
    </footer>

    <script>
        function showSection(id, el) {{
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            el.classList.add('active');
        }}
    </script>
</body>
</html>"""

    with open(os.path.join(DOCS_DIR, "index.html"), "w") as f:
        f.write(page)

    print(f"  Site built: docs/index.html (Day {day_count}, {entry_count} entries)")


if __name__ == "__main__":
    build_site()
