# TakeMeter — Collector's Cheat Sheet

*Quick reference for collecting and labeling r/CryptoCurrency posts/comments. The full label taxonomy (definitions, key signals, full edge-case rules) lives in `data/taxonomy.md`; the design rationale lives in `planning.md`. This file is just the pocket version for fast annotation.*

---

## The 4 labels (one-sentence each)

| Label | Definition | Direction |
|---|---|---|
| **`signal`** | Claim backed by *load-bearing, verifiable* evidence (on-chain data, mechanism, named source, concrete historical comparison). Bullish or bearish both qualify. | Either |
| **`hype`** | Bullish claim with no real evidence. Price targets with no reasoning, FOMO, "to the moon." | Bullish |
| **`panic`** | Bearish claim with no real evidence. Panic, "scam," doom with nothing behind it. | Bearish |
| **`filter`** | No take at all — news links, neutral questions, memes, sponsored posts. Excluded from training/eval. | N/A |

`signal`/`hype`/`panic` are the three-way take-quality taxonomy. `filter` is a gate applied first — it's not a take-quality judgment, it just means there's no take to judge.

> **The one rule:** *If the post backs its claim with real, checkable evidence, it is `signal` — whether bullish or bearish. If there is no real evidence, it is `hype` when the post is positive and `panic` when the post is negative.* (full version: `data/taxonomy.md`)

---

## Quick decision flowchart

```
Is there a take / stance in the post?
  ├── NO  →  filter (stanceless)
  └── YES
        │
        Does it cite checkable evidence?
        (named source, specific number, mechanism, 
         on-chain data, named historical comparison,
         methodology)
          ├── YES  →  signal
          └── NO
                │
                Is the stance bullish or negative?
                  ├── Bullish / excited  →  hype
                  └── Bearish / panicky  →  panic
```

---

## Evidence-test (the "load-bearing" check)

A piece of evidence is **load-bearing** if removing it makes the argument fall apart. Examples:

- ✅ **Load-bearing:** "ETH has been net deflationary since the Merge — 1.2M ETH burned per ultrasound.money — while staking locks ~28% of supply." (specific numbers + named source)
- ❌ **Decorative:** "It's down 90% from ATH, it's dead." (one cherry-picked stat used to decorate a feeling)

> **Test:** if you strip the opinion framing, does the evidence still support a real claim? If yes → `signal`. If nothing's left → label by sentiment (`hype`/`panic`).

---

## Edge cases (with rules)

| Case | Rule |
|---|---|
| **Single cherry-picked stat** ("down 90% from ATH, dead") | Decorative. Label by sentiment. |
| **Technical analysis with named method** ("RSI oversold, $10k") | Specific mechanism → `signal` if reasoning, else `hype`/`panic` by direction. |
| **Sarcasm / irony** | Label the author's *genuine* stance, not the surface words. If undecidable, default to literal sentiment and flag in `notes`. |
| **Stanceless posts** (news links, neutral questions, memes) | **Filter.** Don't label. |
| **Sponsored/promoted posts** (ads) | **Filter.** Don't label. |
| **One-line comments** ("lol," "agreed," "this") | Usually **filter** — no real take. |
| **Long bearish with named mechanism** | `signal` (sentiment ≠ panic). The Cramer/BTC-as-money post is the model. |
| **Long bearish with no mechanism** | `panic`. |
| **Cross-posts / weekly thread headers** | **Filter.** |

---

## Is this `hype` or `signal`? (test cases)

| Post | Label | Why |
|---|---|---|
| "SOL is so back. This is the floor, screenshot this. We are NOT staying down here for long. LFG 🚀🚀" | `hype` | No evidence, pure emotion. |
| "ETH staking yield + deflationary supply = structurally bullish. Burning ~1.2M ETH/year since Merge while Dencun cut L2 fees 90%." | `signal` | Named mechanism, specific numbers, source. |
| "Bitcoin triggers people. If I dont like something, I stay away from it and ignore it." | `hype` | No claim, just vibes. |
| "If BTC stays above the 200-week MA for another cycle, the historical pattern suggests..." | `signal` | Named method (200-week MA) + historical comparison. |

## Is this `panic` or `signal`? (test cases)

| Post | Label | Why |
|---|---|---|
| "It's over. Retail gets dumped on again while insiders cash out. The whole space is a rigged casino, I'm done." | `panic` | Pure doom, no evidence. |
| "From $124k down to the $60k range. Cramer's right: BTC is bad money. Medium of exchange is dead, store of value only." | `signal` | Named price range, named source, structural claim. |
| "Bitcoin has no fundamentals, no income to underpin valuation, just gambling." | `panic` | Bare assertion, no mechanism. *(Hard case #3 — re-review.)* |
| "9 UMA whale wallets control 53.1% of voting power. Same wallets fund $12.5M Polymarket side-bets on markets they resolve. The oracle is mathematically incentivized to lie." | `signal` | Specific contract data, named addresses, structural mechanism. |

---

## What to collect, where to find it

The dataset is now final at **65 signal / 54 panic / 34 hype / 53 filter (206 total)** in `takemeter_dataset.csv`.

| Slice of r/CryptoCurrency | What you'll find | Use it for |
|---|---|---|
| **Top → This Month** | Self-posts, long DDs | `signal` mostly |
| **Controversial → This Month** | Heated arguments, panic/hype pile-ons | `panic` and `hype` |
| **New**, then filter to **self-posts only** (no link flair) | Avoids the link-aggregator feed you collected from | balanced |
| **Daily Discussion thread** (sort by **Top**) | Hundreds of takes, easy to skim | balanced |
| **r/CryptoCurrency daily discussion** sorted by **Controversial** | The angriest takes in one place | `panic` and `hype` |

**Browser filter while collecting:** discard anything where the post body is one sentence, a link only, or a question. Keep anything with **≥ 3 sentences of opinion**. That alone gets you 70% quality.

---

## Targets

- **~70 examples per class** is the planning.md §5 goal. (`hype` is the bottleneck.)
- **No label > 70%** of the dataset. (Spec floor.)
- **Every label ≥ 20%** of the dataset. (Spec floor.)
- Total target: **~210–250 labeled examples** so the 70/15/15 split leaves usable per-class counts in the 15% test slice.

---

## Per-row CSV format

When adding to `takemeter_dataset.csv`:

```csv
text,label,notes
"Post text goes here, with CSV escaping for any commas or quotes.","hype","Why you chose this label; prelabeled if AI-assisted"
```

**`notes` column** is your audit trail. Use it for:
- `prelabeled` (or `prelabeled; corrected to panic`) — disclosure for AI-assisted labels
- *Hard case reasoning* — e.g., `long bearish with named price range, default signal but could be panic`
- *Why filtered* — e.g., `stanceless news link` or `sponsored ad`

The notebook does the 70/15/15 train/val/test split automatically. **Don't pre-split the file.**
