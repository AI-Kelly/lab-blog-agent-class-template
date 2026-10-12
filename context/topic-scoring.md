# Topic scoring

> How the Topic Researcher ranks blog topics. You can edit anything here: the definitions, the weights, and the two lists at the bottom. The agent reads this file fresh every run.

## How scoring works

Each topic gets a score from 1 (weak) to 5 (strong) on six criteria. Each score is multiplied by its weight, and the topics with the highest totals go to the top of the shortlist.

To make a criterion count double, change its weight to 2. To make it count less, change it to 0.5.

| Criterion | Weight |
|---|---|
| Buying intent | 1 |
| ICP fit | 1 |
| Search demand | 1 |
| Winnable | 1 |
| AI citation | 1 |
| Offer connection | 1 |

## The six criteria

### Buying intent
How close the searcher is to buying. Comparisons, pricing, "best X for Y", "X vs Y", "how to choose", and "is X worth it" score high. General "what is X" education scores low.
- **5:** They're choosing between options or ready to buy.
- **3:** They know they have the problem and are exploring solutions.
- **1:** They're just learning the topic exists.

### ICP fit
How closely the topic matches the "Questions they ask right before buying" section of `icp.md`, and whether the searcher sounds like the buyer described there.
- **5:** Nearly the same as a question on that list, asked by the right buyer.
- **3:** Related to a question on the list, or asked by an adjacent buyer.
- **1:** Our buyer wouldn't ask this.

### Search demand
How many people search for it each month in your country, from DataForSEO. Buying-stage searches are small by nature, so judge demand against your niche, not against big consumer topics.
- **5:** Clearly one of the bigger searches in your niche.
- **3:** Steady, modest searches.
- **1:** Little or no recorded search volume. (A topic can still win on the other criteria, especially if buyers ask it in meetings or emails.)

### Winnable
How realistic it is to reach page 1. Keyword difficulty (0-100) comes from DataForSEO. Search Console shows whether you already rank on pages 1-2 (positions 1-20) for this search without a post written for it, which is the easiest kind of win.
- **5:** Low difficulty, or you already rank on pages 1-2 without a dedicated post.
- **3:** Medium difficulty and no current ranking.
- **1:** High difficulty, crowded by big brands.

### AI citation
How likely AI assistants (ChatGPT, Perplexity, Google's AI answers) are to quote or cite a post on this topic. They tend to cite pages that answer a specific question directly, compare named options, give clear steps or numbers, or share firsthand experience.
- **5:** A specific question with a clear answer you can give from real experience.
- **3:** A useful topic, but the answer is common knowledge.
- **1:** A broad or opinion-only topic with no clear answer to quote.

### Offer connection
How naturally the post leads to one of your offers in `offers.md`.
- **5:** The post's answer points straight to one of your offers.
- **3:** An offer fits, but the reader needs a step or two to get there.
- **1:** No honest link to anything you sell.

## Ground rules
- Drop any topic that scores 1 on buying intent or offer connection.
- When two topics score the same, prefer the one that came from your own meetings, emails, or Search Console data.

## Never suggest
Topics, keywords, or angles the agent must never put on the shortlist. Add one per line.
-

## Always prefer
Topics, keywords, or angles the agent should favor when scores are close. Add one per line.
-
