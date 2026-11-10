---
name: blog-dashboard
description: Build and open the blog agent dashboard, one page showing what needs the owner's attention, every topic and the owner's approve or reject call, every post and its status, what the reviewer asked the writer to fix, every run and what it cost, and weekly Search Console clicks and impressions from Databox. Saves output/dashboard.html. Use when the owner types /blog-dashboard or asks to see the dashboard, progress, costs, or how the blog agent is doing.
---

# Blog dashboard

Speak in plain English throughout. The owner is a marketing leader, not a developer.

The dashboard is built by `tools/build_dashboard.py` from files already in this project: `post-log.csv`, the shortlists in `output/topics/`, the run logs in `output/logs/`, and the review files in `output/drafts/`. The only thing this command fetches is Search Console numbers from Databox.

## 1. Get the latest files

If this project has a GitHub remote, run `git pull --ff-only` quietly so the dashboard includes the latest scheduled run. If it fails (for example, there are local changes), carry on with the files as they are and mention it in one line at the end.

## 2. Refresh the Search Console numbers

Read `context/settings.md`.

- If the Databox account ID or the Google Search Console data source ID is still TODO, or the Databox tools aren't available, skip this step. If `output/search-console.csv` already exists, the dashboard uses those older numbers. Mention this in one line at the end, with the fix (run `/research-topics` to fill in the Databox settings, or connect Databox at claude.ai → Customize → Connectors and restart Claude Code).
- Otherwise, use the Databox connector with that account and Search Console data source:
  1. Get today's date from Databox's date helper or `date +%F`.
  2. List the data source's metrics and find the ones for **clicks** and **impressions** (whole site, not by page or query).
  3. Load both, by week, for the last 26 weeks (about 180 days), so the dashboard can compare the last 13 weeks with the 13 before. If weekly values aren't offered, load daily values and add them up into weeks starting on Monday.
  4. Save them to `output/search-console.csv`, replacing the old file, with exactly this header and one row per week, oldest first:

     ```
     week,clicks,impressions
     2026-05-04,120,4310
     ```

     `week` is the Monday the week starts on, as YYYY-MM-DD. Numbers have no commas or currency signs.
  If a request times out, try once more. If it still fails, keep the old file and mention it at the end.

These are whole-site totals only. Never save queries, page lists, or anything about clients.

## 3. Build the dashboard

Run:

```
python3 tools/build_dashboard.py
```

It prints a summary. If it prints an `error`, tell the owner in one line what went wrong and stop.

## 4. Open it

On a Mac, run `open output/dashboard.html`. On Windows, run `start output/dashboard.html`. Otherwise, give the owner the file path to open in their browser.

The dashboard and `output/search-console.csv` are git-ignored, because they're rebuilt from the other files each time. Don't commit them.

## 5. Show the summary

In the chat, show in a few short lines:
- The "What you need to do" list from the summary, numbered, or "Nothing right now".
- Posts ready to publish, published, and in progress; approved topics waiting to be written.
- Paid data spend so far (DataForSEO and Perplexity).
- Anything skipped in step 1 or 2, with how to fix it.

Then tell them they can type `/blog-dashboard` any time to rebuild it with the latest numbers.
