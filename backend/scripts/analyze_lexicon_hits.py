#!/usr/bin/env python3
"""
Read app log(s), parse lexicon_hit JSON lines, and print statistics:
- Trigger count per keyword (lexicon_id / word)
- Counts by outcome, severity, category
- Optional: top N keywords, date range filter.

Usage:
  python scripts/analyze_lexicon_hits.py [LOG_FILE ...]
  python scripts/analyze_lexicon_hits.py                    # default: backend/logs/app.log
  python scripts/analyze_lexicon_hits.py app.log app.log.1
  cat app.log | python scripts/analyze_lexicon_hits.py -   # stdin
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional


EVENT = "lexicon_hit"


def extract_json_from_line(line: str) -> Optional[dict]:
    """Extract JSON object from a log line. Log format may be [timestamp] LEVEL ... message."""
    line = line.strip()
    start = line.find("{")
    if start < 0:
        return None
    try:
        return json.loads(line[start:])
    except json.JSONDecodeError:
        return None


def iter_lexicon_hits(files):
    """Yield parsed lexicon_hit records from log file(s) or stdin."""
    if not files or (len(files) == 1 and files[0] == "-"):
        streams = [sys.stdin]
    else:
        streams = []
        for p in files:
            path = Path(p)
            if not path.exists():
                print(f"Warning: file not found: {p}", file=sys.stderr)
                continue
            streams.append(path.open("r", encoding="utf-8", errors="replace"))
    for f in streams:
        try:
            for line in f:
                obj = extract_json_from_line(line)
                if obj and obj.get("event") == EVENT:
                    yield obj
        finally:
            if f is not sys.stdin:
                f.close()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze lexicon_hit events from log file(s) and print statistics."
    )
    parser.add_argument(
        "log_files",
        nargs="*",
        help="Log file path(s). Default: backend/logs/app.log. Use '-' for stdin.",
    )
    parser.add_argument(
        "-n", "--top",
        type=int,
        default=50,
        help="Show top N keywords by hit count (default: 50). Use 0 for all.",
    )
    parser.add_argument(
        "--by-word",
        action="store_true",
        help="Aggregate by word instead of lexicon_id (same word in different lexicons counted separately per lexicon).",
    )
    args = parser.parse_args()
    if not args.log_files:
        backend_dir = Path(__file__).resolve().parents[1]
        default_log = backend_dir / "logs" / "app.log"
        if not default_log.exists():
            print(f"Default log not found: {default_log}", file=sys.stderr)
            print("Usage: python scripts/analyze_lexicon_hits.py [LOG_FILE ...]", file=sys.stderr)
            sys.exit(1)
        args.log_files = [str(default_log)]

    by_key = defaultdict(int)  # (lexicon_id, word) or word -> count
    by_outcome = defaultdict(int)
    by_severity = defaultdict(int)
    by_category = defaultdict(int)
    total_lines = 0

    for rec in iter_lexicon_hits(args.log_files):
        total_lines += 1
        outcome = rec.get("outcome") or "unknown"
        severity = rec.get("severity") or "unknown"
        category = rec.get("category") or "unknown"
        lexicon_id = rec.get("lexicon_id")
        word = rec.get("word") or ""

        by_outcome[outcome] += 1
        by_severity[severity] += 1
        by_category[category] += 1
        if args.by_word:
            by_key[word] += 1
        else:
            key = (lexicon_id, word)
            by_key[key] += 1

    print("=== Lexicon hit statistics ===\n")
    print(f"Total lexicon_hit events: {total_lines}\n")

    print("--- By outcome ---")
    for k, v in sorted(by_outcome.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print()

    print("--- By severity ---")
    for k, v in sorted(by_severity.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print()

    print("--- By category ---")
    for k, v in sorted(by_category.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    print()

    n = args.top
    if n == 0:
        n = len(by_key)
    sorted_keys = sorted(by_key.items(), key=lambda x: -x[1])[:n]
    if args.by_word:
        print(f"--- Top {n} keywords by word (hit count) ---")
        for (word, count) in sorted_keys:
            print(f"  {count:6d}  {word}")
    else:
        print(f"--- Top {n} keywords by (lexicon_id, word) (hit count) ---")
        for ((lexicon_id, word), count) in sorted_keys:
            print(f"  {count:6d}  lexicon_id={lexicon_id}  word={word!r}")
    print()


if __name__ == "__main__":
    main()
