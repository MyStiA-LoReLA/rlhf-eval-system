# Lightweight RLHF-style Evaluation System for LLM Output Analysis

An elegant, interactive CLI tool for structured prompt testing and LLM output evaluation, designed to mimic real-world RLHF (Reinforcement Learning from Human Feedback) data collection workflows.

Inspired by platforms like **Outlier**, **Toloka**, and internal LLM alignment pipelines, this system provides a complete evaluation loop: prompt → multi-model inference → side-by-side comparison → structured scoring → failure tagging → JSONL dataset export.

## Key Features

- **Structured Scoring**: Evaluate LLM outputs across four standardized dimensions (correctness, reasoning quality, instruction following, hallucination risk), each scored 0-5.
- **Failure Tagging**: Automatic pre-scan detects common failure modes (incomplete, abstain, repetition), with full manual override and custom tag support.
- **Multi-Model Comparison**: Run two simulated models (Standard-LLM vs. Reasoning-LLM) on the same prompt, with visual side-by-side and structural diff display.
- **Dataset Export**: Output results in standard JSONL format, ready for RLHF training pipelines. Supports both raw evaluation records and pairwise preference datasets.
- **Trace Logging**: Every evaluation is logged with full metadata (prompt, response, scores, tags, timestamp) for auditability and reproducibility.
- **Interactive CLI**: Clean, guided terminal interface with real-time statistics and export options.

## Project Structure

```
rlhf-eval-system/
├── core/
│   ├── llm_runner.py        # Mock model inference (Model_A & Model_B)
│   ├── evaluator.py         # Structured scoring & failure tagging
│   └── comparator.py        # Response comparison & diff display
├── schemas/
│   └── rlhf_schema.py       # Evaluation metrics & data structures
├── logging/
│   ├── trace_logger.py      # Execution trace recording (JSONL)
│   └── dataset_writer.py    # Dataset export & pairwise builder
├── cli/
│   └── main.py              # Interactive CLI entry point
├── data/
│   └── logs.jsonl           # (auto-generated) Evaluation log file
└── README.md
```

## Installation

### Requirements
- Python 3.8 or higher
- No external dependencies required (standard library only)

### Setup

```bash
# Clone or copy the project to your local machine
cd rlhf-eval-system

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

# Ready to run! No pip install needed.
```

## Usage

### Start the Evaluation Terminal

```bash
python cli/main.py
```

### Workflow

1. **Enter a prompt** — Type any question or instruction as you would for an LLM.
2. **Model inference** — Two simulated models generate responses (with simulated latency for realism).
3. **Compare outputs** — View a structured comparison of Model_A (Standard-LLM) and Model_B (Reasoning-LLM).
4. **Score each model** — Rate each response on four dimensions (0-5):
   - `correctness` — Is the answer factually accurate?
   - `reasoning_quality` — Is the logic clear and well-structured?
   - `instruction_following` — Does it follow the user"s instructions?
   - `hallucination_risk` — Does it fabricate information? (higher = safer)
5. **Tag failures** — Confirm or modify automatically detected failure tags, or add custom ones.
6. **Save & continue** — Results are appended to `data/logs.jsonl`. Start a new evaluation or view statistics.

### Menu Options

| Option | Description |
|--------|-------------|
| 1. Start New Evaluation | Run a full evaluation loop on a new prompt |
| 2. View Statistics | Show historical score averages per model and tag distribution |
| 3. Export Dataset | Export evaluation logs in various JSONL formats |
| 4. Export Comparison Dataset | Generate pairwise preference data for RLHF training |
| 5. Exit | Quit the application |

## Dataset Format

### Standard Evaluation Record (JSONL)

```json
{
  "prompt": "Explain supervised vs unsupervised learning.",
  "response": "Supervised learning uses labeled data...",
  "model_name": "Model_B",
  "scores": {
    "correctness": 4,
    "reasoning_quality": 5,
    "instruction_following": 4,
    "hallucination_risk": 4,
    "final_score": 4.25
  },
  "failure_tags": [],
  "timestamp": 1718800000.0
}
```

### Pairwise Preference Record (JSONL)

```json
{
  "prompt": "Explain supervised vs unsupervised learning.",
  "chosen": {
    "response": "Let me break this down step by step...",
    "score": 4.25,
    "model": "Model_B"
  },
  "rejected": {
    "response": "This is a classic ML question...",
    "score": 3.0,
    "model": "Model_A"
  }
}
```

## Extending the System

- **Add real LLM backends**: Replace the mock functions in `core/llm_runner.py` with actual API calls (OpenAI, Anthropic, local models, etc.).
- **Customize scoring criteria**: Edit `SCORE_DIMENSIONS` and `FAILURE_TAGS` in `schemas/rlhf_schema.py`.
- **Add new export formats**: Extend `logging/dataset_writer.py` for custom data pipelines.

## License

This project is provided as an open-source educational tool for LLM evaluation and alignment research.

Built with Python — no external dependencies needed.
