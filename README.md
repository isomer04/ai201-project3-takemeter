# TakeMeter

TakeMeter is a fine-tuned text classifier that sorts crypto-community posts by the *quality of the take* — not whether a post is bullish or bearish, but whether it's grounded in real, checkable evidence. It's a narrow slice of what commercial crypto-sentiment classifiers (Augmento, LunarCrush, Santiment, StockGeist) sell at scale: separating signal from noise.

> **Status:** Community/label design, dataset collection + annotation, fine-tuning, and the zero-shot baseline are complete; the evaluation report below is written from the actual Colab run (test set = 23 posts). The Hugging Face Hub model push and the live Gradio demo are the only remaining steps and are still marked **Pending**. See [planning.md](docs/planning.md) for the full design rationale and the working annotation notes.

## Demo

**[▶ Watch the walkthrough (Loom)](https://www.loom.com/share/b1a6d49f7665437db84418751f383359)** — video walking through the project, the labels, and the evaluation findings.

## Repo structure

| Path | Purpose |
|---|---|
| `app.py` | Gradio demo — paste a post, get a label + confidence. Also the entrypoint for the deployed Hugging Face Space. |
| `classifier.py` | `TakeClassifier` — the single inference engine used by both `app.py` and `evaluate.py`. |
| `evaluate.py` | Reproduces the notebook's locked test split locally and evaluates the fine-tuned model — no API key needed. |
| `groq_baseline.py` | Standalone zero-shot baseline against the same test split (`GROQ_API_KEY` required). |
| `config.py` | Label map, model id, dataset path, random seed — single source of truth. |
| `data/takemeter_dataset.csv` | The labeled dataset. |
| `data/taxonomy.md` | Label definitions, decision tree, and edge-case rules — the labeling source of truth. |
| `docs/` | `planning.md` (design rationale), `collecting.md` (annotation cheat sheet). |
| `results/` | `confusion_matrix.png`, `evaluation_results.json` (produced by Colab, committed here). |

**Live demo:** _pending — link added after the model is fine-tuned in Colab and the Space is deployed (see "Fine-tuning approach" below)._

**Run it locally:**

```bash
pip install -r requirements.txt
python app.py          # Gradio demo at http://localhost:7860
python evaluate.py     # reproduces test-set metrics for the fine-tuned model
```

## Community

**[r/CryptoCurrency](https://www.reddit.com/r/CryptoCurrency/)** — one of the largest finance communities on Reddit, with enormous variance in discourse quality within the same thread: a tokenomics breakdown with on-chain numbers can sit three comments above a one-line "🚀🚀 to the moon." Regulars in the community already draw this exact distinction natively, calling weak takes "hopium" or "FUD" — so the labels reflect a real, pre-existing community norm rather than one imposed from outside.

## Labels

Four labels, defined by one decision rule: **if a post backs its claim with real, checkable evidence, it's `signal` — whether bullish or bearish. If there's no real evidence, it's `hype` when positive and `panic` when negative. If there's no take at all, it's `filter`.**

| Label | Definition | Examples |
|---|---|---|
| `signal` | Claim backed by load-bearing, verifiable evidence — on-chain data, a named mechanism, a concrete historical comparison. Direction doesn't matter. | **1.** *"9 UMA whale wallets control 53.1% of voting power. Same wallets fund $12.5M Polymarket side-bets on markets they resolve. The oracle is mathematically incentivized to lie."* <br>**2.** *(bearish)* *"Compare fully-diluted valuations to actual fee revenue: several top-20 chains carry tens of billions in FDV while generating under $100k/day in fees, and most still have heavy token unlocks ahead. That's a steep revenue multiple plus a supply overhang."* |
| `hype` | Bullish claim with no real evidence — bare price targets, FOMO, "to the moon." | **1.** *"SOL is so back. This is the floor, screenshot this. LFG 🚀🚀"* <br>**2.** *"Just put my whole paycheck in, feeling unbelievably bullish rn. Easy 10x, you'll all wish you listened when we're at the moon 🌙"* |
| `panic` | Bearish claim with no real evidence — doom, "scam," nothing behind it. (The community's native term for this is "FUD.") | **1.** *"It's over. Retail gets dumped on again while insiders cash out. The whole space is a rigged casino, I'm done."* <br>**2.** *"Why is nobody talking about how this is obviously going to zero? Get out while you can — they're going to rug us all."* |
| `filter` | No take at all — news links with no body argument, neutral questions, memes. Excluded from training/eval; not part of the 3-way quality taxonomy. | **1.** *"Bitcoin drops 5% after Fed announcement. [link]"* <br>**2.** *"What's everyone's cost basis on ETH right now?"* (neutral question, no stance) |

`signal`/`hype`/`panic` are mutually exclusive and apply to every post that has a stance. `filter` is a gate applied first, before the quality question, so the 3-way taxonomy stays exhaustive over posts that actually express a take. Full definitions, decision tree, and edge-case rules: [data/taxonomy.md](data/taxonomy.md).

## Data collection

**Source:** public posts and comments from r/CryptoCurrency, hand-picked by browsing the sub directly across `hot`/`new`/`top`/`controversial` listings and Daily Discussion threads and manually copying selected posts into the dataset — no scraping or API pull, so every example was read at collection time — see [planning.md §5](docs/planning.md) for the full collection plan and [collecting.md](docs/collecting.md) for the working annotation cheat sheet.

**Labeling process:**
1. **AI-assisted cleaning pass.** After collecting ~250 candidate posts by hand from r/CryptoCurrency, I used Claude to filter out stanceless content (news links, questions, memes, sponsored posts) *before* any quality label was assigned. This left the candidate pool that actually expresses a take, which is what the 3-way taxonomy applies to.
2. **AI pre-labeling.** An LLM (Claude — deliberately *not* the `llama-3.3-70b` model used later as the zero-shot baseline, to keep that comparison honest) pre-labeled each remaining candidate as a starting point, flagged in the `notes` column as `prelabeled`.
3. **Hand-review pass.** Every one of the 206 final rows was then read and hand-reviewed against the [taxonomy](data/taxonomy.md) decision rule. 16 of 206 rows (7.8%) had their label corrected on review; all 206 rows are now marked `[REVIEWED]` in `notes`, with the original prelabel preserved in the note text where it was overridden along with the reasoning for the change. No row is still just `prelabeled` with no human check.

**Label distribution** (206 total rows; `filter` rows are excluded from training/eval):

| Label | Count | % of total | % of usable (153) |
|---|---|---|---|
| `signal` | 65 | 31.6% | 42.5% |
| `panic` | 54 | 26.2% | 35.3% |
| `hype` | 34 | 16.5% | 22.2% |
| `filter` | 53 | 25.7% | — |

No class exceeds 70% of the usable set; every quality class is at or above the 20% floor.

**Three genuinely difficult examples** (full log of these plus three more from the hand-review pass: [planning.md §4](docs/planning.md)):

1. **"I have been a Bitcoiner for a long while... is humanity just too stupid for this to ever stick?"** — long, bearish-feeling, and references a real use case (BTC as inflation hedge) that almost reads as a structural argument. **Decided `panic`**: stripped of its rhetorical framing, there's no actual checkable claim left — just sentiment.
2. **"Btc will never replace fiat."** — appears twice in the dataset: once as a long, fully-argued post (price range, a named source, a structural store-of-value-vs-medium-of-exchange argument → correctly `signal`), and once as a bare one-line duplicate with none of that supporting reasoning. **Decided `panic`** for the bare duplicate — the load-bearing test has to apply to each post's own text, not borrow evidence from a different post making the same claim.
3. **"But man what a deal the whales are going to get when they buy back at $50k."** — names an actor and a specific price level, which initially read as evidence. **Decided `hype`** on review: a specific number isn't the same as a named *mechanism* — there's no argument for why $50k is the level, just a bullish-flavored prediction.

## AI usage

AI was used at three distinct stages of dataset preparation, and a human reviewed its work at each one:

- **AI-assisted cleaning (stanceless filtering).** After hand-collecting ~250 candidates from r/CryptoCurrency, I used Claude to filter out posts that didn't take a stance on the market — news links, pure questions, memes, sponsored content. The remaining posts are the ones the 3-way taxonomy actually applies to. I then re-read the kept posts to confirm nothing load-bearing was dropped, because a headline can mention a number or a named source and still not contain a take.
- **AI pre-labeling.** Claude pre-labeled the remaining candidates as a starting point (flagged `prelabeled` in `notes`); every label was then hand-reviewed and corrected where wrong (16/206 corrected) before being treated as ground truth.
- **Hand-review pass:** Claude was directed to re-read every row against `data/taxonomy.md`'s decision rule rather than trust the prelabel, specifically because the prelabeler's own notes had flagged many rows "re-review recommended." This surfaced a systematic pattern — headline-only link posts were getting prelabeled `signal`/`panic` whenever the headline itself contained a number or named source, when the `filter` rule should have applied regardless of headline content — which a spot-check alone likely would have missed. The correction reasoning for each changed row is recorded directly in the dataset's `notes` column and summarized in [planning.md](docs/planning.md).
- Further AI usage (label stress-testing before annotation, failure-pattern analysis after evaluation) is planned per [planning.md §8](docs/planning.md) but the failure-analysis step depends on Milestone 5 (fine-tuning) being run first.

## Fine-tuning approach

**Base model:** [`distilbert-base-uncased`](https://huggingface.co/distilbert-base-uncased) with a 3-class sequence-classification head (`id2label` taken from [config.py](config.py), so the head's label order matches the rest of the repo). `filter` rows are dropped before training, so the model only ever sees `signal`/`hype`/`panic`.

**Data:** the 153 usable rows, stratified-split 70/15/15 → **107 train / 23 validation / 23 test**. The split is seeded (`random_state=42`) so the test set is reproducible locally via [evaluate.py](evaluate.py).

**Training setup** (HuggingFace `Trainer`):

| Hyperparameter | Value |
|---|---|
| Epochs | 3 |
| Learning rate | 2e-5 |
| Train batch size | 16 |
| Weight decay | 0.01 |
| Warmup steps | 50 |
| Max sequence length | 256 |
| Best-model selection | highest validation accuracy (`load_best_model_at_end`) |

**Key hyperparameter decision — I kept epochs at 3 rather than raising them.** With only 107 training examples spread across 3 classes (and as few as 24 for `hype`), the tempting fix when a class underperforms is "train longer." I deliberately did **not** raise epochs, because the bottleneck here is *data quantity*, not training duration. Re-running this exact notebook (same code, same seed) actually produced two different fine-tuned models with two different weak classes — one run collapsed `hype` to 0% recall while `panic`/`signal` held up; the other (reported below) instead weakened `signal` while `hype` partially recovered. Training longer on a dataset this thin would just let the model memorize whichever idiosyncratic split of 107 rows it gets, not generalize better — it would not fix the underlying problem. The honest fix is more data per class, so I left the training schedule at the documented defaults and treated both the collapse and its instability across runs as findings to analyze (see Evaluation report and Reflection).

Once training completes in Colab, the model is pushed to the Hugging Face Hub
(`model.push_to_hub(...)`, `tokenizer.push_to_hub(...)`) and `config.HF_MODEL_ID`
is updated to point at it — `classifier.py` and the deployed Gradio Space then
load the same weights with one line, no local training required. **(Hub push still pending.)**

## Baseline

**Model:** `llama-3.3-70b-versatile` via the Groq API, **zero-shot** (no task-specific training), `temperature=0`, `max_tokens=20`, run on the **same locked 23-post test split** as the fine-tuned model.

**Prompt:** a system prompt that states the task (judge take-quality on r/CryptoCurrency), gives the plain-language definition of each label straight from [taxonomy.md](data/taxonomy.md) plus one example post per label, and instructs the model to output **only** the label name. The notebook then matches the model's reply to one of `signal`/`hype`/`panic`; any reply that matches no label is flagged unparseable (the notebook prints the count, and warns if it exceeds ~10%).

**Result:** overall accuracy **0.783** — see the Evaluation report for the side-by-side and per-class breakdown.

## Evaluation report

All numbers below are on the **same locked 23-post test set**.

### Overall accuracy

| Model | Accuracy |
|---|---|
| Zero-shot baseline (`llama-3.3-70b`) | **0.783** |
| Fine-tuned DistilBERT | **0.522** |
| Difference | **−0.261** (fine-tuning *regressed* vs. baseline) |

The fine-tuned model lost to the zero-shot baseline by a wide margin. That is the central finding of this evaluation, and the rest of this section explains why — it is a data-quantity/class-imbalance failure, not a pipeline bug.

### Per-class metrics — fine-tuned model

Computed from the confusion matrix below; matches the `classification_report` printed by the notebook.

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `hype` | 0.67 | 0.40 | 0.50 | 5 |
| `panic` | 0.43 | 0.75 | 0.55 | 8 |
| `signal` | 0.67 | 0.40 | 0.50 | 10 |
| **macro avg** | 0.59 | 0.52 | 0.52 | 23 |
| **weighted avg** | 0.58 | 0.52 | 0.52 | 23 |

The headline this run: **`signal` recall dropped to 0.40** — the model misses 6 of its 10 true `signal` posts, almost all of them absorbed into `panic`. `hype` is still the weakest class by F1 (0.50, tied with `signal`), but it's no longer a total collapse like an earlier run produced (see the note on run-to-run instability below). `panic` is over-predicted across the board: 14 of 23 posts were classified `panic` even though only 8 actually are.

### Per-class metrics — baseline (`llama-3.3-70b`)

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| `hype` | 0.67 | 0.80 | 0.73 | 5 |
| `panic` | 0.78 | 0.88 | 0.82 | 8 |
| `signal` | 0.88 | 0.70 | 0.78 | 10 |
| **macro avg** | 0.77 | 0.79 | 0.78 | 23 |
| **weighted avg** | 0.80 | 0.78 | 0.78 | 23 |

The contrast with the fine-tuned model holds across every class: baseline beats fine-tuned on `hype` (0.73 vs 0.50), `panic` (0.82 vs 0.55), and `signal` (0.78 vs 0.50) F1. The zero-shot model never saw a single training example for any of these classes and still outperforms a model trained directly on 107 labeled posts, because it brings pretrained world knowledge of what each kind of take sounds like — knowledge that 107 examples can't replace.

### Confusion matrix — fine-tuned model (test set)

Rows = true label, columns = predicted label.

| True ↓ \ Pred → | `hype` | `panic` | `signal` | Total |
|---|---|---|---|---|
| **`hype`** | **2** | 2 | 1 | 5 |
| **`panic`** | 1 | **6** | 1 | 8 |
| **`signal`** | 0 | 6 | **4** | 10 |
| **Total predicted** | 3 | 14 | 6 | 23 |

The dominant pattern is the **`signal` row**: 6 of 10 true-`signal` posts were misread as `panic`, and zero `signal` posts were ever called `hype`. `panic` absorbs errors from every other class (2 from `hype`, 6 from `signal`) and is over-predicted overall (14 of 23 calls). `hype` does get predicted occasionally this run (3 times total, 2 of them correct) — a partial recovery compared to a prior run where the `hype` column was entirely empty (see the run-to-run note below).

### Wrong predictions, analyzed

The fine-tuned model missed **11 of 23** test posts. The dominant pattern is `signal` → `panic` (6 posts); the rest are 3 `hype` misses (2 → `panic`, 1 → `signal`) and 2 `panic` misses (1 → `hype`, 1 → `signal`). Three representative cases:

**1. `signal` → `panic`** (confidence 0.34) — *"just your daily reminder that FTX held 7.84% of Anthropic. Anthropic's latest reported valuation: ~$965B implied former FTX stake: ~$75B before dilution FTX hole: ~$8.9B food for thought"*
This is exactly the kind of post `signal` is supposed to capture — specific percentages, a named entity, a derived dollar figure, a checkable claim. But the language is saturated with loss-coded vocabulary ("FTX hole," a bankrupt exchange, dilution) and the model appears to key off that negative framing rather than the underlying evidentiary structure. A post can be analytically rigorous *and* read as bad news, and the model conflates "sounds bad" with `panic` regardless of whether there's a checkable claim underneath.

**2. `signal` → `panic`** (confidence 0.34) — *"It is actually more profitable now to rent out GPU time to Ai than it is to mine w/ ASICs"*
A genuine `signal` post — it makes a specific, checkable economic comparison (mining profitability vs. GPU-rental profitability) — but it's short and doesn't use any of the citation-heavy phrasing (named sources, percentages, dollar figures) that dominates the longer `signal` examples in the 107-row training set. With so few training rows, the model may have implicitly learned "long and numerically dense" as a proxy for `signal` rather than the actual evidence test, so a terse-but-valid argument like this one falls through.

**3. `hype` → `signal`** (confidence 0.35) — *"Time to start buying. I had buys set at 60k for awhile. Will buy more at 55 and 50 and 45 if it gets there. I am betting on BTC going to around 200k next cycle..."*
The same error as in an earlier run: dense with specific numbers (60k/55/50/45/200k), which the model treats as a proxy for evidence. Per the taxonomy's own **"decorative single-stat / price-target" rule**, bare price targets are `hype`, not `signal` — there's no mechanism, just a prediction. This is the one error pattern that recurred identically across both training runs, which makes it the most robust finding in this whole evaluation: the model reliably substitutes "contains numbers" for "is evidence."

**Common thread:** the model isn't applying the taxonomy's actual decision rule (does this claim survive without the opinion framing?). It's using two cheaper proxies instead — *negative-sounding words ⇒ `panic`* and *numeric density ⇒ `signal`/non-`panic`* — and those proxies are wrong often enough, on a dataset this size, to misfire on genuinely evidence-backed posts that happen to sound bad, and to misfire on evidence-free posts that happen to be number-dense.

**A second finding, from the confidence values: every single prediction in this run — right or wrong — falls in a 0.34–0.35 band**, essentially indistinguishable from the 0.333 a uniform 3-way guess would produce. This is stronger than just "the model is unsure when it's wrong" — it's unsure *all the time*, including when it happens to be correct. That's consistent with a model that, on 107 training examples spread across 3 overlapping classes, never developed a confidently-separated decision boundary for any class — it landed on a weak, noisy heuristic rather than a wrong-but-confident one.

**A third finding worth being explicit about: this failure mode is not stable across training runs.** Re-running this exact notebook (same code, same data, same seed) on a fresh Colab session produced a *different* fine-tuned model where `hype` collapsed to 0% recall instead of `signal`. Two runs of an identical pipeline producing two different "broken" classes is itself a diagnosable result: it shows the training process isn't converging to a single, reproducible decision boundary on a dataset this small — small perturbations in initialization or GPU non-determinism are enough to flip which class the model fails to learn. That instability is a symptom of the same root cause as everything else in this report: not enough data per class to pin down a stable boundary.

### Sample Classifications

Fine-tuned model on a handful of test posts, with predicted label and confidence (softmax probability of the predicted class).

| Post (truncated) | True | Predicted | Confidence |
|---|---|---|---|
| Time in the market basically always beats timing the market. If you have access to 0% inte… | `signal` | `signal` | 0.34 |
| How else is Trump supposed to get his cut? He didn't make world liberty financial for noth… | `panic` | `panic` | 0.35 |
| Just a reminder to everyone else, just because this dude won the 50/50 between life destru… | `hype` | `panic` | 0.35 |
| Time to start buying. I had buys set at 60k for awhile. Will buy more at 55 and 50 and 45 … | `hype` | `signal` | 0.35 |
| Some only care what they make this week or month, and if BTC goes down they will think you… | `hype` | `panic` | 0.34 |

*One correct example explained:* the first row — "Time in the market basically always beats timing the market..." — is correctly tagged `signal` because it makes a structural, checkable argument (access to 0% interest rates as a specific, named factor in the timing-vs.-holding comparison) rather than asserting a price prediction. It's a reasonable call, though worth noting honestly: at 0.34 confidence, the model is barely more sure of this correct answer than it is of any of its wrong ones — it landed on the right label without a strong internal signal that it was right, which fits the broader near-chance-confidence pattern across this entire run.

## Reflection — what the model learned vs. what I intended

**Intended:** a *direction-agnostic* take-quality classifier. The decision boundary I designed (see [taxonomy.md](data/taxonomy.md)) is "is the claim backed by load-bearing, checkable evidence?" — `signal` if yes, and `hype`/`panic` split by sentiment only *after* evidence is ruled out. Direction (bullish or bearish) was explicitly supposed to be irrelevant to the hard part — a post can be `signal` whether it's good news or bad news, as long as it's checkable.

**Learned:** something closer to a sentiment-and-density classifier than an evidence classifier. The errors show two cheap proxies standing in for the real rule:
- **Negative-sounding language ⇒ `panic`**, even on posts with genuine load-bearing evidence (the FTX/Anthropic stake breakdown is the clearest example — rigorous, but reads as bad news, and gets `panic`'d).
- **Numeric density ⇒ `signal`/non-`panic`**, even when the numbers are bare price targets with no mechanism behind them (the "buying at 60k, betting on 200k" post — `hype` by the taxonomy, called `signal` by the model).

So direction, which I explicitly designed to *not* matter, ended up mattering more than the evidentiary structure I designed the labels around. The model partially recovered the sentiment axis (positive/negative) it was never asked to learn on its own, instead of the evidence axis it was asked to learn.

**The most important finding came from comparing two training runs of the identical pipeline.** The first run collapsed `hype` to 0% recall while `panic`/`signal` held up reasonably (F1 0.57/0.70); re-running the same notebook on the same data produced a model that instead weakened `signal` (F1 dropped to 0.50, dominated by `signal`→`panic` errors) while `hype` partially recovered. Two different "broken" classes from one unchanged pipeline means the specific failure mode isn't a stable thing the model reliably learns wrong — it's *noise*, consistent with 107 training rows split across 3 overlapping classes not being enough to pin down a reproducible decision boundary at all. Reinforcing this: in both runs, every prediction's confidence — right or wrong — sits within a few points of chance (1/3 for 3 classes). The model isn't confidently wrong in a consistent way; it's weakly, almost randomly positioned near the boundary between all three classes. That is a more honest and more useful finding than "the model is biased toward panic" would have been, because it points squarely at *data volume* as the fix rather than at a specific mislearned rule that could be patched with a better prompt or a reweighted loss.

## Spec reflection

**One way the spec helped:** the spec's "Reading Evaluation Output" table and the Milestone 5 checkpoint *named this failure mode in advance* — "One class F1 ≈ 0 → model can't learn that boundary, check labels and examples," and "if the fine-tuned model performs worse than the baseline, investigate class imbalance." When a class came back near zero, that turned a discouraging result into a predicted, explainable one and pointed me straight at training-set size as the cause, instead of burning time tuning hyperparameters that were never the problem.

**One way the implementation diverged:** the spec frames the whole project as living inside the Colab notebook — upload CSV, run cells, download outputs. This implementation diverged by restructuring into a standalone local repo: [config.py](config.py) as a single source of truth for the label map and seed, [classifier.py](classifier.py) as one shared inference engine, [evaluate.py](evaluate.py) to reproduce the locked split and re-score the fine-tuned model locally, [groq_baseline.py](groq_baseline.py) for the baseline, and a Gradio [app.py](app.py), with the trained weights handed off via the Hugging Face Hub. The reason was reproducibility and deployability — being able to re-derive the exact test set and re-run both models outside a transient Colab session — at the cost of more moving parts than the single-notebook workflow the spec assumes.
