# Build plan

## The finished system

| Step | Who | What happens |
|---|---|---|
| 1. Wake up | Scheduled run | Starts in the cloud, loads this repository and the context files |
| 2. Research | Topic Researcher agent | Finds and ranks bottom-of-the-funnel topics; the owner approves the ones to write |
| 3. Write | Writer agent | Drafts the post in the owner's voice, following the post structure |
| 4. Source | Source Finder agent | Adds credible supporting links and internal links |
| 5. Review | Reviewer agent (independent) | Checks style, facts, and FAQ answers; up to two rounds of fixes |
| 6. Deliver | `/finish-post` | Saves the HTML post and publishing card |
| 7. Log | `/finish-post`, `/mark-published` | Records the post in `post-log.csv` |

## Session 1: Foundation

- Private copy of the template
- Context files written by interview (`/setup-context`)
- Example posts saved
- Databox and DataForSEO connected and tested (`/check-setup`)
- Finish-line test passed

## Session 2: Topic Researcher

- Settings file (`context/settings.md`): blog URL, Databox account and data sources, keyword country and language, paid-call limit
- Editable scoring rules (`context/topic-scoring.md`), with "Never suggest" and "Always prefer" lists
- Optional `my-sources.md`, listing where meeting notes and emails live
- Topic Researcher agent (`.claude/agents/topic-researcher.md`)
- `/research-topics` command: saves a 10-topic shortlist with approve and reject boxes to `output/topics/`, and a run log to `output/logs/`
- `/check-setup` also checks the settings file
- Finish-line test: a shortlist you'd happily write from, with approve or reject marked on every topic

## Session 3: Writer

- Writer agent (`.claude/agents/writer.md`): picks the highest-scoring approved topic (or the one the owner names), reads Google's page-one results for the target keyword with one paid DataForSEO call, reads the top 3-5 articles, writes a brief, then writes the draft following `templates/post-structure.md`
- Never invents statistics, quotes, client names, results, or prices, and leaves prices out unless `offers.md` says they can be published (`/setup-context` now asks); facts that need a source are marked `[SOURCE NEEDED: ...]` for the Source Finder
- `/write-post` command: shows the brief and asks "Write it, or change anything first?", then saves the brief and draft to `output/drafts/`, marks the topic "Drafted" on its shortlist, adds a `draft` row to `post-log.csv`, and saves a run log to `output/logs/`
- `/revise-post` command: edits a draft from the owner's feedback, then offers to save the feedback as permanent rules: style and tone in `context/voice-and-style.md`, claims and facts under "Claims we must never make" in `context/offers.md`
- Finish-line test: a draft that sounds like you and that you'd publish after filling in the sources and a light edit

## Session 4: Source Finder and Reviewer

- Source finding tool (`tools/find_sources.py`, standard Python only): sends every `[SOURCE NEEDED]` claim to Perplexity (`perplexity/sonar` through the Agent API) at the same time and returns up to 3 candidate sources per claim, each with the supporting sentence Perplexity found. Optional `PERPLEXITY_API_KEY` in `.env`; `/check-setup` tests it with one tiny call
- Source Finder agent (`.claude/agents/source-finder.md`): runs the tool, then for each claim picks an original, credible source (studies, government and industry data, well-known publications, official documentation; never competitors' blogs, self-ranking lists, or content farms), opens it to confirm the supporting sentence is really on the page (at most 3 pages per claim), and links it. Without a Perplexity key it uses web search instead, at most 2 searches and 3 pages per claim, and the run log suggests adding a key. If the page says something different, the sentence changes to match the source. Claims with no solid source are rewritten or cut. Adds 2-4 links to the owner's own related posts from the blog page in `context/settings.md`
- Reviewer agent (`.claude/agents/reviewer.md`): independent; reads only the draft, its sources file, `templates/post-structure.md`, `context/voice-and-style.md`, and `context/offers.md`, never the brief or the writer's notes. Checks structure, every style rule, every banned claim, prices, every fact against the supporting sentence saved in the sources file (opening the page only when that sentence doesn't clearly support the claim or the claim has changed), the FAQ answers, leftover marks, length, and every link. Returns PASS or FAIL with numbered fixes, each quoting the problem and naming the rule. After a fix round it re-checks only its earlier fixes and the lines that changed
- Writer agent gains a fix mode: it fixes only the items the reviewer listed
- `/revise-post` sets a checked post's status back to `draft`, and `/check-post` picks up drafts changed since their last review (each review file records a fingerprint of the draft)
- `/check-post` command: runs the Source Finder, then the Reviewer; on FAIL, the writer fixes the listed items and the Reviewer checks again, for at most 2 fix rounds. Saves `<draft>-sources.md` and `<draft>-review.md` to `output/drafts/`, sets the post's status in `post-log.csv` to `reviewed` or `needs attention`, saves a run log to `output/logs/` (including Perplexity calls and cost, web searches, and pages opened), and shows PASS or a "Needs you" list
- Finish-line test: every fact in the post links to a page that says the same thing, and the review either passes or flags only things you agree need your call

## Session 5: Finish, run, and schedule

- HTML builder (`tools/build_post.py`, standard Python only): converts a reviewed draft to clean HTML, builds FAQPage schema from the FAQ section, fills in `templates/post.html`, and warns about leftover `[SOURCE NEEDED]` or TODO marks. Code, not AI, because it's the same job every time
- `/finish-post` command: only finishes posts that passed review (or the owner says finish anyway), notes if the draft was edited after review, builds the HTML, writes the publishing card (meta description, slug, category, tags, image alt text, links, how to publish), sets status to `ready to publish`, and saves a run log. Optional: creates a **draft** in the owner's blog platform through a connector, if the owner said yes under "Publishing" in `context/settings.md`. Never publishes
- `/mark-published` command: checks the live page loads and shows the title, then records `published` and the `published_url` in `post-log.csv` and on the card
- `/run-blog-agent` command: a full run with no questions. Finishes posts already reviewed, writes one post from the top approved topic (brief approved automatically, because the owner approved the topic), runs `/check-post`, finishes it on PASS, researches new topics when approved ones run low (but not while a recent shortlist still waits for decisions), saves a run report that leads with "What you need to do", and commits and pushes. Never writes unapproved topics
- Scheduled task (`docs/scheduling.md`): runs `/run-blog-agent` in the cloud on Sonnet 5.5, with a "Blog agent" cloud environment (Full network access; DataForSEO and Perplexity keys as environment variables) and only the needed connectors. Results land on the main branch
- Finish-line test: the first scheduled run's report says clearly what to do, and its finished post is one you'd publish after a quick read

## Optional add-ons

- Hero images for each post
- Swapping a cheaper, faster model into yes-or-no checks, such as confirming a source page supports a claim
- A refresh command that finds old posts losing traffic in Databox and updates them
- Turning other repeated steps into small scripts, the way `build_post.py` did for the HTML
