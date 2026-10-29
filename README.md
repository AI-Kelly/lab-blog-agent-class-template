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
| Perplexity API account (optional, pay as you go) | Finds sources for your facts quickly (from Session 4) |

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

## Session 4: Source Finder and Reviewer

Goal: one command backs every fact in your draft with a real source, links it to your own past posts, and has an independent reviewer check it against your rules, fixing what it can and telling you what it can't.

1. **Get the new files.** Paste the prompt from [docs/updating-from-template.md](docs/updating-from-template.md) into Claude Code.
2. **Add a Perplexity key (optional, recommended).** It lets the Source Finder look up every fact at once, so `/check-post` takes a couple of minutes instead of much longer. Without it, everything still works using regular web search, just slower.
   - Go to the [Perplexity API Console](https://console.perplexity.ai), sign in, and add a few dollars of credit under **Billing**. Five dollars lasts a long time.
   - On the [API Keys](https://console.perplexity.ai/project/keys) page, create a key and copy it.
   - Open your `.env` file and add a line: `PERPLEXITY_API_KEY=` followed by your key. (Ask Claude Code to open `.env` for you if you can't find it. Don't paste the key into the chat.)
   - Type `/check-setup`. The Perplexity line should say it works.
3. **Check your rules.** The reviewer checks every post against `context/voice-and-style.md` and `context/offers.md`, and skips any rule still marked TODO. Make sure "Words and phrases we never use", "Post length", "Prices in blog posts", "Competitors and alternatives buyers consider", and "Claims we must never make" are filled in. Check that the Blog URL in `context/settings.md` is the page that lists your posts, so the agent can link to them.
4. **Check a draft.** Type `/check-post`. It picks your newest draft that hasn't been reviewed, or that you've changed since its last review. To choose one, add its name, like `/check-post how-to-choose-a-payroll-provider`. It usually takes a couple of minutes and runs on its own:
   - The **Source Finder** finds a credible source for every `[SOURCE NEEDED]` mark: original studies, government or industry data, well-known publications, or official documentation, never a competitor's blog. Perplexity suggests up to three sources per fact, with the sentence on each page that supports it. The Source Finder opens the best one to confirm the claim is really there, and tries the next if it isn't. If the page says something different, it changes your sentence to match the source. If no solid source exists, it rewrites the claim so it doesn't need one, or cuts it. It also adds 2-4 links to your own related posts.
   - The **Reviewer** checks the post without seeing the brief or any of the writer's notes, the way a new editor would. It checks the structure, every style rule, every claim you've said never to make, every fact against the supporting sentence saved from its source page (opening the page itself when that sentence isn't clear), every FAQ answer, the length, and every link.
   - If the review fails, the writer fixes only the items the reviewer listed, and the reviewer re-checks just those items and the lines that changed, for up to two rounds of fixes.
5. **Read the result.** The chat shows **PASS**, or a **Needs you** list of what's still wrong, each item quoting the problem and naming the rule it breaks. Fix those by hand or with `/revise-post`, then run `/check-post` again. If an item comes from a rule you don't agree with, change the rule instead.
6. **Spot-check the sources.** Open the sources file next to your draft in `output/drafts/`. It lists every claim, its link, and the sentence on the page that supports it. Click two or three links and see for yourself.
7. **Save and sync.** Ask Claude Code to commit and push.

Your post log now shows each checked post as `reviewed` or `needs attention`. If you change a checked post with `/revise-post`, its status goes back to `draft`, and the next `/check-post` checks it again.

**What it costs:** no paid DataForSEO calls. With a Perplexity key, each post makes one small Perplexity call per fact, usually a few cents per post in total; the run log in `output/logs/` shows the number of calls and the exact cost. Everything else uses web search and page reads, which are part of your Claude plan.

### The finish-line test

Pick three facts in your checked post and click their links. *Does each page say exactly what your post says?* Then read the review file. *Is every item it flagged something you'd want fixed?* If yes to both, the Source Finder and Reviewer work. If the reviewer flags things you don't care about, loosen that rule in your context files; if it misses things you'd catch, add a rule.

---

## Folder map

```
CLAUDE.md                 Master instructions Claude Code reads every time
context/                  Your business: ICP, offers, voice, example posts,
                          settings, and topic scoring rules
my-sources.md             Where your meeting notes and emails live (you create this)
templates/                The post structure and HTML shell every post uses
.claude/agents/           The agents that do the work: Topic Researcher, Writer,
                          Source Finder, and Reviewer
.claude/skills/           Commands you can type, like /write-post and /check-post
output/topics/            Topic shortlists, with your approve and reject decisions
output/drafts/            Post drafts, with their briefs, sources, and reviews
output/logs/              A short log of each run: data used and cost
output/posts/             Finished posts land here
post-log.csv              A record of every post
tools/                    Small scripts the agents run, like the Perplexity source search
docs/                     Build plan and how to get template updates
.env                      Your keys (you create this; it is never uploaded)
```

## Getting updates from the class template

See [docs/updating-from-template.md](docs/updating-from-template.md).
