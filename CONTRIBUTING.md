# CONTRIBUTING.md – Agentic Enterprise Chapter Pipeline

Welcome! This repo powers the **Agentic Enterprise chapter pipeline** – a structured, multi-step LLM workflow that treats the book like a software project.

This guide explains how **authors, editors, and engineers** can safely extend and modify the system without breaking the pipeline.

---

## 1. Roles & Responsibilities

### Authors / Subject-Matter Experts

- Provide:
  - Rough chapter drafts in Markdown (`rough_chapter_{CHAPTER_ID}.md`).
  - High-level book outline (`raw_book_outline.md`) and example style chapter (`example_style.md`).
- Review:
  - `chapter_outline_{CHAPTER_ID}.md` – confirm central questions, key ideas, and placeholders.
  - `Chapter_{CHAPTER_ID}.md` – final text before publication.

### Editors

- Own:
  - `book_outline.md` – the canonical book spine.
  - `style_profile.md` – book-level style guide.
  - `structure_chapter_{CHAPTER_ID}.md` – chapter-level structure specs.
  - Placeholder resolution and high-level editorial changes.
- Decide:
  - When to lock sections or chapters.
  - When to update prompts (via `prompts/prompts_reference.md`).

### Engineers

- Own:
  - Orchestration code (`src/`, especially `orchestrator.py`).
  - Model configuration (`config.yaml`).
  - Logging, error handling, and integrations (QUCreate, Smolagents, LangGraph, etc.).

---

## 2. File Layout – What Lives Where

```text
/global/
  raw_book_outline.md        # Human-written initial outline (optional, one-time)
  book_outline.md            # Structured spine (Step 0 output)
  example_style.md           # Example chapter used to infer style
  style_profile.md           # Canonical book style (Step 2 output)

/chapters/
  /ch01/
    rough_chapter_1.md       # Human rough draft
    structure_chapter_1.md   # Structure spec (Step 1 output)
    chapter_outline_1.md     # Content outline + placeholders (Step 3 output)
    Chapter_1.md             # Generated chapter (Step 4 output)
  /ch02/
    ...

/prompts/
  prompts_reference.md       # All system + user template prompts

/src/
  orchestrator.py            # Sample orchestrator (pipeline runner)
  ...                        # Future QUCreate/Smolagents/LangGraph integrations

/logs/
  ...                        # JSONL logs for runs, judges, etc.
```

---

## 3. Working with Global Files

### 3.1 `book_outline.md`

- **Source of truth** for:
  - Chapter IDs, titles, roles in the arc.
  - Agentic Enterprise Principle numbers and working titles.
  - Cross-cutting constraints.
- **DO:**
  - Update chapter metadata here when:
    - Titles change.
    - New chapters are added.
    - Principle numbers/titles are finalized.
- **DO NOT:**
  - Change chapter IDs once they’re in use (`CHAPTER_ID` must remain stable).
  - Remove sections used by prompts (e.g., “Chapter Map”, “Cross-Cutting Themes”).

After meaningful changes to `book_outline.md`:

- Re-run:
  - Step 1 (structure) for affected chapters.
  - Step 3 (outline) if chapter scope changed.
  - Step 4 (chapter generation) as needed.

### 3.2 `style_profile.md`

- Defines:
  - Voice & tone.
  - Narrative and exposition patterns.
  - Formatting conventions and “don’ts”.
- **If you tweak tone** (e.g., more conversational, more formal):
  - Update `style_profile.md`.
  - Re-run Step 4 for any chapters that should adopt the new tone.

### 3.3 `example_style.md`

- Acts as the **style exemplar** from which `style_profile.md` was derived.
- Usually a polished chapter such as Chapter 0.
- Update this only if you deliberately want to **re-derive** the style.

---

## 4. Per-Chapter Workflow

For a new chapter `CHAPTER_ID`:

1. **Author writes rough draft:**
   - Save as `/chapters/ch{CHAPTER_ID}/rough_chapter_{CHAPTER_ID}.md`.

2. **Engineer/Editor runs Step 1 (optional if pattern already stable):**
   - Produces `structure_chapter_{CHAPTER_ID}.md`.
   - Often copied/derived from an existing structure (e.g., Chapter 1/2).

3. **Engineer runs Step 3 – Chapter Outline Abstractor:**
   - Inputs:
     - `book_outline.md` slice.
     - `rough_chapter_{CHAPTER_ID}.md`.
   - Output:
     - `chapter_outline_{CHAPTER_ID}.md` with `[[PLACEHOLDER: ...]]` markers.

4. **Editor reviews `chapter_outline_{CHAPTER_ID}.md`:**
   - Refines:
     - Central question.
     - Key tensions & core ideas.
     - Framework definitions & roadmap phases.
   - Fills or clarifies placeholders when possible.

5. **Engineer runs Step 4 – Chapter Generator:**
   - Inputs:
     - `book_outline.md` slice.
     - `structure_chapter_{CHAPTER_ID}.md`.
     - `style_profile.md`.
     - `chapter_outline_{CHAPTER_ID}.md`.
   - Output:
     - `Chapter_{CHAPTER_ID}.md`.

6. **Judges (optional but recommended):**
   - Run Outline Judge after Step 3.
   - Run Chapter Judge after Step 4.
   - Use scores to decide:
     - Auto-accept.
     - Flag for manual review.
     - Re-run with adjusted instructions.

---

## 5. Placeholders – Critical Rules

Placeholders use the format:

```text
[[PLACEHOLDER: clear description of what is missing or needs a decision]]
```

**DO:**

- Insert placeholders in outlines whenever:
  - Information is missing.
  - A decision is editorial (e.g., “Sri to confirm whether to include Nationwide example”).
- Move placeholders around in `Chapter_{CHAPTER_ID}.md` to place them where contextually appropriate.

**DO NOT:**

- Delete placeholders silently.
- Rewrite the text inside a placeholder in a way that changes its meaning.
- Ask the LLM to “fill in” placeholders; they are for humans.

If a placeholder is resolved:

- Replace the entire `[[PLACEHOLDER: ...]]` with real text.
- Optionally, note this in commit messages for traceability.

---

## 6. Editing Prompts

All prompts live in:

- `prompts/prompts_reference.md`

**When editing prompts:**

- Keep **section headers** unchanged:
  - `## Step 0 – Book Outline Abstractor`
  - `## Step 1 – Chapter Structure Abstractor`
  - `## Step 2 – Style Abstractor`
  - `## Step 3 – Chapter Outline Abstractor`
  - `## Step 4 – Chapter Generator`
  - `## Outline Judge – Evaluation Prompt`
  - `## Chapter Judge – Evaluation Prompt`
- Avoid renaming or removing these headers; the orchestrator uses them for lookup.
- Maintain:
  - Clear `System Prompt` and `User Prompt` code blocks under each header.
  - The output contracts (e.g., “Return ONLY the Markdown for …”).

**Best practice:**

- If making substantial prompt changes:
  - Add a brief comment at the top of the section with date + reason.
  - Update `config.yaml` with a new `project.version` if the behavior is meaningfully different.

---

## 7. Code Contributions

### 7.1 Python / Orchestration

- Primary entry point:
  - `src/orchestrator.py` (sample pipeline runner)
- When adding integrations (e.g., QUCreate, Smolagents, LangGraph):
  - Put them in `src/` under a clear module namespace (e.g., `src/qucreate/`, `src/workflows/`).
  - Keep **core pipeline logic** (step runners, prompt loaders) reusable and UI-agnostic.

### 7.2 Tests / Dry Runs

At a minimum:

- Add a **“smoke test”** that:
  - Loads `book_outline.md` and `style_profile.md`.
  - Runs Step 3 and Step 4 for Chapter 1 using the provided fixtures.
  - Validates:
    - Outputs are non-empty.
    - Placeholders from `chapter_outline_1.md` are present in `Chapter_1.md`.

- Future:
  - Add snapshot-based tests for prompts, outlines, and chapters.

---

## 8. Commit & PR Guidelines

When opening a PR:

- Clearly indicate what you changed:

  - `[content]` if you changed outlines/chapters.
  - `[style]` if you changed `style_profile.md`.
  - `[structure]` if you changed `book_outline.md` or `structure_chapter_*`.
  - `[prompts]` if you changed `prompts_reference.md`.
  - `[engine]` if you changed orchestration code.

- Include a short checklist such as:

  - [ ] Ran Step 3 + Step 4 for affected chapters (list them).
  - [ ] Verified placeholders preserved in final chapters.
  - [ ] Ran outline/chapter judges for affected chapters.
  - [ ] Updated `config.yaml` if model or threshold changes were made.

---

## 9. Questions & Future Extensions

If you’re unsure whether something belongs in:

- `book_outline.md` vs `chapter_outline_x.md`
- `style_profile.md` vs `prompts_reference.md`

Use this rule of thumb:

- **Book-level & cross-cutting?** → `book_outline.md` or `style_profile.md`.
- **Chapter-specific content or decisions?** → `chapter_outline_{CHAPTER_ID}.md`.
- **How models should think / behave?** → `prompts_reference.md`.
- **How code should run?** → `config.yaml` and `src/`.

As the project evolves, we may add:

- Section-level regeneration (e.g., regenerate only Part II).
- More granular judges (e.g., style-only, structure-only).
- Exporters (e.g., to Word/LaTeX/InDesign).

Contributions toward these directions are welcome—just keep the pipeline modular, testable, and respectful of the editorial contracts described here.