---
name: write-post
description: Write one blog post draft in the owner's voice. Takes an optional topic; otherwise uses the highest-scoring approved topic not yet written. Runs the writer agent, shows a brief for approval, then saves the brief and draft to output/drafts/, marks the topic Drafted, adds a row to post-log.csv, saves a run log, and shows the opening. Use when the owner types /write-post or asks for a blog post to be written.
---

# Write a post

Speak in plain English throughout. The owner is a marketing leader, not a developer.

The owner may give a topic after the command, for example `/write-post how to choose a payroll provider` or `/write-post topic 3`. If they don't, the writer picks the highest-scoring approved topic that hasn't been written yet.

## 1. Check the basics

Get today's date with `date +%F`.

- **Context files.** If `context/icp.md`, `context/offers.md`, or `context/voice-and-style.md` still has TODO lines, tell the owner which sections are empty and that the post will sound less like them without them. Offer to run `/setup-context` first. Carry on only if they want to.
- **Example posts.** If `context/example-posts/` has no posts besides its README, mention in one sentence that adding 3-5 posts there helps the writer match their voice. Carry on.
- **Settings.** If the Country or Language line in `context/settings.md` is still TODO, suggest values based on `context/icp.md`, ask the owner to confirm, and save their answer in place of the TODO. Don't change any other part of the file.

## 2. Write the brief

Tell the owner the writer is researching the topic, which usually takes a few minutes.

Run the `writer` agent in **brief mode**. Tell it today's date and the topic the owner gave, if any. It returns a **Brief**, **Notes for the owner**, and a **Run record**.

- If it returns `No topic:`, tell the owner there are no approved topics left to write. Suggest they mark `[x] approve` on topics in their latest shortlist in `output/topics/`, run `/research-topics` for new ones, or name a topic with `/write-post <topic>`. Stop here.
- If the notes say the topic already has a row in `post-log.csv`, tell the owner where the earlier draft is and ask whether to write a new one anyway. Stop if they say no.

## 3. Check for private details

Read the brief. If any line contains a client's name, a person's name, a quote from a meeting or email, or a private deal detail, rewrite it as a general theme. These files are saved in the repository.

## 4. Ask before writing

Show the owner the whole brief, plus any notes for the owner. Then ask exactly:

> Write it, or change anything first?

Wait for their answer.

- If they ask for changes, make them in the brief yourself, show the changed parts, and ask again. Keep a short note of what they changed.
- If they want a different topic altogether, run the writer in brief mode again with the new topic. Tell them first that this makes another paid DataForSEO call.
- When they say to write it, go on.

## 5. Save the brief

Make a short URL-style slug from the target keyword: lowercase, words joined by hyphens, 3-6 words, for example `how-to-choose-a-payroll-provider`.

Save the brief to `output/drafts/YYYY-MM-DD-slug-brief.md`, creating the folder if needed. If a draft with that date and slug already exists, add `-2`, `-3`, and so on after the slug, for both files. Never overwrite an earlier draft or brief.

## 6. Write the draft

Tell the owner the draft is being written.

Run the `writer` agent in **draft mode**. Tell it today's date and the path of the saved brief. It returns a **Draft** and a **Draft record**.

Check the draft for private details the same way as in step 3. Then save it to `output/drafts/YYYY-MM-DD-slug.md`, with the same suffix as the brief if one was added.

Count the words with `wc -w` and the `[SOURCE NEEDED` marks with `grep -o "\[SOURCE NEEDED" <file> | wc -l`. Use these numbers, not the writer's estimates, from here on.

## 7. Mark the topic Drafted

If the topic came from a shortlist in `output/topics/`, open that file and find the topic. Right under its "Decision:" line, add:

```
Status: Drafted <date>. Draft: output/drafts/<draft file name>
```

Don't change anything else in the shortlist. If the topic was named by the owner and isn't on a shortlist, skip this step.

## 8. Add a row to post-log.csv

Add one row to `post-log.csv`. Keep the header and every existing row exactly as they are.

| Column | Value |
|---|---|
| post_id | One more than the highest post_id already in the file, or 1 if it's empty |
| date | Today's date |
| title | The draft's title |
| target_keyword | The target keyword |
| source_ideas | "Where the idea came from" from the brief |
| file | `output/drafts/<draft file name>` |
| status | `draft` |
| published_url | Leave empty |

Put double quotes around any value that contains a comma, and double any quote marks inside a value.

## 9. Save the run log

Save to `output/logs/YYYY-MM-DD-write.md`. If that file already exists, add `-2`, `-3`, and so on before `.md`.

Find the most recent earlier file in `output/logs/` that ends in `-write.md`. Compare each step of this run with that one. A step "ran the same way" if it used the same method and settings: the same way of choosing the topic (named by the owner or picked automatically), the same DataForSEO endpoint, country, and language, and the same number of pages read. The topic and the amount of text can differ. If there's no earlier log, write "First run" in the comparison column.

Use this layout:

```
# Write run: <date>

**Brief:** output/drafts/<brief file name>
**Draft:** output/drafts/<draft file name>
**Paid DataForSEO calls:** <n> of <limit>
**Estimated cost:** $<total from the run record>
**Pages read:** <n>
**[SOURCE NEEDED] marks:** <n>
**Word count:** <n> (target <n>)

## Steps

| Step | What happened | Same as last run? |
|---|---|---|
| Context files | <files read, any TODOs, number of example posts> | <Yes / No: what changed / First run> |
| Topic choice | <named by owner, or picked automatically; which shortlist and rank> | |
| DataForSEO free check | <OK or the problem> | |
| Google page-one results | <endpoint, keyword, country, language; or skipped and why> | |
| Top articles read | <sites and their ranks; any skipped and why> | |
| Brief | <approved as is, or what the owner changed> | |
| Draft | <word count vs target, FAQ questions, action steps yes or no> | |
| Writer's self-check | <all passed, or what still fails> | |
| Shortlist and post log | <shortlist marked Drafted, or "Named by owner: no shortlist"; post_id added> | |

## Skipped or failed
<from the run record, or "Nothing">
```

Never put key values, quotes, or client names in the log.

## 10. Show the results

In the chat, show:
- The title, then the first paragraph and the TL;DR, exactly as they appear in the draft.
- Where the draft and brief are saved.
- The word count against the target, and the number of `[SOURCE NEEDED]` marks, with one sentence explaining that each mark is a fact that still needs a source, which the Source Finder will fill in a later session.
- Anything the writer's self-check still flagged.
- Paid calls made and the estimated cost.

Then tell them: read the draft, and if anything needs changing, type `/revise-post` with their feedback. Offer to commit and push the new files.
