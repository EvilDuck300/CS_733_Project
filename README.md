# Presentation Generator - AI-Powered Slide Creation System

A complete AI-powered system that transforms PDF textbooks into professional PowerPoint presentations using GNN-based retrieval, Gemini AI slide generation, and VLM analysis with local models.

## Recent Changes (2025-12-10)

- **Migrated from OpenAI to Google Gemini API** - Now uses `gemini-1.5-pro` model with free tier support
- **API Rate Limiting** - Implemented limits: 6 calls for slide generation, 6 calls for evaluation (total 12 per session)
- **Automatic Fallbacks** - System gracefully falls back to retrieval-based slides when API limits are reached
- **Rate Limiting Protection** - 5-second delays between requests, 20-second waits on rate limit errors
- Added VS Code launch configuration for easier debugging with venv
- Updated `requirements.txt` with Gemini API dependencies

## Features

- **PDF Upload**: Drag-and-drop or click to upload PDF files (max 50MB)
- **Intelligent Retrieval**: GNN-based system extracts relevant content chunks (works offline, no API keys)
- **AI Slide Generation**: Google Gemini API integration with `gemini-1.5-pro` model
- **Multi-Version Generation**: Generates 3 different versions for comparison
- **Automatic Evaluation**: Scores slides on clarity, accuracy, visual balance, and audience fit
- **API Rate Limiting**: Smart limits prevent quota exhaustion (6 generation + 6 evaluation calls)
- **VLM Analysis**: Vision Language Model analysis using local models (NO API KEYS REQUIRED!)
- **Improved Slide Generation**: VLM generates improved slide content from existing presentations
- **Critic in the Loop**: User reviews and selects the best version
- **Quality Iteration**: Automatically regenerates slides until quality threshold is met
- **Feedback Loops**: Content, style, and information correction mechanisms
- **PowerPoint Export**: Downloads final presentation as .pptx file
- **Modern UI**: Clean, responsive design with intuitive workflow

## System Architecture

### Implementation Architecture

- **Flask-based REST API**: Exposes REST endpoints for each workflow stage
- **Modular design**: Retrieval, generation, and evaluation are separate, independently testable modules
- **Multi-stage pipeline**: Sequential processing from user input through retrieval, generation, evaluation, and final output
- **Feedback loops**: Multiple correction points allow refinement at different stages
- **Critic-in-the-loop interface**: Review interface for comparing versions, providing feedback, and selecting the best output
- **Independent development**: Each component can be developed, tested, and improved separately without affecting others
- **Quality assurance**: Built-in evaluation stage assesses slide quality before final delivery
- **User oversight**: Reviewers can inspect, compare, and provide feedback on multiple slide versions

### Workflow Pipeline

```
User Input → Retrieval (GNN) → Slide Generation (Gemini API) → Evaluation (Gemini API) → 
VLM Analysis (Local Models) → Critic in the Loop → Final Output (PowerPoint)
```

### Workflow Stages

1. **Input Stage**: User uploads PDF, selects audience, provides description
2. **Retrieval Stage**: GNN decomposes document into relevant chunks (always runs, no API keys)
3. **Slide Generation Stage**: Gemini API creates slides using `gemini-1.5-pro` model (optional, requires API key)
4. **Evaluation Stage**: Gemini API grades slides on 4 criteria (optional, requires API key)
5. **VLM Analysis Stage**: Analyze and improve presentations using local vision models (NO API KEYS!)
6. **Critic in the Loop Stage**: User reviews and selects best version
7. **Final Output Stage**: PowerPoint presentation delivered

### Feedback Loops

- **Loop 1**: Content Correction → Re-runs retrieval with updated description
- **Loop 2**: Information Correction → Re-generates slides with corrected information
- **Loop 3**: Style Correction → Re-generates slides with style adjustments
- **Loop 4**: Quality Iteration → Automatically regenerates until scores meet threshold

## Project Structure

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
│   ├──               
│   ├── retrieval_gnn.py           # GNN-based retrieval system
│   ├── slide_generator.py          # Gemini API slide generation
│   ├── evaluator.py                # Gemini API evaluation system
│   ├──           
│   └──           
├── ppt4web_01.jsonl/               # Presentation dataset (reference data)
│   └── ppt4web_01.jsonl            # JSONL file with presentation examples
├── uploads/                        # Directory for uploaded PDF files
├── retrieval_output/               # Directory for JSON retrieval outputs
├── slides_output/                  # Directory for generated slide versions
├── presentations/                  # Directory for final PowerPoint files
├── run_vlm_analysis.py            # Script to run VLM analysis (no API keys)
├── create_improved_presentation.py # Create PowerPoint from improved slides
├── example_dataset_usage.py        # Example script for dataset usage
└── VLM_ANALYSIS_GUIDE.md          # Complete guide for VLM analysis
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Required Dependencies:**
- Flask (web framework)
- pdfplumber (PDF processing)
- python-pptx (PowerPoint generation)
- google-genai (Gemini API integration)
- sentence-transformers, numpy (semantic similarity)
- scikit-learn (evaluation support)

**Optional (for VLM Analysis - NO API KEYS REQUIRED!):**
```bash
# For local VLM models
pip install transformers torch Pillow

# For Ollama (alternative local models)
# Install Ollama from https://ollama.ai/
# Then: ollama pull llava
```

### 2. Set Up Gemini API Key

#### Get Your API Key
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

#### Set Environment Variable

**On Windows (PowerShell):**
```powershell
# Set for current session only
$env:GEOGRAPHY_KEY = "your-api-key-here"

# Or set permanently in PowerShell profile:
Add-Content -Path $PROFILE -Value '$env:GEOGRAPHY_KEY = "your-api-key-here"'
```

**On Linux/Mac:**
```bash
export GEOGRAPHY_KEY="your-api-key-here"
```

**Or create a `.env` file in your project root:**
```
GEOGRAPHY_KEY=your-api-key-here
```

The application uses `python-dotenv` to automatically load `.env` files.

### 3. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 4. Access the Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

##  Usage Guide

### Basic Workflow

1. **Upload PDF**: Click the upload area or drag and drop a PDF file
2. **Select Audience**: Choose the appropriate audience type (Students, Professionals, Academic, etc.)
3. **Enter Description**: Provide a description of what you want in your presentation
4. **Submit**: Click "Generate Presentation" to start processing
5. **Retrieval Output**: System generates JSON retrieval output file (saved in `retrieval_output/` directory)
6. **Slide Generation**: If Gemini API key is set, slides are generated automatically (up to 6 API calls)
7. **Evaluation**: System evaluates all versions (up to 6 API calls)
8. **Review**: User reviews and selects best version
9. **Download**: Download the generated PowerPoint

**Note:** The retrieval system works without API keys. VLM analysis uses local models (free, no API keys required).

### Using Feedback Loops

The system supports multiple feedback mechanisms:

- **Content Issue**: Click "Report Content Issue" → Enter feedback → System re-runs retrieval with updated focus
- **Style Issue**: Click "Report Style Issue" → Enter feedback → System re-generates slides with style adjustments
- **Information Error**: Click "Report Information Error" → System re-generates with corrected information
- **Quality Iteration**: Click "Regenerate for Better Quality" → System generates improved versions until threshold met

##  System Components

### 1. Retrieval GNN System

**File:** `utils/retrieval_gnn.py`

The GNN-based retrieval system processes PDFs and extracts relevant content:

- **PDF Text Extraction**: Extracts all text from uploaded PDF using `pdfplumber`
- **Document Chunking**: Breaks document into chunks (nodes) - typically 500 words each with 3-word overlap
- **Graph Construction**: Creates edges between related chunks based on:
  - Semantic similarity using `all-MiniLM-L6-v2` embeddings (if sentence-transformers installed)
  - Keyword overlap (fallback method)
  - Sequential relationships
- **Relevant Chunk Retrieval**: Identifies top-k most relevant chunks (default: 20) based on user description and audience type
- **JSON Output**: Saves results to `retrieval_output/` directory
- **No API Keys Required**: Works completely offline

### 2. Slide Generation System

**File:** `utils/slide_generator.py`

Intelligent slide generation using Google Gemini API:

- **Model**: `gemini-1.5-pro` (free tier available)
- **API Call Limit**: Maximum 6 calls per session (with automatic fallback)
- **Features**:
  - Generates professional, well-structured slides
  - Uses few-shot learning from ppt4web dataset (3,647 presentations)
  - Adapts language and complexity to audience type
  - Theme support (executive, technical, results)
  - Creates 3 different versions for user selection
  - JSON schema validation for structured output
- **Configuration**: Temperature 0.7, max tokens 4000
- **Rate Limiting**: 5-second delay between requests, 20-second wait on rate limit errors
- **Fallback**: Creates basic slides from retrieval data if API limit reached or unavailable

### 3. Evaluation System

**File:** `utils/evaluator.py`

Comprehensive evaluation using Google Gemini API:

- **Model**: `gemini-1.5-pro` (free tier available)
- **API Call Limit**: Maximum 6 calls per session (with default evaluation fallback)
- **Evaluation Criteria** (0-100 scale):
  - **Clarity**: Language clarity, structure, organization
  - **Accuracy**: Factual correctness, source alignment
  - **Visual Balance**: Content distribution, layout quality
  - **Audience Fit**: Language appropriateness, complexity level
- **Output**: Detailed feedback, strengths, weaknesses, and recommendations
- **Configuration**: Temperature 0.3, max tokens 2000
- **Fallback**: Returns default evaluation scores if API limit reached or unavailable

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

##  API Endpoints

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
    "download_url": "/api/download-presentation/uuid-string"
}
```

### GET `/api/download-presentation/<filename>`

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

1. **Few-shot Learning**: Provides examples to Gemini API during slide generation
2. **Format Reference**: Helps AI understand presentation structure
3. **Evaluation Benchmark**: Compares generated slides against real presentations
4. **Audience-specific Examples**: Finds relevant examples based on audience type

The dataset is automatically integrated into the slide generation process.

## ⚙️ Configuration

### Environment Variables

- `GEOGRAPHY_KEY` (Required for slide generation/evaluation): Google Gemini API key
  - Get your key from [Google AI Studio](https://aistudio.google.com/apikey)
  - Set as environment variable or in `.env` file

### Configuration Constants (in `app.py`)

- `EVALUATION_THRESHOLD = 75.0`: Minimum score for acceptance
- `MAX_ITERATIONS = 3`: Maximum quality iteration attempts
- `MAX_FILE_SIZE = 50MB`: Maximum PDF file size
- `ALLOWED_EXTENSIONS = {'pdf'}`: Allowed file types

### API Rate Limits

- **Slide Generation**: Maximum 6 API calls per session
- **Evaluation**: Maximum 6 API calls per session
- **Total**: 12 API calls maximum per session
- **Rate Limiting**: 5-second delay between requests, 20-second wait on 429 errors
- **Automatic Fallback**: System uses fallback mechanisms when limits are reached

##  Notes

- **✅ Retrieval System**: Works independently (no API keys required)
- **✅ VLM Analysis**: Uses local models (BLIP-2, LLaVA, Ollama) - completely FREE!
- **✅ Slide Generation**: Optional - requires Gemini API key (free tier available)
- **✅ Evaluation**: Optional - requires Gemini API key (free tier available)
- **✅ API Rate Limiting**: Smart limits prevent quota exhaustion with automatic fallbacks
- **✅ Error Handling**: All stages have proper error handling and fallbacks
- **✅ File Storage**: 
  - Uploaded PDFs: `uploads/`
  - Retrieval outputs: `retrieval_output/`
  - Generated slides: `slides_output/`
  - Final presentations: `presentations/`
  - VLM analysis: `slides_output/*_vlm_analysis.json` and `*_improved_slides.json`

##  Testing

### Test Retrieval System

```bash
python example_retrieval.py
```



### Test VLM Analysis

```bash
# Analyze a presentation with local models (no API keys!)
python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx

# Create improved presentation from VLM analysis
python create_improved_presentation.py submission_id_improved_slides.json
```

## Documentation

- **`PIPELINE.md`**: Complete pipeline architecture and data flow
- **`IMPLEMENTATION_COMPLETE.md`**: Complete implementation details
- **`IMPLEMENTATION_STATUS.md`**: Status tracking document
- **`RETRIEVAL_GNN_INFO.md`**: Retrieval system documentation
- **`DATASET_INFO.md`**: Dataset usage guide
- **`VLM_ANALYSIS_GUIDE.md`**: Complete guide for VLM analysis (local models, no API keys)
- **`GEMINI_SETUP.md`**: Gemini API setup and configuration guide
- **`GEMINI_QUICKSTART.md`**: Quick start guide for Gemini integration

##  Troubleshooting

### Gemini API Errors

- **API key not found**: Ensure `GEOGRAPHY_KEY` environment variable is set
- **Rate limit errors**: System automatically waits and retries, or uses fallback
- **Model not found**: Ensure you're using `gemini-1.5-pro` (free tier model)
- **Quota exceeded**: Check usage at [Google AI Studio Usage](https://ai.dev/usage?tab=rate-limit)
- **429 errors**: System automatically waits 20 seconds and uses fallback if limit reached

### PDF Processing Errors

- Ensure PDF is not corrupted
- Check file size is under 50MB
- Try with a different PDF file

### Slide Generation Fails

- **API limit reached**: System automatically uses fallback slides from retrieval data
- **No API key**: Set `GEOGRAPHY_KEY` environment variable
- **Check API key**: Verify key is valid and has quota remaining
- **Check error logs**: Review console output for detailed error messages

### VLM Analysis Issues

- **Local models not loading**: Install dependencies: `pip install transformers torch Pillow`
- **Ollama not working**: Install Ollama from https://ollama.ai/ and run `ollama pull llava`
- **No improved slides generated**: Check that `generate_improved=True` in the request
- See `VLM_ANALYSIS_GUIDE.md` for detailed troubleshooting

##  Project Status

**All features from the flowchart are fully implemented and working!**

- ✅ Input Stage
- ✅ Retrieval Stage (GNN) - Works offline, no API keys
- ✅ Slide Generation (Gemini API) - Free tier available
- ✅ Evaluation Stage (Gemini API) - Free tier available
- ✅ API Rate Limiting - Smart limits with fallbacks
- ✅ VLM Analysis (Local models - NO API KEYS!)
- ✅ Improved Slide Generation (VLM-based)
- ✅ Critic in the Loop
- ✅ Final Output
- ✅ All 4 Feedback Loops

**Overall Project Completion: 100%**

**Recent Updates:**
- ✅ Migrated from OpenAI to Google Gemini API
- ✅ Implemented API rate limiting (6 generation + 6 evaluation calls)
- ✅ Added automatic fallback mechanisms
- ✅ Rate limiting protection with delays
- ✅ VLM Analysis with local models (no API keys required)
- ✅ Improved slide content generation
- ✅ Multiple VLM backends (local, Ollama, text-based)
- ✅ Complete offline functionality for retrieval and VLM analysis

## License

This project is part of a CS 733 course project.

##  Credits

- **Retrieval System**: GNN-based document processing
- **Slide Generation**: Google Gemini API (`gemini-1.5-pro` model)
- **Evaluation**: Google Gemini API (`gemini-1.5-pro` model)
- **VLM Analysis**: Local models (BLIP-2, LLaVA, Ollama) - no API keys required
- **Dataset**: ppt4web presentation examples (3,647 presentations)

---

For detailed implementation information, see `IMPLEMENTATION_COMPLETE.md` and `GEMINI_SETUP.md`.
