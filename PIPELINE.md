# Recent changes (2025-12-10)

- Pipeline and run instructions clarified: when running the full pipeline via `app.py` or example scripts, activate the project venv and run `pip install -r requirements.txt` inside it. A `.vscode/launch.json` file was added to run `app.py` in the integrated terminal for easier debugging.

# Presentation Generator Pipeline

## Overview

This document describes the complete pipeline for transforming PDF documents into professional PowerPoint presentations using GNN-based retrieval, optional AI slide generation, and VLM analysis.

## 🏗️ Complete Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PRESENTATION GENERATOR PIPELINE                 │
└─────────────────────────────────────────────────────────────────────────┘

INPUT STAGE
    │
    ├─► PDF Upload
    ├─► Audience Type Selection
    └─► Description Input
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: RETRIEVAL (GNN) - ALWAYS RUNS (NO API KEYS)                  │
└─────────────────────────────────────────────────────────────────────────┘
    │
    ├─► PDF Text Extraction
    ├─► Document Chunking (500 words, 3 overlap)
    ├─► Graph Construction
    │   ├─► Nodes: Document chunks
    │   ├─► Edges: Semantic similarity / Keyword overlap
    │   └─► Graph Structure Creation
    ├─► Relevance Scoring
    │   ├─► User description matching
    │   ├─► Audience type filtering
    │   └─► Top-K chunk selection (K=20)
    └─► JSON Output Generation
        │
        └─► retrieval_output/{submission_id}_retrieval_output.json
            │
            ├─► metadata (description, audience, timestamps)
            ├─► graph_structure (nodes, edges)
            └─► relevant_chunks (top-k with scores)
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: SLIDE GENERATION (OPTIONAL - Requires OpenAI API Key)        │
└─────────────────────────────────────────────────────────────────────────┘
    │
    ├─► Check for OpenAI API Key
    │   │
    │   ├─► [YES] → Generate Slides with ChatGPT 4o
    │   │   ├─► Load ppt4web dataset for few-shot learning
    │   │   ├─► Build prompt with relevant chunks
    │   │   ├─► Generate 3 versions of slides
    │   │   └─► Save to slides_output/
    │   │
    │   └─► [NO] → Skip to VLM Analysis or Manual Upload
    │       └─► User can upload JSON to Gemini website
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: EVALUATION (OPTIONAL - Requires OpenAI API Key)               │
└─────────────────────────────────────────────────────────────────────────┘
    │
    ├─► Check for OpenAI API Key
    │   │
    │   ├─► [YES] → Evaluate Each Slide Version
    │   │   ├─► Clarity Score (0-100)
    │   │   ├─► Accuracy Score (0-100)
    │   │   ├─► Visual Balance Score (0-100)
    │   │   ├─► Audience Fit Score (0-100)
    │   │   ├─► Overall Score Calculation
    │   │   └─► Quality Iteration (if scores < 75)
    │   │
    │   └─► [NO] → Skip evaluation
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: VLM ANALYSIS (NO API KEYS REQUIRED!)                         │
└─────────────────────────────────────────────────────────────────────────┘
    │
    ├─► PowerPoint Presentation Available?
    │   │
    │   ├─► [YES] → Run VLM Analysis
    │   │   ├─► Backend Selection (auto-detect)
    │   │   │   ├─► Local Models (BLIP-2, LLaVA)
    │   │   │   ├─► Ollama (if installed)
    │   │   │   └─► Text-based (fallback)
    │   │   │
    │   │   ├─► Extract Text from Slides
    │   │   ├─► Generate Improved Slide Content
    │   │   │   ├─► Analyze current slides
    │   │   │   ├─► Generate improved titles
    │   │   │   ├─► Generate improved bullet points
    │   │   │   └─► Maintain key information
    │   │   │
    │   │   └─► Save Results
    │   │       ├─► slides_output/{submission_id}_vlm_analysis.json
    │   │       └─► slides_output/{submission_id}_improved_slides.json
    │   │
    │   └─► [NO] → Provide Instructions
    │       └─► Manual upload to Gemini website
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: CRITIC IN THE LOOP (HUMAN REVIEW)                           │
└─────────────────────────────────────────────────────────────────────────┘
    │
    ├─► Display Slide Versions
    ├─► Show Evaluation Scores (if available)
    ├─► User Reviews and Selects Best Version
    └─► Collect User Feedback
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ STAGE 6: FINAL OUTPUT                                                  │
└─────────────────────────────────────────────────────────────────────────┘
    │
    ├─► Create PowerPoint from Selected Version
    │   ├─► Title Slide
    │   ├─► Content Slides
    │   └─► Formatting and Styling
    │
    └─► Save to presentations/{submission_id}_final_presentation.pptx
    │
    ▼
    OUTPUT: PowerPoint Presentation (.pptx)
```

## 🔄 Feedback Loops

The pipeline includes 4 feedback loops for iterative improvement:

### Feedback Loop 1: Content Correction
```
User Feedback (Content Issue)
    │
    ▼
Re-run Retrieval Stage
    ├─► Update description with feedback
    ├─► Re-process document
    └─► Generate new relevant chunks
    │
    ▼
Re-generate Slides (if API key available)
    │
    └─► Return to Stage 5 (Critic in the Loop)
```

### Feedback Loop 2: Information Correction
```
User Feedback (Information Error)
    │
    ▼
Re-generate Slides (if API key available)
    ├─► Use corrected information
    └─► Maintain same retrieval output
    │
    └─► Return to Stage 5 (Critic in the Loop)
```

### Feedback Loop 3: Style Correction
```
User Feedback (Style Issue)
    │
    ▼
Re-generate Slides (if API key available)
    ├─► Apply style adjustments
    └─► Maintain content accuracy
    │
    └─► Return to Stage 5 (Critic in the Loop)
```

### Feedback Loop 4: Quality Iteration
```
Evaluation Scores < Threshold (75)
    │
    ▼
Automatic Quality Iteration
    ├─► Generate new slide versions
    ├─► Evaluate each version
    ├─► Keep best version
    └─► Repeat until threshold met (max 3 iterations)
    │
    └─► Return to Stage 5 (Critic in the Loop)
```

## 📊 Data Flow

### Input Data
```
{
    "pdf_file": File object,
    "audience_type": "students|professionals|academic|business|beginners|advanced|general",
    "description": "User's description of desired presentation (max 1000 chars)"
}
```

### Stage 1 Output (Retrieval)
```json
{
    "metadata": {
        "description": "...",
        "audience_type": "...",
        "pdf_path": "...",
        "timestamp": "..."
    },
    "graph_structure": {
        "nodes": [...],
        "edges": [...]
    },
    "relevant_chunks": [
        {
            "chunk_id": "...",
            "text": "...",
            "relevance_score": 0.85,
            "page_number": 1
        }
    ]
}
```

### Stage 2 Output (Slides - Optional)
```json
{
    "title_slide": {
        "title": "...",
        "subtitle": "..."
    },
    "slides": [
        {
            "slide_number": 1,
            "title": "...",
            "content": ["bullet 1", "bullet 2", ...],
            "notes": "..."
        }
    ],
    "metadata": {
        "description": "...",
        "audience_type": "...",
        "num_slides": 3,
        "model_used": "gpt-4o"
    }
}
```

### Stage 3 Output (Evaluation - Optional)
```json
{
    "scores": {
        "clarity": 85,
        "accuracy": 90,
        "visual_balance": 80,
        "audience_fit": 88
    },
    "overall_score": 86,
    "feedback": {
        "clarity": "...",
        "accuracy": "...",
        "visual_balance": "...",
        "audience_fit": "..."
    },
    "strengths": [...],
    "weaknesses": [...],
    "recommendations": [...]
}
```

### Stage 4 Output (VLM Analysis)
```json
{
    "success": true,
    "backend": "local",
    "num_slides": 3,
    "original_slides": [...],
    "improved_slides": {
        "title_slide": {...},
        "slides": [
            {
                "slide_number": 1,
                "title": "Improved Title",
                "content": ["Improved bullet 1", ...],
                "notes": "Generated by VLM analysis"
            }
        ]
    },
    "has_improvements": true
}
```

### Final Output
```
PowerPoint Presentation (.pptx)
    ├─► Title Slide
    ├─► Content Slide 1
    ├─► Content Slide 2
    └─► Content Slide 3
```

## 🔀 Decision Points

### Decision Point 1: OpenAI API Key Available?
```
┌─────────────────────┐
│ OpenAI API Key?     │
└─────────────────────┘
         │
    ┌────┴────┐
    │          │
   YES        NO
    │          │
    ▼          ▼
Generate    Skip to
Slides      VLM or
            Manual
            Upload
```

### Decision Point 2: VLM Backend Selection
```
┌─────────────────────┐
│ VLM Backend?        │
└─────────────────────┘
         │
    ┌────┴────┐
    │          │
  AUTO      SPECIFIED
    │          │
    ▼          ▼
Detect      Use
Best        Specified
Available   Backend
```

### Decision Point 3: Quality Threshold Met?
```
┌─────────────────────┐
│ Score >= 75?        │
└─────────────────────┘
         │
    ┌────┴────┐
    │          │
   YES        NO
    │          │
    ▼          ▼
Proceed    Quality
to Review  Iteration
           (Loop 4)
```

## 🚀 Pipeline Execution Modes

### Mode 1: Full Pipeline (With OpenAI API Key)
```
Input → Retrieval → Slide Generation → Evaluation → 
VLM Analysis → Critic in Loop → Final Output
```

### Mode 2: No API Keys (Recommended)
```
Input → Retrieval → VLM Analysis → Critic in Loop → Final Output
         │
         └─► (Optional) Upload JSON to Gemini website
```

### Mode 3: Minimal (Retrieval Only)
```
Input → Retrieval → JSON Output
         │
         └─► User manually processes JSON
```

## 📝 Pipeline Stages Detail

### Stage 1: Retrieval (GNN)
- **Status**: Always runs
- **Dependencies**: PyPDF2, scikit-learn, numpy
- **Optional**: sentence-transformers (for better semantic similarity)
- **Output**: JSON file with relevant chunks
- **Time**: ~5-30 seconds (depends on PDF size)

### Stage 2: Slide Generation
- **Status**: Optional (requires OpenAI API key)
- **Dependencies**: openai package
- **Alternative**: Manual upload to Gemini website
- **Output**: JSON files with slide data
- **Time**: ~10-30 seconds per version

### Stage 3: Evaluation
- **Status**: Optional (requires OpenAI API key)
- **Dependencies**: openai package
- **Alternative**: Manual review
- **Output**: Evaluation scores and feedback
- **Time**: ~5-15 seconds per version

### Stage 4: VLM Analysis
- **Status**: Optional (but recommended)
- **Dependencies**: transformers, torch, Pillow (for local models)
- **Alternative**: Ollama or text-based
- **Output**: Improved slide content
- **Time**: ~10-60 seconds (depends on backend and slides)

### Stage 5: Critic in the Loop
- **Status**: Always runs (user interaction)
- **Dependencies**: Web UI
- **Output**: User selection and feedback
- **Time**: User-dependent

### Stage 6: Final Output
- **Status**: Always runs
- **Dependencies**: python-pptx
- **Output**: PowerPoint file
- **Time**: ~1-5 seconds

## 🔧 Pipeline Configuration

### Configuration Parameters
```python
# app.py
CHUNK_SIZE = 500              # Words per chunk
OVERLAP = 3                   # Overlap between chunks
SIMILARITY_THRESHOLD = 0.5    # Minimum similarity for edges
TOP_K = 20                    # Number of relevant chunks
EVALUATION_THRESHOLD = 75.0   # Minimum score for acceptance
MAX_ITERATIONS = 3            # Max quality iterations
MAX_FILE_SIZE = 50MB          # Maximum PDF size
```

### Backend Selection (VLM)
```python
# Auto-detection order
1. Local models (if transformers installed)
2. Ollama (if running)
3. Gemini API (if API key set)
4. Text-based (fallback)
```

## 📈 Pipeline Performance

### Typical Execution Times
- **Retrieval**: 5-30 seconds
- **Slide Generation** (if enabled): 10-30 seconds per version
- **Evaluation** (if enabled): 5-15 seconds per version
- **VLM Analysis**: 10-60 seconds
- **PowerPoint Creation**: 1-5 seconds

### Total Pipeline Time
- **With API keys**: ~60-120 seconds
- **Without API keys (VLM only)**: ~20-90 seconds
- **Retrieval only**: ~5-30 seconds

## 🎯 Pipeline Outputs

### File Structure
```
project/
├── uploads/
│   └── {submission_id}_{filename}.pdf
├── retrieval_output/
│   └── {submission_id}_retrieval_output.json
├── slides_output/
│   ├── {submission_id}_slides_v1.json
│   ├── {submission_id}_slides_v2.json
│   ├── {submission_id}_slides_v3.json
│   ├── {submission_id}_evaluations.json
│   ├── {submission_id}_vlm_analysis.json
│   └── {submission_id}_improved_slides.json
└── presentations/
    └── {submission_id}_final_presentation.pptx
```

## 🔍 Pipeline Monitoring

### Log Points
1. **Submission received**: User input logged
2. **Retrieval started**: GNN processing begins
3. **Retrieval completed**: JSON saved
4. **Slide generation started**: (if API key available)
5. **Evaluation started**: (if API key available)
6. **VLM analysis started**: Local model processing
7. **Final output created**: PowerPoint saved

### Error Handling
- Each stage has try-catch blocks
- Errors are logged but don't stop pipeline
- Fallback options available for each stage
- User receives error messages in response

## 🎓 Pipeline Best Practices

1. **Always run Retrieval**: This is the core stage and always works
2. **Use VLM Analysis**: Generates improved content without API keys
3. **Manual Upload Option**: If no API keys, use Gemini website
4. **Iterative Improvement**: Use feedback loops for better results
5. **Monitor Quality**: Check evaluation scores (if available)

---

For more details on specific stages, see:
- `RETRIEVAL_GNN_INFO.md` - Retrieval system details
- `VLM_ANALYSIS_GUIDE.md` - VLM analysis guide
- `IMPLEMENTATION_COMPLETE.md` - Full implementation details

