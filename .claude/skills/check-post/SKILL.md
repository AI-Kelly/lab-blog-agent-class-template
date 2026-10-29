---
name: check-post
description: Source and review one blog post draft. Takes an optional draft name; otherwise uses the newest draft that hasn't been reviewed or was changed since its last review. Runs the source-finder agent to fill every [SOURCE NEEDED] mark and add links to the owner's own posts, then the independent reviewer agent. On FAIL, has the writer fix only the listed items and re-checks only those items and the lines that changed, for at most 2 fix rounds. Saves a sources file and a review file to output/drafts/, sets the post's status in post-log.csv, saves a run log, and shows PASS or a "Needs you" list. Use when the owner types /check-post or asks for a draft to be sourced, fact-checked, or reviewed.
---

# Check a post

Speak in plain English throughout. The owner is a marketing leader, not a developer.

The owner may name a draft after the command, for example `/check-post how-to-choose-a-payroll-provider` or `/check-post 2026-10-29-how-to-choose-a-payroll-provider.md`. If they don't, use the newest draft that hasn't been reviewed, or was changed since its last review.

## 1. Find the draft

Get today's date with `date +%F`.

Drafts are the files in `output/drafts/` ending in `.md` that don't end in `-brief.md`, `-sources.md`, or `-review.md`, and aren't the README.

- **If the owner named one,** find the draft whose file name contains what they typed. If more than one matches, list them and ask which. If none match, list the drafts and ask.
- **Otherwise,** use the newest draft (by the date at the start of its file name, then by the `-2`, `-3` suffix) that needs checking. A draft needs checking if either:
  - it has no review file yet (the same name ending in `-review.md`), or
  - it was changed after its last review. Run `git hash-object output/drafts/<draft file>` to get the draft's fingerprint, and compare it with the **last** "Draft fingerprint" line in its review file. If they differ, or the review file has no fingerprint line, the draft was changed.

  Say which reason applies in the one-line message below, for example "changed since its last review on <date>".

If no draft needs checking, say so. Suggest `/write-post` for a new draft, or `/check-post <draft name>` to check one again anyway. Stop here.

Tell the owner which draft you're checking in one line, and that sourcing and review usually take a couple of minutes (longer without a Perplexity key).

In the steps below, `<draft>` means the draft's file name without `.md`, for example `2026-10-29-how-to-choose-a-payroll-provider`.

If `context/voice-and-style.md` or `context/offers.md` still has TODO lines, tell the owner in one sentence that the reviewer skips any rule still marked TODO, so the check is less thorough until they run `/setup-context`. Carry on.

## 2. Find sources

Count the marks with `grep -o "\[SOURCE NEEDED" output/drafts/<draft>.md | wc -l`.

If there are no marks and `output/drafts/<draft>-sources.md` already exists, the draft has been sourced before. Skip to step 3 and note "Source Finder: skipped, already sourced" for the log.

Otherwise, run the `source-finder` agent. Tell it today's date and the draft's path. It runs `tools/find_sources.py` to get candidate sources from Perplexity (or uses web search if there's no key), then confirms each one on the page. It returns a **Draft**, a **Sources file**, and a **Source record**. Keep the source record for the run log.

- Save the draft over `output/drafts/<draft>.md`.
- Save the sources file to `output/drafts/<draft>-sources.md`.
- Check both for private details: if a line contains a client's name, a person's name from the owner's meetings or emails, or a private deal detail, rewrite it as a general theme. These files are saved in the repository.

Count the marks again. If any are left, note them; the reviewer will flag them.

## 3. Review

Run the `reviewer` agent for a **full review**. Tell it **only** the path of the draft, the path of its sources file, and today's date. Don't pass the brief, the Source Finder's record, the writer's notes, earlier review results, or your own opinion of the draft. The reviewer is independent, and it only stays independent if it sees nothing but the files its instructions name.

It returns a **Result** (PASS or FAIL), a numbered list of **Fixes** (each marked Writer or Owner), a **Checks** table, and **Optional suggestions**.

Keep each round's full result for the review file. This first review is "Review 1".

- **PASS:** go to step 5.
- **FAIL:** go to step 4.

## 4. Fix and review again (at most 2 rounds)

If every fix is marked **Owner**, there's nothing the writer can do. Skip to step 5.

Otherwise, first save a copy of the draft as it is now, outside the project, so you can see what the fix round changes:

```
cp output/drafts/<draft>.md "${TMPDIR:-/tmp}/<draft>-before-fix.md"
```

Then run the `writer` agent in **fix mode**. Tell it today's date, the draft's path, and the fixes marked **Writer**, copied exactly as the reviewer wrote them, with their numbers. Don't pass the Owner fixes, the checks table, or the optional suggestions. It returns a **Draft** and a **Fix record**.

- Save the draft over `output/drafts/<draft>.md`.
- Check it for private details the same way as in step 2.
- Keep the fix record: what was changed for each fix, and any fix the writer couldn't make.

If the fixed draft has any new `[SOURCE NEEDED` marks, run the `source-finder` agent again on the draft, the same way as in step 2. It keeps everything already in the sources file and adds the new entries. Save both files again.

Then get the lines that changed:

```
diff "${TMPDIR:-/tmp}/<draft>-before-fix.md" output/drafts/<draft>.md
```

Run the `reviewer` again for a **re-check**. Tell it the two paths, the date, every fix from its last review (Writer and Owner, copied exactly as it wrote them, with their numbers), and the diff output, labeled "Lines changed since your last review". Nothing else: not the writer's fix record, the Source Finder's record, or your opinion. It checks only those fixes and the changed lines, plus a few quick whole-draft checks. This is "Review 2" (or "Review 3" after the second fix round). Delete the copy in the temporary folder afterwards.

- **PASS:** go to step 5.
- **FAIL after fix round 1:** repeat this step once more.
- **FAIL after fix round 2:** stop. Don't run a third fix round. Go to step 5.

## 5. Save the review file

Save to `output/drafts/<draft>-review.md`. If that file already exists from an earlier check, keep everything in it and add the new check at the bottom, starting with a `---` line, in the same layout. Never delete an earlier check.

Take the draft fingerprint last, after every change to the draft in this run is saved. The next `/check-post` uses it to tell whether the draft has been edited since.

```
# Review: <post title>

**Draft:** output/drafts/<draft>.md
**Sources:** output/drafts/<draft>-sources.md
**Checked:** <date>
**Final result:** <PASS or NEEDS ATTENTION>
**Review rounds:** <number of reviews> (<number of fix rounds> fix rounds)
**Draft fingerprint:** <output of `git hash-object output/drafts/<draft>.md`>

## Review 1: <PASS or FAIL>

<the reviewer's Fixes and Checks, exactly as returned>

### What changed after Review 1
<for each fix the writer made: the fix number and one line on what changed. Any fix the writer couldn't make, and why. Any new sources added. Or "Nothing: passed".>

## Review 2: <PASS or FAIL>

<same layout, for each later round>

## Needs you
<only if the final result isn't PASS: every fix from the last review that's still open, numbered, each quoting the problem text, the rule, and what to do. Or "Nothing".>

## Optional suggestions
<from the last review, or "None">
```

## 6. Update post-log.csv

Find the row whose `file` column is `output/drafts/<draft>.md`. Set its `status` to:
- `reviewed` if the final result is PASS
- `needs attention` if it isn't

Change nothing else in that row, and leave every other row and the header exactly as they are.

If the title changed during the fixes, update the `title` in that row too.

If there's no row for this draft, add one the same way `/write-post` does: the next `post_id`, today's date, the title, the target keyword from the brief (or empty if there's no brief), the source ideas from the brief (or empty), the file, the status, and an empty `published_url`. Put double quotes around any value that contains a comma.

## 7. Save the run log

Save to `output/logs/YYYY-MM-DD-check.md`. If that file already exists, add `-2`, `-3`, and so on before `.md`.

Find the most recent earlier file in `output/logs/` that ends in `-check.md` (with or without a number). Compare each step of this run with that one. A step "ran the same way" if it used the same method: the same way of choosing the draft (named by the owner or picked automatically), the Source Finder running or being skipped, internal links found from the same place (blog page, sitemap, or post log), the same reviewer checks run and skipped, the same search method (Perplexity or web search), and the same number of review rounds. The draft, the counts, and the specific fixes can differ. If there's no earlier log, write "First run" in the comparison column.

```
# Check run: <date>

**Draft:** output/drafts/<draft>.md
**Final result:** <PASS or NEEDS ATTENTION>
**Sources found:** <n> (<n> matched as written, <n> changed to match the source)
**Claims rewritten without a fact:** <n>
**Claims cut:** <n>
**Links to own posts added:** <n>
**Review rounds:** <n> reviews, <n> fix rounds
**Word count:** <before> before, <after> after (target <n>)
**Paid DataForSEO calls:** 0
**Search method:** <Perplexity, or web search and why>
**Perplexity calls:** <n> (cost $<n>)
**Web searches made:** <n>
**Pages opened:** <n> by the Source Finder (<n> for sources, <n> for links to own posts), <n> by the Reviewer

## Steps

| Step | What happened | Same as last run? |
|---|---|---|
| Draft choice | <named by owner, or picked automatically: not yet reviewed, or changed since its last review> | <Yes / No: what changed / First run> |
| Source Finder | <search method; marks found, sourced, rewritten, cut; Perplexity calls, web searches, and pages opened; or skipped and why> | |
| Links to own posts | <how many, found from where; or skipped and why> | |
| Review 1 | <PASS or FAIL; number of fixes; checks skipped because of TODO rules; facts checked against the sources file only, and source pages opened> | |
| Fix round 1 | <fixes made, fixes the writer couldn't make; or "Not needed"> | |
| Review 2 | <re-check: PASS or FAIL; earlier fixes still open, new fixes, pages opened; or "Not needed"> | |
| Fix round 2 | <or "Not needed"> | |
| Review 3 | <or "Not needed"> | |
| Post log | <status set to reviewed or needs attention; row added or updated> | |

## Skipped or failed
<if the Source Finder used web search because there's no Perplexity key: "No Perplexity key, so sourcing used web search. Adding PERPLEXITY_API_KEY to .env makes /check-post faster (see the README, Session 4)." Then pages that wouldn't load, the blog page being unavailable, anything else from the source record or reviews that didn't fully run, or "Nothing">
```

Never put key values, quotes from meetings or emails, or client names in the log.

## 8. Show the result

**If it passed,** show in the chat:
- **PASS** and the title.
- In one or two sentences: how many sources were added, how many claims were rewritten or cut (and that the details are in the sources file), how many links to the owner's own posts were added, and how many review rounds it took.
- Where the review file and sources file are saved.
- Any optional suggestions, labeled as optional.

If the Source Finder used web search because there's no Perplexity key, add one sentence: adding a Perplexity key makes this faster, and the README's Session 4 section shows how.

Then tell them the post is ready for the next step, which turns it into finished HTML in a later session. Offer to commit and push the new files.

**If it didn't pass,** show in the chat:
- **Needs you** and the title, with one sentence saying the reviewer still found problems after <n> fix rounds.
- The "Needs you" list from the review file: each item numbered, quoting the problem text, naming the rule, and saying what to do. Mark the items only the owner can resolve, such as a broken offer page or two rules that contradict each other.
- Where the review file is saved.

If the Source Finder used web search because there's no Perplexity key, add the same one-sentence tip as above.

Then tell them how to finish: fix the items by hand or type `/revise-post` with what to change, then type `/check-post <draft name>` to check it again. If an item comes from a rule they don't agree with, they can change the rule in `context/voice-and-style.md` or `context/offers.md` instead. Offer to commit and push the files so far.
