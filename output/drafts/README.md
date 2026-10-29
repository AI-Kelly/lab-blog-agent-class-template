# Drafts

Each time you type `/write-post`, two files are saved here:

- `YYYY-MM-DD-slug-brief.md` – the brief you approved: the angle, what Google's first page covers and misses, the headings, the FAQ questions, the matching offer, and the target length
- `YYYY-MM-DD-slug.md` – the draft, written in your voice

Any fact in the draft that still needs a source is marked `[SOURCE NEEDED: what to find]`. Leave these marks in place; `/check-post` finds the sources.

To change a draft, type `/revise-post` with your feedback. It edits the draft and asks whether your feedback should become a permanent rule for every post.

When you type `/check-post`, two more files are saved next to the draft:

- `YYYY-MM-DD-slug-sources.md` – every source added: the claim, the link, the sentence on the page that supports it, and the date it was checked. It also lists any claim that was rewritten or cut because no solid source exists, and the links added to your own posts
- `YYYY-MM-DD-slug-review.md` – each review round's result, the fixes asked for, and what changed. If the post still needs you, the list is at the bottom

Drafts move to `output/posts/` as finished HTML once they've been sourced and reviewed.
