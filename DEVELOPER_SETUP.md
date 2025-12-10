# Developer Setup Guide – Agentic Enterprise Chapter Pipeline

This guide explains, step by step, how to create a GitHub repo and plug in all the provided pipeline files so your engineering team can start using and extending the system.

---

## 0. Files you already have

From the shared package, you should have (or can download) the following:

Top-level:

- `README.md`
- `IMPLEMENTATION_NOTES.md`
- `CONTRIBUTING.md`
- `PIPELINE_USAGE.md`
- `config.yaml`
- `Makefile`

Prompts:

- `prompts_reference.md`  (you’ll put this in `prompts/`)

Global artifacts:

- `book_outline.md`
- `style_profile.md`

Chapter 1 artifacts:

- `structure_chapter_1.md`
- `chapter_outline_1.md`
- `Chapter_1.md`

Code & tests:

- `orchestrator.py`
- `tests/smoke_ch1.py` (you may receive it simply as `smoke_ch1.py` to place in `tests/`)

You’ll place these into a repo with the structure described below.

---

## 1. Create a new GitHub repo (web UI)

1. Go to **https://github.com** and log in.
2. Click the **“+”** icon in the top right → **“New repository”**.
3. Fill in:
   - **Repository name**: e.g. `agentic-enterprise-chapters`
   - **Description**: e.g. `LLM-driven chapter pipeline for "The Agentic Enterprise"`
   - Choose **Public** or **Private** (your call).
4. Either:
   - Don’t add a README, or
   - Be okay with overwriting the default README later.
5. Click **“Create repository”**.

You’ll see a repo URL like:

```text
https://github.com/<your-username>/agentic-enterprise-chapters.git
```

You’ll need this in the next step.

---

## 2. Clone the repo locally

On your dev machine (Terminal / PowerShell):

```bash
cd /path/where/you/want/the/repo
git clone https://github.com/<your-username>/agentic-enterprise-chapters.git
cd agentic-enterprise-chapters
```

Now you’re inside the repo folder.

---

## 3. Create the folder structure

From the repo root:

```bash
mkdir -p global
mkdir -p chapters/ch01
mkdir -p prompts
mkdir -p src
mkdir -p tests
mkdir -p logs
```

This matches the structure used in the documentation.

---

## 4. Place the files in the right locations

Download or copy the files into these paths **relative to the repo root**.

### 4.1 Top-level files

Place in repo root:

- `README.md`
- `IMPLEMENTATION_NOTES.md`
- `CONTRIBUTING.md`
- `PIPELINE_USAGE.md`
- `config.yaml`
- `Makefile`

Result:

```text
./README.md
./IMPLEMENTATION_NOTES.md
./CONTRIBUTING.md
./PIPELINE_USAGE.md
./config.yaml
./Makefile
```

### 4.2 Global artifacts

Place in `global/`:

- `book_outline.md`
- `style_profile.md`

Result:

```text
./global/book_outline.md
./global/style_profile.md
```

### 4.3 Chapter 1 artifacts

Place in `chapters/ch01/`:

- `structure_chapter_1.md`
- `chapter_outline_1.md`
- `Chapter_1.md`

Result:

```text
./chapters/ch01/structure_chapter_1.md
./chapters/ch01/chapter_outline_1.md
./chapters/ch01/Chapter_1.md
```

Later you’ll also add:

- `./chapters/ch01/rough_chapter_1.md` (the human rough draft for Chapter 1)

### 4.4 Prompts

Place in `prompts/`:

- `prompts_reference.md`

Result:

```text
./prompts/prompts_reference.md
```

### 4.5 Code & tests

Place in `src/` and `tests/`:

- `orchestrator.py` → `src/orchestrator.py`
- `smoke_ch1.py` → `tests/smoke_ch1.py`

Result:

```text
./src/orchestrator.py
./tests/smoke_ch1.py
```

At this point your tree should roughly look like:

```text
agentic-enterprise-chapters/
  README.md
  IMPLEMENTATION_NOTES.md
  CONTRIBUTING.md
  PIPELINE_USAGE.md
  config.yaml
  Makefile
  /global
    book_outline.md
    style_profile.md
  /chapters
    /ch01
      structure_chapter_1.md
      chapter_outline_1.md
      Chapter_1.md
      # later: rough_chapter_1.md
  /prompts
    prompts_reference.md
  /src
    orchestrator.py
  /tests
    smoke_ch1.py
  /logs
    (empty for now)
```

---

## 5. Initialize and push to GitHub

From the repo root:

```bash
git status        # see all untracked files
git add .
git commit -m "Initial commit: Agentic Enterprise chapter pipeline skeleton"
git push origin main    # or 'master' if your default branch is master
```

Your GitHub repo now has all the pipeline files.

---

## 6. Set up Python environment (recommended)

From the repo root:

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   # Activate the venv:
   source .venv/bin/activate      # macOS/Linux
   # or on Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies (adjust as needed):

   ```bash
   pip install openai
   ```

3. Optionally capture dependencies:

   ```bash
   pip freeze > requirements.txt
   git add requirements.txt
   git commit -m "Add requirements.txt"
   git push
   ```

---

## 7. Wire up `src/orchestrator.py` CLI

The sample `orchestrator.py` is a skeleton. You should:

1. Add CLI argument parsing (e.g., with `argparse`) to support:

   - `--mode outline` → run Step 3 (Chapter Outline Abstractor) for a chapter  
   - `--mode chapter` → run Step 4 (Chapter Generator) for a chapter  
   - `--mode full` → run Step 3 + Step 4 + judges  
   - `--chapter 1` → select `CHAPTER_ID = "1"` (and so on)

2. Implement your actual LLM call in `call_llm()`:
   - Use your chosen provider (OpenAI / Anthropic / Gemini / DeepSeek).
   - Read the model names from `config.yaml` (e.g., `MODEL_CONFIG`).

3. Ensure that the functions:

   - `run_step3_outline(chapter_id, rough_chapter_path)`
   - `run_step4_chapter(chapter_id)`
   - `run_outline_judge(chapter_id)`
   - `run_chapter_judge(chapter_id)`

   are invoked based on the chosen `--mode`.

Once this is wired, the Makefile targets will work as intended.

---

## 8. Use the Makefile commands

From the repo root:

### 8.1 Show available commands

```bash
make help
```

You should see something like:

```text
Agentic Enterprise Chapter Pipeline – Make Targets

  make ch1-outline   # Run Step 3 (outline) for Chapter 1 (requires rough_chapter_1.md)
  make ch1-chapter   # Run Step 4 (chapter generation) for Chapter 1 (after outline exists)
  make ch1-all       # Run outline + chapter + judges for Chapter 1
  make test-ch1      # Run smoke test for Chapter 1 (placeholders, file existence)
```

### 8.2 Run the smoke test

Once files are in place:

```bash
make test-ch1
# or directly:
python -m tests.smoke_ch1
```

You want to see:

```text
Running Chapter 1 smoke test...

Chapter 1 smoke test PASSED.
```

If there are errors (missing files, mismatched placeholders), fix the underlying issue and rerun.

### 8.3 Regenerate Chapter 1 outline and chapter

After you extend `orchestrator.py` for CLI:

- Outline (Step 3):

  ```bash
  make ch1-outline
  ```

- Full chapter (Step 4):

  ```bash
  make ch1-chapter
  ```

- Full pipeline (outline + chapter + judges):

  ```bash
  make ch1-all
  ```

---

## 9. Extend to other chapters

Once Chapter 1 is working end-to-end, you can:

1. Create directories like:

   ```bash
   mkdir -p chapters/ch02
   mkdir -p chapters/ch03
   ```

2. Add human drafts:

   - `chapters/ch02/rough_chapter_2.md`
   - `chapters/ch03/rough_chapter_3.md`
   - etc.

3. Run the same pipeline per `CHAPTER_ID`:
   - Step 1 (structure) as needed.
   - Step 3 (outline extraction).
   - Step 4 (chapter generation).
   - Judges for quality scoring.

4. Optionally, add more smoke tests:
   - e.g., `tests/smoke_ch2.py` and `tests/smoke_ch3.py`, reusing the placeholder-check logic.

---

This document is designed to be drop-in sharable with your developers. They can follow it end-to-end to set up the repo, run the basic tests, and begin integrating the pipeline into QUCreate, Smolagents, LangGraph, or other orchestration frameworks.