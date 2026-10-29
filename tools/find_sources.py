#!/usr/bin/env python3
"""Find candidate sources for every [SOURCE NEEDED: ...] mark in a draft.

Used by the source-finder agent during /check-post. For each mark it asks
Perplexity's search model ("sonar", through the Agent API) for up to 3
candidate sources and the exact sentence on each page that supports the
claim. All claims are searched at the same time.

Standard library only, so there is nothing to install.

    python3 tools/find_sources.py output/drafts/<draft>.md
    python3 tools/find_sources.py output/drafts/<draft>.md --exclude competitor.com,other.com
    python3 tools/find_sources.py --test        # one tiny call to check the key

Prints JSON to stdout. Reads PERPLEXITY_API_KEY from .env (or the
environment) and never prints it. Exit codes: 0 ok, 2 no key, 1 error.
"""

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

API_URL = "https://api.perplexity.ai/v1/agent"
MODEL = "perplexity/sonar"
MAX_CANDIDATES = 3
MAX_PARALLEL = 10
# New Perplexity accounts (Tier 0) may start 1 Agent API request per second.
# Requests still run at the same time; only their starts are spaced out.
START_GAP_SECONDS = 1.1
MAX_RETRIES = 3
TIMEOUT_SECONDS = 120

# Never useful as a source. Competitor domains passed with --exclude are added.
# Perplexity allows at most 20 domains in one filter.
DEFAULT_EXCLUDE = [
    "reddit.com", "quora.com", "linkedin.com", "youtube.com", "facebook.com",
    "x.com", "twitter.com", "medium.com", "pinterest.com", "tiktok.com",
    "instagram.com",
]
MAX_DOMAIN_FILTER = 20

MARK = re.compile(r"\[SOURCE NEEDED:?\s*([^\]]*)\]")

INSTRUCTIONS = """You find sources for one factual claim in a business blog post.

Search the web and return up to 3 pages that state the claim, best first.

Prefer, in this order:
1. Original research and data: studies, surveys with a stated method, government and official statistics, industry bodies.
2. Official documentation from the organization the claim is about.
3. Well-known publications with editorial standards reporting their own research.

Avoid vendor blogs selling to the same buyers, "top 10" or "best tools" lists, content farms, AI-written roundups, forums, and social posts. If an article quotes a study, return the study itself when you can find it.
For numbers that change over time, prefer data from the last three years.

For each page, copy the one or two sentences from that page that support the claim, word for word, exactly as they appear in the search results. Never paraphrase, round, or combine them. Only return pages that appeared in your search results. If the page says something different from the claim (another number, group, place, or year), still return it and copy what it actually says.

If nothing solid supports the claim, return an empty list. Never invent a page, a URL, or a sentence."""

SCHEMA = {
    "type": "object",
    "properties": {
        "candidates": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "url": {"type": "string"},
                    "title": {"type": "string"},
                    "publisher": {"type": "string"},
                    "date": {"type": "string"},
                    "supporting_sentence": {"type": "string"},
                },
                "required": ["url", "title", "publisher", "date", "supporting_sentence"],
                "additionalProperties": False,
            },
        },
        "note": {"type": "string"},
    },
    "required": ["candidates", "note"],
    "additionalProperties": False,
}


def load_key():
    """Return the API key from the environment or the project's .env."""
    key = os.environ.get("PERPLEXITY_API_KEY", "").strip()
    if key:
        return key
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if not env_file.exists():
        return ""
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[len("export "):]
        if line.startswith("PERPLEXITY_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def find_claims(text):
    """Return one entry per mark: what it asks for and the sentence it sits in."""
    claims = []
    for number, match in enumerate(MARK.finditer(text), start=1):
        line_start = text.rfind("\n", 0, match.start()) + 1
        line_end = text.find("\n", match.end())
        if line_end == -1:
            line_end = len(text)

        # Sentence start: the last ". ", "? " or "! " before the mark on this line.
        start = line_start
        for boundary in re.finditer(r"[.!?][\"')\]]?\s+", text[line_start:match.start()]):
            start = line_start + boundary.end()
        # Sentence end: the first ".", "?" or "!" after the mark that ends a sentence.
        rest = text[match.end():line_end]
        end_match = re.search(r"[.!?](?=[\"')\]]?(\s|$))", rest)
        end = match.end() + end_match.end() if end_match else line_end

        sentence = text[start:end].strip()
        sentence = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", sentence)  # list markers
        clean = MARK.sub("", sentence)
        clean = re.sub(r"\s+([.,;:!?])", r"\1", re.sub(r"\s{2,}", " ", clean)).strip()
        claims.append({
            "number": number,
            "mark": match.group(1).strip(),
            "sentence": sentence,
            "claim": clean,
        })
    return claims


def normalize_url(url):
    url = url.strip().lower().split("#", 1)[0]
    url = re.sub(r"^https?://", "", url)
    url = re.sub(r"^www\.", "", url)
    return url.rstrip("/")


def post(body, key):
    """POST to the Agent API. Returns (status code, parsed JSON or text, retry-after)."""
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.status, json.loads(response.read().decode("utf-8")), None
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw)
        except ValueError:
            payload = raw[:300]
        return error.code, payload, error.headers.get("Retry-After")
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        return 0, str(getattr(error, "reason", error)), None


def error_message(status, payload):
    if isinstance(payload, dict):
        detail = payload.get("error", payload)
        if isinstance(detail, dict):
            detail = detail.get("message") or detail.get("type") or json.dumps(detail)
        payload = detail
    if status == 401:
        return "Perplexity rejected the key (401). Check PERPLEXITY_API_KEY in .env."
    if status == 402:
        return "Perplexity says the account is out of credit (402)."
    if status == 0:
        return "Couldn't reach Perplexity: " + str(payload)
    return "Perplexity returned HTTP {}: {}".format(status, str(payload)[:300])


class Counter:
    """Counts calls and cost across threads, and spaces out request starts."""

    def __init__(self):
        self.lock = threading.Lock()
        self.calls = 0
        self.cost = 0.0
        self.next_start = 0.0

    def wait_turn(self):
        with self.lock:
            now = time.monotonic()
            start = max(now, self.next_start)
            self.next_start = start + START_GAP_SECONDS
            self.calls += 1
        time.sleep(max(0.0, start - now))

    def add_cost(self, response):
        try:
            value = float(response["usage"]["cost"]["total_cost"])
        except (KeyError, TypeError, ValueError):
            return
        with self.lock:
            self.cost += value


def call_with_retries(body, key, counter):
    for attempt in range(MAX_RETRIES + 1):
        counter.wait_turn()
        status, payload, retry_after = post(body, key)
        if status == 200:
            counter.add_cost(payload)
            return payload, None
        retryable = status in (0, 429, 500, 502, 503, 504)
        if status in (401, 402, 403) or not retryable or attempt == MAX_RETRIES:
            return None, (status, payload)
        try:
            wait = float(retry_after) if retry_after else 2.0 * (attempt + 1)
        except ValueError:
            wait = 2.0 * (attempt + 1)
        time.sleep(min(wait, 30.0))
    return None, (0, "No response")


def response_parts(response):
    """Return (answer text, search results) from an Agent API response."""
    text = response.get("output_text") or ""
    results = []
    for item in response.get("output") or []:
        if item.get("type") == "search_results":
            results.extend(item.get("results") or [])
        elif item.get("type") == "message" and not text:
            for part in item.get("content") or []:
                if part.get("type") == "output_text":
                    text += part.get("text", "")
    return text, results


def parse_answer(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except ValueError:
        found = re.search(r"\{.*\}", text, re.S)
        if found:
            try:
                return json.loads(found.group(0))
            except ValueError:
                pass
    return None


def search_claim(claim, key, exclude, counter):
    body = {
        "model": MODEL,
        "instructions": INSTRUCTIONS,
        "input": (
            "Claim to source: {claim}\n"
            "What the writer needs: {mark}\n"
            "Today's date: {today}\n"
            "Return JSON with up to {n} candidates, best first."
        ).format(claim=claim["claim"], mark=claim["mark"] or "a source for this claim",
                 today=date.today().isoformat(), n=MAX_CANDIDATES),
        "tools": [{
            "type": "web_search",
            "max_results": 8,
            "max_tokens_per_page": 1500,
            "filters": {"search_domain_filter": ["-" + d for d in exclude]},
        }],
        "max_steps": 2,
        "max_output_tokens": 1500,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "claim_sources", "schema": SCHEMA},
        },
    }
    result = {
        "number": claim["number"],
        "mark": claim["mark"],
        "claim": claim["claim"],
        "sentence_in_draft": claim["sentence"],
        "candidates": [],
        "dropped": 0,
        "note": "",
        "error": None,
    }

    response, failure = call_with_retries(body, key, counter)
    if failure:
        result["error"] = error_message(*failure)
        return result

    text, search_results = response_parts(response)
    answer = parse_answer(text)
    if not isinstance(answer, dict):
        result["error"] = "Perplexity's answer wasn't in the expected format."
        return result
    result["note"] = str(answer.get("note") or "")

    seen = {normalize_url(r.get("url", "")): r for r in search_results if r.get("url")}
    for candidate in answer.get("candidates") or []:
        url = str(candidate.get("url") or "").strip()
        match = seen.get(normalize_url(url))
        host = normalize_url(url).split("/", 1)[0]
        is_excluded = any(host == d or host.endswith("." + d) for d in exclude)
        # Guard against made-up links: keep only pages Perplexity actually found.
        if not url or match is None or is_excluded:
            result["dropped"] += 1
            continue
        sentence = str(candidate.get("supporting_sentence") or "").strip()
        snippet = match.get("snippet") or ""
        result["candidates"].append({
            "url": match.get("url") or url,
            "title": match.get("title") or candidate.get("title") or "",
            "publisher": candidate.get("publisher") or "",
            "date": match.get("date") or candidate.get("date") or "",
            "supporting_sentence": sentence,
            "sentence_in_search_snippet": bool(sentence) and sentence[:80] in snippet,
        })
        if len(result["candidates"]) == MAX_CANDIDATES:
            break
    return result


def build_exclude(extra):
    domains = []
    for domain in DEFAULT_EXCLUDE + [d for d in (extra or "").split(",")]:
        domain = re.sub(r"^https?://", "", domain.strip().lower())
        domain = re.sub(r"^www\.", "", domain).split("/", 1)[0]
        if domain and domain not in domains:
            domains.append(domain)
    # Keep the owner's competitors first if the list is too long.
    extras = [d for d in domains if d not in DEFAULT_EXCLUDE]
    defaults = [d for d in domains if d in DEFAULT_EXCLUDE]
    return (extras + defaults)[:MAX_DOMAIN_FILTER]


def run_test(key):
    counter = Counter()
    body = {"model": MODEL, "input": "Reply with the single word OK.", "max_output_tokens": 5}
    response, failure = call_with_retries(body, key, counter)
    if failure:
        return {"status": "error", "message": error_message(*failure), "calls_made": counter.calls}
    return {"status": "ok", "message": "Perplexity key works.", "calls_made": counter.calls,
            "cost_usd": round(counter.cost, 4)}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("draft", nargs="?", help="path to the draft, e.g. output/drafts/<draft>.md")
    parser.add_argument("--exclude", default="", help="comma-separated competitor domains to skip")
    parser.add_argument("--test", action="store_true", help="make one tiny call to check the key")
    args = parser.parse_args()

    key = load_key()
    if not key:
        print(json.dumps({
            "status": "no_key",
            "message": "No PERPLEXITY_API_KEY in .env. Use web search instead.",
            "calls_made": 0,
        }, indent=2))
        return 2

    if args.test:
        result = run_test(key)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "ok" else 1

    if not args.draft:
        parser.error("give the draft's path, or --test")
    draft = Path(args.draft)
    if not draft.exists():
        print(json.dumps({"status": "error", "message": "Draft not found: " + str(draft),
                          "calls_made": 0}, indent=2))
        return 1

    claims = find_claims(draft.read_text(encoding="utf-8"))
    exclude = build_exclude(args.exclude)
    counter = Counter()
    started = time.monotonic()
    if claims:
        with ThreadPoolExecutor(max_workers=min(MAX_PARALLEL, len(claims))) as pool:
            results = list(pool.map(lambda c: search_claim(c, key, exclude, counter), claims))
    else:
        results = []

    failed = [r for r in results if r["error"]]
    status = "ok"
    if results and len(failed) == len(results):
        status = "error"
    elif failed:
        status = "partial"
    output = {
        "status": status,
        "draft": str(draft),
        "claims_found": len(claims),
        "calls_made": counter.calls,
        "cost_usd": round(counter.cost, 4),
        "seconds": round(time.monotonic() - started, 1),
        "excluded_domains": exclude,
        "claims": results,
    }
    if status == "error":
        output["message"] = failed[0]["error"]
    print(json.dumps(output, indent=2, ensure_ascii=False))
    print("Perplexity calls made: {}".format(counter.calls), file=sys.stderr)
    return 1 if status == "error" else 0


if __name__ == "__main__":
    sys.exit(main())
