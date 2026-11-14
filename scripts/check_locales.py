#!/usr/bin/env python3
"""Checks locales/<code>.json against locales/source.json (written by build.py --export):
the same texts, none empty, and each translation keeps its text's tags, links and placeholders.
    python3 scripts/check_locales.py [code ...]
"""
import json
import os
import re
import sys

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "locales")


def marks(text):
    """What a translation may not change: tags with their attributes, and {placeholders}."""
    return sorted(re.findall(r"<[^>]+>|\{[a-z]+\}", text))


def check(code, source):
    path = os.path.join(DIR, code + ".json")
    try:
        with open(path, encoding="utf-8") as f:
            texts = json.load(f)
    except (OSError, ValueError) as e:
        return [f"cannot read: {e}"]
    errors = [f"missing: {k[:70]}" for k in source if k not in texts]
    errors += [f"not in source.json: {k[:70]}" for k in texts if k not in source]
    for k, v in texts.items():
        if k not in source:
            continue
        if not isinstance(v, str) or not v.strip():
            errors.append(f"empty: {k[:70]}")
        elif marks(k) != marks(v):
            errors.append(f"tags or placeholders differ: {k[:70]}")
    return errors


if __name__ == "__main__":
    with open(os.path.join(DIR, "source.json"), encoding="utf-8") as f:
        source = json.load(f)
    codes = sys.argv[1:] or sorted(n[:-5] for n in os.listdir(DIR) if n.endswith(".json") and n != "source.json")
    failed = False
    for code in codes:
        errors = check(code, source)
        print(f"{code}: {'ok, ' + str(len(source)) + ' texts' if not errors else str(len(errors)) + ' problems'}")
        for e in errors[:40]:
            print("   ", e)
        failed = failed or bool(errors)
    sys.exit(1 if failed else 0)
