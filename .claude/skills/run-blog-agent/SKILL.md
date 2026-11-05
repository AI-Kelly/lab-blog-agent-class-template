---
name: run-blog-agent
description: Run the whole blog agent from start to finish with no questions, the way a scheduled run does. Writes, sources, reviews, and finishes one post from the highest-scoring approved topic; if no approved topics are left, researches new ones for the owner to approve instead. Also finishes any post already marked reviewed, tops up the topic shortlist when approved topics run low, saves a run report, and commits and pushes the results. Use when the owner types /run-blog-agent, when a scheduled task runs the blog agent, or when the owner asks for a full run.
---

# Run the blog agent

This is the command a scheduled run uses, so it **never stops to ask a question**. Nobody may be watching. Where another command would ask the owner something, follow the "Unattended" rule for that step below and note what you decided in the run report.

Speak in plain English in everything you write. The owner is a marketing leader, not a developer.

The steps below reuse the other commands. "Follow `/write-post`" means: read `.claude/skills/write-post/SKILL.md` and carry out its steps, with the changes listed here.

## 1. Start

Get today's date with `date +%F` and note the start time with `date +%H:%M`.

Check what you have to work with. Don't stop for any of these; note each one for the report.
- **Context files:** if `context/icp.md`, `context/offers.md`, or `context/voice-and-style.md` still has TODO lines, the post will be weaker. Carry on.
- **Keys:** the DataForSEO login and password come from `.env` on the owner's computer, or from the `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` environment variables in a scheduled run. The Perplexity key works the same way with `PERPLEXITY_API_KEY`. Check that each one is set without printing it, for example `[ -n "$DATAFORSEO_LOGIN" ] || grep -q '^DATAFORSEO_LOGIN=.' .env 2>/dev/null && echo set`. Missing DataForSEO keys mean no keyword or Google data; a missing Perplexity key means slower sourcing with web search.
- **Databox:** check that the Databox tools are available. If not, research runs without Search Console data.

## 2. Finish posts that already passed review

Read `post-log.csv`. For each row with status `reviewed`, oldest first (at most 3), follow `/finish-post` for that draft, with these changes:
- **Unattended:** skip step 6's question about the blog platform. If `context/settings.md` already has a `## Publishing` section that says yes and a connector for that platform is available, create the draft there as `/finish-post` describes. Never publish.
- Don't show results in the chat or offer to commit; keep them for the report.

## 3. Pick today's topic

Use the same rule as the writer: the highest-scoring approved topic (`[x] approve`) in `output/topics/` that has no "Status: Drafted" line and whose title or target keyword isn't already in `post-log.csv`. On a tie, the newer shortlist wins.

- **An approved topic is left:** go to step 4.
- **None left:** go to step 7 to research new topics, then step 8. Don't write a post from a topic the owner hasn't approved.

## 4. Write the post

Follow `/write-post`, with these changes:
- **Step 1, unattended:** don't offer `/setup-context`. If Country or Language in `context/settings.md` is still TODO, use the values that fit `context/icp.md` for this run only, don't save them, and note it for the report.
- **Step 2:** let the writer pick the topic (don't pass one). If it returns `No topic:`, go to step 7. If its notes say the topic already has a row in `post-log.csv`, skip it, note it, and go to step 7.
- **Step 4, unattended:** don't show the brief or ask. The owner approved the topic, so the brief is approved automatically. In the run log's Brief row, write "Approved automatically (unattended run)".
- **Step 10:** don't show results in the chat or offer to commit; keep them for the report.

If the writer fails (for example, no example posts and no context at all), note why and go to step 7.

## 5. Source and review it

Follow `/check-post` on the draft you just wrote (name it, so it doesn't pick another one), with these changes:
- Run every step as written, including up to 2 fix rounds.
- **Step 8:** don't show results in the chat or offer to commit; keep the result (PASS, or the "Needs you" list) for the report.

## 6. Finish it

- **PASS:** follow `/finish-post` on the same draft, with the same changes as in step 2.
- **Needs attention:** don't finish it. The "Needs you" list goes at the top of the report, so the owner sees what to fix. They fix it by hand or with `/revise-post`, then run `/check-post` and `/finish-post` themselves.

## 7. Top up the topic shortlist

Research new topics if either:
- there were no approved topics left in step 3, or
- after today's post, 2 or fewer approved topics are left unwritten **and** no shortlist in `output/topics/` is dated in the last 7 days.

Otherwise skip this step.

Also skip it if the newest shortlist is less than 7 days old and still has topics with no decision marked. The owner hasn't finished choosing yet, and another shortlist would only pile up. Note "Waiting for your decisions on <shortlist file>" for the report, and put "Mark approve or reject on <shortlist file>" in its "What you need to do" list.

To research, follow `/research-topics`, with these changes:
- **Step 1, unattended:** don't ask about TODO settings. If Blog URL or the Databox lines are still TODO, run without them. Use Country and Language values that fit `context/icp.md` for this run only, without saving them. Note every gap for the report.
- **Step 2, unattended:** don't offer to create `my-sources.md`.
- **Step 7:** don't show results in the chat or offer to commit; keep the top 3 for the report.

The new shortlist waits for the owner to mark approve or reject. The next run writes from it.

## 8. Save the run report

Save to `output/logs/YYYY-MM-DD-run.md`. If that file already exists, add `-2`, `-3`, and so on before `.md`.

Lead with what the owner has to do, if anything. Keep it short; the other logs from this run hold the details.

```
# Blog agent run: <date>

**Started:** <time>  **Finished:** <time from `date +%H:%M`>
**Result:** <one line, for example "1 post ready to publish", "Post needs your attention", or "No approved topics: new shortlist ready for your decisions">

## What you need to do
<numbered list, or "Nothing. Have a good day.">
<for example: publish the ready post using its card, then type /mark-published; fix the "Needs you" items below; mark approve or reject on the new shortlist; add the missing key or connector named below>

## Ready to publish
<for each post finished in this run: title, output/posts/<file>.html, its card, and the blog platform draft link if one was made. Or "None">

## Needs you
<the "Needs you" list from /check-post, if the review didn't pass. Or "Nothing">

## New topics
<the top 3 from the new shortlist and its file, if research ran. Or "No research this run: <n> approved topics still waiting">

## Steps

| Step | What happened |
|---|---|
| Setup | <context files, keys, and Databox: OK, or what's missing> |
| Finished earlier posts | <titles, or "None waiting"> |
| Topic | <title, shortlist and rank; or "None approved"> |
| Write | <draft file, word count; or skipped and why> |
| Source and review | <PASS or NEEDS ATTENTION, review rounds; or skipped> |
| Finish | <post file; or skipped and why> |
| Research | <shortlist file; or skipped and why> |
| Decisions made without asking | <each default used, for example "Brief approved automatically", or "None"> |
| Cost | <paid DataForSEO calls and cost, Perplexity calls and cost, from the other logs> |

## Logs from this run
<the path of every log saved in output/logs/ during this run>
```

Never put key values, quotes from meetings or emails, or client names in the report.

## 9. Save and push

Save everything the run made to GitHub, so the owner sees it on any computer:

```
git add output post-log.csv context/settings.md
git commit -m "Blog agent run <date>: <the Result line>"
git push origin "$(git branch --show-current)"
```

Only add those paths. Never add `.env` or any file holding a key. If `context/settings.md` didn't change, git skips it. Push to the branch you're on (the repository's main branch in a scheduled run), not a new branch, so the owner finds the files where they expect them.

If the push is rejected because GitHub has newer changes (for example, the owner pushed while the run was going), run `git pull --rebase origin "$(git branch --show-current)"` and push again. If it still fails, say so in the summary below; the work is in this run's session and isn't lost.

## 10. Summary

End with a short plain-English summary: the Result line, the "What you need to do" list, and where the run report is. This is what the owner sees first when they open the run.
