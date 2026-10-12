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

## Later sessions

Announced in the Lab. Each session adds one or more of the steps above, and the class template gets the new files. See [updating-from-template.md](updating-from-template.md) to bring them into your copy.
