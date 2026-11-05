---
name: finish-post
description: Turn a reviewed blog post draft into a finished post. Takes an optional draft name; otherwise uses the oldest post marked reviewed. Builds the HTML with FAQ schema using tools/build_post.py, writes a publishing card (title, meta description, URL slug, category, alt text, target keyword, how to publish), saves both to output/posts/, sets the post's status in post-log.csv to "ready to publish", and saves a run log. Can also create a draft in the owner's blog platform if a connector for it is set up. Use when the owner types /finish-post or asks for a post to be made ready to publish.
---

# Finish a post

Speak in plain English throughout. The owner is a marketing leader, not a developer.

The owner may name a draft after the command, for example `/finish-post how-to-choose-a-payroll-provider`. If they don't, use the oldest post in `post-log.csv` whose status is `reviewed`.

## 1. Find the post

Get today's date with `date +%F`.

- **If the owner named one,** find the draft in `output/drafts/` whose file name contains what they typed (not the `-brief`, `-sources`, or `-review` files). If more than one matches, list them and ask which. If none match, list the drafts and ask.
- **Otherwise,** read `post-log.csv` and pick the oldest row with status `reviewed`. If there is none, say so: list any posts marked `needs attention` and suggest `/check-post` for drafts not checked yet. Stop here.

In the steps below, `<draft>` means the draft's file name without `.md`, for example `2026-11-05-how-to-choose-a-payroll-provider`, and `<slug>` is that name without the date at the start.

## 2. Make sure it passed review

Read `output/drafts/<draft>-review.md`.

- **No review file,** or its last "Final result" isn't PASS: tell the owner the post hasn't passed review yet and suggest `/check-post <draft>`. Stop, unless the owner said to finish it anyway; then carry on and note "Finished without passing review: owner's call" in the card and log.
- **Changed since review:** run `git hash-object output/drafts/<draft>.md` and compare it with the last "Draft fingerprint" line in the review file. If they differ, the draft was edited after it passed. Small edits by the owner are normal, so don't stop: tell them in one line, and say that `/check-post <draft>` will re-check it if the change was more than a light edit. Note it in the log.

## 3. Build the HTML

Run:

```
python3 tools/build_post.py output/drafts/<draft>.md output/posts/<draft>.html
```

The script converts the draft to HTML, builds the FAQ schema from the FAQ section, and fills in `templates/post.html`. It prints a summary: title, answer, TL;DR, word count, headings, FAQ questions, links, and warnings.

- If it prints `"status": "error"`, tell the owner what went wrong in one sentence and stop.
- If there are **warnings** (for example `[SOURCE NEEDED]` marks or a missing FAQ), list them for the owner. Leftover `[SOURCE NEEDED]` or TODO marks mean the post isn't ready: delete the HTML file, suggest `/check-post <draft>`, and stop. Other warnings: carry on and put them on the card.

If `output/posts/<draft>.html` already exists from an earlier finish, the script replaces it. That's fine; the draft is the master copy.

## 4. Write the publishing card

Read `context/settings.md`, `context/offers.md`, the draft, its brief (`output/drafts/<draft>-brief.md`, if there is one), and the build summary. Then save `output/posts/<draft>-card.md`:

```
# Publishing card: <title>

**Post file:** output/posts/<draft>.html
**Status:** Ready to publish
**Finished:** <date>

| Field | Value |
|---|---|
| Title | <title from the summary> (<n> characters) |
| Meta description | <your meta description> (<n> characters) |
| URL slug | <slug> |
| Category | <one suggested category> |
| Tags | <2-4 short tags> |
| Target keyword | <from the brief, or post-log.csv> |
| Matching offer | <offer name, from the brief> |
| Word count | <from the summary> |
| FAQ schema | <Included, with <n> questions / Not included: no FAQ section> |

## Image
- **Suggested image:** <one sentence describing a simple image that fits the post>
- **Alt text:** <alt text for that image, under 125 characters>

## Links in this post
<every link from the summary, one per line, marked "own post", "offer page", or "source">

## How to publish
1. In your blog editor, start a new post and paste the **Title** above into the title field.
2. Switch the body to its HTML or code view and paste everything in `<draft>.html` between `<article>` and `</article>`.
3. If your editor removes the FAQ schema block (the part starting `<script type="application/ld+json">`), paste that block into the post's head HTML, custom code, or SEO plugin schema field instead.
4. Fill in the meta description, URL slug, category, and tags from the table above. Add an image with the alt text above if you use one.
5. Preview it, publish it, then type `/mark-published <slug> <live URL>` so the agent can track how it performs.

## Notes
<any warnings from the build, "Edited after review", "Finished without passing review: owner's call", or "None">
```

Rules for the card:
- **Meta description:** 140-155 characters, includes the target keyword naturally, answers the question in the title, and follows `context/voice-and-style.md` (including "Words and phrases we never use"). Count the characters with a command, not by eye.
- **URL slug:** the `<slug>` from the file name, unless it's longer than 6 words; then shorten it, keeping the target keyword.
- **Category:** if the blog already has categories you can see on the blog page in `context/settings.md`, pick one of those. Otherwise suggest one.
- If the title is over 65 characters, add a note suggesting a shorter version, but don't change the post.

## 5. Update post-log.csv

Find the row whose `file` column is `output/drafts/<draft>.md`. Set its `status` to `ready to publish`. Change nothing else in that row, and leave every other row and the header exactly as they are. If there's no row, add one the same way `/check-post` does, with status `ready to publish`.

## 6. Create a draft in the blog platform (optional)

Look in `context/settings.md` for a `## Publishing` section.

- **If it isn't there,** and the owner is here to answer, ask: "Which platform hosts your blog, and do you want the agent to create a draft there for you when a post is finished? It never publishes; you always press publish yourself." Add their answer to the end of `context/settings.md`, changing nothing else:

  ```
  ## Publishing
  - **Blog platform:** <their answer, for example WordPress, HubSpot, Webflow, Squarespace>
  - **Create drafts in the blog platform:** <yes or no>
  ```

  If nobody is there to answer (a scheduled run), skip this step.

- **If it says yes,** check whether you have a connector for that platform that can create blog posts (its tools will name the platform). If you do, create the post there as a **draft**, never published: the title, the body HTML, the meta description, and the URL slug, with the FAQ schema wherever that platform takes custom code. Read back the draft's edit link or ID and add it to the card's Notes. If there's no such connector, or creating the draft fails, say so in one line and note it on the card; the HTML file is still ready to paste.

Never publish a post, schedule it, or change a live page. Creating a draft is as far as the agent goes.

## 7. Save the run log

Save to `output/logs/YYYY-MM-DD-finish.md`. If that file already exists, add `-2`, `-3`, and so on before `.md`.

```
# Finish run: <date>

**Draft:** output/drafts/<draft>.md
**Post:** output/posts/<draft>.html
**Card:** output/posts/<draft>-card.md
**Review:** <PASS on <date>, edited after review, or finished without passing review>
**Build warnings:** <list, or "None">
**FAQ schema:** <n questions, or "Not included">
**Blog platform draft:** <created (link or ID), skipped and why, or "Not set up">
**Paid calls:** 0
```

## 8. Show the result

In the chat, show:
- **Ready to publish** and the title.
- The meta description and URL slug.
- Where the HTML file and card are saved, and one line saying the card has the step-by-step publishing instructions.
- Any warnings or notes.
- If a draft was created in their blog platform, say so and give the link.

Then tell them: after the post is live, type `/mark-published <slug> <live URL>`. Offer to commit and push the new files.
