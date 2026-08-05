#!/usr/bin/env python3
"""Flatten index.html's Jekyll {% include %} tags into one static file.

GitHub Pages runs Jekyll automatically, so index.html works there as-is.
Any other host (one that doesn't run Jekyll) needs a plain, already-merged
HTML file instead. This script builds that file without needing Ruby/Jekyll
installed -- only Python's standard library.

Usage:
    python build.py

Output:
    dist/index.html - deploy this next to style.css and assets/.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parent
INCLUDES_DIR = ROOT / "_includes"
INCLUDE_RE = re.compile(r"\{%-?\s*include\s+([^\s%]+)\s*-?%\}")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n---\s*\n")


def render(path: Path, seen: tuple[Path, ...] = ()) -> str:
    if path in seen:
        chain = " -> ".join(p.name for p in seen + (path,))
        raise RecursionError(f"circular include: {chain}")

    text = path.read_text(encoding="utf-8")

    def replace(match: re.Match) -> str:
        include_path = INCLUDES_DIR / match.group(1)
        if not include_path.exists():
            raise FileNotFoundError(f"include not found: {include_path}")
        return render(include_path, seen + (path,))

    return INCLUDE_RE.sub(replace, text)


def main() -> None:
    source = ROOT / "index.html"
    text = source.read_text(encoding="utf-8")
    text = FRONT_MATTER_RE.sub("", text, count=1)
    text = INCLUDE_RE.sub(
        lambda m: render(INCLUDES_DIR / m.group(1)),
        text,
    )

    out_dir = ROOT / "dist"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(text, encoding="utf-8")
    print(f"Wrote {out_file}")
    print("Deploy dist/index.html together with style.css and assets/.")


if __name__ == "__main__":
    main()
