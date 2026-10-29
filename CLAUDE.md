# Autonomous Blog Agent

You are helping the owner of this repository build and run an autonomous blog agent for their business.

## What this agent does

When finished, each run will:

1. **Research topics.** Find bottom-of-the-funnel topics the owner's buyers search for or ask AI about, using the owner's ICP and offers, their own unstructured content (meetings, emails, notes), past results from Databox, and keyword data from DataForSEO.
2. **Write.** Draft one post in the owner's voice, following `templates/post-structure.md`.
3. **Find sources.** Add credible supporting links and links to the owner's own past posts.
4. **Review.** An independent reviewer checks style rules, every fact, and every FAQ answer. Up to two rounds of fixes; if it still fails, flag it for the owner.
5. **Deliver.** Save finished HTML (with FAQ schema) and a publishing card in `output/posts/`.
6. **Log.** Add a row to `post-log.csv`.

The agents for these steps are added one session at a time. **Steps 1 to 4 are built:** type `/research-topics` to run the Topic Researcher agent, `/write-post` to run the Writer agent, `/revise-post` to revise a draft from feedback, and `/check-post` to run the Source Finder and the independent Reviewer on a draft. The other steps come in later sessions.

## Where things live

- `context/icp.md` – who the owner sells to. Source of truth for audience.
- `context/offers.md` – what the owner sells. Source of truth for bottom-of-the-funnel topics.
- `context/voice-and-style.md` – how the owner writes. Rules the reviewer will enforce.
- `context/example-posts/` – the owner's best posts, used as voice samples.
- `context/settings.md` – the owner's blog URL, Databox account and data source IDs, keyword country and language, and paid-call limit.
- `context/topic-scoring.md` – how topics are scored, plus the owner's "Never suggest" and "Always prefer" lists.
- `my-sources.md` (optional, made by the owner) – where the owner's meeting notes and emails live. Tool names and folders only, never content.
- `templates/post-structure.md` – required structure for every post.
- `templates/post.html` – HTML shell for finished posts.
- `.claude/agents/` – the agents that do each step: `topic-researcher.md`, `writer.md`, `source-finder.md`, and `reviewer.md`.
- `.claude/skills/` – commands the owner types, such as `/research-topics`, `/write-post`, and `/check-post`.
- `output/topics/` – topic shortlists, with the owner's approve and reject decisions.
- `output/drafts/` – post drafts, with their briefs, sources files, and review files.
- `output/logs/` – a short log of each run: data used, paid calls, cost.
- `output/posts/` – finished posts.
- `post-log.csv` – one row per post.
- `docs/build-plan.md` – what gets built and in what order.

Always read the context files before doing any research or writing. If `icp.md`, `offers.md`, or `voice-and-style.md` still contains `TODO` lines, tell the owner and offer to run `/setup-context`. Missing lines in `settings.md` are filled in by `/research-topics`.

## Rules

- **Never commit secrets.** API keys live only in `.env`, which is git-ignored. Never print key values in chat.
- **Keep private content out of the repository.** Meeting notes, emails, and client conversations are read live through connectors during a run. Never save them as files in this repository. Summaries of themes are fine; quotes and names of clients are not.
- **Read data from Databox, not from ad platforms or CRMs directly.** Use only the Databox account in `context/settings.md`.
- **Watch DataForSEO spending.** Batch keywords into as few calls as possible, and never make more paid calls in one run than the limit in `context/settings.md`.
- **Write in plain English.** The owner is a marketing or sales leader, not a developer. Explain what you did in one or two sentences, not a list of commands.
- **Ask before anything that publishes or sends** (posting to a blog, emailing, posting to social).

## Data access

- **Databox** – through the Databox connector on the owner's claude.ai account. Use it for Search Console, GA4, and CRM results.
- **DataForSEO** – through its REST API with HTTP basic auth, using `DATAFORSEO_LOGIN` and `DATAFORSEO_PASSWORD` from `.env`. Base URL: `https://api.dataforseo.com/v3/`.
