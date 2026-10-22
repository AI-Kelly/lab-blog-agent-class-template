# Build plan

## The finished system

| Step | Who | What happens |
|---|---|---|
| 1. Wake up | Scheduled run | Starts in the cloud, loads this repository and the context files |
| 2. Research | Topic Researcher agent | Finds and ranks bottom-of-the-funnel topics; the owner approves the ones to write |
| 3. Write | Writer agent | Drafts the post in the owner's voice, following the post structure |
| 4. Source | Source Finder agent | Adds credible supporting links and internal links |
| 5. Review | Reviewer agent (independent) | Checks style, facts, and FAQ answers; up to two rounds of fixes |
| 6. Deliver | Finisher | Saves the HTML post and publishing card |
| 7. Log | Finisher | Records the post in `post-log.csv` |

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

## Later sessions

Announced in the Lab. Each session adds one or more of the steps above, and the class template gets the new files. See [updating-from-template.md](updating-from-template.md) to bring them into your copy.
