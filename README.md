# Autonomous Blog Agent (Class Template)

The starter kit for the AI Marketing Automation Lab's Autonomous Blog Agent build.

Over the build, this repository becomes an agent that runs on a schedule, finds bottom-of-the-funnel topics your buyers are searching for, writes a post in your voice, has it checked by an independent reviewer, and delivers finished HTML you can paste into any blog platform.

This is the **class template**. It holds blank starter files only. Your own business details go in your private copy.

---

## Step 1: Make your own private copy

### The easy way: let Claude Code do it

First, make sure Claude Code is signed in to GitHub (your instructor will walk you through this). Then paste this into Claude Code:

> Make my own private copy of this GitHub template: https://github.com/AI-Kelly/lab-blog-agent-class-template
> - Use GitHub's template option, not a fork. Name the new repository blog-agent and make it private under my GitHub account.
> - Download it into my Documents folder. Then check that the downloaded folder contains README.md and CLAUDE.md. If it's empty, wait 10 seconds and download it again.
> - When you're done, give me the link to my new repository and the folder location on my computer.

Then start a new Claude Code session in the **Documents/blog-agent** folder.

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

## Session 2: Topic Researcher

Goal: one command gives you a ranked shortlist of 10 blog topics your buyers are searching for right before they buy, and you choose which ones to write.

1. **Get the new files.** Paste the prompt from [docs/updating-from-template.md](docs/updating-from-template.md) into Claude Code. It adds this session's files without touching your context files, outputs, or keys.
2. **Tell it where your meeting notes and emails live** (optional, but it makes the topics much better). Paste this into Claude Code:
   > Create my-sources.md listing where my meeting notes and emails live. Ask me which tools I use, which folders or labels to look in, and how far back to read. Tool names and folders only, no content.

   Then make sure each of those tools is connected at claude.ai → Customize → Connectors. The agent reads them live during a run and keeps only themes, never quotes or client names.
3. **Review the scoring rules.** Open `context/topic-scoring.md`. It scores topics on buying intent, fit with your ICP, search demand, how winnable they are, how likely AI assistants are to cite them, and connection to your offers. Change any weights you like, and add anything to the "Never suggest" or "Always prefer" lists.
4. **Run it.** Type `/research-topics`. The first time, it asks for your blog URL, your Databox account, and the country and language for keyword data. It then researches for a few minutes and shows the top 3.
5. **Make your decisions.** Open the shortlist in `output/topics/`. On each topic, put an x in approve or reject, like `[x] approve`, and add a short reason. The next run reads your decisions and learns from them.
6. **Save and sync.** Ask Claude Code to commit and push.

**What it costs:** each run makes at most 3 paid DataForSEO calls (you can change this in `context/settings.md`), usually a few cents in total. The run log in `output/logs/` shows the exact amount.

### The finish-line test

Look at your shortlist and ask yourself: *Would I happily write at least three of these this month?* If yes, the researcher works. If not, mark your reasons on the rejects, adjust `context/topic-scoring.md`, and run `/research-topics` again.

---

## Session 3: Writer

Goal: one command turns your best approved topic into a full draft in your voice, and your feedback on each draft becomes a rule the writer follows from then on.

1. **Get the new files.** Paste the prompt from [docs/updating-from-template.md](docs/updating-from-template.md) into Claude Code.
2. **Check your voice file.** Open `context/voice-and-style.md` and make sure the "Post length" target and the "Words and phrases we never use" list are filled in. The writer follows them exactly. To let posts show your prices, run `/setup-context` and answer the new prices question; until then, the writer leaves prices out. Make sure you have 3-5 posts in `context/example-posts/` too.
3. **Write a post.** Type `/write-post`. It picks your highest-scoring approved topic that hasn't been written yet. To choose the topic yourself, add it after the command, like `/write-post topic 3` or `/write-post <your topic>`.
4. **Approve the brief.** Before writing, it checks what ranks on Google's first page today, reads the top articles, and shows you a short brief: the angle, the headings, the FAQ questions, the offer it leads to, and the length. Say "write it", or tell it what to change.
5. **Read the draft.** It's saved in `output/drafts/`, next to the brief. The chat shows the opening paragraph and TL;DR. Any fact that still needs a source is marked `[SOURCE NEEDED: ...]`; leave those for now, because the Source Finder fills them in a later session.
6. **Give feedback.** Type `/revise-post` followed by what you'd change, for example `/revise-post the intro is too long and don't use the word "robust"`. It edits the draft, then asks whether any of it should become a permanent rule. Say yes to anything you'd want in every post. Style and tone rules go in `context/voice-and-style.md`; rules about claims, facts, or results go under "Claims we must never make" in `context/offers.md`. It tells you which file each rule went to.
7. **Save and sync.** Ask Claude Code to commit and push.

**What it costs:** each post makes one paid DataForSEO call to see Google's first page, usually a few cents or less. The run log in `output/logs/` shows the exact amount.

### The finish-line test

Read your draft out loud. *Does it sound like you, does the first paragraph answer the title's question, and would you publish it after filling in the sources and a light edit?* If yes, the writer works. If not, run `/revise-post` with what's off and save the fixes as permanent rules, then write your next post and see the difference.

---

## Folder map

```
CLAUDE.md                 Master instructions Claude Code reads every time
context/                  Your business: ICP, offers, voice, example posts,
                          settings, and topic scoring rules
my-sources.md             Where your meeting notes and emails live (you create this)
templates/                The post structure and HTML shell every post uses
.claude/agents/           The agents that do the work, like the Topic Researcher and Writer
.claude/skills/           Commands you can type, like /research-topics and /write-post
output/topics/            Topic shortlists, with your approve and reject decisions
output/drafts/            Post drafts and their briefs, before review
output/logs/              A short log of each run: data used and cost
output/posts/             Finished posts land here
post-log.csv              A record of every post
docs/                     Build plan and how to get template updates
.env                      Your keys (you create this; it is never uploaded)
```

## Getting updates from the class template

See [docs/updating-from-template.md](docs/updating-from-template.md).
