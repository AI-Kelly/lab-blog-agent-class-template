# Running the blog agent on a schedule

Once `/run-blog-agent` works on your computer, you can have it run in the cloud on a schedule, even when your laptop is closed. Claude calls this a **scheduled task** (some screens still say **routine**).

Each run starts a fresh copy of your repository in the cloud, does a full run, and pushes the results back to GitHub. You check the run report, publish the ready post, and mark approve or reject on new topics. The agent never publishes anything.

Setup takes about 15 minutes, once.

## Before you start

- `/run-blog-agent` has worked at least once on your computer.
- Everything is committed and pushed. Ask Claude Code: *"Commit and push everything."* Your `.env` file stays on your computer; the cloud gets your keys a different way (step 2).
- You're on a Claude Pro plan or higher.

## 1. Connect GitHub to Claude Code on the web

Open [claude.ai/code](https://claude.ai/code). If it asks you to connect GitHub, do it, and give it access to your `blog-agent` repository. If you connected GitHub before, check that this repository is included.

## 2. Make a cloud environment for the agent

The environment decides what the cloud run can reach and holds your keys.

1. At [claude.ai/code](https://claude.ai/code), click the environment selector (it usually says **Default**) and add a new environment. Name it **Blog agent**.
2. **Network access:** choose **Full**. The agent reads Google's top articles and checks source pages on many different websites, so a short list of allowed sites isn't enough.
3. **Environment variables:** add your keys, one per line, copied from your `.env` file:

   ```
   DATAFORSEO_LOGIN=your-login
   DATAFORSEO_PASSWORD=your-api-password
   PERPLEXITY_API_KEY=your-perplexity-key
   ```

   Leave out the Perplexity line if you don't use it. These values are visible only to people who use this environment, which is just you. Don't share the environment with anyone.
4. Leave **Setup script** empty. The agent needs only standard Python, which is already there.
5. Save the environment.

## 3. Check your connectors

Go to [claude.ai → Customize → Connectors](https://claude.ai/customize/connectors) and make sure **Databox** is connected, plus any tools listed in your `my-sources.md` (meeting recorder, Gmail, Google Drive, and so on). Scheduled runs can only use connectors added there, not ones added from the terminal.

## 4. Create the scheduled task

1. Go to [claude.ai/code/routines](https://claude.ai/code/routines) and click **New task** (or **New routine**). If it offers **Create with Claude** or **Set up manually**, choose **Set up manually**.
2. **Name:** Blog agent
3. **Prompt:** copy this exactly:

   > Run the blog agent: follow the /run-blog-agent command in .claude/skills/run-blog-agent/SKILL.md from start to finish. Nobody is watching, so don't ask questions; use the defaults the command describes. Commit and push the results to the repository's main branch, not a new branch.

4. **Model:** choose **Sonnet 5.5**. It does this job well and uses much less of your plan than Opus.
5. **Trigger:** choose **Schedule**. Start with **weekly**, or **weekdays** once you trust it. Pick a time a few minutes past the hour, like 6:07 AM; runs set exactly on the hour can start late.
6. **Repository:** your `blog-agent` repository. **Cloud environment:** Blog agent. (These may be under **Advanced settings**.)
7. **Connectors:** keep Databox and your meeting and email tools. Remove every other connector, so the agent can only reach what it needs.
8. Click **Create**.

## 5. Test it now

On the task's page, click **Run now**. A full run usually takes 15 to 30 minutes.

- Click the run in the **History** list to watch it or read what happened. The last message is a short summary of what you need to do.
- When it's done, open your repository on GitHub. You should see a new commit called "Blog agent run ..." with the run report in `output/logs/`.
- If the run stopped with a question or a permission prompt, answer it in the run, then tell your instructor what it asked, so the command can be fixed.

## 6. After each run

1. Open the run report: `output/logs/<date>-run.md` on GitHub, or the summary at the end of the run.
2. **Before you work on your computer, get the cloud's changes first.** Ask Claude Code: *"Get the latest from GitHub."* Otherwise your computer's copy is behind, and your next push can clash with the cloud's.
3. Do what the report says under **What you need to do**: publish the ready post using its card, fix anything under **Needs you**, or mark approve or reject on a new shortlist.
4. After you publish a post, type `/mark-published <slug> <live URL>`.
5. Commit and push. The cloud only sees what's on GitHub, so your approvals and changes reach the next run only after you push.

## Common problems

| What you see | What to do |
|---|---|
| The report says DataForSEO or Perplexity keys are missing | Check the environment variables in step 2: the names must match exactly, with no spaces around `=`. |
| "Databox tools aren't available" | Connect Databox at claude.ai → Customize → Connectors, and make sure the task's **Connectors** list includes it. |
| No new commit on GitHub | Open the run. If the push failed, the reason is in the summary. Make sure GitHub access includes your repository (step 1). |
| A commit appeared on a branch starting with `claude/` | The prompt didn't say to push to main. Fix the prompt (step 4), then merge that branch on GitHub or ask Claude Code to bring its files into main. |
| "The last run didn't start..." under History | Follow the message. Most often GitHub needs reconnecting, or the environment was deleted. |
| Runs use too much of your plan | Check the model is Sonnet 5.5, run less often, and check usage at [claude.ai/settings/usage](https://claude.ai/settings/usage). |

To pause the agent, use the on/off switch at the top of the task's page.
