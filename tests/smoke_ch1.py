# tests/smoke_ch1.py – Simple smoke test for Chapter 1 pipeline
"""Run this after wiring your API keys and generating artifacts.

This test checks:
1. Required files for Chapter 1 exist and are non-empty.
2. All placeholders from chapter_outline_1.md appear verbatim in Chapter_1.md.

Usage:
    python -m tests.smoke_ch1
from the repo root (where config.yaml lives).
"""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_DIR = ROOT / "global"
CH_DIR = ROOT / "chapters" / "ch01"


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise AssertionError(f"File is empty: {path}")
    return text


def extract_placeholders(text: str) -> list[str]:
    pattern = r"\[\[PLACEHOLDER:.*?\]\]"
    return re.findall(pattern, text, flags=re.DOTALL)


def main() -> None:
    print("Running Chapter 1 smoke test...")

    # 1. Check global files
    book_outline = read_text(GLOBAL_DIR / "book_outline.md")
    style_profile = read_text(GLOBAL_DIR / "style_profile.md")

    # 2. Check chapter 1 files
    chapter_outline = read_text(CH_DIR / "chapter_outline_1.md")
    chapter_md = read_text(CH_DIR / "Chapter_1.md")

    # 3. Check placeholders
    outline_placeholders = extract_placeholders(chapter_outline)
    chapter_placeholders = extract_placeholders(chapter_md)

    missing = [ph for ph in outline_placeholders if ph not in chapter_md]
    if missing:
        print("\nERROR: The following placeholders from chapter_outline_1.md are missing in Chapter_1.md:")
        for ph in missing:
            print(" -", ph)
        raise AssertionError("Some placeholders from outline are not present in chapter.")

    # For debugging, you can also check for extra placeholders in the chapter.
    extra = [ph for ph in chapter_placeholders if ph not in outline_placeholders]
    if extra:
        print("\nWARNING: Found placeholders in Chapter_1.md that are not in chapter_outline_1.md:")
        for ph in extra:
            print(" -", ph)

    print("\nChapter 1 smoke test PASSED.")


if __name__ == "__main__":
    main()