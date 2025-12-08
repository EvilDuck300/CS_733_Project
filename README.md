# Presentation Generator - AI-Powered Slide Creation System

A complete AI-powered system that transforms PDF textbooks into professional PowerPoint presentations using ChatGPT 4o, GNN-based retrieval, and intelligent evaluation with human-in-the-loop feedback.

## 🎯 Features

- **PDF Upload**: Drag-and-drop or click to upload PDF files (max 50MB)
- **Intelligent Retrieval**: GNN-based system extracts relevant content chunks
- **AI Slide Generation**: ChatGPT 4o creates professional, audience-appropriate slides
- **Multi-Version Generation**: Generates 3 different versions for comparison
- **Automatic Evaluation**: Scores slides on clarity, accuracy, visual balance, and audience fit
- **Critic in the Loop**: User reviews and selects the best version
- **Quality Iteration**: Automatically regenerates slides until quality threshold is met
- **Feedback Loops**: Content, style, and information correction mechanisms
- **PowerPoint Export**: Downloads final presentation as .pptx file
- **Modern UI**: Clean, responsive design with intuitive workflow

## 🏗️ System Architecture

The system implements a complete workflow with multiple stages and feedback loops:

```
User Input → Retrieval (GNN) → Slide Generation (ChatGPT 4o) → Evaluation → 
Critic in the Loop → Final Output (PowerPoint)
```

### Workflow Stages

1. **Input Stage**: User uploads PDF, selects audience, provides description
2. **Retrieval Stage**: GNN decomposes document into relevant chunks
3. **Slide Generation Stage**: ChatGPT 4o creates slides from retrieved content
4. **Evaluation Stage**: System grades slides on 4 criteria
5. **Critic in the Loop Stage**: User reviews and selects best version
6. **Final Output Stage**: PowerPoint presentation delivered

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
│   ├── slide_generator.py           # ChatGPT 4o slide generation
│   ├── evaluator.py                # Evaluation system
│   ├── presentation_builder.py     # PowerPoint builder
│   └── dataset_loader.py           # Dataset loader for ppt4web
├── ppt4web_01.jsonl/               # Presentation dataset (reference data)
│   └── ppt4web_01.jsonl            # JSONL file with presentation examples
├── uploads/                         # Directory for uploaded PDF files
├── retrieval_output/               # Directory for JSON retrieval outputs
├── slides_output/                   # Directory for generated slide versions
├── presentations/                   # Directory for final PowerPoint files
├── example_dataset_usage.py        # Example script for dataset usage
└── example_retrieval.py            # Example script for retrieval system
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
- openai (ChatGPT 4o integration)
- scikit-learn, numpy (evaluation support)

**Optional (for better semantic similarity):**
```bash
pip install sentence-transformers numpy
```

### 2. Set OpenAI API Key

The system requires an OpenAI API key for ChatGPT 4o integration:

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Windows:**
```cmd
set OPENAI_API_KEY=your-api-key-here
```

**Or create a `.env` file:**
```
OPENAI_API_KEY=your-api-key-here
```

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

## 📖 Usage Guide

### Basic Workflow

1. **Upload PDF**: Click the upload area or drag and drop a PDF file
2. **Select Audience**: Choose the appropriate audience type (Students, Professionals, Academic, etc.)
3. **Enter Description**: Provide a description of what you want in your presentation
4. **Submit**: Click "Generate Presentation" to start processing
5. **Review**: System automatically redirects to review page showing 3 versions
6. **Select**: Click on your preferred version to select it
7. **Download**: PowerPoint presentation automatically downloads

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

### 2. Slide Generation (ChatGPT 4o)

**File:** `utils/slide_generator.py`

Intelligent slide generation using OpenAI's ChatGPT 4o:

- Generates professional, well-structured slides
- Uses few-shot learning from ppt4web dataset
- Adapts language and complexity to audience type
- Creates 3 different versions for user selection
- Outputs structured JSON with title slide and content slides

### 3. Evaluation System

**File:** `utils/evaluator.py`

Comprehensive evaluation on 4 criteria:

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

Converts ChatGPT-generated slide data to PowerPoint:

- Creates professional .pptx files
- Proper slide layouts and formatting
- Title slide and content slides
- Formatted text and bullet points

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

- `OPENAI_API_KEY` (Required): OpenAI API key for ChatGPT 4o

### Configuration Constants (in `app.py`)

- `EVALUATION_THRESHOLD = 75.0`: Minimum score for acceptance
- `MAX_ITERATIONS = 3`: Maximum quality iteration attempts
- `MAX_FILE_SIZE = 50MB`: Maximum PDF file size

## 📝 Notes

- **OpenAI API Key Required**: System needs valid OpenAI API key to function
- **Dataset Integration**: ppt4web dataset automatically used for few-shot learning
- **Quality Iteration**: System automatically tries to improve scores if below threshold
- **Error Handling**: All stages have proper error handling and fallbacks
- **File Storage**: 
  - Uploaded PDFs: `uploads/`
  - Retrieval outputs: `retrieval_output/`
  - Generated slides: `slides_output/`
  - Final presentations: `presentations/`

## 🧪 Testing

### Test Retrieval System

```bash
python example_retrieval.py
```

### Test Dataset Usage

```bash
python example_dataset_usage.py
```

## 📚 Documentation

- **`IMPLEMENTATION_COMPLETE.md`**: Complete implementation details
- **`IMPLEMENTATION_STATUS.md`**: Status tracking document
- **`RETRIEVAL_GNN_INFO.md`**: Retrieval system documentation
- **`DATASET_INFO.md`**: Dataset usage guide

## 🐛 Troubleshooting

### OpenAI API Errors

- Ensure `OPENAI_API_KEY` is set correctly
- Check API key has sufficient credits
- Verify internet connection

### PDF Processing Errors

- Ensure PDF is not corrupted
- Check file size is under 50MB
- Try with a different PDF file

### Slide Generation Fails

- Check OpenAI API key is valid
- Verify retrieval output exists
- Check error logs in console

## 🎉 Project Status

**All features from the flowchart are fully implemented and working!**

- ✅ Input Stage
- ✅ Retrieval Stage (GNN)
- ✅ Slide Generation (ChatGPT 4o)
- ✅ Evaluation Stage
- ✅ Critic in the Loop
- ✅ Final Output
- ✅ All 4 Feedback Loops

**Overall Project Completion: 100%**

## 📄 License

This project is part of a CS 733 course project.

## 👥 Credits

- **Retrieval System**: GNN-based document processing
- **Slide Generation**: OpenAI ChatGPT 4o
- **Evaluation**: AI-powered scoring system
- **Dataset**: ppt4web presentation examples

---

For detailed implementation information, see `IMPLEMENTATION_COMPLETE.md`.
