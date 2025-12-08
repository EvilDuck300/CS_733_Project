# Presentation Generator - AI-Powered Slide Creation System

A complete AI-powered system that transforms PDF textbooks into professional PowerPoint presentations using GNN-based retrieval, optional AI slide generation, and VLM analysis with local models. **NO API KEYS REQUIRED** - works completely offline for retrieval and VLM analysis!

## 🎯 Features

- **PDF Upload**: Drag-and-drop or click to upload PDF files (max 50MB)
- **Intelligent Retrieval**: GNN-based system extracts relevant content chunks
- **AI Slide Generation**: Optional ChatGPT 4o integration (or use Gemini website)
- **Multi-Version Generation**: Generates 3 different versions for comparison
- **Automatic Evaluation**: Scores slides on clarity, accuracy, visual balance, and audience fit
- **VLM Analysis**: Vision Language Model analysis using local models (NO API KEYS REQUIRED!)
- **Improved Slide Generation**: VLM generates improved slide content from existing presentations
- **Critic in the Loop**: User reviews and selects the best version
- **Quality Iteration**: Automatically regenerates slides until quality threshold is met
- **Feedback Loops**: Content, style, and information correction mechanisms
- **PowerPoint Export**: Downloads final presentation as .pptx file
- **Modern UI**: Clean, responsive design with intuitive workflow

## 🏗️ System Architecture

The system implements a complete workflow with multiple stages and feedback loops:

```
User Input → Retrieval (GNN) → Slide Generation (Optional) → Evaluation (Optional) → 
VLM Analysis (Local Models) → Critic in the Loop → Final Output (PowerPoint)
```

### Workflow Stages

1. **Input Stage**: User uploads PDF, selects audience, provides description
2. **Retrieval Stage**: GNN decomposes document into relevant chunks
3. **Slide Generation Stage**: Optional - ChatGPT 4o creates slides (or upload JSON to Gemini website)
4. **Evaluation Stage**: Optional - System grades slides on 4 criteria
5. **VLM Analysis Stage**: Analyze and improve presentations using local vision models (NO API KEYS!)
6. **Critic in the Loop Stage**: User reviews and selects best version
7. **Final Output Stage**: PowerPoint presentation delivered

### Feedback Loops

- **Loop 1**: Content Correction → Re-runs retrieval with updated description
- **Loop 2**: Information Correction → Re-generates slides with corrected information
- **Loop 3**: Style Correction → Re-generates slides with style adjustments
- **Loop 4**: Quality Iteration → Automatically regenerates until scores meet threshold

## 📁 Project Structure

```
.
├── app.py                          # Main Flask application with full workflow
├── requirements.txt                # Python dependencies
├── templates/
│   ├── index.html                  # Input form UI
│   └── review.html                 # Critic in the loop review UI
├── static/
│   ├── css/
│   │   └── style.css               # Styling
│   └── js/
│       └── main.js                 # Frontend JavaScript
├── utils/
│   ├── __init__.py                 # Utils package init
│   ├── retrieval_gnn.py           # GNN-based retrieval system
│   ├── slide_generator.py           # Optional ChatGPT 4o slide generation
│   ├── evaluator.py                # Optional evaluation system
│   ├── presentation_builder.py     # PowerPoint builder
│   ├── vlm_analyzer.py             # VLM analyzer (local models, no API keys)
│   └── dataset_loader.py           # Dataset loader for ppt4web
├── ppt4web_01.jsonl/               # Presentation dataset (reference data)
│   └── ppt4web_01.jsonl            # JSONL file with presentation examples
├── uploads/                         # Directory for uploaded PDF files
├── retrieval_output/               # Directory for JSON retrieval outputs
├── slides_output/                   # Directory for generated slide versions
├── presentations/                   # Directory for final PowerPoint files
├── run_vlm_analysis.py             # Script to run VLM analysis (no API keys)
├── create_improved_presentation.py # Create PowerPoint from improved slides
├── example_dataset_usage.py        # Example script for dataset usage
├── example_retrieval.py            # Example script for retrieval system
└── VLM_ANALYSIS_GUIDE.md          # Complete guide for VLM analysis
```

## 🚀 Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Required Dependencies:**
- Flask (web framework)
- PyPDF2 or pdfplumber (PDF processing)
- python-pptx (PowerPoint generation)
- scikit-learn, numpy (evaluation support)

**Optional (for better semantic similarity):**
```bash
pip install sentence-transformers numpy
```

**Optional (for VLM Analysis - NO API KEYS REQUIRED!):**
```bash
# For local VLM models
pip install transformers torch Pillow

# For Ollama (alternative local models)
# Install Ollama from https://ollama.ai/
# Then: ollama pull llava
```

**Note:** OpenAI or Gemini API keys are **NOT required**. The system:
- Generates JSON retrieval output that can be uploaded to Gemini website
- Supports VLM analysis using local models (completely free, no API keys)
- Works entirely offline for retrieval and VLM analysis

### 2. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 3. Access the Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

## 📖 Usage Guide

### Basic Workflow

1. **Upload PDF**: Click the upload area or drag and drop a PDF file
2. **Select Audience**: Choose the appropriate audience type (Students, Professionals, Academic, etc.)
3. **Enter Description**: Provide a description of what you want in your presentation
4. **Submit**: Click "Generate Presentation" to start processing
5. **Retrieval Output**: System generates JSON retrieval output file (saved in `retrieval_output/` directory)
6. **Optional - Slide Generation**: If OpenAI API key is set, slides are generated automatically
7. **VLM Analysis**: Analyze and improve presentations using local models:
   ```bash
   python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx
   ```
8. **Upload to Gemini**: Upload the JSON file to the Gemini website to generate PowerPoint presentation
9. **Download**: Download the generated PowerPoint

**Note:** The system works without API keys. VLM analysis uses local models (free, no API keys required).

### Using Feedback Loops

The system supports multiple feedback mechanisms:

- **Content Issue**: Click "Report Content Issue" → Enter feedback → System re-runs retrieval with updated focus
- **Style Issue**: Click "Report Style Issue" → Enter feedback → System re-generates slides with style adjustments
- **Information Error**: Click "Report Information Error" → System re-generates with corrected information
- **Quality Iteration**: Click "Regenerate for Better Quality" → System generates improved versions until threshold met

## 🔧 System Components

### 1. Retrieval GNN System

**File:** `utils/retrieval_gnn.py`

The GNN-based retrieval system processes PDFs and extracts relevant content:

- **PDF Text Extraction**: Extracts all text from uploaded PDF
- **Document Chunking**: Breaks document into chunks (nodes) - typically 500 words each
- **Graph Construction**: Creates edges between related chunks based on:
  - Semantic similarity (if sentence-transformers installed)
  - Keyword overlap (fallback method)
  - Sequential relationships
- **Relevant Chunk Retrieval**: Identifies top-k most relevant chunks based on user description and audience type
- **JSON Output**: Saves results to `retrieval_output/` directory

### 2. Slide Generation (Optional - ChatGPT 4o)

**File:** `utils/slide_generator.py`

**Note:** This module requires OpenAI API key. If not available, you can upload the JSON retrieval output to Gemini website instead.

Intelligent slide generation using OpenAI's ChatGPT 4o (if API key is provided):

- Generates professional, well-structured slides
- Uses few-shot learning from ppt4web dataset
- Adapts language and complexity to audience type
- Creates 3 different versions for user selection
- Outputs structured JSON with title slide and content slides

### 3. Evaluation System (Optional)

**File:** `utils/evaluator.py`

**Note:** This module requires OpenAI API key. If not available, evaluation will return default scores.

Comprehensive evaluation on 4 criteria (if API key is provided):

- **Clarity (0-100)**: Language clarity, structure, organization
- **Accuracy (0-100)**: Factual correctness, source alignment
- **Visual Balance (0-100)**: Content distribution, layout quality
- **Audience Fit (0-100)**: Language appropriateness, complexity level

Provides detailed feedback, strengths, weaknesses, and recommendations.

### 4. Critic in the Loop UI

**File:** `templates/review.html`

Interactive review interface:

- Displays all 3 slide versions side-by-side
- Shows evaluation scores for each version
- Visual score badges for each criterion
- Slide preview with formatted content
- User selection mechanism
- Feedback collection options

### 5. PowerPoint Builder

**File:** `utils/presentation_builder.py`

Converts slide data to PowerPoint:

- Creates professional .pptx files
- Proper slide layouts and formatting
- Title slide and content slides
- Formatted text and bullet points

### 6. VLM Analyzer (NO API KEYS REQUIRED!)

**File:** `utils/vlm_analyzer.py`

Vision Language Model analysis using local/open-source models:

- **Local Models**: BLIP-2, LLaVA via Hugging Face (FREE, runs locally)
- **Ollama**: Local models via Ollama (FREE, easy setup)
- **Text-based**: Fallback analysis (no dependencies)
- **Improved Content Generation**: Generates improved slide content (not just extraction)
- **No API Keys**: Works completely offline, no costs

**Usage:**
```bash
# Auto-detect best backend
python run_vlm_analysis.py presentations/file.pptx

# Use local model
python run_vlm_analysis.py presentations/file.pptx --backend local

# Use Ollama
python run_vlm_analysis.py presentations/file.pptx --backend ollama --model llava
```

See `VLM_ANALYSIS_GUIDE.md` for complete documentation.

## 🌐 API Endpoints

### POST `/api/submit`

Submit PDF, audience type, and description. Triggers full workflow.

**Request:**
- `pdfFile`: PDF file (multipart/form-data)
- `audienceType`: Selected audience type (string)
- `description`: User description (string, max 1000 characters)

**Response:**
```json
{
    "success": true,
    "message": "Form submitted and processed successfully",
    "submission_id": "uuid-string",
    "status": "evaluation_completed",
    "has_slides": true,
    "num_versions": 3,
    "has_evaluations": true
}
```

### GET `/review/<submission_id>`

Review page showing all slide versions with evaluations.

### GET `/api/slides/<submission_id>`

Get all slide versions and evaluations for a submission.

**Response:**
```json
{
    "success": true,
    "versions": [
        {
            "version_number": 1,
            "slides": {...},
            "evaluation": {
                "scores": {
                    "clarity": 85,
                    "accuracy": 90,
                    "visual_balance": 80,
                    "audience_fit": 88
                },
                "overall_score": 86
            }
        },
        ...
    ]
}
```

### POST `/api/select-slide`

User selects best slide version.

**Request:**
```json
{
    "submission_id": "uuid-string",
    "version_number": 1,
    "feedback": "Optional feedback"
}
```

**Response:**
```json
{
    "success": true,
    "download_url": "/api/download/uuid-string"
}
```

### GET `/api/download/<submission_id>`

Download the final PowerPoint presentation.

### POST `/api/feedback`

Submit feedback for content/style/information correction.

**Request:**
```json
{
    "submission_id": "uuid-string",
    "feedback_type": "content|style|information",
    "feedback": "Feedback text"
}
```

### POST `/api/regenerate`

Quality iteration - regenerate slides until scores meet threshold.

**Request:**
```json
{
    "submission_id": "uuid-string",
    "min_score": 75.0,
    "max_iterations": 3
}
```

### POST `/api/analyze-vlm/<submission_id>`

Analyze PowerPoint presentation using VLM (local models - NO API KEYS).

**Request:**
```json
{
    "backend": "auto|local|ollama|text",
    "model_name": "optional-model-name",
    "generate_improved": true,
    "analysis_type": "comprehensive"
}
```

**Response:**
```json
{
    "success": true,
    "backend": "local",
    "has_improvements": true,
    "improved_slides_file": "path/to/improved_slides.json",
    "analysis": {...}
}
```

### GET `/api/vlm-instructions/<submission_id>`

Get instructions for VLM analysis (local models or manual upload).

**Response:**
```json
{
    "success": true,
    "instructions": {
        "options": {
            "option_1_local": {...},
            "option_2_ollama": {...},
            "option_3_manual": {...}
        }
    }
}
```

## 📊 Evaluation Criteria

The system evaluates slides on four key dimensions:

1. **Clarity**: How clear and understandable is the content?
   - Language clarity and appropriateness
   - Concept explanation quality
   - Logical structure and flow
   - Bullet point organization

2. **Accuracy**: How accurate is the information?
   - Source content alignment
   - Factual correctness
   - Information representation
   - Error detection

3. **Visual Balance**: How well-balanced is the presentation?
   - Content distribution across slides
   - Appropriate text amount per slide
   - Structural quality
   - Layout appeal

4. **Audience Fit**: How well does it match the target audience?
   - Language appropriateness
   - Complexity level
   - Audience needs addressing
   - Style suitability

## 🎓 The ppt4web Dataset

The `ppt4web_01.jsonl` file contains **3,647 real presentation examples** used for:

1. **Few-shot Learning**: Provides examples to ChatGPT 4o during slide generation
2. **Format Reference**: Helps AI understand presentation structure
3. **Evaluation Benchmark**: Compares generated slides against real presentations
4. **Audience-specific Examples**: Finds relevant examples based on audience type

The dataset is automatically integrated into the slide generation process.

## ⚙️ Configuration

### Environment Variables

- `OPENAI_API_KEY` (Optional): OpenAI API key for ChatGPT 4o integration. If not provided, the system will generate JSON retrieval output that can be uploaded to Gemini website.

### Configuration Constants (in `app.py`)

- `EVALUATION_THRESHOLD = 75.0`: Minimum score for acceptance
- `MAX_ITERATIONS = 3`: Maximum quality iteration attempts
- `MAX_FILE_SIZE = 50MB`: Maximum PDF file size

## 📝 Notes

- **✅ NO API KEYS REQUIRED**: The system works completely without OpenAI or Gemini API keys:
  - Retrieval system: Works independently (no API keys)
  - VLM Analysis: Uses local models (BLIP-2, LLaVA, Ollama) - completely FREE!
  - Slide Generation: Optional - can use Gemini website manually
  - Evaluation: Optional - can use Gemini website manually

- **VLM Analysis Features**:
  - Uses local/open-source models (no API costs)
  - Generates improved slide content (not just extraction)
  - Works offline, privacy guaranteed
  - Multiple backend options (local, Ollama, text-based)

- **Gemini Website Integration**: Upload the JSON retrieval output file (from `retrieval_output/` directory) to Gemini website to generate PowerPoint presentations.

- **Optional OpenAI Integration**: If OpenAI API key is provided, the system can generate slides automatically.

- **Dataset Integration**: ppt4web dataset automatically used for few-shot learning (when OpenAI API is available)

- **Quality Iteration**: System automatically tries to improve scores if below threshold (when OpenAI API is available)

- **Error Handling**: All stages have proper error handling and fallbacks

- **File Storage**: 
  - Uploaded PDFs: `uploads/`
  - Retrieval outputs: `retrieval_output/` (main output for Gemini upload)
  - Generated slides: `slides_output/` (includes VLM improved slides)
  - Final presentations: `presentations/`
  - VLM analysis: `slides_output/*_vlm_analysis.json` and `*_improved_slides.json`

## 🧪 Testing

### Test Retrieval System

```bash
python example_retrieval.py
```

### Test Dataset Usage

```bash
python example_dataset_usage.py
```

### Test VLM Analysis

```bash
# Analyze a presentation with local models (no API keys!)
python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx

# Create improved presentation from VLM analysis
python create_improved_presentation.py submission_id_improved_slides.json
```

## 📚 Documentation

- **`PIPELINE.md`**: Complete pipeline architecture and data flow
- **`IMPLEMENTATION_COMPLETE.md`**: Complete implementation details
- **`IMPLEMENTATION_STATUS.md`**: Status tracking document
- **`RETRIEVAL_GNN_INFO.md`**: Retrieval system documentation
- **`DATASET_INFO.md`**: Dataset usage guide
- **`VLM_ANALYSIS_GUIDE.md`**: Complete guide for VLM analysis (local models, no API keys)

## 🐛 Troubleshooting

### OpenAI API Errors (Optional)

- If you see warnings about missing API keys, this is normal - the system will still generate JSON retrieval output
- To use OpenAI features, ensure `OPENAI_API_KEY` is set correctly
- Check API key has sufficient credits
- Verify internet connection

### PDF Processing Errors

- Ensure PDF is not corrupted
- Check file size is under 50MB
- Try with a different PDF file

### Slide Generation Fails

- **This is expected if no OpenAI API key is set** - the system will still generate JSON retrieval output
- Upload the JSON file from `retrieval_output/` directory to Gemini website instead
- Use VLM analysis to generate improved slides: `python run_vlm_analysis.py presentations/file.pptx`
- If using OpenAI, check API key is valid
- Verify retrieval output exists
- Check error logs in console

### VLM Analysis Issues

- **Local models not loading**: Install dependencies: `pip install transformers torch Pillow`
- **Ollama not working**: Install Ollama from https://ollama.ai/ and run `ollama pull llava`
- **No improved slides generated**: Check that `generate_improved=True` in the request
- See `VLM_ANALYSIS_GUIDE.md` for detailed troubleshooting

## 🎉 Project Status

**All features from the flowchart are fully implemented and working!**

- ✅ Input Stage
- ✅ Retrieval Stage (GNN)
- ✅ Slide Generation (Optional - ChatGPT 4o or Gemini website)
- ✅ Evaluation Stage (Optional)
- ✅ VLM Analysis (Local models - NO API KEYS!)
- ✅ Improved Slide Generation (VLM-based)
- ✅ Critic in the Loop
- ✅ Final Output
- ✅ All 4 Feedback Loops

**Overall Project Completion: 100%**

**New Features Added:**
- ✅ VLM Analysis with local models (no API keys required)
- ✅ Improved slide content generation
- ✅ Multiple VLM backends (local, Ollama, text-based)
- ✅ Complete offline functionality for retrieval and VLM analysis

## 📄 License

This project is part of a CS 733 course project.

## 👥 Credits

- **Retrieval System**: GNN-based document processing
- **Slide Generation**: Optional OpenAI ChatGPT 4o (or Gemini website)
- **VLM Analysis**: Local models (BLIP-2, LLaVA, Ollama) - no API keys required
- **Evaluation**: Optional AI-powered scoring system
- **Dataset**: ppt4web presentation examples

---

For detailed implementation information, see `IMPLEMENTATION_COMPLETE.md`.
