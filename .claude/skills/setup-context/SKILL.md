---
name: setup-context
description: Interview the owner and fill in context/icp.md, context/offers.md, and context/voice-and-style.md. Use when the owner types /setup-context, asks to set up or update their context files, or when those files still contain TODO lines.
---

# Set up the context files

Your job is to interview the owner and turn their answers into three files: `context/icp.md`, `context/offers.md`, and `context/voice-and-style.md`. These files are what every agent in this project reads, so specific answers matter more than polished ones.

## Before you start

1. Read all three files to see what's already filled in. Only ask about sections still marked TODO, unless the owner wants to redo a file.
2. Ask if they have existing material to start from: an ICP document, a positioning doc, a sales deck, their website, or a brand guide. If they share any, read it first and draft from it, then use the interview to fill gaps and confirm.
3. Tell them how it works in one sentence: you'll go file by file, a few questions at a time, and show each file before saving it.

## How to interview

- Ask two or three questions at a time, never a long list.
- Push gently for specifics. If an answer is vague ("marketing leaders at mid-size companies"), ask for an example of a real customer or a real deal.
- Capture their buyers' own words where you can. Ask: "What does a prospect actually say on the first call?"
- For the "questions they ask right before buying" section of the ICP, aim for at least ten questions. These become blog topics.
- For voice, ask them to describe how they write, then check it against their example posts in `context/example-posts/` if any exist. Point out anything in the posts that differs from how they described themselves.
- Make every voice rule checkable. "Be conversational" is not checkable; "Use contractions; average sentence under 20 words" is.

## Order

1. `icp.md`
2. `offers.md`
3. `voice-and-style.md`

After each file: show a short summary of what you wrote, ask for corrections, then save it. Remove every TODO you filled. Leave TODO only where the owner truly doesn't know yet, and list those at the end.

## Privacy

Don't put client names, private deal details, or quotes from specific clients in these files. Describe patterns instead ("buyers often say…").

## When done

Tell the owner which files are complete, list any remaining TODOs, and suggest the next step: add example posts if `context/example-posts/` is still empty, otherwise run `/check-setup`. Offer to commit and push.
