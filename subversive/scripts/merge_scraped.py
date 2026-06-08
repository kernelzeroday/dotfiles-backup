#!/usr/bin/env python3
"""Merge scraped_quotes.json into quotes.json using the same dedup logic as expand_quotes.py."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUOTES_PATH = ROOT / "data" / "quotes.json"
SCRAPED_PATH = ROOT / "data" / "scraped_quotes.json"


def load_json(path: Path):
    with open(path) as f:
        return json.load(f)


def write_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def is_dup(figure: str, text: str, existing: list[dict]) -> bool:
    text_lower = text.lower().strip()
    for eq in existing:
        if eq["text"].lower().strip() == text_lower and eq["figure"].lower() == figure.lower():
            return True
    return False


def merge(existing: dict, scraped: dict) -> tuple[dict, int]:
    """Merge scraped quotes into existing quotes dict. Returns (merged, added_count)."""
    added = 0
    for category, new_quotes in scraped.items():
        if category not in existing:
            existing[category] = []
        for q in new_quotes:
            if not is_dup(q["figure"], q["text"], existing[category]):
                existing[category].append(q)
                added += 1
    return existing, added


def stats(data: dict):
    total = sum(len(v) for v in data.values())
    figures = set()
    for qs in data.values():
        for q in qs:
            figures.add(q["figure"])
    return total, len(figures), len(data)


def main():
    if not SCRAPED_PATH.exists():
        print(f"Error: {SCRAPED_PATH} not found. Run wikiquote_scraper.py first.")
        sys.exit(1)

    print(f"Reading existing DB: {QUOTES_PATH}")
    existing = load_json(QUOTES_PATH)
    existing_quotes = existing["quotes"]
    old_total, old_figures, old_cats = stats(existing_quotes)
    print(f"  Before: {old_total} quotes, {old_figures} figures, {old_cats} categories")

    print(f"Reading scraped data: {SCRAPED_PATH}")
    scraped = load_json(SCRAPED_PATH)
    scraped_quotes = scraped["quotes"]
    scraped_total = sum(len(v) for v in scraped_quotes.values())
    print(f"  Scraped: {scraped_total} quotes across {len(scraped_quotes)} categories")

    merged, added = merge(existing_quotes, scraped_quotes)
    new_total, new_figures, _ = stats(merged)
    skipped = scraped_total - added

    print(f"\nMerge complete!")
    print(f"  Added:  {added}")
    print(f"  Skipped (duplicates): {skipped}")
    print(f"  After:  {new_total} quotes, {new_figures} figures")
    print(f"  Growth: {new_total - old_total} new quotes ({((new_total/old_total)-1)*100:.0f}% increase)")

    write_json(QUOTES_PATH, {"quotes": merged})
    print(f"\nWrote updated DB to {QUOTES_PATH}")


if __name__ == "__main__":
    main()
