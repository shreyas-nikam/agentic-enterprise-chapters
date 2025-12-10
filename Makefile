# Makefile – Agentic Enterprise Chapter Pipeline
#
# Simple convenience targets for running the pipeline and tests.
# Assumes:
#   - Python environment is active
#   - src/orchestrator.py exists
#   - tests/smoke_ch1.py exists
#
# You can run:
#   make help
#   make ch1-outline
#   make ch1-chapter
#   make ch1-all
#   make test-ch1

.PHONY: help ch1-outline ch1-chapter ch1-all test-ch1 lint

help:
	@echo "Agentic Enterprise Chapter Pipeline – Make Targets"
	@echo ""
	@echo "  make ch1-outline   # Run Step 3 (outline) for Chapter 1 (requires rough_chapter_1.md)"
	@echo "  make ch1-chapter   # Run Step 4 (chapter generation) for Chapter 1 (after outline exists)"
	@echo "  make ch1-all       # Run outline + chapter + judges for Chapter 1"
	@echo "  make test-ch1      # Run smoke test for Chapter 1 (placeholders, file existence)"
	@echo ""

# Run Step 3 (outline) + judges for Chapter 1.
# Note: the sample orchestrator currently runs Step 3 + Step 4 + judges together.
# If you split orchestrator.py later, you can refine these targets.
ch1-outline:
	@echo ">>> Generating outline for Chapter 1 (Step 3)..."
	python src/orchestrator.py --mode outline --chapter 1

# Generate full Chapter 1 (Step 4) using existing outline, structure, style.
ch1-chapter:
	@echo ">>> Generating full Chapter 1 (Step 4)..."
	python src/orchestrator.py --mode chapter --chapter 1

# Convenience target: run the full pipeline for Chapter 1.
ch1-all:
	@echo ">>> Running full pipeline for Chapter 1 (outline + chapter + judges)..."
	python src/orchestrator.py --mode full --chapter 1

# Run the smoke test for Chapter 1.
test-ch1:
	@echo ">>> Running smoke test for Chapter 1..."
	python -m tests.smoke_ch1
