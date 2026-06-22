# TakeMeter — Label Taxonomy

This is the **single source of truth** for TakeMeter's four labels.
The plan that led here lives in `../planning.md`; the working annotation
cheat-sheet (decision tree + test cases) lives in `../collecting.md`.
If anything in those files disagrees with this one, this file wins.

Use these labels when annotating `takemeter_dataset.csv`. Three of them
(`signal`/`hype`/`panic`) capture the **quality of the take** — whether a
post is grounded in real, checkable evidence — not whether it is bullish
or bearish. The fourth (`filter`) is a gate that runs first: it marks
posts that express no take at all, so they never reach the quality
question.

---

## The decision boundary (the one rule)

> **If the post backs its claim with real, checkable evidence, it is `signal` — whether bullish or bearish. If there is no real evidence, it is `hype` when the post is positive and `panic` when the post is negative.**

"Evidence" means something a reader could actually verify or reason about:
on-chain data, tokenomics, a specific mechanism, a fundamentals argument,
or a concrete historical comparison. Sentiment only becomes the deciding
factor *after* evidence is ruled out.

```txt
                        ┌─ YES ──► signal
post backs claim with   │
real, checkable evidence?
                        └─ NO
                            │
                            ├─ Bullish / excited ──► hype
                            └─ Bearish / panicky ──► panic
```

---

## Labels

### `signal`
The post makes a claim and supports it with specific, verifiable evidence
— on-chain metrics, tokenomics, a described mechanism, fundamentals, or a
concrete historical comparison. The evidence is **load-bearing**: it would
still support the claim if you stripped away the opinion framing. Direction
(bullish or bearish) does not matter.

**Key signal:** Removing the opinion framing still leaves a claim the
evidence actually supports.

**Illustrative examples:**
- *(bullish)* "ETH has been net deflationary since the Merge — roughly 1.2M ETH net burned over the past year per ultrasound.money — while staking now locks ~28% of supply and Dencun cut L2 fees ~90%. The supply/demand structure is stronger than the price implies."
- *(bearish)* "I'm cautious on most 'ETH killers.' Compare fully-diluted valuations to actual fee revenue: several top-20 chains carry tens of billions in FDV while generating under $100k/day in fees, and most still have heavy token unlocks ahead. That's a steep revenue multiple plus a supply overhang."

---

### `hype`
A bullish or excited opinion with **no real evidence** behind it — price
predictions with nothing supporting them, "to the moon," pure emotion or
FOMO. The claim might turn out to be true, but the post *asserts* rather
than *argues*.

**Key signal:** Bullish energy + no mechanism, no data, no source. Strip
the opinion framing and nothing checkable is left.

**Illustrative examples:**
- "SOL is so back. This is the floor, screenshot this. We are NOT staying down here for long. LFG 🚀🚀"
- "Just put my whole paycheck in, feeling unbelievably bullish rn. Easy 10x, you'll all wish you listened when we're at the moon 🌙"

---

### `panic`
A fearful or bearish opinion with **no real evidence** — panic, "this is
a scam," doom with nothing to support it. (The community calls this
"FUD" — fear, uncertainty, doubt; `panic` is the label string for the
same concept, chosen for clarity.)

**Key signal:** Bearish energy + no mechanism, no data, no source. Strip
the opinion framing and nothing checkable is left.

**Illustrative examples:**
- "It's over. Retail gets dumped on again while insiders cash out. The whole space is a rigged casino, I'm done."
- "Why is nobody talking about how this is obviously going to zero? Get out while you can — they're going to rug us all."

---

### `filter`
Not a take at all — the post expresses no stance on an asset or the market,
so it doesn't fit the `signal`/`hype`/`panic` taxonomy in the first place.
This includes pure news links and headline-only posts with no body argument,
neutral or factual questions, memes/jokes with no embedded opinion,
cross-posts and weekly-thread headers, and sponsored/promotional posts.
`filter` rows are excluded from training and evaluation — they exist in
the CSV only as a record of what was reviewed and deliberately excluded.

**Key signal:** Read the post and ask "is there a bullish-or-bearish take
here at all?" If no — not "is the take good or bad," but "is there a take
to judge" — it's `filter`, regardless of sentiment or evidence.

**Illustrative examples:**
- "Bitcoin drops 5% after Fed announcement. [link]" (pure news aggregation, no body opinion)
- "What's everyone's cost basis on ETH right now?" (neutral question, no stance)

---

## Hard Edge Cases

Some posts genuinely sit on a boundary. Each gets an explicit decision
rule *before* annotation so labels stay consistent.

- **Decorative single-stat.** A post drops one cherry-picked number for effect rather than reasoning ("It's down 90% from ATH, it's dead"). **Rule:** evidence must be load-bearing and non-trivial. A single stat used to *decorate* a feeling, not to *build* an argument, does **not** qualify → label by sentiment (`hype`/`panic`). **Test:** if removing the opinion framing leaves a claim the stat actually supports, it's `signal`; if it leaves nothing, it isn't.
- **Technical analysis / price targets.** "RSI is oversold, $10k incoming." **Rule:** a specific, checkable mechanism or method → `signal`; a bare target or "trust me, it's going up" with chart vibes only → `hype` (or `panic` if bearish).
- **Sarcasm / irony.** A post that sounds bullish but is mocking hype (or vice versa). **Rule:** label the author's *genuine* stance, not the surface words. If it's truly undecidable, default to the literal sentiment and record it in the `notes` column. (Sarcasm is a known failure mode — track these for error analysis.)
- **Stanceless posts (exhaustiveness guard).** Pure news links, neutral questions, and memes express no *take*, so they don't fit a three-way take taxonomy. **Rule:** filter these out at collection time rather than create an "other" bucket. This keeps the taxonomy ≥90% applicable to what I actually collect (per the spec's exhaustiveness requirement) by only collecting posts that express a stance.

---

## Valid Labels (for reference)

```
signal
hype
panic
filter
```

These are the only four valid labels. Use exactly these strings in the
`label` column of `takemeter_dataset.csv`. (`panic` is the project's
label for what r/CryptoCurrency calls "FUD".)

`signal`, `hype`, and `panic` are the three-way *take-quality* taxonomy —
mutually exclusive, every post that has a stance gets exactly one.
`filter` sits outside that taxonomy: it's applied instead of a quality
label whenever a post has no take to judge in the first place (see
`filter`'s definition above), and those rows are excluded from training
and eval.
