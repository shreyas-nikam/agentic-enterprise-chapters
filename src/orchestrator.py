# orchestrator.py – Sample Pipeline Orchestrator for Agentic Enterprise
"""
Minimal example of how to wire Steps 0–4 + judges in Python.

Assumptions:
- You are using an OpenAI-compatible client.
- Prompts are stored in `prompts/prompts_reference.md`.
- Artifacts are stored under `/global` and `/chapters/chXX`.

This is intentionally simple and can be adapted into QUCreate/Smolagents/LangGraph.
"""

import os
from pathlib import Path
from typing import Dict, Tuple

import openai  # or from openai import OpenAI (depending on SDK)


# -------------------- Config --------------------

BASE_DIR = Path(__file__).resolve().parent.parent
GLOBAL_DIR = BASE_DIR / "global"
CHAPTERS_DIR = BASE_DIR / "chapters"
PROMPTS_PATH = BASE_DIR / "prompts" / "prompts_reference.md"

MODEL_CONFIG = {
    "step0": "gpt-5.1-mini",
    "step1": "gpt-5.1-thinking",
    "step2": "gpt-5.1-thinking",
    "step3": "gpt-5.1-mini",
    "step4": "gpt-5.1-thinking",
    "outline_judge": "gpt-5.1-thinking",
    "chapter_judge": "gpt-5.1-thinking",
}


# -------------------- Helpers --------------------

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def call_llm(system_prompt: str, user_prompt: str, model_name: str) -> str:
    """Simple wrapper around an OpenAI-style chat completion call.

    Replace with your actual SDK usage.
    """
    client = openai.Client()
    resp = client.responses.create(
        model=model_name,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    # Extract text from the first output
    return resp.output[0].content[0].text


# -------------------- Prompt Loading --------------------

def load_prompts_section(section_header: str) -> Tuple[str, str]:
    """Very simple extractor: finds a section in prompts_reference.md
    by its markdown header and returns (system_prompt, user_prompt).

    In production, you may want a more robust parser or separate files.
    """
    text = read_text(PROMPTS_PATH)
    if not text:
        raise RuntimeError(f"prompts_reference.md not found at {PROMPTS_PATH}")

    # naive split by section header
    sections = text.split("## ")
    target = None
    for sec in sections:
        if sec.strip().startswith(section_header):
            target = sec
            break
    if target is None:
        raise ValueError(f"Section '{section_header}' not found in prompts_reference.md")

    # Extract code blocks labelled System/User Prompt
    # This is intentionally simple: assumes one system and one user block per section.
    system_prompt = ""
    user_prompt = ""

    blocks = target.split("```")
    for i, block in enumerate(blocks):
        if "System Prompt" in blocks[i - 1]:
            system_prompt = block.strip("text\n").strip()
        if "User Prompt" in blocks[i - 1]:
            user_prompt = block.strip("text\n").strip()

    if not system_prompt or not user_prompt:
        raise ValueError(f"Could not parse system/user prompts for '{section_header}'")

    return system_prompt, user_prompt


# -------------------- Step Runners --------------------

def slice_book_outline_for_chapter(book_outline: str, chapter_id: str) -> str:
    """Very basic heuristic: extracts the chapter map entry for CHAPTER_ID plus
    global metadata and constraints.

    In production, consider adding explicit markers in book_outline.md.
    """
    # For now, just return full book_outline; editors can refine later.
    return book_outline


def run_step0_book_outline(raw_book_outline_path: Path) -> Path:
    system_prompt, user_template = load_prompts_section("Step 0 – Book Outline Abstractor")
    raw_outline = read_text(raw_book_outline_path)
    user_prompt = user_template.replace("{{raw_book_outline_md}}", raw_outline)
    user_prompt = user_prompt.replace("{{user_instructions_step0}}", "")

    model = MODEL_CONFIG["step0"]
    output = call_llm(system_prompt, user_prompt, model)

    out_path = GLOBAL_DIR / "book_outline.md"
    write_text(out_path, output)
    return out_path


def run_step2_style(example_style_path: Path) -> Path:
    system_prompt, user_template = load_prompts_section("Step 2 – Style Abstractor")
    book_outline = read_text(GLOBAL_DIR / "book_outline.md")
    example_style = read_text(example_style_path)

    user_prompt = user_template.replace("{{book_outline_global_sections}}", book_outline)
    user_prompt = user_prompt.replace("{{example_style_md}}", example_style)
    user_prompt = user_prompt.replace("{{user_instructions_step2}}", "")

    model = MODEL_CONFIG["step2"]
    output = call_llm(system_prompt, user_prompt, model)

    out_path = GLOBAL_DIR / "style_profile.md"
    write_text(out_path, output)
    return out_path


def run_step1_structure(chapter_id: str, sample_chapter_path: Path) -> Path:
    system_prompt, user_template = load_prompts_section("Step 1 – Chapter Structure Abstractor")
    book_outline = read_text(GLOBAL_DIR / "book_outline.md")
    sample_chapter = read_text(sample_chapter_path)

    user_prompt = user_template
    user_prompt = user_prompt.replace("{{book_outline_slice_for_chapter}}", slice_book_outline_for_chapter(book_outline, chapter_id))
    user_prompt = user_prompt.replace("{{CHAPTER_ID}}", chapter_id)
    user_prompt = user_prompt.replace("{{sample_chapter_md}}", sample_chapter)
    user_prompt = user_prompt.replace("{{user_instructions_step1}}", "")
    # In this simple example, we do not inline the STRUCTURE_SCHEMA; you can if desired.

    model = MODEL_CONFIG["step1"]
    output = call_llm(system_prompt, user_prompt, model)

    out_path = CHAPTERS_DIR / f"ch{chapter_id.zfill(2)}" / f"structure_chapter_{chapter_id}.md"
    write_text(out_path, output)
    return out_path


def run_step3_outline(chapter_id: str, rough_chapter_path: Path) -> Path:
    system_prompt, user_template = load_prompts_section("Step 3 – Chapter Outline Abstractor")
    book_outline = read_text(GLOBAL_DIR / "book_outline.md")
    rough_chapter = read_text(rough_chapter_path)

    user_prompt = user_template
    user_prompt = user_prompt.replace("{{book_outline_slice_for_chapter}}", slice_book_outline_for_chapter(book_outline, chapter_id))
    user_prompt = user_prompt.replace("{{CHAPTER_ID}}", chapter_id)
    user_prompt = user_prompt.replace("{{rough_chapter_md}}", rough_chapter)
    user_prompt = user_prompt.replace("{{user_instructions_step3}}", "")

    model = MODEL_CONFIG["step3"]
    output = call_llm(system_prompt, user_prompt, model)

    out_path = CHAPTERS_DIR / f"ch{chapter_id.zfill(2)}" / f"chapter_outline_{chapter_id}.md"
    write_text(out_path, output)
    return out_path


def run_step4_chapter(chapter_id: str) -> Path:
    system_prompt, user_template = load_prompts_section("Step 4 – Chapter Generator")
    book_outline = read_text(GLOBAL_DIR / "book_outline.md")
    style_profile = read_text(GLOBAL_DIR / "style_profile.md")

    ch_dir = CHAPTERS_DIR / f"ch{chapter_id.zfill(2)}"
    structure_chapter = read_text(ch_dir / f"structure_chapter_{chapter_id}.md")
    chapter_outline = read_text(ch_dir / f"chapter_outline_{chapter_id}.md")

    user_prompt = user_template
    user_prompt = user_prompt.replace("{{book_outline_slice_for_chapter}}", slice_book_outline_for_chapter(book_outline, chapter_id))
    user_prompt = user_prompt.replace("{{CHAPTER_ID}}", chapter_id)
    user_prompt = user_prompt.replace("{{structure_chapter_md}}", structure_chapter)
    user_prompt = user_prompt.replace("{{style_profile_md}}", style_profile)
    user_prompt = user_prompt.replace("{{chapter_outline_md}}", chapter_outline)
    user_prompt = user_prompt.replace("{{user_instructions_step4}}", "")

    model = MODEL_CONFIG["step4"]
    output = call_llm(system_prompt, user_prompt, model)

    out_path = ch_dir / f"Chapter_{chapter_id}.md"
    write_text(out_path, output)
    return out_path


# -------------------- Judges (Skeleton) --------------------

def run_outline_judge(chapter_id: str) -> str:
    system_prompt, user_template = load_prompts_section("Outline Judge – Evaluation Prompt")
    book_outline = read_text(GLOBAL_DIR / "book_outline.md")
    style_profile = read_text(GLOBAL_DIR / "style_profile.md")
    ch_dir = CHAPTERS_DIR / f"ch{chapter_id.zfill(2)}"
    chapter_outline = read_text(ch_dir / f"chapter_outline_{chapter_id}.md")

    user_prompt = user_template
    user_prompt = user_prompt.replace("{{book_outline_slice_for_chapter}}", slice_book_outline_for_chapter(book_outline, chapter_id))
    user_prompt = user_prompt.replace("{{style_profile_excerpt}}", style_profile[:2000])
    user_prompt = user_prompt.replace("{{chapter_outline_md}}", chapter_outline)

    model = MODEL_CONFIG["outline_judge"]
    output = call_llm(system_prompt, user_prompt, model)
    return output


def run_chapter_judge(chapter_id: str) -> str:
    system_prompt, user_template = load_prompts_section("Chapter Judge – Evaluation Prompt")
    book_outline = read_text(GLOBAL_DIR / "book_outline.md")
    style_profile = read_text(GLOBAL_DIR / "style_profile.md")
    ch_dir = CHAPTERS_DIR / f"ch{chapter_id.zfill(2)}"
    structure_chapter = read_text(ch_dir / f"structure_chapter_{chapter_id}.md")
    chapter_outline = read_text(ch_dir / f"chapter_outline_{chapter_id}.md")
    chapter_md = read_text(ch_dir / f"Chapter_{chapter_id}.md")

    user_prompt = user_template
    user_prompt = user_prompt.replace("{{book_outline_slice_for_chapter}}", slice_book_outline_for_chapter(book_outline, chapter_id))
    user_prompt = user_prompt.replace("{{structure_chapter_md}}", structure_chapter)
    user_prompt = user_prompt.replace("{{style_profile_md}}", style_profile)
    user_prompt = user_prompt.replace("{{chapter_outline_md}}", chapter_outline)
    user_prompt = user_prompt.replace("{{chapter_md}}", chapter_md)

    model = MODEL_CONFIG["chapter_judge"]
    output = call_llm(system_prompt, user_prompt, model)
    return output


# -------------------- Example main() --------------------

def main():
    """Example: run the pipeline for Chapter 1.

    This assumes:
    - /global/book_outline.md and /global/style_profile.md already exist, OR
    - You call run_step0_book_outline + run_step2_style first.
    """
    chapter_id = "1"
    ch_dir = CHAPTERS_DIR / f"ch{chapter_id.zfill(2)}"

    # Example: run Step 3 (outline) and Step 4 (chapter) for Chapter 1
    rough_path = ch_dir / f"rough_chapter_{chapter_id}.md"
    if not rough_path.exists():
        raise FileNotFoundError(f"Missing {rough_path}; add the human rough draft first.")

    outline_path = run_step3_outline(chapter_id, rough_path)
    print(f"Wrote chapter outline to: {outline_path}")

    chapter_path = run_step4_chapter(chapter_id)
    print(f"Wrote chapter draft to: {chapter_path}")

    # Optional: run judges
    outline_eval = run_outline_judge(chapter_id)
    chapter_eval = run_chapter_judge(chapter_id)
    print("Outline Judge:\n", outline_eval)
    print("Chapter Judge:\n", chapter_eval)


if __name__ == "__main__":
    main()