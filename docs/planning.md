# TakeMeter — Planning

*Written before data collection (Milestone 2). This is my design thinking and working notes; the polished, reader-facing version lives in `README.md`.*

## 1. Overview

**TakeMeter** is a fine-tuned text classifier that sorts crypto-community posts by the *quality of the take* — not by whether the post is bullish or bearish, but by whether it is grounded in real evidence.

This is a small version of something people actually pay for. Companies like **Augmento** (ML classifiers trained on ~32k manually labeled crypto posts), **LunarCrush**, **Santiment**, and **StockGeist** all sell roughly the same product: separating actionable signal from noise, and distinguishing temporary hype from substantive sentiment. TakeMeter does a narrow slice of that — three classes, one clean decision boundary — and then honestly measures where it works and where it falls apart.

## 2. Community

**Chosen community: [r/CryptoCurrency](https://www.reddit.com/r/CryptoCurrency/).**

It is a strong fit for a discourse-quality classifier for three reasons:

- **Scale and activity.** One of the largest finance communities on Reddit (millions of subscribers, hundreds of new comments per hour), so collecting 200+ public examples is easy and I can be selective about quality.
- **Quality is genuinely all over the map.** The same thread routinely contains a deeply-researched tokenomics breakdown three comments above a one-line "🚀🚀 to the moon." That variance is exactly what makes the classification task non-trivial and interesting.
- **The distinction matters to participants.** Regulars in the community openly distinguish "actual DD/analysis" from "hopium" and "FUD" — those are native terms there. So the labels reflect a real distinction the community itself cares about, not one I imposed from outside. (I label the "FUD" class `panic` — same community-recognized concept, clearer label string.)

## 3. Label Taxonomy

The full label taxonomy — definitions, the one-rule decision boundary,
illustrative examples per label, and hard-edge-case rules — lives in
[`data/taxonomy.md`](data/taxonomy.md). That file is the single source of
truth; this section just points at it so the plan stays scannable.

**TL;DR:** three mutually exclusive labels (`signal` / `hype` / `panic`)
drawn by one sentence: *if the post backs its claim with real, checkable
evidence, it is `signal` — whether bullish or bearish; if not, it is
`hype` when positive and `panic` when negative.* See `data/taxonomy.md`
for definitions, examples, and edge-case decision rules.

## 4. Hard Edge Cases

Edge-case *rules* (decorative single-stats, technical analysis, sarcasm,
stanceless posts) are documented in `data/taxonomy.md` so they live next
to the labels they apply to. This section keeps only the running
*difficult-cases log* — real posts I wrestled with during annotation.

> *Difficult cases log — filled during Milestone 3 annotation:*
>
> 1. **`signal` vs `panic` — "I have been a Bitcoiner for a long while, through several cycles..."** (long Bitcoiner post, lines 414–424 of raw file). Long bearish-feeling post: "less confident than I ever have," "floundering," "is humanity just too stupid for this to ever stick?" But the post also makes a structural argument (BTC isn't picking up the inflation-hedge use case it should have after 2026) and references a specific historical shift (Pre-COVID vs Post-COVID inflation awareness). **Decided: `panic`** because the load-bearing claims are rhetorical and emotional, not data-grounded. The "structural argument" is a vibe, not an argument with a verifiable mechanism. **Why it's hard:** length + named use case (inflation hedge) make it *feel* analytical, but stripping the opinion framing leaves no checkable claim. **Re-review strongly recommended** — this one could flip to `signal` if a stricter reading accepts "BTC failing to be adopted as inflation hedge" as a verifiable structural claim.
>
> 2. **`signal` vs `panic` — "Btc will never replace fiat."** (long structural bearish post, lines 752–761). Bullish-or-bearish sentiment split: cites a specific price correction ($124k → $60k range), references Cramer's "bad money" claim, makes a structural argument about BTC as a store of value vs. medium of exchange. **Decided: `signal`** because the price range is verifiable, the Cramer reference is named/quoteable, and the medium-of-exchange argument is a load-bearing structural claim (not panic). **Why it's hard:** bears all the surface markers of panic (bearish, 'bitter pill to swallow,' 'disappointed') but the post reasons about token economics structurally. The sentiment-decoration test in §4 says this passes.
>
> 3. **`panic` vs `signal` — "Bitcoin has no fundamentals, it has no assets or income to underpin its valuation..."** (one-line comment in the all-in thread, lines 1451–1455). Short bearish claim with a load-bearing structural assertion: BTC has no fundamentals / no income. **Decided: `panic`** because (a) the claim is bare assertion without mechanism — *what* would BTC fundamentals look like, *how* does that compare to gold's, *what* does "no income" mean for a non-dividend-paying store of value? The post asserts the conclusion but does not reason to it. **Why it's hard:** the surface statement is arguably a verifiable methodological claim, and a stricter reading could call it `signal` for that reason. Default `panic` because the planning.md §4 evidence rule says bare assertion doesn't qualify. **Re-review recommended.**
>
> *Annotation note (2026-06-21, batch 1):* 77 rows in `takemeter_dataset.csv`, all `prelabeled`. Per planning.md §8, the prelabels are starting points, not ground truth — every row needs hand review before training. Current distribution: 24 `signal` / 15 `panic` / 7 `hype` / 31 `filter` (stanceless or sponsored). Imbalance problem: `hype` is severely underrepresented (7/46 usable = 15%) and `signal` is the majority (52%). Need to collect ~50 more `hype` examples and ~25 more `panic` examples before training. `signal` is fine, can thin out.
>
> *Annotation note (2026-06-21, batch 2 — final):* 206 rows in `takemeter_dataset.csv`, all `prelabeled`. Distribution: 77 `signal` (46.7%) / 54 `panic` (32.7%) / 34 `hype` (20.6%) / 41 `filter`. Usable total: 165. All spec floors satisfied: 200+ examples ✓, no class > 70% ✓, every class ≥ 20% ✓. `hype` is still the smallest usable class but now above the 20% floor. The 70/15/15 split will leave ~25 examples per class in the test slice — enough for a per-class F1 signal. The next step is hand review of every row's label (prelabels are starting points, not ground truth).
>
> *Hand-review pass (2026-06-21, batch 3 — final):* Read every one of the 206 rows against the `data/taxonomy.md` decision rule and corrected the prelabel where it didn't hold up. 16 of 206 rows (7.8%) changed label; all 206 rows are now marked `[REVIEWED]` in `notes` (no `prelabeled`-only rows remain). New distribution: `signal` 65 (31.6%) / `panic` 54 (26.2%) / `hype` 34 (16.5%) / `filter` 53 (25.7%); usable total 153, with signal 42.5% / panic 35.3% / hype 22.2% of the usable set — every spec floor (no class >70%, every class ≥20% of usable) still holds.
>
> Two systematic problems drove most of the corrections, not one-off mistakes:
> 1. **Headline-only link posts kept getting prelabeled `signal` or `panic` whenever the headline itself contained a number or named source** (e.g. "TradFi plans to deploy $650 million...", "Iran reportedly funneled billions through Binance..."). The `filter` rule is about whether the *poster* made an argument, not whether the *headline* contains data — a specific dollar figure sitting in a news headline with no body text is still link aggregation, not a take. 9 of the 16 corrections were this pattern. Posts that weren't headline-links (e.g. the senator quote, a vague "easy to track" prediction, a bare price level, a bare one-liner duplicate of a fully-argued post elsewhere) got individually re-judged against the bare-assertion rule instead.
> 2. **The prelabeler flagged its own uncertainty ("Re-review recommended") on most of these rows**, and on review nearly every flagged row did need to flip — the prelabeler's instinct that something was off was usually right, but its default (favor `signal`/keep direction) was usually the wrong resolution.
>
> Three genuinely hard calls from this pass, beyond the three already logged above:
> 4. **`hype` vs `filter` — "may i interest you in a USD1 ?"** A one-line sarcastic jab referencing Trump's USD1 stablecoin. The prelabel's own note was self-contradictory, flagging both `hype` and `filter` in the same breath. **Decided: `filter`** — once the joke format is stripped, there's no actual claim about USD1's quality, just a meme reference. **Why it's hard:** sarcasm about a real, named financial product reads as more substantive than it is; the named-entity reference doesn't make it evidence.
> 5. **`signal` vs `panic` — "Btc will never replace fiat." as a bare one-liner.** The exact same thesis, fully argued with a price range and a named source (Cramer), appears as its own full post elsewhere in the dataset and correctly stays `signal` there. **Decided: `panic`** for the bare duplicate — the taxonomy's "load-bearing" test has to apply to *this specific post's* text, not to evidence that lives in a different post. **Why it's hard:** it's tempting to let a strong claim borrow credibility from elsewhere in the dataset; the rule has to be applied post-by-post.
> 6. **`signal` vs `hype` — "But man what a deal the whales are going to get when they buy back at $50k."** Names an actor (whales) and a price level ($50k), which made the prelabeler call it `signal`. **Decided: `hype`** — naming a price level isn't the same as naming a mechanism; there's no argument for *why* $50k specifically, just a bullish-flavored prediction. **Why it's hard:** specificity (a concrete number) is easy to mistake for evidence, but the number itself isn't load-bearing here the way a percentage or an on-chain stat is elsewhere in the dataset.

## 5. Data Collection Plan

**Source:** public posts and comments from r/CryptoCurrency. Comments (especially in Daily Discussion threads) are the richest source of takes, so they're the bulk; substantive self-posts count too.

**Method — manual copy-paste hand-pick (what I actually did):**
1. Browse r/CryptoCurrency directly in the browser across `hot`, `new`, `top` (week/month), `controversial`, and the Daily Discussion threads, and **manually copy the text** of posts and comments I judged useful straight into the dataset.
2. **Read and select each one by hand** as I copied it — no scraping, no automated pull. This kept me close to the data and let me deliberately hunt for the full quality spectrum and balanced classes, instead of inheriting whatever bias a "top posts" scrape would give. The trade-off vs. a script: slower and a smaller candidate pool, but every example was read at collection time.
3. Filter out stanceless posts (news/questions/memes) during selection, per the edge-case rule above.

*(Original plan was a PRAW script to gather a 600–1000 candidate pool; in practice I collected by hand directly from the sub, which is why the pool is smaller but every example was deliberately chosen.)*

**Per-label target:** roughly even — about **70–90 examples per label**, **no label above 70%** of the set, every label **≥20%** (spec floor). Slightly over-collecting (~250 for a 200 minimum) ensures the automatic 70/15/15 split still leaves a usable per-class count in the 15% test slice.

**If a label is underrepresented after the first pass:** targeted second pass. `panic` tends to spike in `controversial`/bear-market threads; `signal` clusters in posts containing links, charts, or data. I'll search those slices specifically rather than collect more random posts (which would just inflate the majority class).

**Storage:** a single CSV in the repo with columns `text`, `label`, and `notes` (notes capture difficult-case reasoning and a `prelabeled` flag — see AI Tool Plan). One combined file, **not** pre-split — the notebook does the 70/15/15 split itself.

## 6. Evaluation Metrics

Accuracy alone is not enough: on a 3-class subjective task, a model can post decent accuracy while completely failing one class. So I'll report, for **both** the fine-tuned model and the baseline, on the same locked test set:

- **Overall accuracy** — headline sanity number, but never the only one.
- **Per-class precision, recall, and F1** — the core of the evaluation. These reveal *which* distinction the model learned and which it didn't.
- **Macro-F1 as the single headline metric.** Macro (unweighted mean across the three classes) rather than weighted, because I care equally about all three — especially the hard `signal ↔ hype` boundary — not just whichever class ends up most common. A collapsed minority class tanks macro-F1 even when accuracy looks fine.
- **Confusion matrix.** The *direction* of errors is the most actionable output: a cluster at (true=`signal`, pred=`hype`) means the model is missing evidence and defaulting to sentiment — a specific, diagnosable failure I can write about.

**Why these for this task specifically:** the interesting failures here are boundary confusions, not raw accuracy. Macro-F1 plus the confusion matrix surface exactly those; accuracy would hide them.

## 7. Definition of Success

Concrete, checkable thresholds (so at the end I can objectively say whether I hit them):

- **Primary:** fine-tuned **macro-F1 ≥ 0.70** *and* it **beats the `llama-3.3-70b` zero-shot baseline's macro-F1 by ≥ ~10 points.** Beating the baseline is the whole point — it's what tells me fine-tuning actually added value.
- **No collapsed class:** **every per-class F1 ≥ 0.55.** A model that nails two classes and ignores the third hasn't learned the taxonomy.
- **"Good enough to deploy" in a real community tool:** macro-F1 **~0.75+** with **high `signal` precision** specifically — if the tool flags a post as `signal`, that post should almost always be genuinely substantive, because a "quality filter" that cries wolf is worse than none.
- **Honesty guardrail:** if accuracy exceeds **~95%** on this subjective task, I'll treat it as a red flag (test-set leakage, or labels too easy) and investigate before trusting it — per the spec's own warning.

## 8. AI Tool Plan

There's no application code to generate here, so AI tools help in three specific places:

- **Label stress-testing (before annotating).** Give Claude the three definitions and the decision boundary, and ask it to generate 5–10 posts that sit *between* two labels. If I can't classify any of them cleanly with my rules, my definitions are too loose — I'll tighten them *before* committing to 200 labels.
- **Annotation assistance (pre-labeling).** I will use an LLM to **pre-label** the candidate pool to speed up annotation, then **read and correct every single label by hand** — my reviewed labels are ground truth, no rubber-stamping. **Critical choice:** I'll pre-label with **Claude, not `llama-3.3-70b`**, because llama is my zero-shot *baseline*; pre-labeling with the baseline model and accepting its answers would grade the baseline against its own output and inflate it. Using a different model keeps the baseline comparison honest. I'll flag pre-labeled rows in the `notes` column (`prelabeled`) and **disclose this in the README AI-usage section.**
- **Failure analysis (after evaluation).** Paste the fine-tuned model's misclassified test examples into an LLM and ask it to spot systematic patterns (a recurring confused label pair, sarcasm, short/low-information posts, etc.). Then **verify every proposed pattern myself by re-reading the examples** before writing it up — the LLM surfaces candidates, it doesn't get the final word.

## 9. Planned Stretch: Deployed Interface

*(Committing to this one stretch now; per the spec I'll update this section before starting any others.)*

A simple interface that accepts a new post, runs it through the fine-tuned classifier, and displays the predicted label plus confidence (softmax probability).

- **Serving the model:** save the fine-tuned DistilBERT artifact from Colab — either push to the HuggingFace Hub or download the weights and commit/load them locally.
- **UI:** a minimal **Gradio** app (one textbox in, label + confidence bars out) — easiest to run from Colab or locally, and the interface code commits cleanly to the repo.
- **Docs:** README will document how to run it.

Other stretch options (inter-annotator reliability, confidence calibration, systematic error-pattern analysis) remain open and will be planned here before I start them.

---

### Requirement coverage (Milestone 2 checklist)

| Required question | Section |
|---|---|
| Community + why | §2 |
| Labels (definitions + 2 examples each) | §3 |
| Hard edge cases + handling | §4 |
| Data collection plan + imbalance remedy | §5 |
| Evaluation metrics + why | §6 |
| Definition of success (specific threshold) | §7 |
| AI Tool Plan (stress-test / annotation / failure analysis) | §8 |
