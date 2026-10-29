---
name: revise-post
description: Revise a blog post draft from the owner's feedback, then offer to turn the feedback into permanent rules (style and tone in context/voice-and-style.md, claims and facts in context/offers.md) so future posts get it right the first time. Use when the owner types /revise-post, gives feedback on a draft, or asks for changes to a post in output/drafts/.
---

# Revise a post

Speak in plain English throughout. The owner is a marketing leader, not a developer.

## 1. Find the draft and the feedback

- **Which draft:** the one the owner names. If they don't name one, use the most recent file in `output/drafts/` that doesn't end in `-brief.md`. Say which draft you're revising in one line. If there are no drafts, suggest `/write-post` and stop.
- **The feedback:** whatever the owner typed after the command. If they didn't give any, ask: "What would you like changed?"

## 2. Read what you need

Read the draft, its brief (the same file name ending in `-brief.md`), `context/voice-and-style.md`, `context/offers.md`, and `templates/post-structure.md`. If the feedback is about how the post sounds, also read two or three posts in `context/example-posts/`.

## 3. Edit the draft

Make the changes the owner asked for, editing the draft file in place. Change only what the feedback covers; leave the rest as it is, including any edits the owner made by hand.

While editing:
- **Keep the structure** from `templates/post-structure.md`: the answer in the first paragraph, the TL;DR, the FAQ with answers that stand on their own, and the call to action.
- **Keep the voice** in `voice-and-style.md`.
- **Don't invent facts.** If the feedback asks for a statistic, example, or result the owner didn't supply, add it as `[SOURCE NEEDED: what to find]`. If the owner gives the fact and its source, use it and add the source as a link.
- **Keep existing `[SOURCE NEEDED]` marks** unless the owner supplied that source or the claim was removed.
- **No client names** unless the owner confirms the client agreed to be named. Describe the situation without the name instead.
- **If the feedback conflicts** with a rule in `voice-and-style.md`, `offers.md`, or `post-structure.md`, point out the conflict and ask which should win before editing that part.

If the title, FAQ questions, or matching offer changed, update the brief to match. In `post-log.csv`, find the row whose `file` column is this draft. If its `status` is `reviewed` or `needs attention`, set it back to `draft`, because the edited post hasn't been checked yet. If the title changed, update the `title` in that row too. Leave every other row and column as it is.

## 4. Show what changed

In the chat, list the changes in a few short lines. Then show the new word count (`wc -w`) and the number of `[SOURCE NEEDED]` marks (`grep -o "\[SOURCE NEEDED" <file> | wc -l`).

If you set the status back to `draft`, say in one sentence that the post needs checking again and that `/check-post` will pick it up.

## 5. Offer a permanent rule

Ask exactly:

> Should any of this become a permanent rule?

To help them decide, suggest the parts of their feedback that would apply to every post, each written as a rule specific enough to check. For example, "make it punchier" becomes "Keep paragraphs to 3 sentences or fewer", and "don't say leverage" becomes adding "leverage" to "Words and phrases we never use". Leave out feedback that only fits this one topic.

If they say no, stop here.

If they say yes:
1. Write each rule they want so it can be checked, and decide where it goes:
   - **Claims, facts, or results** (what the post may say is true, such as numbers, outcomes, guarantees, or comparisons with competitors) go under "Claims we must never make" in `context/offers.md`.
   - **Style and tone** (wording, sentence and paragraph length, formatting, structure, how the post sounds) go in `context/voice-and-style.md`, in the section that fits, such as "Rules", "Words and phrases we never use", or "Formatting".
2. Show the exact wording of each rule and which file and section it goes in.
3. Check that section first. If a rule already says something similar, update that rule instead of adding a second one. If the new rule contradicts an existing one, show both and ask which to keep. If the section still says TODO, replace the TODO with the new rule.
4. Save each rule in its file. Don't change any other part of either file.
5. Tell them which file each rule went to, and that the writer and the reviewer will follow these rules from now on.

Then offer to commit and push the changes.
