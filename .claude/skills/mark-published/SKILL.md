---
name: mark-published
description: Record that a finished blog post is live. Takes the post's slug or title and its live URL, checks the page loads and shows the post's title, then sets the post's status to "published" and its published_url in post-log.csv, and updates its publishing card. Use when the owner types /mark-published or says a post is live.
---

# Mark a post as published

Speak in plain English throughout. The owner is a marketing leader, not a developer.

The owner types something like `/mark-published how-to-choose-a-payroll-provider https://www.example.com/blog/how-to-choose-a-payroll-provider`.

## 1. Find the post and the URL

- **The URL:** the part that starts with `http`. If there isn't one, ask for the live address of the post.
- **The post:** match the rest against the `file` and `title` columns in `post-log.csv`. If they typed nothing else, match the URL's last part against the slugs in the `file` column. If nothing matches, or more than one row matches, list the posts marked `ready to publish` and ask which one.

If the matched post's status isn't `ready to publish`, mention its status in one line (for example "this one never went through /finish-post") and carry on.

## 2. Check the page

Run `curl -sL -o /dev/null -w "%{http_code}" <url>` and then fetch the page and look for the post's title.

- **The page loads and shows the title:** go on.
- **The page loads but the title isn't on it:** tell the owner in one line, and ask whether to save it anyway (titles are sometimes changed at publishing).
- **The page doesn't load** (not a 200): tell the owner the code and ask whether to save it anyway. It may be scheduled or still private.

## 3. Update the records

- In `post-log.csv`, find the post's row. Set `status` to `published` and `published_url` to the URL. If the title on the live page is different, update `title` to match it. Change nothing else, and leave every other row and the header exactly as they are.
- In the post's card (`output/posts/<draft>-card.md`), change the `**Status:**` line to `Published <today's date>: <url>`. If there's no card, skip this.

## 4. Show the result

Say in one or two sentences that the post is recorded as published, with its URL. Mention that the Topic Researcher won't suggest this topic again, and the Source Finder can now link to this post from future posts. Offer to commit and push.
