---
name: check-setup
description: Test that the blog agent's foundation is ready - context files filled in, example posts present, .env set up and ignored by git, Databox connected, and DataForSEO keys working. Use when the owner types /check-setup or asks whether their setup is working.
---

# Check the setup

Run each check in order and report the results as a short pass/fail list in plain English. For anything that fails, say exactly how to fix it. Never print key values.

## 1. Context files
- Read `context/icp.md`, `context/offers.md`, and `context/voice-and-style.md`.
- Pass if no `TODO` lines remain. Otherwise list which sections are still empty and suggest `/setup-context`.

## 2. Example posts
- Pass if `context/example-posts/` holds at least 3 post files besides its README.

## 3. Keys file
- Confirm `.env` exists and contains `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` with values.
- Confirm git ignores it: run `git check-ignore .env`. If it isn't ignored, stop and fix `.gitignore` before anything else.
- If `.env` is missing, tell the owner to copy `.env.example` to `.env` and fill it in.

## 4. Databox
- Use the Databox connector to list connected data sources.
- Pass if Google Search Console and Google Analytics 4 appear. Note any CRM that's connected.
- Then pull the top 20 Search Console queries for the last 90 days and show them.
- If the Databox tools aren't available, tell the owner to connect Databox at claude.ai → Customize → Connectors, then restart Claude Code.

## 5. DataForSEO
- Load the login and password from `.env` without printing them.
- Call `GET https://api.dataforseo.com/v3/appendix/user_data` with HTTP basic auth. This call is free. Pass if it returns status code 20000; report the account balance.
- Then ask the owner for five keywords related to their business and check their search volume with `POST https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live` (location "United States", language "English" unless the owner says otherwise). Tell the owner this costs a few cents before running it.

## Wrap up

If everything passes, suggest the finish-line test from the README:

> Based on our ICP and our Search Console data, what are five topics our buyers are searching for that we haven't covered?
