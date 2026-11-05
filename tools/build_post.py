#!/usr/bin/env python3
"""Turn a reviewed blog post draft (Markdown) into finished HTML.

Used by /finish-post. It does the same job every time, so it's code, not AI:
converts the draft to clean HTML, builds the FAQPage schema from the FAQ
section, fills in templates/post.html, and checks for leftovers such as
[SOURCE NEEDED] marks.

Usage:
    python3 tools/build_post.py <draft.md> <output.html> [--keep-title]

By default the title (the # line) is left out of the HTML, because most blog
editors have a separate title field. --keep-title puts it in as an <h1>.

Prints a JSON summary to stdout: title, answer, TL;DR, word count, headings,
FAQ questions, links, and warnings. Standard Python only.
Exit codes: 0 built, 1 error (nothing written).
"""

import html
import json
import re
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "post.html"

FAQ_HEADING = re.compile(r"^(faq|faqs|frequently asked questions?)\b", re.I)
LINK = re.compile(r"\[([^\]]+)\]\((\S+?)(?:\s+\"[^\"]*\")?\)")
LIST_ITEM_OL = re.compile(r"^\s*\d+[.)]\s+(.*)$")
LIST_ITEM_UL = re.compile(r"^\s*[-*+]\s+(.*)$")
TABLE_DIVIDER = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def inline(text):
    """Convert inline Markdown (links, bold, italics, code) to HTML."""
    saved = []

    def keep(fragment):
        saved.append(fragment)
        return f"\x00{len(saved) - 1}\x00"

    # Inline code first, so nothing inside it is touched.
    text = re.sub(r"`([^`]+)`", lambda m: keep(f"<code>{html.escape(m.group(1))}</code>"), text)

    def link(m):
        label, url = m.group(1), m.group(2)
        return keep(f'<a href="{html.escape(url, quote=True)}">{inline(label)}</a>')

    text = LINK.sub(link, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: saved[int(m.group(1))], text)


def plain(text):
    """Inline Markdown to plain text (for schema, meta, and counts)."""
    text = LINK.sub(lambda m: m.group(1), text)
    text = re.sub(r"(\*\*|__|`)", "", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in line.split("|")]


def parse(markdown):
    """Split the draft into blocks: (kind, data)."""
    lines = markdown.replace("\r\n", "\n").split("\n")
    blocks, i = [], 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            if stripped.startswith("<!--"):
                while i < len(lines) and "-->" not in lines[i]:
                    i += 1
            i += 1
            continue
        heading = re.match(r"^(#{1,4})\s+(.*?)\s*#*\s*$", stripped)
        if heading:
            blocks.append(("h", (len(heading.group(1)), heading.group(2))))
            i += 1
            continue
        if re.match(r"^(-{3,}|\*{3,}|_{3,})$", stripped):
            blocks.append(("hr", None))
            i += 1
            continue
        if "|" in stripped and i + 1 < len(lines) and TABLE_DIVIDER.match(lines[i + 1]):
            header = split_row(stripped)
            rows = []
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            blocks.append(("table", (header, rows)))
            continue
        for kind, pattern in (("ol", LIST_ITEM_OL), ("ul", LIST_ITEM_UL)):
            if pattern.match(line):
                items = []
                while i < len(lines) and lines[i].strip():
                    m = pattern.match(lines[i])
                    if m:
                        items.append(m.group(1))
                    elif items:
                        items[-1] += " " + lines[i].strip()
                    i += 1
                blocks.append((kind, items))
                break
        else:
            if stripped.startswith(">"):
                quote = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote.append(lines[i].strip().lstrip(">").strip())
                    i += 1
                blocks.append(("quote", " ".join(quote)))
                continue
            para = []
            while i < len(lines) and lines[i].strip():
                nxt = lines[i]
                if para and (re.match(r"^#{1,4}\s", nxt.strip()) or LIST_ITEM_OL.match(nxt)
                             or LIST_ITEM_UL.match(nxt) or nxt.strip().startswith(">")):
                    break
                para.append(nxt.strip())
                i += 1
            blocks.append(("p", " ".join(para)))
    return blocks


def render(block):
    kind, data = block
    if kind == "h":
        level, text = data
        return f"<h{level}>{inline(text)}</h{level}>"
    if kind == "p":
        return f"<p>{inline(data)}</p>"
    if kind in ("ol", "ul"):
        items = "\n".join(f"  <li>{inline(item)}</li>" for item in data)
        return f"<{kind}>\n{items}\n</{kind}>"
    if kind == "quote":
        return f"<blockquote><p>{inline(data)}</p></blockquote>"
    if kind == "hr":
        return "<hr>"
    if kind == "table":
        header, rows = data
        head = "".join(f"<th>{inline(c)}</th>" for c in header)
        body = "\n".join(
            "    <tr>" + "".join(f"<td>{inline(c)}</td>" for c in row) + "</tr>" for row in rows)
        return f"<table>\n  <thead><tr>{head}</tr></thead>\n  <tbody>\n{body}\n  </tbody>\n</table>"
    return ""


def build(draft_path, out_path, keep_title=False):
    markdown = Path(draft_path).read_text(encoding="utf-8")
    blocks = parse(markdown)
    warnings = []

    title = next((d[1] for k, d in blocks if k == "h" and d[0] == 1), None)
    if not title:
        raise ValueError("The draft has no title line starting with '# '.")
    if sum(1 for k, d in blocks if k == "h" and d[0] == 1) > 1:
        warnings.append("More than one '# ' title line; only the first is used as the title.")

    body_blocks = []
    seen_title = False
    for block in blocks:
        if block[0] == "h" and block[1][0] == 1 and not seen_title:
            seen_title = True
            if keep_title:
                body_blocks.append(block)
            continue
        body_blocks.append(block)

    paragraphs = [d for k, d in body_blocks if k == "p"]
    answer = plain(paragraphs[0]) if paragraphs else ""
    tldr = next((plain(re.sub(r"^\*\*TL;?DR:?\*\*:?", "", p, flags=re.I)) for p in paragraphs
                 if re.match(r"^\*\*TL;?DR", p, re.I)), "")
    if not tldr:
        warnings.append("No TL;DR line found.")

    # FAQ: the H2 that looks like an FAQ heading, with H3 questions under it.
    faq, in_faq, current = [], False, None
    for kind, data in body_blocks:
        if kind == "h" and data[0] == 2:
            in_faq = bool(FAQ_HEADING.match(plain(data[1])))
            current = None
            continue
        if not in_faq:
            continue
        if kind == "h" and data[0] >= 3:
            current = {"question": plain(data[1]), "answer": []}
            faq.append(current)
        elif current is not None and kind in ("p", "ol", "ul", "quote"):
            text = data if isinstance(data, str) else " ".join(data)
            current["answer"].append(plain(text))
    for item in faq:
        item["answer"] = " ".join(item["answer"]).strip()
        if not item["answer"]:
            warnings.append(f"FAQ question has no answer: {item['question']}")
    if not faq:
        warnings.append("No FAQ section found (an H2 named 'Frequently asked questions' or 'FAQ' with H3 questions), so no FAQ schema was built.")
    elif not 3 <= len(faq) <= 6:
        warnings.append(f"The FAQ has {len(faq)} questions; the post structure asks for 3 to 6.")

    leftovers = {
        "[SOURCE NEEDED] marks": len(re.findall(r"\[SOURCE NEEDED", markdown)),
        "TODO marks": len(re.findall(r"\bTODO\b", markdown)),
        "empty links": len(re.findall(r"\]\(\s*\)", markdown)),
    }
    for name, count in leftovers.items():
        if count:
            warnings.append(f"{count} {name} left in the draft.")

    links = [m.group(2) for m in LINK.finditer(markdown)]

    article = "\n\n".join(render(b) for b in body_blocks)
    schema = ""
    if faq:
        schema_data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q["question"],
                 "acceptedAnswer": {"@type": "Answer", "text": q["answer"]}}
                for q in faq
            ],
        }
        schema = json.dumps(schema_data, indent=2, ensure_ascii=False).replace("</", "<\\/")
        schema = f'<script type="application/ld+json">\n{schema}\n</script>'

    template = TEMPLATE.read_text(encoding="utf-8") if TEMPLATE.exists() else "{{ARTICLE_HTML}}\n\n{{FAQ_SCHEMA}}\n"
    if "{{ARTICLE_HTML}}" not in template:
        raise ValueError("templates/post.html has no {{ARTICLE_HTML}} placeholder. Get the latest template files.")
    output = (template.replace("{{TITLE}}", html.escape(title, quote=False))
              .replace("{{ARTICLE_HTML}}", article)
              .replace("{{FAQ_SCHEMA}}", schema))
    # Drop the template's own instruction comment at the top.
    output = re.sub(r"^\s*<!--.*?-->\s*", "", output, count=1, flags=re.S)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(output.rstrip() + "\n", encoding="utf-8")

    body_text = " ".join(plain(d if isinstance(d, str) else " ".join(d))
                         for k, d in body_blocks if k in ("p", "ol", "ul", "quote"))
    return {
        "status": "ok",
        "output": str(out_path),
        "title": plain(title),
        "title_length": len(plain(title)),
        "answer": answer,
        "tldr": tldr,
        "word_count": len(body_text.split()),
        "headings": [plain(d[1]) for k, d in body_blocks if k == "h" and d[0] == 2],
        "faq_questions": [q["question"] for q in faq],
        "faq_schema": bool(faq),
        "links": links,
        "warnings": warnings,
    }


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 2:
        print(json.dumps({"status": "error", "message": "Usage: build_post.py <draft.md> <output.html> [--keep-title]"}))
        return 1
    try:
        result = build(args[0], args[1], keep_title="--keep-title" in argv)
    except (OSError, ValueError) as err:
        print(json.dumps({"status": "error", "message": str(err)}))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
