#!/usr/bin/env python3
"""
chapter_html_generator.py
从章节内容 dict 生成 book-to-webpage 风格的章节详情 HTML。

用法：
  python3 chapter_html_generator.py ch4_content.json ch04-running-for-your-life.html "Ch 4" \
    --book "The Body Keeps the Score" --author "Bessel van der Kolk" --back "the-body-keeps-the-score.html"
"""

import json
import sys
import argparse
from pathlib import Path

HTML_HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — {book}</title>
<style>
:root {
  --ink: #171411; --muted: #6d6258; --paper: #f8f2e7; --paper-deep: #ece1cf;
  --line: #d8c8af; --red: #b9422f; --blue: #245f73; --green: #4d6f48; --gold: #c2872d;
  --white: #fffaf0; --shadow: 0 18px 50px rgba(55,38,19,.14);
  --font-body: "Songti SC","Noto Serif CJK SC",Georgia,serif;
  --font-display: "PingFang SC","Microsoft YaHei",sans-serif;
  --bg: radial-gradient(circle at 22% 12%,rgba(194,135,45,.18),transparent 28rem),linear-gradient(135deg,#fbf6ec 0%,#efe1ca 100%);
  --surface: rgba(255,250,240,.62); --surface-strong: rgba(255,250,240,.72);
  --bar-bg: rgba(248,242,231,.95); --ink-soft: #3d332b; --ink-soft-2: #44392f;
  --tint-accent: rgba(194,135,45,.12); --tint-accent-strong: rgba(194,135,45,.15);
}
* { box-sizing: border-box; }
body { margin:0; color:var(--ink); background:var(--bg); font-family:var(--font-body); transition: padding-right .3s ease; }
body.drawer-open { padding-right: 420px; }
button { font:inherit; color:inherit; }
.page { width:min(1180px,calc(100% - 32px)); margin:0 auto; padding:24px 0 36px; isolation:isolate; }
.hero { padding:24px 0 20px; }
.eyebrow { margin:0 0 12px; color:var(--red); font:700 12px/1.3 var(--font-display); letter-spacing:.05em; }
h1 { margin:0; max-width:880px; font-size:clamp(28px,4.5vw,52px); line-height:1.1; font-weight:900; }
.hero .lede { margin:14px 0 0; max-width:780px; color:var(--ink-soft); font-size:17px; line-height:1.65; }
.zh-note { color:var(--muted); font-size:14px; line-height:1.6; margin-top:10px; font-style:italic; }
.back-link { display:inline-block; margin-bottom:14px; padding:4px 12px; background:var(--surface); border:1px solid var(--line); color:var(--ink-soft); font:700 12px/1.5 var(--font-display); text-decoration:none; }
.back-link:hover { background:var(--paper-deep); }
.subtabs { display:flex; gap:4px; margin:14px 0 18px; border-bottom:1px solid var(--line); padding-bottom:0; flex-wrap:wrap; }
.subtab { padding:8px 14px; border:1px solid var(--line); background:var(--surface); cursor:pointer; font:800 13px/1.3 var(--font-display); border-bottom:0; }
.subtab[aria-selected="true"] { background:var(--ink); color:var(--white); border-color:var(--ink); }
.subpanel { display:none; animation:rise .3s ease both; }
.subpanel.active { display:block; }
@keyframes rise { from {opacity:0; transform:translateY(12px);} to {opacity:1; transform:translateY(0);} }
.section-title { margin:6px 0 12px; font:900 24px/1.2 var(--font-display); }
.section-lead { margin:0 0 16px; color:var(--ink-soft); font-size:16px; line-height:1.65; }
.grid { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
.note { min-height:160px; padding:18px; border:1px solid var(--line); background:var(--surface); position:relative; transition: border-color .2s, box-shadow .2s; }
.note:hover { border-color:var(--blue); box-shadow:0 4px 18px rgba(36,95,115,.12); }
.note h3 { margin:0 0 8px; font:900 17px/1.25 var(--font-display); }
.note p { margin:0; color:var(--ink-soft-2); font-size:14px; line-height:1.6; }
.note .when { margin-top:6px; color:var(--muted); font:12px/1.5 var(--font-display); }
.note .src-chip { position:absolute; top:8px; right:8px; font:700 10px/1 var(--font-display); color:var(--muted); background:var(--white); border:1px solid var(--line); padding:2px 5px; border-radius:3px; cursor:pointer; }
.note .src-chip:hover { color:var(--blue); border-color:var(--blue); }
.chain { display:grid; gap:6px; margin:14px 0 6px; }
.chain button { min-height:54px; padding:10px 12px; border:1px solid var(--line); background:var(--white); cursor:pointer; text-align:left; font:800 13px/1.3 var(--font-display); position:relative; }
.chain button.active { color:var(--white); background:var(--blue); border-color:var(--blue); }
.explain { min-height:90px; margin-top:8px; padding:16px; color:var(--ink-soft-2); border:1px solid var(--line); background:var(--surface-strong); font-size:15px; line-height:1.65; position:relative; }
.explain .src-link { position:absolute; bottom:6px; right:12px; font:700 10px/1.4 var(--font-display); color:var(--blue); cursor:pointer; }
.timeline { position:relative; padding-left:20px; border-left:2px solid var(--gold); }
.timeline-item { margin-bottom:16px; position:relative; padding-left:10px; }
.timeline-item::before { content:""; position:absolute; left:-25px; top:6px; width:8px; height:8px; border-radius:50%; background:var(--gold); }
.timeline-item .time { color:var(--muted); font:700 11px/1.3 var(--font-display); }
.timeline-item h3 { margin:3px 0 4px; font:900 15px/1.25 var(--font-display); }
.timeline-item p { margin:0; color:var(--ink-soft-2); font-size:13px; line-height:1.6; }
.accordion details { margin-bottom:6px; border:1px solid var(--line); background:var(--surface); }
.accordion summary { padding:12px 16px; cursor:pointer; font:800 14px/1.3 var(--font-display); list-style:none; }
.accordion summary::-webkit-details-marker { display:none; }
.accordion summary::before { content:"▸"; display:inline-block; width:16px; margin-right:6px; color:var(--gold); font-weight:900; }
.accordion details[open] summary::before { content:"▾"; }
.accordion .acc-body { padding:0 16px 12px 32px; color:var(--ink-soft-2); font-size:13px; line-height:1.65; }
.accordion .acc-body strong { color:var(--blue); }
.story { border:1px solid var(--line); background:var(--surface-strong); padding:18px 20px; margin:12px 0; box-shadow:var(--shadow); position:relative; }
.story .story-label { color:var(--red); font:700 11px/1.3 var(--font-display); margin-bottom:6px; }
.story h3 { margin:0 0 10px; font:900 18px/1.2 var(--font-display); }
.story p { margin:0 0 10px; color:var(--ink-soft); font-size:14px; line-height:1.7; }
.story .story-insight { margin-top:10px; padding-top:10px; border-top:1px dashed var(--line); color:var(--blue); font:700 13px/1.5 var(--font-display); }
.story .story-src { position:absolute; top:12px; right:12px; font:700 10px/1 var(--font-display); color:var(--muted); background:var(--white); border:1px solid var(--line); padding:3px 6px; border-radius:3px; cursor:pointer; }
.story .story-src:hover { color:var(--blue); border-color:var(--blue); }
.rules { list-style:none; padding:0; display:grid; gap:8px; }
.rules li { padding:12px 16px; border:1px solid var(--line); background:var(--surface); font-size:14px; line-height:1.6; }
.rules li strong { color:var(--blue); }
.rules li em { display:block; margin-top:3px; color:var(--muted); font-size:12px; font-style:normal; }
.drawer { position:fixed; top:0; right:0; bottom:0; width:420px; max-width:90vw; background:var(--paper); border-left:1px solid var(--line); box-shadow:-16px 0 40px rgba(55,38,19,.18); transform:translateX(100%); transition:transform .3s ease; z-index:90; display:flex; flex-direction:column; }
.drawer.open { transform:translateX(0); }
.drawer-head { padding:14px 18px; border-bottom:1px solid var(--line); display:flex; align-items:flex-start; justify-content:space-between; gap:12px; background:var(--surface-strong); flex-shrink:0; }
.drawer-head .src-title { font:900 14px/1.3 var(--font-display); }
.drawer-head .src-meta { font:11px/1.4 var(--font-display); color:var(--muted); margin-top:3px; }
.drawer-close { border:1px solid var(--line); background:var(--white); cursor:pointer; width:28px; height:28px; border-radius:4px; font-size:16px; line-height:1; display:grid; place-items:center; color:var(--muted); flex-shrink:0; }
.drawer-close:hover { color:var(--red); border-color:var(--red); }
.drawer-body { padding:16px 18px; overflow-y:auto; flex:1; font-size:14px; line-height:1.7; color:var(--ink-soft); }
.drawer-body p { margin:0 0 10px; }
.drawer-body .src-attr { color:var(--muted); font:12px/1.5 var(--font-display); margin-top:14px; padding-top:10px; border-top:1px dashed var(--line); }
.drawer-backdrop { position:fixed; inset:0; background:rgba(23,20,17,.2); z-index:80; opacity:0; pointer-events:none; transition:opacity .3s; }
.drawer-backdrop.open { opacity:1; pointer-events:auto; }
.src-toggle { position:fixed; top:14px; right:14px; z-index:100; padding:6px 12px; border:1px solid var(--line); border-radius:4px; background:var(--bar-bg); cursor:pointer; font:11px/1.2 var(--font-display); color:var(--muted); transition:all .2s; }
.src-toggle:hover { border-color:var(--gold); color:var(--ink); }
body.drawer-open .src-toggle { right:434px; }
.dd-toast { position:fixed; bottom:24px; left:50%; transform:translateX(-50%); padding:10px 20px; background:var(--ink); color:var(--white); border-radius:5px; font:13px/1.4 var(--font-display); opacity:0; transition:opacity .3s; pointer-events:none; z-index:300; }
.dd-toast.show { opacity:1; }
.footer { margin-top:24px; padding-top:12px; border-top:1px solid var(--line); color:var(--muted); font:12px/1.6 var(--font-display); }
@media (max-width:880px) {
  .grid { grid-template-columns:1fr; }
  body.drawer-open { padding-right:0; }
  .drawer { width:100%; }
}
</style>
</head>
<body data-theme="warm-paper">
<button id="srcToggle" class="src-toggle">show sources</button>
<main class="page">

<a class="back-link" href="{back_link}">← Back to Architecture</a>

<section class="hero">
  <p class="eyebrow">{chapter_label} / {total_chapters} · {book_upper}</p>
  <h1>{title}</h1>
  <p class="lede">{lede}</p>
  <p class="zh-note">中文标题：{zh_title}。你的理由：{your_reason}。</p>
</section>

<nav class="subtabs">
  <button class="subtab" data-subtab="s1" aria-selected="true">Overview</button>
  <button class="subtab" data-subtab="s2" aria-selected="false">Causal Chain</button>
  <button class="subtab" data-subtab="s3" aria-selected="false">Frameworks</button>
  <button class="subtab" data-subtab="s4" aria-selected="false">Cases</button>
  <button class="subtab" data-subtab="s5" aria-selected="false">Research + Decision Rules</button>
</nav>

<!-- Sub-panel 1: Overview -->
<div class="subpanel active" data-subpanel="s1">
  <div class="grid">
{notes_html}
  </div>
</div>

<!-- Sub-panel 2: Causal Chain -->
<div class="subpanel" data-subpanel="s2">
  <p class="section-lead">{causal_lead}</p>
  <div class="chain" id="causalChain">
{chain_buttons}
  </div>
  <div class="explain" id="causalExplain">
    {chain_first_detail}
  </div>
</div>

<!-- Sub-panel 3: Frameworks -->
<div class="subpanel" data-subpanel="s3">
  <p class="section-lead">{frameworks_lead}</p>
  <div class="accordion">
{framework_details}
  </div>
</div>

<!-- Sub-panel 4: Cases -->
<div class="subpanel" data-subpanel="s4">
  <p class="section-lead">{cases_lead}</p>
{stories_html}
</div>

<!-- Sub-panel 5: Research + Decision Rules -->
<div class="subpanel" data-subpanel="s5">
  <h3 style="margin:0 0 12px; font:900 20px/1.2 var(--font-display);">Key Research</h3>
  <div class="timeline">
{timeline_items}
  </div>
  <h3 style="margin:24px 0 12px; font:900 20px/1.2 var(--font-display);">Decision Rules</h3>
  <ul class="rules">
{decision_rules}
  </ul>
  <h3 style="margin:24px 0 12px; font:900 20px/1.2 var(--font-display);">Key Takeaways</h3>
  <ul class="rules">
{key_takeaways}
  </ul>
</div>

<footer class="footer">
  <p>Source: {author}, <em>{book}</em> ({year}), Chapter {chapter_num}.</p>
</footer>
</main>

<div class="drawer-backdrop" id="drawerBackdrop" onclick="closeDrawer()"></div>
<aside class="drawer" id="drawer">
  <div class="drawer-head">
    <div>
      <p class="src-title" id="drawerTitle">Source</p>
      <p class="src-meta" id="drawerMeta">Original passage from the book</p>
    </div>
    <button class="drawer-close" onclick="closeDrawer()">×</button>
  </div>
  <div class="drawer-body" id="drawerBody">
    <p style="color:var(--muted);">Click any "src ↗" chip to see the original passage.</p>
  </div>
</aside>
<div class="dd-toast" id="ddToast"></div>

<script>
{js_content}
</script>
</body>
</html>
'''

# ===== Helpers =====

def esc(s):
    """Escape for HTML attribute / text content (basic)."""
    if s is None: return ""
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))

def render_notes(notes):
    out = []
    for n in notes:
        chip = f'<span class="src-chip" onclick="openDrawer(\'{esc(n["source"])}\', event)">src ↗</span>' if n.get("source") else ""
        out.append(f'''    <article class="note">{chip}<h3>{esc(n["title"])}</h3><p>{esc(n["text"])}</p><p class="when">{esc(n["when"])}</p></article>''')
    return "\n".join(out)

def render_chain_buttons(steps):
    out = []
    for i, step in enumerate(steps, 1):
        label = step[0]
        active = ' class="active"' if i == 1 else ""
        out.append(f'    <button data-step="{i}"{active}>{esc(label)}</button>')
    return "\n".join(out)

def render_chain_js(steps):
    """Generate JS object for causal chain explanations (label, detail, [source])."""
    parts = []
    for i, step in enumerate(steps, 1):
        detail = step[1]
        parts.append(f'  "{i}": "{esc(detail)}"')
    return "var causalExplain = {\n" + ",\n".join(parts) + "\n};"

def render_frameworks(frameworks):
    out = []
    for i, fw in enumerate(frameworks, 1):
        body = f'''<div class="acc-body"><strong>{esc(fw["name"])}</strong> — {esc(fw["definition"])}<br><br><strong>Use when:</strong> {esc(fw["use_when"])}<br><strong>How:</strong> {esc(fw["how"])}</div>'''
        out.append(f'    <details><summary><strong>{i}. {esc(fw["name"])}</strong></summary>{body}</details>')
    return "\n".join(out)

def render_stories(cases):
    out = []
    for c in cases:
        src = f'<span class="story-src" onclick="openDrawer(\'{esc(c["source"])}\', event)">src ↗</span>' if c.get("source") else ""
        body_html = "\n      ".join(f"<p>{esc(p)}</p>" for p in c.get("body_paragraphs", [c.get("body", "")]))
        out.append(f'''  <article class="story">{src}
    <p class="story-label">{esc(c["label"])}</p>
    <h3>{esc(c["title"])}</h3>
      {body_html}
    <p class="story-insight">{esc(c["insight"])}</p>
  </article>''')
    return "\n".join(out)

def render_timeline(research):
    out = []
    for r in research:
        out.append(f'''    <div class="timeline-item"><span class="time">{esc(r["year"])}</span><h3>{esc(r["name"])}</h3><p>{esc(r["summary"])}</p></div>''')
    return "\n".join(out)

def render_rules(rules):
    out = []
    for r in rules:
        out.append(f'    <li><strong>{esc(r["condition"])}:</strong> {esc(r["approach"])}<em>Source: {esc(r["source"])}</em></li>')
    return "\n".join(out)

def render_takeaways(takeaways):
    out = []
    for t in takeaways:
        out.append(f'    <li>{esc(t)}</li>')
    return "\n".join(out)

def generate_passages_js(content):
    """Generate passages dict + lookup function JS."""
    # Need passages from content; if not provided, skip
    passages = content.get("passages", {})
    passages_json = json.dumps(passages, ensure_ascii=False)
    return f'''var passages = {passages_json};
var sourceAliases = {{}};
function lookupPassage(key) {{
  if (passages[key]) return {{ text: passages[key], alias: null }};
  var a = sourceAliases[key];
  if (a && passages[a]) return {{ text: passages[a], alias: a }};
  return null;
}}
var currentSource = null;
function openDrawer(sourceKey, evt) {{
  if (evt) {{ evt.stopPropagation(); evt.preventDefault(); }}
  var lookup = lookupPassage(sourceKey);
  if (!lookup) {{ showToast("Source not found: " + sourceKey); return; }}
  currentSource = sourceKey;
  document.getElementById("drawerTitle").textContent = sourceKey;
  document.getElementById("drawerMeta").textContent = "Original passage";
  var text = lookup.text;
  var sepIdx = text.indexOf("\\n\\n— ");
  var body, attr;
  if (sepIdx >= 0) {{ body = text.substring(0, sepIdx); attr = text.substring(sepIdx + 4); }}
  else {{ body = text; attr = ""; }}
  var bodyHtml = body.split("\\n\\n").map(function(p) {{ return "<p>" + p + "</p>"; }}).join("");
  document.getElementById("drawerBody").innerHTML =
    '<div class="src-paragraph">' + bodyHtml + '</div>' +
    (attr ? '<div class="src-attr">' + attr + '</div>' : '');
  document.getElementById("drawer").classList.add("open");
  document.getElementById("drawerBackdrop").classList.add("open");
  document.body.classList.add("drawer-open");
}}
function closeDrawer() {{
  document.getElementById("drawer").classList.remove("open");
  document.getElementById("drawerBackdrop").classList.remove("open");
  document.body.classList.remove("drawer-open");
  currentSource = null;
}}
document.addEventListener("keydown", function(e) {{ if (e.key === "Escape" && currentSource) closeDrawer(); }});
document.querySelectorAll(".subtab").forEach(function(t) {{
  t.onclick = function() {{
    document.querySelectorAll(".subtab").forEach(function(x){{ x.setAttribute("aria-selected","false"); }});
    document.querySelectorAll(".subpanel").forEach(function(x){{ x.classList.remove("active"); }});
    t.setAttribute("aria-selected","true");
    var panel = document.querySelector('.subpanel[data-subpanel="' + t.dataset.subtab + '"]');
    if (panel) panel.classList.add("active");
  }};
}});
{generate_chain_js_inner()}
function showToast(msg) {{
  var toast = document.getElementById("ddToast");
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(function() {{ toast.classList.remove("show"); }}, 2000);
}}
'''

def generate_chain_js_inner():
    # Causal chain interactivity (separate so it can use content)
    return '''document.querySelectorAll("#causalChain button").forEach(function(btn) {
  btn.onclick = function() {
    document.querySelectorAll("#causalChain button").forEach(function(x){ x.classList.remove("active"); });
    btn.classList.add("active");
    document.getElementById("causalExplain").innerHTML = causalExplain[btn.dataset.step];
  };
});'''

def generate_html(content, meta):
    """Main generation function."""
    notes_html = render_notes(content["overview_notes"])
    chain_buttons = render_chain_buttons(content["causal_chain"])
    framework_details = render_frameworks(content["frameworks"])
    stories_html = render_stories(content["cases"])
    timeline_items = render_timeline(content["research"])
    decision_rules = render_rules(content["decisions"])
    key_takeaways = render_takeaways(content["key_takeaways"])
    chain_first_detail = esc(content["causal_chain"][0][1])  # first step detail

    # JS
    js_content = generate_passages_js(content)
    # Inject causalExplain object after the function definition
    chain_js = render_chain_js(content["causal_chain"])
    # Insert chain_js before chain handler
    js_content = js_content.replace(
        "function closeDrawer()",
        chain_js + "\nfunction closeDrawer()"
    )

    html = HTML_HEAD
    # Use replace() instead of .format() to avoid conflicts with CSS curly braces
    replacements = {
        "{title}": esc(meta["title"]),
        "{book}": esc(meta["book"]),
        "{chapter_label}": esc(meta["chapter_label"]),
        "{total_chapters}": str(meta["total_chapters"]),
        "{book_upper}": esc(meta["book"]).upper(),
        "{back_link}": esc(meta["back_link"]),
        "{lede}": esc(meta.get("lede", "")),
        "{zh_title}": esc(content["zh_title"]),
        "{your_reason}": esc(meta.get("your_reason", "directly relevant to your work")),
        "{notes_html}": notes_html,
        "{causal_lead}": esc(meta.get("causal_lead", "Step-by-step causal chain. Click each step for detail.")),
        "{chain_buttons}": chain_buttons,
        "{chain_first_detail}": chain_first_detail,
        "{frameworks_lead}": esc(meta.get("frameworks_lead", "Core frameworks introduced in this chapter.")),
        "{framework_details}": framework_details,
        "{cases_lead}": esc(meta.get("cases_lead", "Real cases from the chapter.")),
        "{stories_html}": stories_html,
        "{timeline_items}": timeline_items,
        "{decision_rules}": decision_rules,
        "{key_takeaways}": key_takeaways,
        "{author}": esc(meta["author"]),
        "{year}": str(meta["year"]),
        "{chapter_num}": str(meta["chapter_num"]),
        "{js_content}": js_content,
    }
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    return html


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("content_json", help="Path to chapter content JSON")
    parser.add_argument("output_html", help="Path to output HTML")
    parser.add_argument("--title", required=True)
    parser.add_argument("--book", default="The Body Keeps the Score")
    parser.add_argument("--author", default="Bessel van der Kolk")
    parser.add_argument("--year", default="2014")
    parser.add_argument("--chapter-num", type=int, required=True)
    parser.add_argument("--chapter-label", default=None, help="e.g. 'Chapter 4'")
    parser.add_argument("--total-chapters", type=int, default=22)
    parser.add_argument("--back-link", default="the-body-keeps-the-score.html")
    parser.add_argument("--lede", default="")
    parser.add_argument("--your-reason", default="")
    parser.add_argument("--causal-lead", default="")
    parser.add_argument("--frameworks-lead", default="")
    parser.add_argument("--cases-lead", default="")
    args = parser.parse_args()

    with open(args.content_json) as f:
        content = json.load(f)

    meta = {
        "title": args.title,
        "book": args.book,
        "author": args.author,
        "year": args.year,
        "chapter_num": args.chapter_num,
        "chapter_label": args.chapter_label or f"Chapter {args.chapter_num}",
        "total_chapters": args.total_chapters,
        "back_link": args.back_link,
        "lede": args.lede,
        "your_reason": args.your_reason,
        "causal_lead": args.causal_lead,
        "frameworks_lead": args.frameworks_lead,
        "cases_lead": args.cases_lead,
    }

    html = generate_html(content, meta)
    Path(args.output_html).write_text(html, encoding="utf-8")
    print(f"✓ Generated {args.output_html} ({len(html):,} bytes)")
