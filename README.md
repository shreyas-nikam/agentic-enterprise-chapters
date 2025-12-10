# Agentic Enterprise Chapter Pipeline – Engineering Guide

This repo describes how to implement a **publisher-grade, multi-step LLM pipeline** for drafting and refining chapters of _The Agentic Enterprise_ (or any similar narrative + analytical book).

It treats LLMs as **junior editors and ghostwriters** that work under:

- A **global book outline** (`book_outline.md`)
- A **book-level style guide** (`style_profile.md`)
- A **chapter-specific structure profile** (`structure_chapter_{CHAPTER_ID}.md`)
- A **chapter-specific content outline** (`chapter_outline_{CHAPTER_ID}.md`)
- A final **chapter draft** (`Chapter_{CHAPTER_ID}.md`)
- Optional **LLM-as-judge** evaluators for outlines and chapters

This README explains:

1. The overall architecture and artifacts  
2. The pipeline steps (0–4) and how to wire prompts  
3. The LLM-as-judge evaluation layer  
4. Suggested folder structure and integration tips  
5. References to all artifacts and prompt templates

---

## 1. High-Level Architecture

We split the process into **global** and **per-chapter** phases:

- **Global (once, occasionally updated)**  
  - Step 0: `raw_book_outline.md` → `book_outline.md`  
  - Step 2: `example_style.md` → `style_profile.md`

- **Per chapter (`CHAPTER_ID`)**  
  - Step 1: `book_outline.md` + `sample_chapter.md` → `structure_chapter_{CHAPTER_ID}.md`  
  - Step 3: `book_outline.md` + `rough_chapter_{CHAPTER_ID}.md` → `chapter_outline_{CHAPTER_ID}.md`  
  - Step 4: `book_outline.md` + `structure_chapter_{CHAPTER_ID}.md` + `style_profile.md` + `chapter_outline_{CHAPTER_ID}.md` → `Chapter_{CHAPTER_ID}.md`

Additionally, we use:

- **Outline Judge** (after Step 3)  
- **Chapter Judge** (after Step 4)

### 1.1 Pipeline Flow (Mermaid)

```mermaid
flowchart TD
    subgraph Global
      RBO[raw_book_outline.md] -->|Step 0| BO[book_outline.md]
      ES[example_style.md] -->|Step 2| SP[style_profile.md]
    end

    subgraph PerChapter[Per Chapter (CHAPTER_ID)]
      BO -->|slice| BOS[book_outline_slice]
      BOS -->|Step 1 + sample_chapter.md| STR[structure_chapter_{CHAPTER_ID}.md]

      BOS -->|Step 3 + rough_chapter_{CHAPTER_ID}.md| OUT[chapter_outline_{CHAPTER_ID}.md]
      OUT -->|Outline Judge| OJ[Outline Score]

      BOS --> CH4[Chapter_{CHAPTER_ID}.md]
      STR --> CH4
      SP --> CH4
      OUT -->|Step 4| CH4

      CH4 -->|Chapter Judge| CJ[Chapter Score]
    end
```

### 1.2 Conceptual Model

At a high level, each step is a **contracted transform**:

- Inputs are clearly labeled blocks (`### BOOK_OUTLINE_SLICE_MD`, `### ROUGH_CHAPTER_MD`, etc.)  
- Outputs have **strict Markdown schemas** (`book_outline.md`, `chapter_outline_{CHAPTER_ID}.md`, etc.)  
- LLMs must not mix commentary with output.

This makes the pipeline:

- Robust across models (OpenAI / Claude / Gemini / DeepSeek)  
- Easy to orchestrate from code (each step is a function call with well-known IO)

---

## 2. Core Artifacts & Schemas

### 2.1 Global Artifacts

#### `book_outline.md`

- **Purpose**: Global spine of the book.
- **Contains**:
  - Book metadata, premise, thesis
  - Primary audiences and book promise
  - Recurring patterns/devices
  - A **Chapter Map**: one entry per `CHAPTER_ID`
  - Cross-cutting themes & constraints
  - Glossary & User Instructions

Each Chapter Map entry includes:

- `Chapter ID` (stable identifier used in all other files)
- `Role in arc`
- `Domain / function`
- `Central question`
- `Key ideas`
- `Key frameworks or tools`
- `Fiction focus`
- `Agentic Enterprise Principle` (number & working title)
- `Dependencies`

#### `style_profile.md`

- **Purpose**: Book-level style guide, derived from a real chapter (`example_style.md`).
- **Contains**:
  - Voice & Tone
  - Narrative patterns (fiction & anecdotes)
  - Exposition patterns (analysis, frameworks)
  - Framing devices
  - Formatting & conventions
  - Constraints & Don’ts
  - Adaptation guidance for other chapters
  - User Instructions

### 2.2 Chapter-Level Artifacts

Each chapter with ID `CHAPTER_ID` has:

- `structure_chapter_{CHAPTER_ID}.md`  
  - Chapter-specific structure (headings, sections, expected content in each Part).
  - No prose; just a spec for shape and headings.

- `chapter_outline_{CHAPTER_ID}.md`  
  - Content outline extracted from a rough human draft.
  - Includes:
    - Central Question, Key Tensions, Core Ideas
    - Fiction elements, Current State themes
    - Frameworks and components
    - Roadmap phases
    - Sidebars
    - Don’ts & Constraints
  - Uses `[[PLACEHOLDER: ...]]` markers for missing or undecided content.

- `Chapter_{CHAPTER_ID}.md`  
  - Full chapter draft:
    - Fiction (Part I)
    - Current State (Part II)
    - Frameworks (Part III)
    - Roadmap (Part IV)
    - Closing Principle section
  - Must preserve all `[[PLACEHOLDER: ...]]` markers.

---

## 3. Placeholders – First-Class Citizens

Throughout the pipeline, we use a strict placeholder format:

```text
[[PLACEHOLDER: clear description of what is missing or needs a decision]]
```

**Rules:**

- Step 3 (Chapter Outline Abstractor) inserts placeholders where information is missing, ambiguous, or requires human judgment.
- Step 4 (Chapter Generator) must:
  - Copy placeholders **verbatim** into the final chapter.
  - Place them in contextually appropriate spots.
  - **Never resolve or rephrase** them.

This pattern gives:

- **Guardrails** against hallucination.
- Clear TODOs for human editors.
- Future-proof integration (editors can search on `[[PLACEHOLDER:`).

---

## 4. Pipeline Steps & Prompt Integration

This section explains how engineers should call each model, what context to send, and how to slice inputs.

We assume:

- You are using a client that supports **system** and **user** messages.
- You will load template prompts from `prompts_reference.md`.

### 4.1 Step 0 – Book Outline Abstractor

**Goal:** Convert a rough book outline into a canonical `book_outline.md`.

**Inputs:**

- `raw_book_outline.md` (human-written)
- `user_instructions_step0` (optional editor notes)

**Model Call:**

- **System**: `Step 0 – Book Outline Abstractor (system prompt)` from `prompts_reference.md`
- **User**: Inject:
  - `### RAW_BOOK_OUTLINE_MD`
  - `### USER_INSTRUCTIONS_STEP0`
  - Schema snippet for `book_outline.md`

**Output:**

- `book_outline.md` (Markdown)
- You should write this to disk and version it.

### 4.2 Step 1 – Chapter Structure Abstractor

**Goal:** Derive `structure_chapter_{CHAPTER_ID}.md` for a specific chapter.

**Inputs:**

- Slice of `book_outline.md`:
  - Global metadata + constraints
  - Chapter Map entry for `CHAPTER_ID`
- `sample_chapter.md` (a polished reference chapter)
- `user_instructions_step1`

**Model Call:**

- **System**: `Step 1 – Chapter Structure Abstractor (system prompt)`
- **User**: Inject:
  - `### BOOK_OUTLINE_SLICE_MD`
  - `### CHAPTER_ID`
  - `### SAMPLE_CHAPTER_MD`
  - `### USER_INSTRUCTIONS_STEP1`
  - `### STRUCTURE_SCHEMA` (schema snippet)

**Output:**

- `structure_chapter_{CHAPTER_ID}.md`

**Note:** You can reuse the same `sample_chapter.md` across multiple `CHAPTER_ID`s as long as structure is shared.

### 4.3 Step 2 – Style Abstractor

**Goal:** From `example_style.md`, derive `style_profile.md`.

**Inputs:**

- Global sections of `book_outline.md`
- `example_style.md` (e.g., Chapter 0)
- `user_instructions_step2`

**Model Call:**

- **System**: `Step 2 – Style Abstractor (system prompt)`
- **User**: Inject:
  - `### BOOK_OUTLINE_SLICE_MD` (just global sections)
  - `### EXAMPLE_STYLE_MD`
  - `### USER_INSTRUCTIONS_STEP2`
  - `### STYLE_SCHEMA` (schema snippet)

**Output:**

- `style_profile.md` (used by all chapters)

### 4.4 Step 3 – Chapter Outline Abstractor

**Goal:** Convert a messy human draft into `chapter_outline_{CHAPTER_ID}.md`.

**Inputs:**

- Slice of `book_outline.md` for `CHAPTER_ID`
- `rough_chapter_{CHAPTER_ID}.md`
- `user_instructions_step3`

**Model Call:**

- **System**: `Step 3 – Chapter Outline Abstractor (system prompt)`
- **User**: Inject:
  - `### BOOK_OUTLINE_SLICE_MD`
  - `### CHAPTER_ID`
  - `### ROUGH_CHAPTER_MD`
  - `### USER_INSTRUCTIONS_STEP3`
  - `### CHAPTER_OUTLINE_SCHEMA` (schema snippet)

**Output:**

- `chapter_outline_{CHAPTER_ID}.md` with:
  - Central question
  - Key tensions, core ideas
  - Fiction, current state, frameworks, roadmap
  - Sidebars
  - `[[PLACEHOLDER: ...]]` entries where needed

**Important:** Engineers must **not post-process** placeholders. Treat them as data.

### 4.5 Step 4 – Chapter Generator

**Goal:** Generate full chapter `Chapter_{CHAPTER_ID}.md`.

**Inputs:**

- Slice of `book_outline.md` for `CHAPTER_ID`
- `structure_chapter_{CHAPTER_ID}.md`
- `style_profile.md`
- `chapter_outline_{CHAPTER_ID}.md`
- `user_instructions_step4`

**Model Call:**

- **System**: `Step 4 – Chapter Generator (system prompt)`
- **User**: Inject:
  - `### BOOK_OUTLINE_SLICE_MD`
  - `### CHAPTER_ID`
  - `### STRUCTURE_CHAPTER_MD`
  - `### STYLE_PROFILE_MD`
  - `### CHAPTER_OUTLINE_MD`
  - `### USER_INSTRUCTIONS_STEP4`
  - Add “Return ONLY the final chapter Markdown.”

**Output:**

- `Chapter_{CHAPTER_ID}.md` (complete chapter)

**Hard constraints for LLM:**

- Must follow section headings from `structure_chapter_{CHAPTER_ID}.md`.
- Must adopt voice from `style_profile.md`.
- Must implement content from `chapter_outline_{CHAPTER_ID}.md`.
- Must copy all placeholders exactly as they appear.

---

## 5. LLM-as-Judge Evaluators

To keep quality high and enable automated checks, we use **LLM-as-judge** patterns.

### 5.1 Outline Judge

**When:** After Step 3, once `chapter_outline_{CHAPTER_ID}.md` is generated.

**Inputs:**

- Chapter slice from `book_outline.md`
- (Optional) high-level excerpt from `style_profile.md`
- `chapter_outline_{CHAPTER_ID}.md`

**Model Call:**

- **System**: `Outline Judge (system prompt)`
- **User**: Provide the three inputs with clear section labels.

**Output:**

- Scores (0–10) on:
  - Structure completeness
  - Alignment with book outline
  - Placeholder clarity
  - Coverage of core content
- 3–5 bullet editorial notes

**Integration Tip:**

- If any score < threshold (e.g., 7/10), you can:
  - Flag the outline for human review, or
  - Re-run Step 3 with updated instructions.

### 5.2 Chapter Judge

**When:** After Step 4, once `Chapter_{CHAPTER_ID}.md` is generated.

**Inputs:**

- Chapter slice from `book_outline.md`
- `structure_chapter_{CHAPTER_ID}.md`
- `style_profile.md`
- `chapter_outline_{CHAPTER_ID}.md`
- `Chapter_{CHAPTER_ID}.md`

**Model Call:**

- **System**: `Chapter Judge (system prompt)`
- **User**: Provide all five inputs with clear labels.

**Output:**

- Scores (0–10) on:
  - Structure adherence
  - Style adherence
  - Content alignment
  - Placeholder handling
- 3–7 bullet editorial notes

**Integration Tip:**

- Use these scores to:
  - Automatically accept/reject drafts.
  - Rank multiple drafts if you generate more than one.

---

## 6. Suggested Folder Structure

A simple structure for engineers:

```text
/agentic-enterprise/
  /global/
    raw_book_outline.md
    book_outline.md
    example_style.md
    style_profile.md

  /chapters/
    /ch01/
      rough_chapter_1.md
      structure_chapter_1.md
      chapter_outline_1.md
      Chapter_1.md
    /ch02/
      rough_chapter_2.md
      structure_chapter_2.md
      chapter_outline_2.md
      Chapter_2.md
    ...

  /prompts/
    prompts_reference.md

  /logs/
    step0_runs.jsonl
    step1_runs.jsonl
    ...
```

**Recommendations:**

- Store each model call’s:
  - Inputs (hash or snapshot)
  - System prompt version ID
  - Model name and parameters
  - Outputs (file paths)
- This will allow reproducibility across prompt/model iterations.

---

## 7. Multi-Model & Config Strategy

Different steps can use different model classes:

- **Steps 0 & 3** (extraction, structuring):
  - Can often use a mid-tier or “fast” model.
- **Steps 1, 2 & 4** (structure, style, final generation):
  - Should use your highest-quality reasoning/completion model.

Make this configurable via a `config.yaml` or environment variables, e.g.:

```yaml
models:
  step0: gpt-5.1-mini
  step1: gpt-5.1-thinking
  step2: gpt-5.1-thinking
  step3: gpt-5.1-mini
  step4: gpt-5.1-thinking
  outline_judge: gpt-5.1-thinking
  chapter_judge: gpt-5.1-thinking
```

---

## 8. References to Artifacts & Prompts

This package includes:

- **Artifacts (Chapter 1 example):**
  - `book_outline.md` – global spine for The Agentic Enterprise.
  - `style_profile.md` – style derived from Chapter 0.
  - `structure_chapter_1.md` – structure for Chapter 1.
  - `chapter_outline_1.md` – outline for Chapter 1 (with placeholders).
  - `Chapter_1.md` – generated chapter draft.

- **Prompt templates:**
  - Step 0 – Book Outline Abstractor (system + user)
  - Step 1 – Chapter Structure Abstractor (system + user)
  - Step 2 – Style Abstractor (system + user)
  - Step 3 – Chapter Outline Abstractor (system + user)
  - Step 4 – Chapter Generator (system + user)
  - Outline Judge (system + user)
  - Chapter Judge (system + user)

All prompt text is collected in `prompts_reference.md` for direct use.

---

## 9. How to Get Started (Engineer Checklist)

1. **Load the global artifacts:**
   - Start with `raw_book_outline.md` and `example_style.md`.
   - Run Step 0 and Step 2 to generate `book_outline.md` and `style_profile.md`.

2. **Wire the prompt templates:**
   - Copy `prompts_reference.md` into your codebase.
   - Build helper functions that:
     - Load system prompt.
     - Inject user sections.
     - Call the LLM.
     - Save outputs.

3. **Implement Chapter 1 as a pilot:**
   - Use `structure_chapter_1.md`, `chapter_outline_1.md`, and `style_profile.md` from this package.
   - Run Step 4 to regenerate `Chapter_1.md`.
   - Run Outline Judge and Chapter Judge evaluators and log scores.

4. **Generalize for all chapters:**
   - For each new `CHAPTER_ID`:
     - Create `rough_chapter_{CHAPTER_ID}.md` (from human drafts).
     - Run Step 1 and Step 3.
     - Optionally review/adjust structure/outline.
     - Run Step 4 to generate the chapter.
     - Evaluate with both judges.

5. **Iterate:**
   - Tweak prompts and schemas in `prompts_reference.md` only.
   - Keep artifacts (`book_outline.md`, `style_profile.md`, `structure_*`, `chapter_outline_*`) as content, not code.

If you follow this structure, your engineering team can treat the book like a reproducible software project: versioned, testable, and ready to evolve alongside the models.