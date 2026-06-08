#!/usr/bin/env python3
"""
Wikiquote scraper — pull all quotes for known figures from en.wikiquote.org.

Usage:
    python3 scripts/wikiquote_scraper.py                         # scrape all figures
    python3 scripts/wikiquote_scraper.py --figures "Vladimir Putin" "Karl Marx"  # specific figures
    python3 scripts/wikiquote_scraper.py --limit 20              # first 20 figures only

Output: data/scraped_quotes.json (same schema as data/quotes.json)
Merge with: python3 scripts/merge_scraped.py
"""

import argparse
import html
import json
import logging
import re
import time
import unicodedata
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
QUOTES_PATH = ROOT / "data" / "quotes.json"
OUTPUT_PATH = ROOT / "data" / "scraped_quotes.json"

# Wikiquote API endpoint
WIKIQUOTE_API = "https://en.wikiquote.org/w/api.php"

# User agent per Wikiquote API terms of service
USER_AGENT = "SubversiveQuoteScraper/1.0 (research project; kelsey@example.com)"

# Sections where we stop collecting quotes
STOP_SECTIONS = {
    "see also", "external links", "references", "further reading",
    "quotes about", "about", "filmography", "discography",
    "see also:", "external links:", "references:", "further reading:",
}

log = logging.getLogger("wikiquote_scraper")


# ──────────────────────────────────────────────────────────
# Phase 1: Extract figure index from existing database
# ──────────────────────────────────────────────────────────

def extract_figure_index(path: Path = QUOTES_PATH):
    """Read existing DB, return (figure→category map, existing quotes by category)."""
    with open(path) as f:
        data = json.load(f)

    quotes_by_cat = data["quotes"]
    figure_categories: dict[str, list[str]] = defaultdict(list)
    figure_quotes: dict[str, list[dict]] = defaultdict(list)

    for cat, qlist in quotes_by_cat.items():
        for q in qlist:
            figure_categories[q["figure"]].append(cat)
            figure_quotes[q["figure"]].append(q)

    # For figures in multiple categories, pick the category with the most quotes
    figure_to_cat: dict[str, str] = {}
    for figure, cats in figure_categories.items():
        counts = defaultdict(int)
        for c in cats:
            counts[c] += 1
        # Most common category; tie-break alphabetically
        best = max(sorted(counts.keys()), key=lambda c: (counts[c], c))
        figure_to_cat[figure] = best

    log.info("Found %d figures across %d categories", len(figure_to_cat), len(quotes_by_cat))
    return figure_to_cat, figure_quotes, quotes_by_cat


# ──────────────────────────────────────────────────────────
# Phase 2: Fetch wikitext from Wikiquote
# ──────────────────────────────────────────────────────────

def figure_to_wikiquote_name(figure: str) -> str:
    """Convert a figure name to a Wikiquote page name.

    Wikiquote pages use underscores and approximate ASCII:
      "Vladimir Putin" → "Vladimir_Putin"
      "Hugo Chávez"    → "Hugo_Chavez"
    """
    # Strip diacritics/accents
    nfkd = unicodedata.normalize("NFKD", figure)
    ascii_ = nfkd.encode("ascii", "ignore").decode("ascii")
    return ascii_.strip().replace(" ", "_")


def fetch_wikitext(page_name: str, session: Optional[urllib.request.OpenerDirector] = None) -> Optional[str]:
    """Fetch the raw wikitext for a Wikiquote page.

    Returns None if the page does not exist or the API errors.
    """
    params = urllib.parse.urlencode({
        "action": "parse",
        "page": page_name,
        "format": "json",
        "prop": "wikitext",
        "redirects": "1",
        "disablelimitreport": "1",
    })
    url = f"{WIKIQUOTE_API}?{params}"

    if session is None:
        opener = urllib.request.build_opener()
    else:
        opener = session

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with opener.open(req, timeout=30) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        log.debug("HTTP %d for %s: %s", e.code, page_name, e)
        return None
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        log.debug("Error fetching %s: %s", page_name, e)
        return None

    if "error" in data:
        return None
    try:
        return data["parse"]["wikitext"]["*"]
    except KeyError:
        return None


# ──────────────────────────────────────────────────────────
# Phase 3: Parse quotes from wikitext
# ──────────────────────────────────────────────────────────

def normalize_section_name(line: str) -> str:
    """Extract the normalized section name from a wiki heading."""
    # == Section Name == or === Subsection ===
    name = line.strip().strip("=").strip().lower()
    return name


def parse_quotes_from_wikitext(wikitext: str, figure: str) -> list[str]:
    """Parse quote text from Wikiquote wikitext.

    Returns a list of raw (still-marked-up) quote strings.
    """
    lines = wikitext.split("\n")
    quotes: list[str] = []
    in_quotes_section = False
    current_quote: Optional[str] = None

    for line in lines:
        stripped = line.strip()

        # ── Section headers ────────────────────────────────
        if stripped.startswith("==") and stripped.endswith("=="):
            section = normalize_section_name(stripped)
            # Check if this is a stop section
            for stop in STOP_SECTIONS:
                if section.startswith(stop):
                    in_quotes_section = False
                    # Flush any pending quote
                    if current_quote is not None:
                        quotes.append(current_quote)
                        current_quote = None
                    break
            else:
                # Not a stop section — entering/enclosed in quotes area
                if not in_quotes_section:
                    # Only enter if we see "quotes" in the section name
                    if "quote" in section or "quotation" in section:
                        in_quotes_section = True
                # Subsections (===, ====) within quotes stay active
            continue

        if not in_quotes_section:
            # Flush pending quote when leaving the section
            if current_quote is not None:
                quotes.append(current_quote)
                current_quote = None
            continue

        # ── Skip non-content lines ─────────────────────────
        if not stripped:
            if current_quote is not None:
                quotes.append(current_quote)
                current_quote = None
            continue

        # Skip file/image lines
        if stripped.startswith("[[File:") or stripped.startswith("[[Image:"):
            continue

        # Skip template-only lines
        if stripped.startswith("{{") and stripped.endswith("}}"):
            continue

        # Skip category lines
        if stripped.startswith("[[Category:"):
            continue

        # ── Bullet lines ───────────────────────────────────
        if stripped.startswith("*"):
            # Flush any pending quote
            if current_quote is not None:
                quotes.append(current_quote)
                current_quote = None

            # Determine bullet depth
            bullet_match = re.match(r"^(\*+)", stripped)
            depth = len(bullet_match.group(1)) if bullet_match else 1

            # Only collect single-bullet (*) lines as quotes
            # Double-bullet (**) and deeper are citations/sources
            if depth == 1:
                # Remove the leading * and optional space
                content = stripped.lstrip("*").strip()
                if content and not content.startswith(":"):
                    current_quote = content
            elif depth >= 1:
                # Skip citations — but check if they contain quote-like content
                # Some pages put quotes under *: or *'' format
                pass

        # ── Continuation lines ─────────────────────────────
        # Lines that start with whitespace but no * continue the previous quote
        elif line.startswith(" ") or line.startswith("\t"):
            if current_quote is not None:
                content = stripped
                if content:
                    current_quote = current_quote.rstrip('\n') + "\n" + content

        # ── Other lines flush ──────────────────────────────
        else:
            if current_quote is not None:
                quotes.append(current_quote)
                current_quote = None

    # Flush final quote
    if current_quote is not None:
        quotes.append(current_quote)

    return quotes


# ──────────────────────────────────────────────────────────
# Phase 4: Clean quote text
# ──────────────────────────────────────────────────────────

def clean_wikitext(text: str) -> str:
    """Strip wiki markup from a quote string."""
    # Remove <br> and <br/> tags (replace with space)
    text = re.sub(r"<br\s*/?>", " ", text, flags=re.IGNORECASE)

    # Remove other HTML tags
    text = re.sub(r"</?(blockquote|poem|div|span|small|big|tt|code|i|b|u|s|center|cite|ref)[^>]*>", "", text, flags=re.IGNORECASE)

    # Remove reference tags with content: <ref>...</ref>
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # Remove {{templates}} — handle simple non-nested templates
    # Run multiple passes to handle nested templates
    for _ in range(5):
        new_text = re.sub(r"\{\{[^{}]*?\}\}", "", text)
        if new_text == text:
            break
        text = new_text

    # Remove [[File:...]] and [[Image:...]] entirely
    text = re.sub(r"\[\[(?:File|Image):[^\]]*?\]\]", "", text, flags=re.IGNORECASE)

    # Convert wiki links: [[target|display]] → display, [[target]] → target
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)

    # Strip bold/italic markers
    text = text.replace("'''", "")
    text = text.replace("''", "")

    # Decode HTML entities
    text = html.unescape(text)

    # Remove remaining square brackets that might be artifacts
    # (but keep actual punctuation brackets)
    text = re.sub(r"\[(?![^\[]*\])", "", text)  # unpaired [
    text = re.sub(r"(?<!\\)\]", "", text)  # unpaired ]

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)

    # Strip leading/trailing whitespace and quotes
    text = text.strip()
    text = text.strip('"').strip("'").strip()
    text = text.strip("“").strip("”").strip("‘").strip("’")

    return text.strip()


def is_valid_quote(text: str) -> bool:
    """Check if the cleaned text is a valid quote worth keeping."""
    if len(text) < 30:
        return False
    if not any(c.isalnum() for c in text):
        return False
    # Skip lines that are just citation remnants
    skip_patterns = [
        r"^[Ii][bB]id[.,]",
        r"^[Ii]bid[.,]",
        r"^[Ss]ource:",
        r"^[Ss]ee also",
        r"^[Mm]ain article",
        r"^[Ff]urther reading",
        r"^\d+$",
    ]
    for pat in skip_patterns:
        if re.match(pat, text):
            return False
    return True


# ──────────────────────────────────────────────────────────
# Phase 5: Dedup and output
# ──────────────────────────────────────────────────────────

def is_duplicate(figure: str, text: str, existing_quotes_by_figure: dict[str, list[dict]]) -> bool:
    """Check if this figure+text pair already exists in the database."""
    existing = existing_quotes_by_figure.get(figure, [])
    text_lower = text.lower().strip()
    for eq in existing:
        if eq["text"].lower().strip() == text_lower and eq["figure"].lower() == figure.lower():
            return True
    return False


# ──────────────────────────────────────────────────────────
# Main scraper logic
# ──────────────────────────────────────────────────────────

def scrape_figure(
    figure: str,
    category: str,
    existing_by_figure: dict[str, list[dict]],
    delay: float = 1.0,
    opener: Optional[urllib.request.OpenerDirector] = None,
) -> tuple[int, int]:
    """Scrape one figure. Returns (new_quotes_count, total_quotes_found)."""
    page_name = figure_to_wikiquote_name(figure)

    wikitext = fetch_wikitext(page_name, opener)
    if wikitext is None:
        return 0, 0, []

    raw_quotes = parse_quotes_from_wikitext(wikitext, figure)
    if not raw_quotes:
        return 0, 0, []

    new_quotes = []
    for raw in raw_quotes:
        cleaned = clean_wikitext(raw)
        if not is_valid_quote(cleaned):
            continue
        if is_duplicate(figure, cleaned, existing_by_figure):
            continue
        new_quotes.append({
            "figure": figure,
            "text": cleaned,
            "category": category,
        })

    time.sleep(delay)
    return len(new_quotes), len(raw_quotes), new_quotes


def main():
    parser = argparse.ArgumentParser(description="Scrape quotes from Wikiquote")
    parser.add_argument("--figures", nargs="+", help="Scrape only these figures (space-separated)")
    parser.add_argument("--limit", type=int, help="Stop after N figures")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API calls (seconds)")
    parser.add_argument("--output", type=str, default=str(OUTPUT_PATH), help="Output JSON path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    # Phase 1: extract figure index
    figure_to_cat, figure_quotes, _ = extract_figure_index()

    # Determine figure list
    if args.figures:
        figures_to_scrape = [(f, figure_to_cat.get(f, "Unknown")) for f in args.figures]
    else:
        figures_to_scrape = sorted(figure_to_cat.items(), key=lambda x: x[0])

    if args.limit:
        figures_to_scrape = figures_to_scrape[: args.limit]

    log.info("Scraping %d figures with %.1fs delay...", len(figures_to_scrape), args.delay)

    # Shared opener for connection pooling
    opener = urllib.request.build_opener()

    # Aggregate new quotes per category
    new_by_category: dict[str, list[dict]] = defaultdict(list)
    total_new = 0
    total_found = 0
    no_page = 0
    no_quotes = 0

    for figure, category in figures_to_scrape:
        new_count, found_count, new_qs = scrape_figure(
            figure, category, figure_quotes, args.delay, opener,
        )
        total_found += found_count
        total_new += new_count

        if found_count == 0:
            no_page += 1
            log.info("  NO PAGE / NO QUOTES: %s", figure)
        elif new_count == 0:
            log.info("  0 new (all %d exist): %s", found_count, figure)
        else:
            for q in new_qs:
                new_by_category[category].append(q)
            log.info("  +%d new (%d found): %s", new_count, found_count, figure)

    log.info("")
    log.info("═" * 50)
    log.info("Scrape complete!")
    log.info("  Figures attempted: %d", len(figures_to_scrape))
    log.info("  No page found:     %d", no_page)
    log.info("  No quotes found:   %d", no_quotes)
    log.info("  Total quotes found (raw): %d", total_found)
    log.info("  New quotes:         %d", total_new)

    if total_new == 0:
        log.warning("No new quotes to write.")
        return

    # Write output
    output = {"quotes": dict(new_by_category)}
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    log.info("Wrote %d new quotes to %s", total_new, output_path)
    log.info("")

    # Per-category breakdown
    for cat in sorted(new_by_category):
        log.info("  %s: +%d", cat, len(new_by_category[cat]))


if __name__ == "__main__":
    main()
