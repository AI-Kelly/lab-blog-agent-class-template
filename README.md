# Autonomous Blog Agent (Class Template)

The starter kit for the AI Marketing Automation Lab's Autonomous Blog Agent build.

Over the build, this repository becomes an agent that runs on a schedule, finds bottom-of-the-funnel topics your buyers are searching for, writes a post in your voice, has it checked by an independent reviewer, and delivers finished HTML you can paste into any blog platform.

This is the **class template**. It holds blank starter files only. Your own business details go in your private copy.

---

## Step 1: Make your own private copy

### The easy way: let Claude Code do it

Open Claude Code in the folder where you keep your projects and say:

> Create a private copy of the class template AI-Kelly/lab-blog-agent-class-template named blog-agent, download it here, and open it.

Claude Code uses GitHub's command-line tool for this. If you haven't used it before, Claude Code will install it and open a browser window so you can sign in to GitHub. That's a one-time step.

### The manual way: use GitHub's website

1. At the top of this page, click **Use this template**, then **Create a new repository**.
2. Name it something like `blog-agent`.
3. Choose **Private**.
4. Click **Create repository**, then ask Claude Code to download it to your computer.

> Use **Use this template**, not **Fork**. A fork of a public repository has to stay public. Your copy will hold your ICP, your voice, and your strategy, so it needs to be private.

Either way, your copy is fully independent. Nothing you add flows back here, and no one else can see it.

---

## What you need

| Tool | What it does here |
|---|---|
| GitHub account | Stores your copy so you can work from any computer |
| Claude Code (Pro plan or higher) | Builds the agents with you and runs them |
| Databox, with Search Console and GA4 connected | Shows the agent your past results |
| DataForSEO account (pay as you go) | Keyword volume and what's ranking today |

Connect Databox through your **claude.ai connectors** (claude.ai → Customize → Connectors), not from the terminal. Scheduled runs can only use connectors added there.

---

## Session 1: Foundation

Goal: your copy is set up, your context files are written, your data is connected, and Claude Code can prove it understands your business.

1. **Make your private copy** (Step 1 above).
2. **Open it in Claude Code** and ask: *"What is this project for?"* It should answer from `CLAUDE.md`.
3. **Write your context files.** Type `/setup-context`. Claude Code interviews you and fills in `context/icp.md`, `context/offers.md`, and `context/voice-and-style.md`.
4. **Add your voice examples.** Save 3–5 of your best posts in `context/example-posts/` (see the README in that folder).
5. **Connect your data.** Copy `.env.example` to a new file named `.env` and add your DataForSEO login. Then type `/check-setup` to test Databox and DataForSEO.
6. **Save and sync.** Ask Claude Code to commit and push. Open the repository on a second computer to see everything waiting there.

### The finish-line test

Ask Claude Code:

> Based on our ICP and our Search Console data, what are five topics our buyers are searching for that we haven't covered?

A sensible answer means the foundation works.

### Before next session

- List where your meeting notes and emails live (recorder app, inbox, Airtable, Google Drive).
- Confirm which platform hosts your blog.

---

## Folder map

```
CLAUDE.md                 Master instructions Claude Code reads every time
context/                  Your business: ICP, offers, voice, example posts
templates/                The post structure and HTML shell every post uses
.claude/skills/           Commands you can type, like /setup-context
output/posts/             Finished posts land here
post-log.csv              A record of every post
docs/                     Build plan and how to get template updates
.env                      Your keys (you create this; it is never uploaded)
```

## Getting updates from the class template

See [docs/updating-from-template.md](docs/updating-from-template.md).
