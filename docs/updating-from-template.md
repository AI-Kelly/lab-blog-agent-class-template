# Getting updates from the class template

Your copy isn't linked to the class template, so new files from later sessions don't arrive on their own. When a new session's files are ready, paste this into Claude Code from inside your project folder:

> Bring in the latest files from the class template at https://github.com/AI-Kelly/lab-blog-agent-class-template. Follow these rules:
> - Download the template into a temporary folder outside this project and copy files across. Don't merge git histories, and don't add the template as a remote.
> - Never overwrite or change existing files in context/ or output/, or post-log.csv, my-sources.md, or .env. Adding new files to those places is fine.
> - For CLAUDE.md and .gitignore, merge in the template's changes and keep every line I added myself.
> - Replace all other files with the template's version, and add any new ones. If you see that I changed one of those files myself, ask me before replacing it.
> - Delete the temporary folder when you're done.
> - Show me a plain-English list of what was added, updated, merged, and left alone. Don't commit until I say so.

Your own business details stay exactly as they are. You get the new commands, agents, and instructions.

## What gets protected

| Never overwritten | Why |
|---|---|
| `context/` | Your ICP, offers, voice, settings, scoring rules, and example posts |
| `output/` | Your shortlists, decisions, logs, and finished posts |
| `post-log.csv` | Your record of every post |
| `my-sources.md` | Where your meeting notes and emails live |
| `.env` | Your keys |

New template files in `context/` or `output/` (for example, a new settings file) are still added, because they don't replace anything of yours.
