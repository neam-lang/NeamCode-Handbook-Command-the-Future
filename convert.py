#!/usr/bin/env python3
"""Convert NeamCode Handbook Markdown chapters to HTML using the Programming Neam template."""

import re
import os
import json
import html

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD_CHAPTERS = os.path.join(REPO, "chapters")
MD_APPENDICES = os.path.join(REPO, "appendices")
HTML_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_CHAPTERS = os.path.join(HTML_DIR, "chapters")
HTML_APPENDICES = os.path.join(HTML_DIR, "appendices")

# Chapter metadata: (filename_without_ext, title, part)
CHAPTERS = [
    ("00-preface", "Preface", "Getting Started"),
    ("01-meet-neamcode", "Meet NeamCode", "Getting Started"),
    ("02-install-first-conversation", "Install & First Conversation", "Getting Started"),
    ("03-art-of-prompting", "The Art of Prompting", "Getting Started"),
    ("04-working-with-files", "Working with Files", "Core Skills"),
    ("05-finding-things", "Finding Things in Code", "Core Skills"),
    ("06-commands-and-git", "Running Commands & Git", "Core Skills"),
    ("07-web-research", "Researching from the Terminal", "Core Skills"),
    ("08-slash-commands", "Slash Commands", "Workflow & Configuration"),
    ("09-modes", "Modes", "Workflow & Configuration"),
    ("10-sessions-context", "Sessions & Context", "Workflow & Configuration"),
    ("11-auto-memory", "Auto Memory", "Workflow & Configuration"),
    ("12-choosing-providers", "Choosing Your AI Provider", "Providers & Cost"),
    ("13-offline-mode", "Offline Mode", "Providers & Cost"),
    ("14-zero-cost-setup", "The $0 AI Setup", "Providers & Cost"),
    ("15-budget-cost", "Budget & Cost Tracking", "Providers & Cost"),
    ("16-agents", "Agents & Delegation", "Advanced Features"),
    ("17-mcp-servers", "MCP Servers", "Advanced Features"),
    ("18-neam-language", "Neam Language Integration", "Advanced Features"),
    ("19-for-students", "For Students", "Audience Guides"),
    ("20-for-researchers", "For Researchers", "Audience Guides"),
    ("21-for-professionals", "For Professionals", "Audience Guides"),
    ("22-walkthrough-build-project", "Walkthrough: Build a Project", "Walkthroughs"),
    ("23-walkthrough-fix-bug", "Walkthrough: Fix a Real Bug", "Walkthroughs"),
    ("24-making-it-yours", "Making NeamCode Yours", "Walkthroughs"),
    ("25-road-ahead", "The Road Ahead", "Closing"),
]

APPENDICES = [
    ("A-slash-commands", "All Slash Commands"),
    ("B-skills-reference", "All Skills Reference"),
    ("C-configuration", "Configuration Reference"),
    ("D-troubleshooting", "Troubleshooting & FAQ"),
    ("E-glossary", "Glossary"),
]

PARTS = [
    ("Getting Started", "#BE0027"),
    ("Core Skills", "#0060B6"),
    ("Workflow & Configuration", "#1a7f37"),
    ("Providers & Cost", "#8250df"),
    ("Advanced Features", "#9a6700"),
    ("Audience Guides", "#cf222e"),
    ("Walkthroughs", "#3730a3"),
    ("Closing", "#0d6efd"),
]

PART_EMOJIS = {
    "Getting Started": "\U0001F680",
    "Core Skills": "\U0001F527",
    "Workflow & Configuration": "\u2699\ufe0f",
    "Providers & Cost": "\U0001F4B0",
    "Advanced Features": "\u2728",
    "Audience Guides": "\U0001F465",
    "Walkthroughs": "\U0001F6A7",
    "Closing": "\U0001F3C1",
    "Appendices": "\U0001F4DA",
}

CHAPTER_EMOJIS = {
    "00-preface": "\U0001F4D6",
    "01-meet-neamcode": "\U0001F44B",
    "02-install-first-conversation": "\U0001F4E5",
    "03-art-of-prompting": "\U0001F3A8",
    "04-working-with-files": "\U0001F4C1",
    "05-finding-things": "\U0001F50D",
    "06-commands-and-git": "\U0001F4BB",
    "07-web-research": "\U0001F310",
    "08-slash-commands": "\u2328\ufe0f",
    "09-modes": "\U0001F3AE",
    "10-sessions-context": "\U0001F9E0",
    "11-auto-memory": "\U0001F4BE",
    "12-choosing-providers": "\U0001F500",
    "13-offline-mode": "\U0001F4F4",
    "14-zero-cost-setup": "\U0001F4B8",
    "15-budget-cost": "\U0001F4CA",
    "16-agents": "\U0001F916",
    "17-mcp-servers": "\U0001F517",
    "18-neam-language": "\U0001F4DD",
    "19-for-students": "\U0001F393",
    "20-for-researchers": "\U0001F52C",
    "21-for-professionals": "\U0001F454",
    "22-walkthrough-build-project": "\U0001F3D7\ufe0f",
    "23-walkthrough-fix-bug": "\U0001F41B",
    "24-making-it-yours": "\U0001F3A8",
    "25-road-ahead": "\U0001F6E4\ufe0f",
}

APPENDIX_EMOJIS = {
    "A-slash-commands": "\u2328\ufe0f",
    "B-skills-reference": "\U0001F4DA",
    "C-configuration": "\u2699\ufe0f",
    "D-troubleshooting": "\U0001F6E0\ufe0f",
    "E-glossary": "\U0001F4D6",
}

def make_id(text):
    """Convert heading text to a URL-safe id."""
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'\s+', '-', text.strip())
    return text

def md_to_html_content(md_text):
    """Convert markdown to HTML content (simplified but comprehensive)."""
    lines = md_text.split('\n')
    html_lines = []
    in_code_block = False
    code_lang = ''
    code_lines = []
    in_table = False
    table_lines = []
    in_list = False
    list_type = None
    list_items = []

    def flush_list():
        nonlocal in_list, list_type, list_items
        if not in_list:
            return
        tag = 'ol' if list_type == 'ol' else 'ul'
        html_lines.append(f'<{tag}>')
        for item in list_items:
            html_lines.append(f'<li>{inline_md(item)}</li>')
        html_lines.append(f'</{tag}>')
        in_list = False
        list_items = []

    def flush_table():
        nonlocal in_table, table_lines
        if not in_table:
            return
        html_lines.append('<div class="table-wrap"><table>')
        for i, row in enumerate(table_lines):
            cells = [c.strip() for c in row.strip('|').split('|')]
            if i == 0:
                html_lines.append('<thead><tr>')
                for cell in cells:
                    html_lines.append(f'<th>{inline_md(cell)}</th>')
                html_lines.append('</tr></thead><tbody>')
            elif i == 1:
                continue  # separator row
            else:
                html_lines.append('<tr>')
                for cell in cells:
                    html_lines.append(f'<td>{inline_md(cell)}</td>')
                html_lines.append('</tr>')
        html_lines.append('</tbody></table></div>')
        in_table = False
        table_lines = []

    def inline_md(text):
        """Convert inline markdown."""
        # Escape HTML entities first (but not our generated HTML)
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Restore HTML entities we want
        text = text.replace('&amp;mdash;', '&mdash;')
        text = text.replace('&amp;rarr;', '&rarr;')
        text = text.replace('&amp;larr;', '&larr;')
        # Bold + italic
        text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*([^*]+?)\*', r'<em>\1</em>', text)
        # Inline code
        text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)
        # Links
        text = re.sub(r'\[([^\]]+?)\]\(([^)]+?)\)', r'<a href="\2">\1</a>', text)
        # Emoji shortcodes to unicode (common ones used in the book)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                flush_list()
                flush_table()
                in_code_block = True
                code_lang = line.strip()[3:].strip()
                code_lines = []
            else:
                lang_display = code_lang or 'text'
                html_lines.append(f'<div class="code-header"><span class="code-lang">{html.escape(lang_display)}</span><button class="copy-btn">Copy</button></div>')
                escaped_code = html.escape('\n'.join(code_lines))
                html_lines.append(f'<pre><code class="language-{html.escape(code_lang)}">{escaped_code}</code></pre>')
                in_code_block = False
                code_lang = ''
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table rows
        if line.strip().startswith('|'):
            flush_list()
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
            i += 1
            continue
        elif in_table:
            flush_table()

        # Headings
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if heading_match:
            flush_list()
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            hid = make_id(text)
            html_lines.append(f'<h{level} id="{hid}">{inline_md(text)} <a href="#{hid}" class="heading-anchor">#</a></h{level}>')
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^---+\s*$', line):
            flush_list()
            html_lines.append('<hr />')
            i += 1
            continue

        # Blockquote
        if line.strip().startswith('>'):
            flush_list()
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('>'):
                quote_lines.append(re.sub(r'^>\s?', '', lines[i]))
                i += 1
            content = '<br>'.join(inline_md(l) for l in quote_lines)
            # Check for callout types
            if any(kw in content for kw in ['Note:', 'note:']):
                html_lines.append(f'<div class="callout callout-note"><div class="callout-title"><span class="callout-icon">&#128221;</span> Note</div><p>{content}</p></div>')
            elif any(kw in content for kw in ['Tip:', 'tip:', 'Tip']):
                html_lines.append(f'<div class="callout callout-tip"><div class="callout-title"><span class="callout-icon">&#128161;</span> Tip</div><p>{content}</p></div>')
            elif any(kw in content for kw in ['Warning:', 'warning:']):
                html_lines.append(f'<div class="callout callout-warning"><div class="callout-title"><span class="callout-icon">&#9888;&#65039;</span> Warning</div><p>{content}</p></div>')
            else:
                html_lines.append(f'<blockquote><p>{content}</p></blockquote>')
            continue

        # Callout paragraphs (emoji-prefixed)
        stripped = line.strip()
        if stripped.startswith(('📝 **Note', '💡 **Tip', '⚠️ **Warning')):
            flush_list()
            # Collect multi-line callout
            callout_lines = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#', '---', '```', '|', '📝', '💡', '⚠️', '🎯')):
                callout_lines.append(lines[i].strip())
                i += 1
            content = inline_md(' '.join(callout_lines))
            if '📝' in callout_lines[0] or 'Note' in callout_lines[0]:
                html_lines.append(f'<div class="callout callout-note"><div class="callout-title"><span class="callout-icon">&#128221;</span> Note</div><p>{content}</p></div>')
            elif '💡' in callout_lines[0] or 'Tip' in callout_lines[0]:
                html_lines.append(f'<div class="callout callout-tip"><div class="callout-title"><span class="callout-icon">&#128161;</span> Tip</div><p>{content}</p></div>')
            elif '⚠️' in callout_lines[0] or 'Warning' in callout_lines[0]:
                html_lines.append(f'<div class="callout callout-warning"><div class="callout-title"><span class="callout-icon">&#9888;&#65039;</span> Warning</div><p>{content}</p></div>')
            continue

        # Exercise paragraphs
        if stripped.startswith('🎯'):
            flush_list()
            content = inline_md(stripped)
            html_lines.append(f'<div class="callout callout-try-it-yourself"><p>{content}</p></div>')
            i += 1
            continue

        # Unordered list
        list_match = re.match(r'^(\s*)[-*]\s+(.+)$', line)
        if list_match:
            if not in_list or list_type != 'ul':
                flush_list()
                in_list = True
                list_type = 'ul'
                list_items = []
            list_items.append(list_match.group(2))
            i += 1
            continue

        # Ordered list
        ol_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
        if ol_match:
            if not in_list or list_type != 'ol':
                flush_list()
                in_list = True
                list_type = 'ol'
                list_items = []
            list_items.append(ol_match.group(2))
            i += 1
            continue

        # End of list
        if in_list and stripped == '':
            flush_list()

        # Empty line
        if stripped == '':
            i += 1
            continue

        # Skip navigation footer lines (we generate our own)
        if re.match(r'^\[?(Previous|Next|←|→)', stripped) or re.match(r'^\|.*←.*\|.*→.*\|', stripped):
            i += 1
            continue

        # Regular paragraph
        flush_list()
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            next_line = lines[i].strip()
            if (next_line == '' or next_line.startswith(('#', '```', '|', '---', '>', '- ', '* ', '📝', '💡', '⚠️', '🎯'))
                or re.match(r'^\d+\.', next_line)
                or re.match(r'^\[?(Previous|Next|←)', next_line)):
                break
            para_lines.append(next_line)
            i += 1
        html_lines.append(f'<p>{inline_md(" ".join(para_lines))}</p>')

    flush_list()
    flush_table()

    return '\n'.join(html_lines)

def build_sidebar(active_file, is_appendix=False):
    """Build sidebar HTML."""
    parts_dict = {}
    for fname, title, part in CHAPTERS:
        parts_dict.setdefault(part, []).append((fname, title))

    sidebar = []
    for part_name, part_color in PARTS:
        if part_name not in parts_dict:
            continue
        sidebar.append(f'<div class="sidebar-part">')
        sidebar.append(f'  <div class="sidebar-part-title">{part_name}</div>')
        sidebar.append(f'  <div class="sidebar-chapters">')
        for fname, title in parts_dict[part_name]:
            active = ' active' if fname == active_file else ''
            ch_prefix = '../chapters/' if is_appendix else ''
            sidebar.append(f'    <a href="{ch_prefix}{fname}.html" class="sidebar-link{active}" title="{title}">{title}</a>')
        sidebar.append(f'  </div>')
        sidebar.append(f'</div>')

    # Appendices
    sidebar.append(f'<div class="sidebar-part">')
    sidebar.append(f'  <div class="sidebar-part-title">Appendices</div>')
    sidebar.append(f'  <div class="sidebar-chapters">')
    for fname, title in APPENDICES:
        active = ' active' if fname == active_file else ''
        prefix = '../appendices/' if not is_appendix else ''
        if is_appendix:
            prefix = ''
        else:
            prefix = '../appendices/'
        sidebar.append(f'    <a href="{prefix}{fname}.html" class="sidebar-link{active}" title="{title}">{title}</a>')
    sidebar.append(f'  </div>')
    sidebar.append(f'</div>')

    return '\n'.join(sidebar)

def get_nav(idx, items, is_appendix=False):
    """Get prev/next navigation."""
    nav = '<nav class="chapter-nav">'
    if idx > 0:
        prev_fname, prev_title = items[idx-1][0], items[idx-1][1]
        nav += f'<a href="{prev_fname}.html" class="nav-prev"><span class="nav-label">\U0001F448 Previous</span><span class="nav-title">{prev_title}</span></a>'
    if idx < len(items) - 1:
        next_fname, next_title = items[idx+1][0], items[idx+1][1]
        nav += f'<a href="{next_fname}.html" class="nav-next"><span class="nav-label">Next \U0001F449</span><span class="nav-title">{next_title}</span></a>'
    elif not is_appendix and idx == len(items) - 1:
        # Last chapter links to first appendix
        nav += f'<a href="../appendices/{APPENDICES[0][0]}.html" class="nav-next"><span class="nav-label">Next \U0001F449</span><span class="nav-title">{APPENDICES[0][1]}</span></a>'
    nav += '</nav>'
    return nav

def build_page(title, content_html, sidebar_html, nav_html, base_path, active_file):
    """Build complete HTML page."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} | Command the Future</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base_path}assets/style.css">
</head>
<body data-base="{base_path}">

<header class="topbar">
  <div class="topbar-left">
    <button class="hamburger" id="hamburger" aria-label="Toggle sidebar">&#9776;</button>
    <a href="{base_path}index.html" class="topbar-title">Command the Future</a>
  </div>
  <div class="topbar-right">
    <button class="topbar-btn search-btn" aria-label="Search"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6.5" cy="6.5" r="5"/><line x1="10.5" y1="10.5" x2="15" y2="15"/></svg><kbd>Ctrl+K</kbd></button>
    <button class="topbar-btn" id="theme-toggle" aria-label="Toggle theme"></button>
  </div>
</header>

<div class="progress-bar"><div class="progress-fill"></div></div>
<div class="sidebar-overlay" id="sidebar-overlay"></div>
<aside class="sidebar" id="sidebar">
{sidebar_html}
</aside>

<main class="main">
  <article class="content">
{content_html}
    {nav_html}
  </article>
  <footer class="site-footer">
    <p>Made with \u2764\ufe0f by <a href="https://github.com/neam-lang">Neam Lang</a> &middot; <a href="https://github.com/neam-lang/NeamCode-Handbook-Command-the-Future">Source on GitHub</a></p>
  </footer>
</main>

<button class="back-to-top" id="back-to-top" aria-label="Back to top">&#8593;</button>

<div class="search-overlay" id="search-overlay">
  <div class="search-modal">
    <div class="search-input-wrap">
      <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6.5" cy="6.5" r="5"/><line x1="10.5" y1="10.5" x2="15" y2="15"/></svg>
      <input type="text" class="search-input" id="search-input" placeholder="Search chapters, topics...">
    </div>
    <div class="search-results" id="search-results">
      <div class="search-empty">Start typing to search...</div>
    </div>
  </div>
</div>

<script src="{base_path}assets/script.js"></script>
</body>
</html>'''

def convert_chapter(idx):
    """Convert a single chapter."""
    fname, title, part = CHAPTERS[idx]
    md_path = os.path.join(MD_CHAPTERS, f"{fname}.md")

    if not os.path.exists(md_path):
        print(f"  SKIP {fname}.md (not found)")
        return

    with open(md_path, 'r') as f:
        md_text = f.read()

    content_html = md_to_html_content(md_text)
    sidebar_html = build_sidebar(fname, is_appendix=False)

    # Fix sidebar paths for chapters (they're in chapters/ subdir)
    # Sidebar links to other chapters are just filename.html (same dir)
    # Sidebar links to appendices need ../appendices/

    items = [(c[0], c[1]) for c in CHAPTERS]
    nav_html = get_nav(idx, items)

    page_title = f"Chapter {idx}: {title}" if idx > 0 else title
    page_html = build_page(page_title, content_html, sidebar_html, nav_html, "../", fname)

    out_path = os.path.join(HTML_CHAPTERS, f"{fname}.html")
    with open(out_path, 'w') as f:
        f.write(page_html)

    print(f"  ✓ {fname}.html")

def convert_appendix(idx):
    """Convert a single appendix."""
    fname, title = APPENDICES[idx]
    md_path = os.path.join(MD_APPENDICES, f"{fname}.md")

    if not os.path.exists(md_path):
        print(f"  SKIP {fname}.md (not found)")
        return

    with open(md_path, 'r') as f:
        md_text = f.read()

    content_html = md_to_html_content(md_text)
    sidebar_html = build_sidebar(fname, is_appendix=True)

    # Chapter links in sidebar already have ../chapters/ prefix from build_sidebar

    items = [(a[0], a[1]) for a in APPENDICES]
    nav_html = get_nav(idx, items, is_appendix=True)

    page_html = build_page(f"Appendix {fname[0]}: {title}", content_html, sidebar_html, nav_html, "../", fname)

    out_path = os.path.join(HTML_APPENDICES, f"{fname}.html")
    with open(out_path, 'w') as f:
        f.write(page_html)

    print(f"  ✓ {fname}.html")

def build_index():
    """Build the index.html landing page."""
    parts_html = []
    part_idx = 0
    parts_dict = {}
    for fname, title, part in CHAPTERS:
        parts_dict.setdefault(part, []).append((fname, title))

    for part_name, part_color in PARTS:
        if part_name not in parts_dict:
            continue
        part_idx += 1
        cards = []
        for fname, title in parts_dict[part_name]:
            num = fname.split('-')[0]
            ch_emoji = CHAPTER_EMOJIS.get(fname, "")
            cards.append(f'''<a href="chapters/{fname}.html" class="chapter-card" data-part="{part_name}">
  <span class="card-num">{ch_emoji}</span>
  <div class="card-info">
    <div class="card-title">{html.escape(title)}</div>
    <div class="card-meta">Chapter {int(num)}</div>
  </div>
  <span class="card-check">&#10003;</span>
</a>''')

        part_emoji = PART_EMOJIS.get(part_name, "")
        parts_html.append(f'''<div class="part-section" data-part="{part_name}">
  <h3>{part_emoji} Part {part_idx}: {part_name}</h3>
  <div class="cards-grid">{"".join(cards)}</div>
</div>''')

    # Appendices cards
    app_cards = []
    for fname, title in APPENDICES:
        letter = fname[0]
        app_emoji = APPENDIX_EMOJIS.get(fname, "")
        app_cards.append(f'''<a href="appendices/{fname}.html" class="chapter-card" data-part="Appendices">
  <span class="card-num">{app_emoji}</span>
  <div class="card-info">
    <div class="card-title">{html.escape(title)}</div>
    <div class="card-meta">Appendix {letter}</div>
  </div>
  <span class="card-check">&#10003;</span>
</a>''')

    parts_html.append(f'''<div class="part-section" data-part="Appendices">
  <h3>{PART_EMOJIS["Appendices"]} Appendices</h3>
  <div class="cards-grid">{"".join(app_cards)}</div>
</div>''')

    # Learning path nodes
    path_nodes = []
    for idx, (part_name, part_color) in enumerate(PARTS, 1):
        path_emoji = PART_EMOJIS.get(part_name, "")
        path_nodes.append(f'''<div class="path-node">
  <div class="path-dot" style="background:{part_color}">{path_emoji}</div>
  <div class="path-label">{part_name}</div>
</div>''')

    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Command the Future — The NeamCode Handbook</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
</head>
<body data-base="">

<header class="topbar">
  <div class="topbar-left">
    <a href="index.html" class="topbar-title">Command the Future</a>
  </div>
  <div class="topbar-right">
    <button class="topbar-btn search-btn" aria-label="Search"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6.5" cy="6.5" r="5"/><line x1="10.5" y1="10.5" x2="15" y2="15"/></svg><kbd>Ctrl+K</kbd></button>
    <button class="topbar-btn" id="theme-toggle" aria-label="Toggle theme"></button>
  </div>
</header>

<main class="main" style="margin-left:0">
  <section class="hero">
    <div class="hero-cover">
      <div class="cover-band">
        <span class="cover-edition">First Edition &middot; March 2026</span>
      </div>
      <div class="cover-title-area">
        <h1 class="cover-title">Command the Future</h1>
        <p class="cover-subtitle">The NeamCode Handbook &mdash; Master the Agentic AI Terminal</p>
        <div class="cover-divider"></div>
      </div>
      <div class="cover-bottom">
        <div class="cover-author">Praveen Govindaraj</div>
        <div class="cover-tag">The NeamCode Handbook</div>
      </div>
    </div>
    <div class="hero-cta">
      <a href="chapters/00-preface.html" class="start-btn">Start Reading &rarr;</a>
      <a href="https://github.com/neam-lang/NeamCode/releases" class="start-btn start-btn-alt" target="_blank" rel="noopener">Get NeamCode &rarr;</a>
      <div class="hero-version">Open Source &middot; Apache 2.0 &middot; March 2026</div>
    </div>
  </section>

  <section class="learning-path">
    <h2>Learning Path</h2>
    <div class="path-nodes">
      {"".join(path_nodes)}
    </div>
  </section>

  <section class="parts-grid">
    {"".join(parts_html)}
  </section>
  <footer class="site-footer">
    <p>Made with \u2764\ufe0f by <a href="https://github.com/neam-lang">Neam Lang</a> &middot; <a href="https://github.com/neam-lang/NeamCode-Handbook-Command-the-Future">Source on GitHub</a></p>
  </footer>
</main>

<div class="search-overlay" id="search-overlay">
  <div class="search-modal">
    <div class="search-input-wrap">
      <svg width="18" height="18" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6.5" cy="6.5" r="5"/><line x1="10.5" y1="10.5" x2="15" y2="15"/></svg>
      <input type="text" class="search-input" id="search-input" placeholder="Search chapters, topics...">
    </div>
    <div class="search-results" id="search-results">
      <div class="search-empty">Start typing to search...</div>
    </div>
  </div>
</div>

<script src="assets/script.js"></script>
</body>
</html>'''

    out_path = os.path.join(HTML_DIR, "index.html")
    with open(out_path, 'w') as f:
        f.write(index_html)
    print("  ✓ index.html")

def build_search_index():
    """Build search index JSON."""
    index = []
    for fname, title, part in CHAPTERS:
        md_path = os.path.join(MD_CHAPTERS, f"{fname}.md")
        if not os.path.exists(md_path):
            continue
        with open(md_path, 'r') as f:
            text = f.read()
        # Extract first meaningful paragraph as preview
        lines = [l.strip() for l in text.split('\n') if l.strip() and not l.startswith('#') and not l.startswith('---') and not l.startswith('>') and not l.startswith('📖')]
        preview = lines[0][:200] if lines else title
        num = fname.split('-')[0]
        index.append({
            "title": f"Chapter {int(num)}: {title}" if int(num) > 0 else title,
            "chapter": f"Part: {part}",
            "url": f"chapters/{fname}.html",
            "preview": preview
        })

    for fname, title in APPENDICES:
        md_path = os.path.join(MD_APPENDICES, f"{fname}.md")
        if not os.path.exists(md_path):
            continue
        with open(md_path, 'r') as f:
            text = f.read()
        lines = [l.strip() for l in text.split('\n') if l.strip() and not l.startswith('#') and not l.startswith('---')]
        preview = lines[0][:200] if lines else title
        index.append({
            "title": f"Appendix {fname[0]}: {title}",
            "chapter": "Appendices",
            "url": f"appendices/{fname}.html",
            "preview": preview
        })

    out_path = os.path.join(HTML_DIR, "assets", "search-index.json")
    with open(out_path, 'w') as f:
        json.dump(index, f, indent=2)
    print("  ✓ search-index.json")

if __name__ == '__main__':
    print("Converting NeamCode Handbook MD → HTML...")
    print()

    print("Chapters:")
    for i in range(len(CHAPTERS)):
        convert_chapter(i)

    print()
    print("Appendices:")
    for i in range(len(APPENDICES)):
        convert_appendix(i)

    print()
    print("Index & Search:")
    # NOTE: index.html has a custom 3D book cover — do NOT regenerate it.
    # build_index()  # Skipped — custom hero section preserved
    print("  ⊘ index.html (skipped — custom cover preserved)")
    build_search_index()

    print()
    total = len(CHAPTERS) + len(APPENDICES) + 1
    print(f"Done! {total} HTML files generated in html/")
