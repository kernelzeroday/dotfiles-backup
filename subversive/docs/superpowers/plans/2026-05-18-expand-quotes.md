# Expand Quotes Database — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the embedded quote database from ~1,360 quotes / 209 figures / 23 categories to ~2,500-2,800 quotes / ~350-400 figures / 27 categories.

**Architecture:** A Python merge script (`scripts/expand_quotes.py`) reads the current `data/quotes.json`, merges new quote data defined as Python dicts, validates no duplicates, and writes the combined JSON back. The script is run after each batch of new quotes is added. No Rust code changes — the schema stays `{figure, text, category}` keyed by category.

**Tech Stack:** Python 3 (stdlib only — `json`, `sys`, `pathlib`), Rust (existing — no changes), JSON

---

## File Map

| File | Role |
|---|---|
| `scripts/expand_quotes.py` | **Create.** Merge engine: reads `data/quotes.json`, combines with new quote data, validates, writes back |
| `data/quotes.json` | **Modify.** The quote database — expanded by the merge script |
| `README.md` | **Modify.** Updated counts in header line and stats description |

No other files change.

---

## Merge Script Design

The script has two sections:
1. **Data section** — Python dicts organized by batch, each batch is a `{category: [quotes]}` dict
2. **Engine section** — `main()` reads JSON, merges batches, checks for duplicates, writes output

Each batch variable is named `BATCH_N` so tasks can add new batch variables without touching the engine section.

```python
#!/usr/bin/env python3
"""Merge new quote batches into data/quotes.json."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUOTES_PATH = ROOT / "data" / "quotes.json"

# ── Quote helper ──────────────────────────────────────────────

def q(figure, text, category):
    """Create a quote dict — validates all fields are non-empty."""
    assert figure and text and category, f"Empty field: {figure=}, {text[:40]=}, {category=}"
    return {"figure": figure, "text": text, "category": category}

# ── Batch data definitions ────────────────────────────────────
# Each BATCH_N is dict[str, list[dict]] keyed by category name.
# Categories that already exist will have quotes appended.
# New category names create new keys.
# Add new BATCH_N variables below — the engine collects them automatically.

BATCH_1 = {}  # Hackers & Cypherpunks (Task 2)
BATCH_2 = {}  # Activists & Dissidents (Task 3)
BATCH_3 = {}  # Economists & Economic Dissidents (Task 4)
BATCH_4 = {}  # Revolutionaries & Guerrillas (Task 5)
BATCH_5 = {}  # Expand thin categories — part 1 (Task 6)
BATCH_6 = {}  # Expand thin categories — part 2 (Task 7)
BATCH_7 = {}  # Well-covered categories + overflow (Task 8)

# ── Engine ────────────────────────────────────────────────────

def load_existing():
    with open(QUOTES_PATH) as f:
        return json.load(f)

def collect_batches():
    """Collect all BATCH_N variables defined in this module."""
    import inspect
    frame = inspect.currentframe()
    # Walk up to module level
    while frame.f_code.co_name != "<module>":
        frame = frame.f_back
    batches = {}
    for name in sorted(frame.f_globals):
        if name.startswith("BATCH_"):
            batches[name] = frame.f_globals[name]
    return batches

def merge(existing, batches):
    """Merge batch data into existing quotes dict. Returns (merged, added_count)."""
    quotes = existing["quotes"]
    added = 0
    duplicates = []

    for batch_name, batch_data in batches.items():
        for category, new_quotes in batch_data.items():
            if category not in quotes:
                quotes[category] = []
            for nq in new_quotes:
                # Check for duplicate (case-insensitive figure + text match)
                is_dup = any(
                    q["figure"].lower() == nq["figure"].lower()
                    and q["text"].lower().strip() == nq["text"].lower().strip()
                    for q in quotes[category]
                )
                if is_dup:
                    duplicates.append(
                        f"  DUPE in {batch_name}: {nq['figure']} — {nq['text'][:60]}"
                    )
                else:
                    quotes[category].append(nq)
                    added += 1

    if duplicates:
        print(f"\n⚠  {len(duplicates)} duplicate(s) found:")
        for d in duplicates:
            print(d)
        print()

    return existing, added

def write_db(data):
    with open(QUOTES_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # Add trailing newline
    with open(QUOTES_PATH, "a") as f:
        f.write("\n")

def stats(data):
    quotes = data["quotes"]
    total = sum(len(v) for v in quotes.values())
    figures = set()
    for qs in quotes.values():
        for q in qs:
            figures.add(q["figure"])
    return total, len(figures), len(quotes)

def main():
    existing = load_existing()
    before_total, before_figs, before_cats = stats(existing)

    batches = collect_batches()
    merged, added = merge(existing, batches)

    after_total, after_figs, after_cats = stats(merged)

    print(f"Before: {before_total} quotes, {before_figs} figures, {before_cats} categories")
    print(f"Added:  {added} quotes")
    print(f"After:  {after_total} quotes, {after_figs} figures, {after_cats} categories")

    write_db(merged)
    print(f"\nWrote {QUOTES_PATH}")

if __name__ == "__main__":
    main()
```

**Data format for each batch:**

```python
BATCH_1 = {
    "Hackers & Cypherpunks": [
        q("Aaron Swartz", "Information is power. But like all power, there are those who want to keep it for themselves.", "Hackers & Cypherpunks"),
        q("Aaron Swartz", "It's not enough to be right. You have to organize. You have to build power.", "Hackers & Cypherpunks"),
        # ... more quotes per figure
    ],
}
```

---

### Task 1: Create merge script infrastructure

**Files:**
- Create: `scripts/expand_quotes.py`

**Steps:**

- [ ] **Step 1: Write the merge script**

Copy the full script from the Merge Script Design section above into `scripts/expand_quotes.py`.

- [ ] **Step 2: Run the merge script (no-op — all batches empty)**

Run: `python3 scripts/expand_quotes.py`
Expected output:
```
Before: 1360 quotes, 209 figures, 23 categories
Added:  0 quotes
After:  1360 quotes, 209 figures, 23 categories
Wrote .../data/quotes.json
```

- [ ] **Step 3: Verify data.json unchanged in structure**

Run: `python3 -c "import json; d=json.load(open('data/quotes.json')); print(f'{sum(len(v) for v in d[\"quotes\"].values())} quotes, {len(d[\"quotes\"])} categories')"`
Expected: `1360 quotes, 23 categories`

- [ ] **Step 4: Run cargo test**

Run: `cargo test`
Expected: 17 tests pass, 0 fail

- [ ] **Step 5: Commit**

```bash
git add scripts/expand_quotes.py
git commit -m "feat: add merge script for quote database expansion

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2: Batch 1 — Hackers & Cypherpunks

**Files:**
- Modify: `scripts/expand_quotes.py` — fill in BATCH_1 data

**Target:** 10-15 figures, 5-8 quotes each (~75-90 quotes total)

**Figures to include:** Aaron Swartz, Richard Stallman, Tim Berners-Lee, Moxie Marlinspike, Phil Zimmermann, John Perry Barlow, Whitfield Diffie, Eric S. Raymond, Linus Torvalds, Edward Snowden, John Gilmore, Julian Assange, Bram Cohen, Cory Doctorow, Jacob Appelbaum

**Steps:**

- [ ] **Step 1: Add BATCH_1 data to expand_quotes.py**

Edit `scripts/expand_quotes.py` — replace `BATCH_1 = {}` with actual quote data. Each figure gets 5-8 real, verified quotes focused on digital freedom, privacy, open information, and the hacker ethos. Use the `q()` helper for every quote.

- [ ] **Step 2: Run the merge script**

Run: `python3 scripts/expand_quotes.py`
Expected: Shows before/after counts with ~75-90 new quotes added, new category "Hackers & Cypherpunks" appears

- [ ] **Step 3: Run cargo test**

Run: `cargo test`
Expected: 17 tests pass, 0 fail

- [ ] **Step 4: Commit**

```bash
git add scripts/expand_quotes.py data/quotes.json
git commit -m "feat: add Hackers & Cypherpunks category (~75-90 quotes)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3: Batch 2 — Activists & Dissidents

**Files:**
- Modify: `scripts/expand_quotes.py` — fill in BATCH_2 data

**Target:** 10-15 figures, 5-8 quotes each (~75-90 quotes total)

**Figures to include:** Martin Luther King Jr, Malcolm X, Mahatma Gandhi, Rosa Parks, Cesar Chavez, Frederick Douglass, Aung San Suu Kyi, Harvey Milk, Emma Goldman, Angela Davis, Susan B. Anthony, Nelson Mandela, Dolores Huerta, W.E.B. Du Bois, Ida B. Wells

**Steps:**

- [ ] **Step 1: Add BATCH_2 data to expand_quotes.py**

Replace `BATCH_2 = {}` with actual quote data using the `q()` helper.

- [ ] **Step 2: Run the merge script**

Run: `python3 scripts/expand_quotes.py`
Expected: ~75-90 new quotes, new category "Activists & Dissidents"

- [ ] **Step 3: Run cargo test**

Run: `cargo test`
Expected: 17 tests pass, 0 fail

- [ ] **Step 4: Commit**

```bash
git add scripts/expand_quotes.py data/quotes.json
git commit -m "feat: add Activists & Dissidents category (~75-90 quotes)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4: Batch 3 — Economists & Economic Dissidents

**Files:**
- Modify: `scripts/expand_quotes.py` — fill in BATCH_3 data

**Target:** 10-15 figures, 5-8 quotes each (~75-90 quotes total)

**Figures to include:** Karl Marx, John Maynard Keynes, Friedrich Hayek, Adam Smith, Amartya Sen, Naomi Klein, Thomas Piketty, Milton Friedman, John Kenneth Galbraith, Thorstein Veblen, David Ricardo, Joan Robinson, Joseph Stiglitz, Ha-Joon Chang, Yanis Varoufakis

**Steps:**

- [ ] **Step 1: Add BATCH_3 data to expand_quotes.py**

Replace `BATCH_3 = {}` with actual quote data using the `q()` helper.

- [ ] **Step 2: Run the merge script**

Run: `python3 scripts/expand_quotes.py`
Expected: ~75-90 new quotes, new category "Economists & Economic Dissidents"

- [ ] **Step 3: Run cargo test**

Run: `cargo test`
Expected: 17 tests pass, 0 fail

- [ ] **Step 4: Commit**

```bash
git add scripts/expand_quotes.py data/quotes.json
git commit -m "feat: add Economists & Economic Dissidents category (~75-90 quotes)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 5: Batch 4 — Revolutionaries & Guerrillas

**Files:**
- Modify: `scripts/expand_quotes.py` — fill in BATCH_4 data

**Target:** 10-15 figures, 5-8 quotes each (~75-90 quotes total)

**Figures to include:** Che Guevara, Emiliano Zapata, Leon Trotsky, Subcomandante Marcos, Toussaint Louverture, Simon Bolivar, Giuseppe Garibaldi, Michael Collins, Ho Chi Minh (as revolutionary), Fidel Castro (as revolutionary), Patrice Lumumba, Thomas Sankara, Augusto Sandino, Camilo Cienfuegos, Buenaventura Durruti

**Steps:**

- [ ] **Step 1: Add BATCH_4 data to expand_quotes.py**

Replace `BATCH_4 = {}` with actual quote data using the `q()` helper.

- [ ] **Step 2: Run the merge script**

Run: `python3 scripts/expand_quotes.py`
Expected: ~75-90 new quotes, new category "Revolutionaries & Guerrillas"

- [ ] **Step 3: Run cargo test**

Run: `cargo test`
Expected: 17 tests pass, 0 fail

- [ ] **Step 4: Commit**

```bash
git add scripts/expand_quotes.py data/quotes.json
git commit -m "feat: add Revolutionaries & Guerrillas category (~75-90 quotes)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6: Expand thin categories — part 1

**Files:**
- Modify: `scripts/expand_quotes.py` — fill in BATCH_5 data

**Target categories and approximate additions:**

| Category | Current | Add | Target |
|---|---|---|---|
| Intelligence Figures | 25 | 35 | 60 |
| Whistleblowers & Spies | 23 | 37 | 60 |
| Media & Propaganda | 28 | 27 | 55 |
| Latin American Leaders | 30 | 25 | 55 |
| Middle Eastern Leaders | 31 | 24 | 55 |
| Chinese Leaders | 34 | 21 | 55 |

**Steps:**

- [ ] **Step 1: Add BATCH_5 data to expand_quotes.py**

Replace `BATCH_5 = {}` with quote data for the 6 categories above. Add new figures and additional quotes for existing figures within each category to hit the targets. Use the `q()` helper.

- [ ] **Step 2: Run the merge script**

Run: `python3 scripts/expand_quotes.py`
Expected: ~169 new quotes across 6 existing categories

- [ ] **Step 3: Run cargo test**

Run: `cargo test`
Expected: 17 tests pass, 0 fail

- [ ] **Step 4: Commit**

```bash
git add scripts/expand_quotes.py data/quotes.json
git commit -m "feat: expand thin categories part 1 — Intelligence, Whistleblowers, Media, LatAm, Middle East, China

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7: Expand thin categories — part 2

**Files:**
- Modify: `scripts/expand_quotes.py` — fill in BATCH_6 data

**Target categories and approximate additions:**

| Category | Current | Add | Target |
|---|---|---|---|
| Military Leaders | 34 | 21 | 55 |
| Ancient & Medieval Rulers | 37 | 28 | 65 |
| African Leaders | 41 | 14 | 55 |
| Secret Societies | 42 | 13 | 55 |
| European Leaders | 43 | 12 | 55 |

**Steps:**

- [ ] **Step 1: Add BATCH_6 data to expand_quotes.py**

Replace `BATCH_6 = {}` with quote data for these 5 categories. For Ancient & Medieval Rulers, add both more rulers and more quotes for existing ones. For Secret Societies, add more occult/esoteric figures and more depth. For Military Leaders, add overlooked subversive commanders. Use the `q()` helper.

- [ ] **Step 2: Run the merge script**

Run: `python3 scripts/expand_quotes.py`
Expected: ~88 new quotes across 5 existing categories

- [ ] **Step 3: Run cargo test**

Run: `cargo test`
Expected: 17 tests pass, 0 fail

- [ ] **Step 4: Commit**

```bash
git add scripts/expand_quotes.py data/quotes.json
git commit -m "feat: expand thin categories part 2 — Military, Ancient, African, Secret Societies, European

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 8: Well-covered categories + README update

**Files:**
- Modify: `scripts/expand_quotes.py` — fill in BATCH_7 data
- Modify: `README.md`

**Target:** Add overlooked subversive figures and additional quotes to the 12 well-covered categories. Each category gets 10-25 new quotes focused on figures not yet represented. Target ~200 additional quotes across all 12 categories.

**README changes:**
- Line 3: Update quote count from "1,360+" to the final total
- Line 3: Update figure count from "200+" to the final total
- Line 7: Same counts in Features section
- Line 71 (architecture): Update "1,360+ embedded quotes" to final total

**Steps:**

- [ ] **Step 1: Add BATCH_7 data to expand_quotes.py**

Replace `BATCH_7 = {}` with quote data for well-covered categories. Focus on adding new figures not yet in the database, rather than more quotes for already-represented figures. Use the `q()` helper.

- [ ] **Step 2: Run the merge script**

Run: `python3 scripts/expand_quotes.py`
Expected: ~200 new quotes across 12 existing categories. Final output shows target ~2,500-2,800 total.

- [ ] **Step 3: Verify final stats**

Run: `cargo run -- stats`
Expected: Shows total categories = 27, quotes in target range

- [ ] **Step 4: Run cargo test**

Run: `cargo test`
Expected: 17 tests pass, 0 fail

- [ ] **Step 5: Update README.md counts**

Edit `README.md` — update the three locations with final quote/figure/category counts from the stats output.

- [ ] **Step 6: Commit**

```bash
git add scripts/expand_quotes.py data/quotes.json README.md
git commit -m "feat: expand well-covered categories and update README counts

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 9: Final verification

**Files:** None (verification only)

**Steps:**

- [ ] **Step 1: Run full cargo test**

Run: `cargo test`
Expected: All 17 tests pass

- [ ] **Step 2: Verify random quotes work across all categories**

Run: `for i in $(seq 1 10); do cargo run -- random; done`
Expected: 10 random quotes displayed without errors

- [ ] **Step 3: Test category command works for new categories**

Run:
```
cargo run -- category "Hackers & Cypherpunks"
cargo run -- category "Activists & Dissidents"
cargo run -- category "Economists & Economic Dissidents"
cargo run -- category "Revolutionaries & Guerrillas"
```
Expected: Each returns a quote from the correct category

- [ ] **Step 4: Test figure search works for new figures**

Run: `cargo run -- figure "Aaron Swartz"` and `cargo run -- figure "Che Guevara"`
Expected: Each returns matching quotes

- [ ] **Step 5: Test stats command shows correct totals**

Run: `cargo run -- stats`
Expected: Shows 27 categories, final quote count, and all new categories appear in breakdown

- [ ] **Step 6: Test translation still works**

Run: `cargo run -- -t es`
Expected: Random quote with Spanish translation (original + translated display)

- [ ] **Step 7: Final commit if needed**

```bash
git status
# If only the merge script and data files changed, no commit needed.
# If any fixes were applied, commit them.
```

---

## Summary

| Task | What | Quotes added | Cumulative |
|---|---|---|---|
| 1 | Merge script infrastructure | 0 | 1,360 |
| 2 | Hackers & Cypherpunks | ~75-90 | ~1,445 |
| 3 | Activists & Dissidents | ~75-90 | ~1,530 |
| 4 | Economists & Economic Dissidents | ~75-90 | ~1,615 |
| 5 | Revolutionaries & Guerrillas | ~75-90 | ~1,700 |
| 6 | Expand thin categories (part 1) | ~169 | ~1,869 |
| 7 | Expand thin categories (part 2) | ~88 | ~1,957 |
| 8 | Well-covered categories + README | ~200 | ~2,157 |
| 9 | Final verification | 0 | ~2,157 |

Estimated final: ~2,500-2,800 quotes, ~350-400 figures, 27 categories.
