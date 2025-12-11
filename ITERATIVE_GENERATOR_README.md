# Recent changes (2025-12-10)

- Added note: iterative generation runs should use the repository venv; if you see import/version errors when running the generator, check VS Code's selected interpreter and run `pip install -r requirements.txt` inside the venv.

# Iterative PowerPoint Generator with VLM Evaluation

An intelligent system that generates multiple PowerPoint presentations, evaluates them using Vision Language Models (VLM), and iteratively improves until a quality threshold is met.

## Overview

This system creates **3 different slide decks** from the same source material, each with different themes and layouts:
1. **Executive Overview** - Business-focused, high-level impact
2. **Technical Deep Dive** - Detailed methodology and architecture  
3. **Results & Impact** - Performance metrics and practical applications

Each presentation is evaluated by a VLM that provides:
- **Scores** (0-100) for various criteria
- **Structured suggestions** in JSON format
- **Priority improvements**

The system iterates until one of the presentations meets the score threshold, then sends it to human review.

## Features

- ✅ Generates 3 themed presentations from JSON input
- ✅ VLM-based evaluation with scores and suggestions
- ✅ Iterative improvement loop
- ✅ Multiple VLM backends (Gemini, Ollama, Local, Text-based)
- ✅ Human review notification system
- ✅ Comprehensive result tracking

## Installation

Ensure you have the required dependencies:

```bash
pip install python-pptx openai google-generativeai sentence-transformers
```

For VLM backends:
- **Gemini**: Requires `google-generativeai` and API key
- **Ollama**: Requires Ollama installed locally
- **Local**: Requires `transformers` and `torch`
- **Text-based**: No additional dependencies (fallback)

## Usage

### Basic Usage

```bash
python iterative_powerpoint_generator.py retrieval_output/data.json
```

### With Custom Settings

```bash
python iterative_powerpoint_generator.py retrieval_output/data.json \
    --output-dir my_output \
    --threshold 80 \
    --max-iterations 3 \
    --vlm-backend gemini \
    --vlm-api-key YOUR_GEMINI_KEY
```

### Command Line Arguments

- `json_input` (required): Path to input JSON file (retrieval output)
- `--output-dir`: Output directory (default: `iterative_output`)
- `--threshold`: Score threshold 0-100 (default: 75.0)
- `--max-iterations`: Maximum iterations (default: 5)
- `--vlm-backend`: VLM backend (`auto`, `local`, `ollama`, `gemini`, `text`)
- `--vlm-api-key`: VLM API key (for Gemini)
- `--evaluator-api-key`: Evaluator API key (for OpenAI, or set `OPENAI_API_KEY` env var)

## How It Works

### 1. Generation Phase
- Loads content from JSON input file
- Generates 3 presentations with different themes:
  - **Executive**: Business impact, metrics, ROI
  - **Technical**: Methodology, architecture, details
  - **Results**: Performance, outcomes, visualizations

### 2. Evaluation Phase
- Each presentation is evaluated by:
  - **VLM Analyzer**: Visual and content analysis
  - **Slide Evaluator**: Structured scoring on clarity, accuracy, visual balance, audience fit
- Returns scores and structured suggestions in JSON

### 3. Iteration Loop
- Continues generating and evaluating until:
  - A presentation meets the score threshold, OR
  - Maximum iterations reached
- Tracks best presentation across all iterations

### 4. Human Review
- When threshold is met, creates review notification
- Saves review information to `human_review_info.json`
- Provides instructions for human reviewer

## Output Structure

```
iterative_output/
├── iteration_1_executive_Executive_Overview.pptx
├── iteration_1_technical_Technical_Deep_Dive.pptx
├── iteration_1_results_Results_&_Impact.pptx
├── iteration_2_executive_Executive_Overview.pptx
├── ...
├── iteration_results_20231208_120000.json
└── human_review_info.json
```

## Result JSON Structure

```json
{
  "success": true,
  "best_score": 87.5,
  "threshold": 75.0,
  "iterations_completed": 2,
  "best_presentation": {
    "pptx_path": "iterative_output/iteration_2_executive_Executive_Overview.pptx",
    "slides_data": {...},
    "evaluation": {
      "overall_score": 87.5,
      "scores": {...},
      "suggestions": {...}
    },
    "iteration": 2
  },
  "all_iterations": [...],
  "ready_for_human_review": true
}
```

## VLM Backends

### Auto (Default)
Automatically detects available backend:
1. Gemini (if API key available)
2. Local models (if transformers installed)
3. Ollama (if running locally)
4. Text-based (fallback)

### Gemini API
```bash
export GEMINI_API_KEY=your_key
python iterative_powerpoint_generator.py data.json --vlm-backend gemini
```

### Ollama
```bash
# Start Ollama and pull model
ollama pull llava

# Run generator
python iterative_powerpoint_generator.py data.json --vlm-backend ollama --model llava
```

### Local Models
```bash
python iterative_powerpoint_generator.py data.json --vlm-backend local
```

## Evaluation Criteria

Presentations are scored on:

1. **Clarity** (0-100): Content clarity and understandability
2. **Accuracy** (0-100): Alignment with source content
3. **Visual Balance** (0-100): Content distribution and layout
4. **Audience Fit** (0-100): Appropriateness for target audience

VLM also provides:
- Visual design scores
- Content quality scores
- Layout balance scores
- Readability scores
- Professional appearance scores

## Suggestions Format

The system provides structured suggestions:

```json
{
  "from_evaluator": {
    "recommendations": [...],
    "weaknesses": [...],
    "feedback": {...}
  },
  "from_vlm": {
    "suggestions": {
      "visual": [...],
      "content": [...],
      "layout": [...],
      "general": [...]
    },
    "priority_improvements": [...]
  },
  "priority_actions": [...]
}
```

## Human Review Process

When a presentation meets the threshold:

1. System creates `human_review_info.json` with:
   - Presentation path
   - Score and evaluation
   - Suggestions
   - Review instructions

2. Human reviewer:
   - Opens the presentation
   - Reviews content and design
   - Provides feedback
   - Approves or requests revisions

3. If revisions needed:
   - Adjust threshold or regenerate
   - Or manually edit presentation

## Example Workflow

```python
from iterative_powerpoint_generator import IterativePowerPointGenerator

# Initialize
generator = IterativePowerPointGenerator(
    json_input_path="retrieval_output/data.json",
    output_dir="output",
    score_threshold=80.0,
    max_iterations=5,
    vlm_backend="auto"
)

# Run iterations
results = generator.iterate_until_threshold()

# Check if ready for review
if results['ready_for_human_review']:
    review_info = generator.notify_human_review(results)
    print(f"Ready for review: {review_info['presentation_path']}")
```

## Troubleshooting

### No presentations generated
- Check that JSON input file exists and is valid
- Verify OpenAI API key is set (for slide generation)
- Check API rate limits

### VLM evaluation fails
- Try different VLM backend (`--vlm-backend text` for fallback)
- Check API keys if using Gemini
- Ensure Ollama is running if using Ollama backend

### Low scores
- Lower threshold with `--threshold 70`
- Increase max iterations with `--max-iterations 10`
- Review suggestions in result JSON

## Integration

The system integrates with:
- `utils/slide_generator.py` - Slide generation
- `utils/presentation_builder.py` - PPTX creation
- `utils/vlm_analyzer.py` - VLM evaluation
- `utils/evaluator.py` - Structured scoring

## License

Part of the CS 733 Project implementation.

