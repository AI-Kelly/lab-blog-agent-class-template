#!/usr/bin/env python3
"""Build the blog agent dashboard: one HTML page showing every topic, post,
review fix, run, and cost, plus Search Console clicks and impressions.

Used by /blog-dashboard. It does the same job every time, so it's code, not AI.
It reads only files that are already in the repository:

    post-log.csv                    every post and its status
    output/topics/*-topics*.md      shortlists, with the owner's decisions
    output/logs/*.md                run logs, with paid calls and costs
    output/drafts/*-review.md       the reviewer's fixes
    output/search-console.csv       weekly clicks and impressions (optional,
                                    saved by /blog-dashboard from Databox)

Usage:
    python3 tools/build_dashboard.py [output.html]

Writes output/dashboard.html by default. Prints a JSON summary to stdout.
Standard Python only; the page needs no internet connection to open.
Exit codes: 0 built, 1 error (nothing written).
"""

import csv
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS_DIR = ROOT / "output" / "topics"
LOGS_DIR = ROOT / "output" / "logs"
DRAFTS_DIR = ROOT / "output" / "drafts"
POST_LOG = ROOT / "post-log.csv"
SEARCH_CONSOLE = ROOT / "output" / "search-console.csv"
DEFAULT_OUT = ROOT / "output" / "dashboard.html"

LOG_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(research|write|check|finish|run)(?:-(\d+))?\.md$")
MONEY = re.compile(r"\$\s*([0-9]+(?:\.[0-9]+)?)")
DONE_STATUSES = {"reviewed", "ready to publish", "published"}
STATUS_LABELS = {
    "draft": "Draft",
    "needs attention": "Needs you",
    "reviewed": "Passed review",
    "ready to publish": "Ready to publish",
    "published": "Published",
}
RUN_LABELS = {
    "research": "Research topics",
    "write": "Write post",
    "check": "Source and review",
    "finish": "Finish post",
    "run": "Full run",
}


def esc(value):
    return html.escape("" if value is None else str(value), quote=True)


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def field(text, name):
    """Value of a '**Name:** value' line (with or without a leading '- ')."""
    m = re.search(r"^\s*(?:[-*]\s*)?\*\*" + re.escape(name) + r":\*\*\s*(.*)$", text, re.M | re.I)
    return m.group(1).strip() if m else ""


def number(text):
    m = re.search(r"-?[0-9][0-9,]*(?:\.[0-9]+)?", text or "")
    if not m:
        return None
    try:
        return float(m.group(0).replace(",", ""))
    except ValueError:
        return None


def money(text):
    m = MONEY.search(text or "")
    return float(m.group(1)) if m else None


def fmt_int(value):
    return "–" if value is None else f"{int(round(value)):,}"


def fmt_money(value):
    if value is None:
        return "–"
    return f"${value:,.2f}" if value >= 0.1 or value == 0 else f"${value:,.3f}"


def clean(text):
    """Strip Markdown emphasis and links for display."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text or "")
    return re.sub(r"[*_`]", "", text).strip()


# ---------------------------------------------------------------- reading


def read_posts():
    if not POST_LOG.exists():
        return []
    with POST_LOG.open(newline="", encoding="utf-8") as f:
        return [{k: (v or "").strip() for k, v in row.items() if k} for row in csv.DictReader(f)]


def read_topics(posts):
    by_file = {p.get("file", ""): p for p in posts}
    by_title = {p.get("title", "").lower(): p for p in posts}
    by_keyword = {p.get("target_keyword", "").lower(): p for p in posts if p.get("target_keyword")}
    topics = []
    if not TOPICS_DIR.exists():
        return topics
    for path in sorted(TOPICS_DIR.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        date = path.name[:10]
        text = read(path)
        blocks = re.split(r"^##\s+(?=\d+\.\s)", text, flags=re.M)[1:]
        for block in blocks:
            head = block.splitlines()[0]
            m = re.match(r"(\d+)\.\s+(.*)", head)
            if not m:
                continue
            rank, title = int(m.group(1)), clean(m.group(2))
            keyword = clean(field(block, "Target keyword"))
            scores = field(block, "Scores")
            total = re.search(r"Weighted total\s*\**\s*([0-9.]+)", scores, re.I)
            decision_line = next((l for l in block.splitlines() if l.strip().lower().startswith("decision:")), "")
            approved = bool(re.search(r"\[[xX]\]\s*approve", decision_line))
            rejected = bool(re.search(r"\[[xX]\]\s*reject", decision_line))
            reason = decision_line.split("Reason:", 1)[1].strip() if "Reason:" in decision_line else ""
            status_line = next((l for l in block.splitlines() if l.strip().lower().startswith("status:")), "")
            draft = re.search(r"Draft:\s*(\S+)", status_line)
            post = None
            if draft:
                post = by_file.get(draft.group(1).strip())
            post = post or by_title.get(title.lower()) or (by_keyword.get(keyword.lower()) if keyword else None)
            if post:
                status = STATUS_LABELS.get(post.get("status", "").lower(), post.get("status", "") or "Drafted")
            elif status_line:
                status = "Drafted"
            elif approved:
                status = "Approved, not written"
            elif rejected:
                status = "Rejected"
            else:
                status = "Waiting for your decision"
            topics.append({
                "shortlist": date,
                "shortlist_file": f"output/topics/{path.name}",
                "rank": rank,
                "title": title,
                "keyword": keyword,
                "searches": number(field(block, "Monthly searches")),
                "difficulty": number(field(block, "Keyword difficulty")),
                "score": float(total.group(1)) if total else None,
                "offer": clean(field(block, "Matching offer")),
                "decision": "Approved" if approved else "Rejected" if rejected else "",
                "reason": clean(reason),
                "status": status,
                "written": bool(post or status_line),
            })
    return topics


def read_runs():
    runs = []
    if not LOGS_DIR.exists():
        return runs
    for path in sorted(LOGS_DIR.glob("*.md")):
        m = LOG_NAME.match(path.name)
        if not m:
            continue
        date, kind, n = m.group(1), m.group(2), int(m.group(3) or 1)
        text = read(path)
        calls = field(text, "Paid DataForSEO calls")
        dfs_calls = number(calls) if calls else None
        dfs_cost = perplexity_cost = None
        result = ""
        draft = clean(field(text, "Draft"))
        if kind == "research":
            dfs_cost = money(field(text, "Estimated cost"))
            result = "Shortlist " + clean(field(text, "Shortlist")).replace("output/topics/", "")
        elif kind == "write":
            dfs_cost = money(field(text, "Estimated cost"))
            words = field(text, "Word count")
            result = f"Draft, {clean(words)} words" if words else "Draft written"
        elif kind == "check":
            dfs_cost = money(field(text, "Estimated cost")) or 0.0
            perplexity_cost = money(field(text, "Perplexity calls")) or 0.0
            result = clean(field(text, "Final result")) or "Checked"
            rounds = clean(field(text, "Review rounds"))
            if rounds:
                result += f" ({rounds})"
        elif kind == "finish":
            dfs_cost = perplexity_cost = 0.0
            result = "Ready to publish"
        else:
            result = clean(field(text, "Result"))
        runs.append({
            "date": date,
            "order": n,
            "kind": kind,
            "step": RUN_LABELS[kind],
            "file": f"output/logs/{path.name}",
            "draft": draft,
            "result": result,
            "dataforseo_calls": dfs_calls,
            "dataforseo_cost": dfs_cost,
            "perplexity_cost": perplexity_cost,
            "words": number(field(text, "Word count")) if kind == "write" else None,
            "final": clean(field(text, "Final result")) if kind == "check" else "",
            "rounds": clean(field(text, "Review rounds")) if kind == "check" else "",
        })
    runs.sort(key=lambda r: (r["date"], r["order"]))
    return runs


def rule_area(rule):
    r = rule.lower()
    if "voice-and-style" in r or "voice and style" in r:
        return "Voice and style"
    if "offers" in r or "claim" in r or "price" in r:
        return "Claims and offers"
    if "post-structure" in r or "structure" in r:
        return "Post structure"
    if r.startswith("source") or "http" in r:
        return "Fact check"
    if "link" in r:
        return "Links"
    return "Other"


def read_fixes():
    fixes = []
    if not DRAFTS_DIR.exists():
        return fixes
    for path in sorted(DRAFTS_DIR.glob("*-review.md")):
        draft = path.name[: -len("-review.md")]
        check, review, skip = 1, 0, False
        current = None
        for line in read(path).splitlines():
            stripped = line.strip()
            if stripped == "---":
                check, review, skip, current = check + 1, 0, False, None
                continue
            m = re.match(r"^##\s+Review\s+(\d+)", stripped, re.I)
            if m:
                review, skip, current = int(m.group(1)), False, None
                continue
            if re.match(r"^#{2,3}\s+(Needs you|Optional suggestions|What changed|Checks)", stripped, re.I):
                skip, current = True, None
                continue
            if re.match(r"^##\s+Fixes", stripped, re.I):
                skip = False
                continue
            if skip or not review:
                continue
            m = re.match(r"^\d+\.\s+\*\*Problem:\*\*", stripped)
            if m:
                current = {"draft": draft, "check": check, "review": review, "rule": "", "fix": "", "who": ""}
                fixes.append(current)
                continue
            if current:
                for name in ("Rule", "Fix", "Who"):
                    mm = re.match(r"^\*\*" + name + r":\*\*\s*(.*)$", stripped)
                    if mm:
                        current[name.lower()] = clean(mm.group(1))
    for f in fixes:
        f["area"] = rule_area(f["rule"])
    return fixes


def read_search_console():
    if not SEARCH_CONSOLE.exists():
        return []
    rows = []
    with SEARCH_CONSOLE.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            week = (row.get("week") or "").strip()
            if not week:
                continue
            rows.append({
                "week": week,
                "clicks": number(row.get("clicks")) or 0,
                "impressions": number(row.get("impressions")) or 0,
            })
    rows.sort(key=lambda r: r["week"])
    return rows


# ---------------------------------------------------------------- drawing


def bars_svg(rows, key, label):
    """A small weekly bar chart as inline SVG, sized by the page."""
    if not rows:
        return ""
    w, h, pad_b, pad_t = 600, 150, 1, 8
    peak = max(r[key] for r in rows) or 1
    step = w / len(rows)
    bw = max(2, step * 0.7)
    split = len(rows) - 13 if len(rows) > 13 else 0
    parts = [f'<svg class="chart" viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" aria-label="{esc(label)} by week">']
    for i, r in enumerate(rows):
        bh = (h - pad_b - pad_t) * r[key] / peak
        x = i * step + (step - bw) / 2
        cls = "bar" if i >= split else "bar old"
        parts.append(
            f'<rect class="{cls}" x="{x:.1f}" y="{h - pad_b - bh:.1f}" width="{bw:.1f}" height="{max(bh, 0.5):.1f}">'
            f'<title>Week of {esc(r["week"])}: {fmt_int(r[key])} {esc(label.lower())}</title></rect>'
        )
    parts.append(f'<line class="axis" x1="0" y1="{h - pad_b}" x2="{w}" y2="{h - pad_b}" vector-effect="non-scaling-stroke"/>')
    parts.append("</svg>")
    parts.append(f'<div class="ticks"><span>Week of {esc(rows[0]["week"])}</span><span>Week of {esc(rows[-1]["week"])}</span></div>')
    return "".join(parts)


def hbars(items, total=None):
    """Horizontal bars as plain HTML: [(label, value, note)]."""
    peak = max((v for _, v, _ in items), default=0) or 1
    out = ['<div class="hbars">']
    for name, value, note in items:
        pct = 100 * value / peak
        out.append(
            f'<div class="hrow"><span class="hname">{esc(name)}</span>'
            f'<span class="htrack"><span class="hfill" style="width:{pct:.1f}%"></span></span>'
            f'<span class="hval">{fmt_int(value)}{(" " + esc(note)) if note else ""}</span></div>'
        )
    out.append("</div>")
    return "".join(out)


def table(headers, rows, numeric=()):
    out = ['<div class="tablebox"><table><thead><tr>']
    for i, h in enumerate(headers):
        out.append(f'<th class="{"n" if i in numeric else ""}">{esc(h)}</th>')
    out.append("</tr></thead><tbody>")
    for row in rows:
        out.append("<tr>")
        for i, cell in enumerate(row):
            out.append(f'<td class="{"n" if i in numeric else ""}">{cell}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def pill(text):
    tone = {
        "Published": "good", "Ready to publish": "good", "Passed review": "good", "Approved": "good", "PASS": "good",
        "Needs you": "warn", "NEEDS ATTENTION": "warn", "Waiting for your decision": "warn",
        "Rejected": "muted", "Approved, not written": "info", "Draft": "info", "Drafted": "info",
    }.get(text, "muted")
    return f'<span class="pill {tone}">{esc(text)}</span>' if text else "–"


def empty(message):
    return f'<p class="empty">{esc(message)}</p>'


CSS = """
:root{--bg:#f7f7f5;--card:#fff;--fg:#1d1d1b;--muted:#6b6b66;--line:#e4e4df;--accent:#2f6fde;--accent-soft:#c9dafa;
--good:#1f7a4d;--good-bg:#e3f3ea;--warn:#9a5b00;--warn-bg:#fdf0d9;--info:#2a5bb8;--info-bg:#e6eefc;--muted-bg:#efefeb}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#161615;--card:#20201e;--fg:#ececea;--muted:#a3a39d;
--line:#34342f;--accent:#7aa7ff;--accent-soft:#34476b;--good:#7dd3a6;--good-bg:#1d3a2b;--warn:#f2c06b;--warn-bg:#3d2f14;
--info:#9dbcff;--info-bg:#1f2c47;--muted-bg:#2b2b28}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 16px 60px}
h1{font-size:28px;margin:0 0 4px}h2{font-size:19px;margin:36px 0 12px}h3{font-size:15px;margin:0 0 6px}
.lede{color:var(--muted);margin:0 0 20px;max-width:760px}
.todo{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--warn);border-radius:10px;padding:14px 18px;margin-bottom:20px}
.todo ol{margin:6px 0 0;padding-left:20px}.todo.clear{border-left-color:var(--good)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px}
.tile .lbl{display:block;color:var(--muted);font-size:13px}.tile .num{display:block;font-size:28px;font-weight:650;margin-top:2px}
.tile .sub{display:block;color:var(--muted);font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:14px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;min-width:0}
.note{color:var(--muted);font-size:13px;margin:0 0 12px}
.big{display:flex;gap:28px;margin-bottom:8px}.big .v{display:block;font-size:24px;font-weight:650}.big .c{color:var(--muted);font-size:12px}
.chart{width:100%;height:150px;display:block}.bar{fill:var(--accent)}.bar.old{fill:var(--accent-soft)}
.axis{stroke:var(--line)}.ticks{display:flex;justify-content:space-between;color:var(--muted);font-size:12px;margin-top:4px}
.nowrap{white-space:nowrap}.stack{display:grid;gap:14px}
.hbars{display:grid;gap:8px}.hrow{display:grid;grid-template-columns:minmax(110px,170px) 1fr auto;gap:10px;align-items:center;font-size:14px}
.htrack{background:var(--muted-bg);border-radius:4px;height:14px;overflow:hidden}.hfill{display:block;height:100%;background:var(--accent);border-radius:4px}
.hval{font-variant-numeric:tabular-nums;color:var(--muted);min-width:2ch;text-align:right}
.tablebox{overflow-x:auto;border:1px solid var(--line);border-radius:8px}
table{border-collapse:collapse;width:100%;font-size:13.5px}th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{background:var(--muted-bg);font-weight:600;white-space:nowrap;position:sticky;top:0}tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;white-space:nowrap}
.pill.good{background:var(--good-bg);color:var(--good)}.pill.warn{background:var(--warn-bg);color:var(--warn)}
.pill.info{background:var(--info-bg);color:var(--info)}.pill.muted{background:var(--muted-bg);color:var(--muted)}
.empty{color:var(--muted);font-style:italic;margin:4px 0}a{color:var(--accent)}code{font-size:13px}
footer{color:var(--muted);font-size:12px;margin-top:40px}
@media (max-width:520px){.hrow{grid-template-columns:96px 1fr auto}.big{gap:18px}h1{font-size:24px}}
"""


def build(out_path):
    posts = read_posts()
    topics = read_topics(posts)
    runs = read_runs()
    fixes = read_fixes()
    sc = read_search_console()

    status = lambda p: p.get("status", "").lower()  # noqa: E731
    approved = [t for t in topics if t["decision"] == "Approved"]
    waiting = [t for t in approved if not t["written"]]
    undecided = [t for t in topics if not t["decision"] and not t["written"]]
    ready = [p for p in posts if status(p) == "ready to publish"]
    published = [p for p in posts if status(p) == "published"]
    attention = [p for p in posts if status(p) == "needs attention"]
    reviewed = [p for p in posts if status(p) == "reviewed"]
    in_progress = [p for p in posts if status(p) in ("draft", "needs attention", "reviewed")]
    dfs_total = sum(r["dataforseo_cost"] or 0 for r in runs if r["kind"] != "run")
    ppx_total = sum(r["perplexity_cost"] or 0 for r in runs if r["kind"] != "run")
    calls_total = sum(r["dataforseo_calls"] or 0 for r in runs if r["kind"] != "run")
    shortlists = sorted({t["shortlist_file"] for t in topics})

    # What you need to do
    todo = []
    for p in ready:
        todo.append(f'Publish <b>{esc(p.get("title"))}</b> using its card in <code>output/posts/</code>, then type <code>/mark-published</code>.')
    for p in attention:
        todo.append(f'<b>{esc(p.get("title"))}</b> didn\'t pass review. Read the "Needs you" list in its review file, fix it with <code>/revise-post</code>, then type <code>/check-post</code>.')
    for p in reviewed:
        todo.append(f'<b>{esc(p.get("title"))}</b> passed review. Type <code>/finish-post</code> to make it ready to publish.')
    if undecided:
        files = sorted({t["shortlist_file"] for t in undecided})
        todo.append(f'Mark approve or reject on {len(undecided)} topic{"s" if len(undecided) != 1 else ""} in ' + ", ".join(f"<code>{esc(f)}</code>" for f in files) + ".")
    if topics and len(waiting) <= 2 and not undecided:
        todo.append(f'Only {len(waiting)} approved topic{"s" if len(waiting) != 1 else ""} left to write. Type <code>/research-topics</code> for more, or let the next scheduled run do it.')
    if not topics:
        todo.append("No topics yet. Type <code>/research-topics</code> to get your first shortlist.")

    h = []
    h.append(f"<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
             f"<title>Blog Agent Dashboard</title><style>{CSS}</style></head><body><div class=\"wrap\">")
    built = datetime.now().strftime("%B %-d, %Y at %-I:%M %p") if sys.platform != "win32" else datetime.now().strftime("%Y-%m-%d %H:%M")
    h.append("<h1>Blog agent dashboard</h1>")
    summary = (f"{len(topics)} topics researched, {len(approved)} approved by you, {len(posts)} posts started, "
               f"{len(ready)} ready to publish and {len(published)} published. Paid data so far: {fmt_money(dfs_total + ppx_total)}.")
    h.append(f'<p class="lede">{esc(summary)} Updated {esc(built)}.</p>')

    if todo:
        h.append('<div class="todo" id="todo"><h3>What you need to do</h3><ol>' + "".join(f"<li>{t}</li>" for t in todo) + "</ol></div>")
    else:
        h.append('<div class="todo clear" id="todo"><h3>What you need to do</h3><p class="note" style="margin:0">Nothing right now. The agent has what it needs.</p></div>')

    # Tiles
    rate = f"{round(100 * len(approved) / len([t for t in topics if t['decision']]))}% of your decisions" if any(t["decision"] for t in topics) else "No decisions yet"
    tiles = [
        ("Topics researched", fmt_int(len(topics)), f"{len(shortlists)} shortlist{'s' if len(shortlists) != 1 else ''}"),
        ("Approved by you", fmt_int(len(approved)), rate),
        ("Approved, not written", fmt_int(len(waiting)), "The writer's queue"),
        ("In progress", fmt_int(len(in_progress)), "Drafts and posts in review"),
        ("Ready to publish", fmt_int(len(ready)), "Waiting for you"),
        ("Published", fmt_int(len(published)), "Live, with a URL"),
        ("Paid data so far", fmt_money(dfs_total + ppx_total), f"DataForSEO {fmt_money(dfs_total)} · Perplexity {fmt_money(ppx_total)}"),
    ]
    h.append('<section class="tiles" id="summary">' + "".join(
        f'<div class="tile"><span class="lbl">{esc(a)}</span><span class="num">{esc(b)}</span><span class="sub">{esc(c)}</span></div>' for a, b, c in tiles
    ) + "</section>")

    # Pipeline and reject reasons
    h.append('<h2 id="pipeline">Where topics are in the pipeline</h2><div class="grid">')
    funnel = [
        ("Researched", len(topics), ""),
        ("Approved", len(approved), ""),
        ("Drafted", len(posts), ""),
        ("Passed review", len([p for p in posts if status(p) in DONE_STATUSES]), ""),
        ("Finished", len([p for p in posts if status(p) in ("ready to publish", "published")]), ""),
        ("Published", len(published), ""),
    ]
    h.append('<div class="card"><h3>From research to published</h3><p class="note">Each stage counts topics and posts that got at least that far. The gap after "Approved" is the writer\'s queue.</p>'
             + (hbars(funnel) if topics or posts else empty("Nothing yet. Type /research-topics to start.")) + "</div>")
    status_counts = {}
    for t in topics:
        status_counts[t["status"]] = status_counts.get(t["status"], 0) + 1
    h.append('<div class="card"><h3>Every topic, by where it is now</h3><p class="note">From your shortlists and the post log.</p>'
             + (hbars(sorted(((k, v, "") for k, v in status_counts.items()), key=lambda x: -x[1])) if topics else empty("No shortlists yet."))
             + "</div></div>")

    # Search Console
    h.append('<h2 id="search">Search Console clicks and impressions</h2>')
    if sc:
        recent, before = sc[-13:], sc[-26:-13]
        h.append('<div class="grid">')
        for key, label in (("clicks", "Clicks"), ("impressions", "Impressions")):
            now_total = sum(r[key] for r in recent)
            prev_total = sum(r[key] for r in before) if before else None
            change = ""
            if prev_total:
                pct = 100 * (now_total - prev_total) / prev_total
                change = f'<div><span class="v">{"+" if pct >= 0 else ""}{pct:.0f}%</span><span class="c">Change</span></div>'
            h.append(f'<div class="card"><h3>{label} from Google, by week</h3><div class="big">'
                     f'<div><span class="v">{fmt_int(now_total)}</span><span class="c">Last 13 weeks</span></div>'
                     + (f'<div><span class="v">{fmt_int(prev_total)}</span><span class="c">13 weeks before</span></div>' if prev_total is not None else "")
                     + change + "</div>" + bars_svg(sc, key, label) + "</div>")
        h.append('</div><p class="note" style="margin-top:10px">Your whole site, from Databox. Darker bars are the last 13 weeks. Point at a bar to see its number. '
                 f'Weeks at each end may be partial. Saved {esc(sc[-1]["week"])} or later; type <code>/blog-dashboard</code> to refresh.</p>')
    else:
        h.append('<div class="card">' + empty("No Search Console numbers yet. Type /blog-dashboard with Databox connected and this section fills in.") + "</div>")

    # Posts
    h.append('<h2 id="posts">Every post</h2><div class="card">')
    if posts:
        writes = {r["draft"]: r for r in runs if r["kind"] == "write" and r["draft"]}
        checks = {}
        for r in runs:
            if r["kind"] == "check" and r["draft"]:
                checks[r["draft"]] = r
        fix_counts = {}
        for f in fixes:
            fix_counts[f"output/drafts/{f['draft']}.md"] = fix_counts.get(f"output/drafts/{f['draft']}.md", 0) + 1
        rows = []
        for p in sorted(posts, key=lambda p: (p.get("date", ""), p.get("post_id", "")), reverse=True):
            fpath = p.get("file", "")
            w = writes.get(fpath)
            c = checks.get(fpath)
            live = p.get("published_url", "")
            rows.append([
                esc(p.get("title")) + (f'<br><a href="{esc(live)}">{esc(live)}</a>' if live.startswith("http") else ""),
                esc(p.get("target_keyword")) or "–",
                f'<span class="nowrap">{esc(p.get("date"))}</span>' if p.get("date") else "–",
                pill(STATUS_LABELS.get(status(p), p.get("status", ""))),
                fmt_int(w["words"]) if w and w["words"] else "–",
                esc(c["rounds"]) if c and c["rounds"] else "–",
                fmt_int(fix_counts.get(fpath)) if fix_counts.get(fpath) else "–",
            ])
        h.append(table(["Post", "Target keyword", "Started", "Status", "Words", "Reviews", "Fixes asked"], rows, numeric=(4, 6)))
    else:
        h.append(empty("No posts yet. Type /write-post to write your first one."))
    h.append("</div>")

    # Topics
    h.append('<h2 id="topics">Every topic researched, and your call</h2><div class="card">')
    if topics:
        h.append('<p class="note">Score is the researcher\'s weighted total. Searches and difficulty come from DataForSEO.</p>')
        rows = []
        for t in sorted(topics, key=lambda t: (t["shortlist"], -t["rank"]), reverse=True):
            rows.append([
                f'<span class="nowrap">{esc(t["shortlist"])}</span>', str(t["rank"]),
                esc(t["title"]) + (f'<br><span class="note">{esc(t["keyword"])}</span>' if t["keyword"] else ""),
                fmt_int(t["searches"]), fmt_int(t["difficulty"]),
                "–" if t["score"] is None else (f'{t["score"]:g}'),
                esc(t["offer"]) or "–", pill(t["decision"]) if t["decision"] else "–",
                esc(t["reason"]) or "–", pill(t["status"]),
            ])
        h.append(table(["Shortlist", "Rank", "Topic", "Searches / mo", "Difficulty", "Score", "Offer", "Your call", "Your reason", "Status"], rows, numeric=(1, 3, 4, 5)))
    else:
        h.append(empty("No shortlists yet. Type /research-topics to get your first one."))
    h.append("</div>")

    # Review fixes
    h.append('<h2 id="quality">What the reviewer asked the writer to fix</h2><div class="stack">')
    if fixes:
        areas = {}
        for f in fixes:
            areas[f["area"]] = areas.get(f["area"], 0) + 1
        h.append('<div class="card"><h3>Fixes by rule area</h3><p class="note">If one area keeps failing, tighten that rule in your context files, or teach the writer with <code>/revise-post</code>.</p>'
                 + hbars(sorted(((k, v, "") for k, v in areas.items()), key=lambda x: -x[1])) + "</div>")
        rows = [[esc(f["draft"]), f'{f["check"]}.{f["review"]}' if f["check"] > 1 else str(f["review"]), esc(f["rule"]) or "–", esc(f["fix"]) or "–", esc(f["who"]) or "–"] for f in fixes]
        h.append('<div class="card"><h3>Every fix</h3><p class="note">Review number is the round within each check.</p>'
                 + table(["Draft", "Review", "Rule", "Fix", "Who"], rows, numeric=(1,)) + "</div>")
    else:
        h.append('<div class="card">' + empty("No fixes yet. They appear after /check-post reviews a draft and finds something to fix.") + "</div>")
    h.append("</div>")

    # Runs and costs
    h.append('<h2 id="runs">Every run, and what it cost</h2><div class="card">')
    if runs:
        h.append(f'<p class="note">{fmt_int(calls_total)} paid DataForSEO calls so far. Full runs list their steps as separate rows, so their cost isn\'t counted twice. '
                 "Claude usage comes from your plan and isn't counted here.</p>")
        rows = []
        for r in reversed(runs):
            full = r["kind"] == "run"
            rows.append([
                f'<span class="nowrap">{esc(r["date"])}</span>', esc(r["step"]), esc(r["result"]) or "–",
                "–" if full or r["dataforseo_calls"] is None else fmt_int(r["dataforseo_calls"]),
                "–" if full else fmt_money(r["dataforseo_cost"]),
                "–" if full else fmt_money(r["perplexity_cost"]),
                f'<code>{esc(r["file"])}</code>',
            ])
        rows.append(["<b>Total</b>", "", "", f"<b>{fmt_int(calls_total)}</b>", f"<b>{fmt_money(dfs_total)}</b>", f"<b>{fmt_money(ppx_total)}</b>", ""])
        h.append(table(["Date", "Step", "Result", "Paid calls", "DataForSEO", "Perplexity", "Log"], rows, numeric=(3, 4, 5)))
    else:
        h.append(empty("No runs yet."))
    h.append("</div>")

    h.append('<footer>Built by <code>tools/build_dashboard.py</code> from your post log, shortlists, run logs, and review files. '
             "Type <code>/blog-dashboard</code> to rebuild it with the latest numbers.</footer></div></body></html>")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("".join(h), encoding="utf-8")
    return {
        "dashboard": str(out_path.relative_to(ROOT)) if out_path.is_relative_to(ROOT) else str(out_path),
        "topics": len(topics), "approved": len(approved), "approved_not_written": len(waiting),
        "waiting_for_decision": len(undecided), "posts": len(posts), "needs_attention": len(attention),
        "ready_to_publish": len(ready), "published": len(published), "runs": len(runs), "fixes": len(fixes),
        "search_console_weeks": len(sc), "dataforseo_cost": round(dfs_total, 4), "perplexity_cost": round(ppx_total, 4),
        "to_do": [re.sub(r"<[^>]+>", "", t) for t in todo],
    }


def main():
    out = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUT
    try:
        summary = build(out)
    except Exception as exc:  # report plainly; nothing half-written matters here
        print(json.dumps({"error": str(exc)}))
        sys.exit(1)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
