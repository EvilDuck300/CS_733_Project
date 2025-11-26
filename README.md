# Presentation Generator - User Input Interface

This is the user input interface component of the Presentation Generator system. It allows users to upload a PDF textbook, select an audience type, and provide a description for generating presentation slides.

## Features

- **PDF Upload**: Drag-and-drop or click to upload PDF files (max 50MB)
- **Audience Selection**: Choose from various audience types (Students, Professionals, Academic, etc.)
- **Description Input**: Provide a detailed description of desired presentation content
- **Modern UI**: Clean, responsive design with gradient styling
- **Form Validation**: Client-side and server-side validation
- **File Management**: Secure file upload handling with unique file naming

## Project Structure

```
.
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── main.js       # Frontend JavaScript
├── utils/
│   ├── __init__.py       # Utils package init
│   ├── dataset_loader.py # Dataset loader for ppt4web dataset
│   └── retrieval_gnn.py  # GNN-based retrieval system
├── ppt4web_01.jsonl/     # Presentation dataset (reference data)
│   └── ppt4web_01.jsonl  # JSONL file with presentation examples
├── uploads/              # Directory for uploaded PDF files
├── retrieval_output/     # Directory for JSON retrieval outputs
├── example_dataset_usage.py # Example script for dataset usage
└── example_retrieval.py  # Example script for retrieval system
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

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

## Usage

1. **Upload PDF**: Click the upload area or drag and drop a PDF file
2. **Select Audience**: Choose the appropriate audience type from the dropdown
3. **Enter Description**: Provide a description of what you want in your presentation
4. **Submit**: Click "Generate Presentation" to submit the form

## API Endpoint

### POST `/api/submit`

Handles form submission with the following data:
- `pdfFile`: PDF file (multipart/form-data)
- `audienceType`: Selected audience type (string)
- `description`: User description (string, max 1000 characters)

**Response:**
```json
{
    "success": true,
    "message": "Form submitted successfully",
    "submission_id": "uuid-string"
}
```

## Retrieval GNN System

The system now includes a **GNN-based Retrieval system** that automatically processes uploaded PDFs:

### How It Works

1. **PDF Text Extraction**: Extracts all text from the uploaded PDF
2. **Document Chunking**: Breaks the document into chunks (nodes) - typically 500 words each
3. **Graph Construction**: Creates edges between related chunks based on:
   - **Semantic similarity** (if sentence-transformers is installed)
   - **Keyword overlap** (fallback method)
   - **Sequential relationships**
4. **Relevant Chunk Retrieval**: Identifies top-k most relevant chunks based on:
   - User's description
   - Target audience type
   - Semantic similarity scores
5. **JSON Output**: Saves results to `retrieval_output/` directory

### Output Structure

The retrieval system generates a JSON file with:
- **Metadata**: Processing information, timestamps, counts
- **Graph Structure**: All nodes (chunks) and edges (relationships)
- **Relevant Chunks**: Top-k chunks ranked by relevance to user's request

### Dependencies

**Required:**
```bash
pip install PyPDF2
# OR
pip install pdfplumber
```

**Optional (for better semantic similarity):**
```bash
pip install sentence-transformers numpy
```

Without sentence-transformers, the system uses keyword-based matching (still functional but less accurate).

### API Response

After form submission, the API now returns:
```json
{
    "success": true,
    "message": "Form submitted and processed successfully",
    "submission_id": "uuid-string",
    "status": "retrieval_completed",
    "json_output_path": "retrieval_output/uuid_retrieval_output.json",
    "relevant_chunks_count": 20,
    "total_chunks": 45
}
```

### Testing the Retrieval System

Run the example script:
```bash
python example_retrieval.py
```

This will process any PDF in the `uploads/` folder and show retrieval results.

## Next Steps

After retrieval, the JSON output is ready for:
- **Slide Generation**: Use relevant chunks to create slides with ChatGPT 4o
- **Evaluation**: Evaluate and refine the generated slides

## The ppt4web Dataset

The `ppt4web_01.jsonl` file contains a dataset of real presentation examples that can be used for:

1. **Few-shot Learning**: Provide examples to ChatGPT 4o during slide generation to improve output quality
2. **Format Reference**: Help the AI understand presentation structure and formatting
3. **Evaluation**: Compare generated slides against real presentation examples
4. **Audience-specific Examples**: Find relevant examples based on audience type

### Using the Dataset

The dataset loader utility (`utils/dataset_loader.py`) provides functions to:
- Load and parse the JSONL file
- Find presentations by keywords or audience type
- Generate few-shot examples for AI prompts
- Get presentation statistics

**Example usage:**
```python
from utils.dataset_loader import get_dataset

dataset = get_dataset()

# Get examples for slide generation
examples = dataset.get_few_shot_examples(
    description="Create slides about computer systems",
    audience_type="students",
    num_examples=3
)
```

Run `python example_dataset_usage.py` to see more examples.

## Notes

- Uploaded files are stored in the `uploads/` directory with unique filenames
- Retrieval outputs (JSON files) are saved in `retrieval_output/` directory
- File size limit: 50MB
- Description character limit: 1000 characters
- **Retrieval GNN system is now fully integrated** - processes PDFs automatically on form submission
- The ppt4web dataset can be used in the Slide Generation stage to improve output quality
- For best results, install `sentence-transformers` for semantic similarity matching

