# Pipeline Usage – Smoke Test & Makefile

This guide explains how to use the **Chapter 1 smoke test** and the **Makefile** targets to quickly verify that the Agentic Enterprise chapter pipeline is wired correctly.

It’s aimed at engineers and technical editors who are integrating the pipeline into their environment.

---

## 1. Prerequisites

Before running any commands, make sure:

1. You’re in the **repo root** (where `config.yaml` and `Makefile` live).
2. You have a working Python environment (e.g., `python` or `python3` on your PATH).
3. The following files exist (from the starter package):
   - `global/book_outline.md`
   - `global/style_profile.md`
   - `chapters/ch01/chapter_outline_1.md`
   - `chapters/ch01/Chapter_1.md`
   - `tests/smoke_ch1.py`
   - `Makefile`

If any of these are missing, fix that first (e.g., by copying from the shared package).

---

## 2. Smoke Test Script – `tests/smoke_ch1.py`

The smoke test is a **lightweight sanity check** for Chapter 1:

- Confirms that global and chapter files exist and are non-empty.
- Ensures that **every placeholder** from `chapter_outline_1.md` appears verbatim in `Chapter_1.md`.
- Warns if there are extra placeholders in `Chapter_1.md` that aren’t in the outline.

### 2.1 Running the Smoke Test

From the repo root:

```bash
python -m tests.smoke_ch1
```

or, depending on your environment:

```bash
python3 -m tests.smoke_ch1
```

### 2.2 What You Should See

On success, output will look like:

```text
Running Chapter 1 smoke test...

Chapter 1 smoke test PASSED.
```

If files are missing or empty, you’ll see errors like:

```text
FileNotFoundError: Missing required file: /path/to/global/book_outline.md
```

If placeholders don’t match, you’ll see something like:

```text
ERROR: The following placeholders from chapter_outline_1.md are missing in Chapter_1.md:
 - [[PLACEHOLDER: ...]]
AssertionError: Some placeholders from outline are not present in chapter.
```

**Action:** If you hit errors, fix the underlying issue (missing outputs, changed placeholder formatting, etc.) and rerun the smoke test.

---

## 3. Makefile – Common Commands

The `Makefile` provides a few convenience targets to run parts of the pipeline and the smoke test.

From the repo root, you can list targets:

```bash
make help
```

You should see:

```text
Agentic Enterprise Chapter Pipeline – Make Targets

  make ch1-outline   # Run Step 3 (outline) for Chapter 1 (requires rough_chapter_1.md)
  make ch1-chapter   # Run Step 4 (chapter generation) for Chapter 1 (after outline exists)
  make ch1-all       # Run outline + chapter + judges for Chapter 1
  make test-ch1      # Run smoke test for Chapter 1 (placeholders, file existence)
```

> **Note:** The sample `orchestrator.py` needs to be extended with CLI handling
> (e.g., `--mode outline|chapter|full --chapter 1`) for these targets to work
> exactly as written. The Makefile assumes that’s in place.

### 3.1 Generate Chapter 1 Outline

Intended to run **Step 3** (Chapter Outline Abstractor) for Chapter 1:

```bash
make ch1-outline
```

This corresponds to:

```bash
python src/orchestrator.py --mode outline --chapter 1
```

**Preconditions:**

- `global/book_outline.md` exists.
- `chapters/ch01/rough_chapter_1.md` exists (human rough draft).

**Expected result:**

- `chapters/ch01/chapter_outline_1.md` is created or updated.

### 3.2 Generate Full Chapter 1 Draft

Intended to run **Step 4** (Chapter Generator) for Chapter 1:

```bash
make ch1-chapter
```

This corresponds to:

```bash
python src/orchestrator.py --mode chapter --chapter 1
```

**Preconditions:**

- `global/book_outline.md`
- `global/style_profile.md`
- `chapters/ch01/structure_chapter_1.md`
- `chapters/ch01/chapter_outline_1.md`

**Expected result:**

- `chapters/ch01/Chapter_1.md` is (re)generated.

### 3.3 Full Pipeline for Chapter 1

To run **outline + chapter + judges** in one go:

```bash
make ch1-all
```

This corresponds to:

```bash
python src/orchestrator.py --mode full --chapter 1
```

**What it should do (once you wire it):**

1. Run Step 3 (outline) for Chapter 1.
2. Run Step 4 (chapter generation) for Chapter 1.
3. Run outline judge and chapter judge for Chapter 1.
4. Print judge scores / notes or log them to `/logs/`.

### 3.4 Run the Smoke Test via Make

You can also run the smoke test using the Makefile:

```bash
make test-ch1
```

Which just executes:

```bash
python -m tests.smoke_ch1
```

This is a nice way to:

- Add to CI (`make test-ch1` in your pipeline).
- Quickly re-validate after any changes to prompts, models, or orchestration code.

---

## 4. Recommended Workflow for Engineers

For Chapter 1:

1. Ensure the starter artifacts are in place:
   - `book_outline.md`, `style_profile.md`
   - `structure_chapter_1.md`, `chapter_outline_1.md`, `Chapter_1.md`

2. Wire `src/orchestrator.py` CLI so that:
   - `--mode outline` → Step 3
   - `--mode chapter` → Step 4
   - `--mode full` → Step 3 + Step 4 + judges

3. Use Makefile commands:
   - `make ch1-outline` to regenerate the outline (after updating the rough draft).
   - `make ch1-chapter` to regenerate the chapter (after updating outline/structure/style).
   - `make ch1-all` when you want an end-to-end run with judges.

4. Run:
   - `make test-ch1`
   - Confirm the smoke test passes before handing drafts to editors.

Once Chapter 1 is stable, you can copy this pattern for `ch02`, `ch03`, etc., adjusting chapter IDs and paths as needed.

---

If you keep this file up to date as the orchestrator’s CLI evolves, it doubles as a quick-start for any new engineer joining the project.