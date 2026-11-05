"""Builds the Everything AI static site from src/*.html fragments.
Run:  python build.py
"""
import re, json, html
from pathlib import Path

ROOT = Path(__file__).parent
SRC, OUT = ROOT / "src", ROOT

PAGES = [
    ("index", "Home", "🏠", "Start here"),
    ("python", "Python", "🐍", "The language of AI: syntax, functions, OOP, threads"),
    ("data-science", "Data Science", "📊", "NumPy, linear algebra, statistics, probability, pandas, visualization"),
    ("machine-learning", "Machine Learning", "🤖", "Regression, classification, clustering, ensembles, recommenders"),
    ("deep-learning", "Deep Learning", "🧠", "Neural nets, optimizers, CNNs, RNNs, transformers, PyTorch"),
    ("generative-ai", "Generative AI", "✨", "LLMs, prompt engineering, APIs, limits and cost"),
    ("playbook", "Project Playbook", "🧭", "A practical checklist from the live classes"),
    ("case-studies", "Case Studies", "🗂️", "All 14 course projects and how AI solves each one"),
    ("tools", "Tools", "🛠️", "Claude, Grok, Cursor, Antigravity, ChatGPT, OpenClaw and OpenCode"),
    ("models", "Models", "🖥️", "Enterprise NVIDIA, big local machines, a 16 GB GPU, model types and BenchLM"),
    ("hardware", "Hardware", "⚙️", "Memory bandwidth and the best use of B200, RTX 5080, DGX, Apple M5 and M6"),
    ("llm", "Creating an LLM", "🏗️", "Build a language model from scratch on one GPU"),
    ("fine-tuning", "Finetuning an LLM", "🎛️", "A QLoRA pipeline for improving a local LLM on one 16 GB GPU"),
    ("loops", "Loops", "🔁", "Repeatable loops for agents, engineering, research and writing"),
    ("history", "History of AI", "📜", "Eight eras from 1943 to today: symbolists vs connectionists, winters, deep learning, transformers"),
    ("pioneers", "AI Pioneers", "🧬", "Goodfellow, Karpathy and Radford, plus a tour of Karpathy's GitHub"),
    ("glossary", "Glossary", "📖", "Searchable definitions"),
]

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"<[^>]+>", "", s).lower()).strip("-")

def strip_tags(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()

index = []
rendered = {}
for i, (key, title, icon, desc) in enumerate(PAGES):
    body = (SRC / f"{key}.html").read_text(encoding="utf-8")
    heads = []
    def add_id(m):
        text = m.group(2)
        hid = slug(text)
        heads.append((hid, strip_tags(text)))
        return f'<h2 id="{hid}">{text}</h2>'
    body = re.sub(r"<h2>(\s*)(.*?)</h2>", add_id, body, flags=re.S)
    seen = {h for h, _ in heads} | set(re.findall(r'id="([^"]+)"', body))
    subs = []
    def add_sub_id(m):
        tag, text = m.group(1), m.group(2)
        base = slug(text) or tag
        hid, n = base, 2
        while hid in seen:
            hid, n = f"{base}-{n}", n + 1
        seen.add(hid)
        subs.append((hid, strip_tags(text)))
        return f'<{tag} id="{hid}">{text}</{tag}>'
    body = re.sub(r"<(h3|h4)>(.*?)</\1>", add_sub_id, body, flags=re.S)
    rendered[key] = (body, heads)
    page_subs = subs
    url = "index.html" if key == "index" else f"{key}.html"
    index.append({"t": title, "u": url, "p": desc, "x": strip_tags(body)[:300]})
    for hid, ht in heads:
        # include the following paragraph text as searchable context
        m = re.search(rf'<h2 id="{hid}">.*?</h2>(.*?)(?=<h2 |$)', body, flags=re.S)
        ctx = strip_tags(m.group(1))[:400] if m else ""
        index.append({"t": ht, "u": f"{url}#{hid}", "p": title, "x": ctx})
    for hid, ht in page_subs:
        m = re.search(rf'<h[34] id="{re.escape(hid)}">.*?</h[34]>(.*?)(?=<h[234] |$)', body, flags=re.S)
        index.append({"t": ht, "u": f"{url}#{hid}", "p": title, "x": strip_tags(m.group(1))[:300] if m else ""})

(OUT / "assets" / "search-index.js").write_text("window.SEARCH_INDEX=" + json.dumps(index) + ";", encoding="utf-8")

def page(i):
    key, title, icon, desc = PAGES[i]
    body, heads = rendered[key]
    nav = "".join(
        f'<a href="{"index.html" if k=="index" else k+".html"}"{" class=active" if k==key else ""}>{t}</a>'
        for k, t, _, _ in PAGES if k != "index"
    )
    toc = ""
    if heads and key != "index":
        toc = '<aside class="toc"><h4>On this page</h4>' + "".join(f'<a href="#{h}">{t}</a>' for h, t in heads) + "</aside>"
    single = " single" if (not toc) else ""
    pager = ""
    if key not in ("index",):
        prev = PAGES[i - 1] if i > 1 else None
        nxt = PAGES[i + 1] if i + 1 < len(PAGES) else None
        pager = '<div class="pager">' + (f'<a href="{prev[0]}.html">← {prev[1]}</a>' if prev else "<span></span>") + (f'<a href="{nxt[0]}.html">{nxt[1]} →</a>' if nxt else "<span></span>") + "</div>"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title if key!='index' else 'Everything AI'} · Everything AI</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="stylesheet" href="assets/style.css">
</head><body>
<header class="top"><div class="bar">
<a class="logo" href="index.html">Everything <b>AI</b></a>
<nav class="main">{nav}</nav>
<div class="search"><input id="q" type="search" placeholder="Search  ( / )" autocomplete="off"><div id="results"></div></div>
</div></header>
<div class="wrap{single}">{toc}<main>{body}{pager}</main></div>
<footer>Everything AI · a study guide built from the Microsoft AI Engineer program (self-learning lessons and live classes).</footer>
<script src="assets/search-index.js"></script><script src="assets/app.js"></script>
</body></html>"""

for i, (key, *_ ) in enumerate(PAGES):
    (OUT / ("index.html" if key == "index" else f"{key}.html")).write_text(page(i), encoding="utf-8")
print("built", len(PAGES), "pages,", len(index), "search entries")
