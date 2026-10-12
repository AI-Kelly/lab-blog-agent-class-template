---
name: research-topics
description: Find and rank bottom-of-the-funnel blog topics. Fills in any missing settings, runs the topic-researcher agent, saves a 10-topic shortlist with approve and reject boxes to output/topics/, saves a run log to output/logs/, and shows the top 3. Use when the owner types /research-topics or asks for new blog topic ideas.
---

# Research topics

Speak in plain English throughout. The owner is a marketing leader, not a developer.

## 1. Fill in missing settings

Read `context/settings.md`. If no TODO lines remain, go to step 2. Otherwise, ask the owner only about the lines still marked TODO, a couple of questions at a time:

- **Blog URL:** ask for the address of the page that lists their posts.
- **Databox account ID:** use the Databox connector to list the accounts they can see.
  - If there's one account, show its name and ask them to confirm it's theirs.
  - If there's more than one, list them by name and ask which one is theirs. Agencies and consultants often see client accounts too, so never guess.
  - If the Databox tools aren't available, tell them to connect Databox at claude.ai → Customize → Connectors and restart Claude Code. Leave the Databox lines as TODO and carry on; the research will run without Search Console data.
- **Search Console and GA4 data source IDs:** list the data sources in the chosen account. Fill in the Google Search Console and Google Analytics 4 IDs yourself. Ask only if there's more than one of either, or if one is missing. If one is missing, tell them to connect it in Databox.
- **Country and language:** suggest values based on `context/icp.md` and ask them to confirm.

Save each answer in `context/settings.md`, replacing its TODO. Don't change any other part of the file. Then show the finished settings in a short summary.

If the "Maximum paid DataForSEO calls per run" line is still 3, mention in one sentence that they can change it in that file.

## 2. Check for my-sources.md

If `my-sources.md` isn't in the main folder, tell the owner in one or two sentences: this file lists where their meeting notes and emails live, and the researcher uses it to find the questions buyers really ask. Offer to create it now.

- If they say yes, ask which tools hold their meeting notes and emails (for example, a meeting recorder, Gmail, Google Drive, or Airtable), which folders or labels to look in, and how far back to read (suggest the last 30 days). Save their answers to `my-sources.md` as a short list. Tool names, folders, and labels only, never content. Remind them that each tool needs to be connected at claude.ai → Customize → Connectors.
- If they say no, carry on. The research runs without meeting and email themes.

## 3. Run the research

Tell the owner the research is starting and usually takes a few minutes.

Run the `topic-researcher` agent. Tell it today's date. It returns a **Shortlist** and a **Run record**.

## 4. Check for private details

Before saving anything, read the shortlist and run record. If any line contains a client's name, a person's name, a quote from a meeting or email, or a private deal detail, rewrite it as a general theme. These files are saved in the repository.

## 5. Save the shortlist

Get today's date with `date +%F` and save to `output/topics/YYYY-MM-DD-topics.md`. If that file already exists, add `-2`, `-3`, and so on before `.md`. Never overwrite an earlier shortlist.

Use this layout:

```
# Topic shortlist: <date>

To choose topics, put an x in a box, like [x] approve, and add a short reason. Your reasons teach the researcher what you want, so the next shortlist gets better.

<each topic from the agent's shortlist, in order, exactly as returned, with this line under each one:>

Decision: [ ] approve [ ] reject. Reason:
```

## 6. Save the run log

Save to `output/logs/YYYY-MM-DD-research.md` with the same date and suffix as the shortlist.

Find the most recent earlier file in `output/logs/` that ends in `-research.md`. Compare each step of this run with that one. A step "ran the same way" if it used the same source, the same settings, and the same method (the same Databox account and data source, the same DataForSEO endpoints, country, and language, and the same meeting and email tools). The amount of data can differ. If there's no earlier log, write "First run" in the comparison column.

Use this layout:

```
# Research run: <date>

**Shortlist:** output/topics/<file name>
**Paid DataForSEO calls:** <n> of <limit>
**Estimated cost:** $<total from the run record>

## Steps

| Step | What happened | Same as last run? |
|---|---|---|
| Context files | <files read, any TODOs> | <Yes / No: what changed / First run> |
| Earlier shortlists and decisions | <counts, what was learned> | |
| Blog posts already covered | <count and source> | |
| Databox: Search Console | <account, data source, date range, queries and pages pulled, any timeouts and retries> | |
| Search Console position | <metric name used, or "Not available: winnable scored from keyword difficulty only"> | |
| Meetings and emails | <tools, items read, themes found> | |
| DataForSEO free check | <OK or the problem> | |
| DataForSEO paid calls | <each call: endpoint, keywords sent, country, language> | |
| Keyword ideas | <seed phrases, ideas returned and kept; "off-topic: results not used"; or skipped and why> | |
| Scoring | <candidates scored, topics kept> | |

## Skipped or failed
<from the run record, or "Nothing">
```

Never put key values, quotes, or client names in the log.

## 7. Show the results

In the chat, show:
- The top 3 topics: title, target keyword, monthly searches, weighted total, and the one-line reason.
- One sentence on what data was used, and anything that was skipped, with how to fix it. For example, if position data wasn't available, say that "winnable" was scored from keyword difficulty only.
- Paid calls made and the estimated cost.
- Where the full shortlist is saved, and a reminder to mark approve or reject on each topic.

Then offer to commit and push the new files.
