# Retrieval GNN System - Implementation Guide

## Overview

The **GNN-based Retrieval System** is now fully implemented and integrated into the Presentation Generator. It processes uploaded PDFs, decomposes them into relevant chunks (nodes), creates a graph structure, and returns a JSON file with the most relevant content for slide generation.

## How It Works

### Process Flow

```
User Uploads PDF → Text Extraction → Document Chunking → Graph Construction → Relevant Chunk Retrieval → JSON Output
```

### Step-by-Step Process

1. **PDF Text Extraction**
   - Extracts all text content from the uploaded PDF
   - Supports PyPDF2 and pdfplumber libraries
   - Handles multi-page documents

2. **Document Chunking (Nodes)**
   - Breaks document into chunks of ~500 words each
   - Each chunk becomes a **node** in the graph
   - Overlaps chunks by 50 words to maintain context
   - Preserves sentence boundaries

3. **Graph Edge Creation**
   - Creates **edges** between related chunks
   - Two methods available:
     - **Semantic Similarity** (if sentence-transformers installed):
       - Uses embeddings to find semantically similar chunks
       - Calculates cosine similarity between chunk embeddings
       - Creates edges for chunks with similarity > threshold (0.5)
     - **Keyword Overlap** (fallback):
       - Finds chunks with shared keywords
       - Creates sequential edges between adjacent chunks
       - Creates edges based on keyword overlap

4. **Relevant Chunk Retrieval**
   - Ranks all chunks based on relevance to:
     - User's description
     - Target audience type
   - Returns top-k most relevant chunks (default: 20)
   - Each chunk includes a relevance score

5. **JSON Output Generation**
   - Saves complete graph structure and relevant chunks
   - Output saved to `retrieval_output/` directory
   - File format: `{submission_id}_retrieval_output.json`

## Output Structure

The JSON output contains:

```json
{
  "metadata": {
    "pdf_path": "path/to/file.pdf",
    "description": "User's description",
    "audience_type": "students",
    "total_chunks": 45,
    "relevant_chunks_count": 20,
    "total_edges": 120,
    "timestamp": "2025-11-23T...",
    "processing_method": "embedding" or "keyword"
  },
  "graph_structure": {
    "nodes": [
      {
        "id": 0,
        "text": "Chunk text content...",
        "word_count": 487,
        "char_count": 2543,
        "start_sentence": true,
        "end_sentence": false
      },
      ...
    ],
    "edges": [
      {
        "source": 0,
        "target": 1,
        "weight": 0.85,
        "type": "semantic_similarity"
      },
      ...
    ]
  },
  "relevant_chunks": [
    {
      "id": 5,
      "text": "Most relevant chunk...",
      "word_count": 512,
      "char_count": 2678,
      "relevance_score": 0.92
    },
    ...
  ]
}
```

## Integration

The retrieval system is **automatically triggered** when a user submits the form:

1. User uploads PDF and submits form
2. System saves PDF to `uploads/` directory
3. Retrieval system processes PDF automatically
4. JSON output saved to `retrieval_output/` directory
5. API response includes retrieval status and file path

## API Response

After processing, the API returns:

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

## Dependencies

### Required
```bash
pip install PyPDF2
# OR
pip install pdfplumber
```

### Optional (Recommended)
For better semantic similarity matching:
```bash
pip install sentence-transformers numpy
```

**Note**: The system works without sentence-transformers, but uses keyword-based matching which is less accurate.

## Configuration

You can customize the retrieval parameters in `app.py`:

```python
retrieval_output = retrieval_system.process_document(
    pdf_path=filepath,
    description=description,
    audience_type=audience_type,
    chunk_size=500,          # Words per chunk
    overlap=50,               # Word overlap between chunks
    similarity_threshold=0.5, # Minimum similarity for edges
    top_k=20                  # Number of relevant chunks to return
)
```

## Usage Examples

### Direct Usage

```python
from utils.retrieval_gnn import GNNRetrieval

# Initialize
retrieval = GNNRetrieval()

# Process document
output = retrieval.process_document(
    pdf_path='document.pdf',
    description='Create slides about computer systems',
    audience_type='students'
)

# Save to JSON
retrieval.save_to_json(output, 'output.json')
```

### Testing

Run the example script:
```bash
python example_retrieval.py
```

This processes any PDF in the `uploads/` folder and displays results.

## Next Steps

The JSON output from retrieval is ready for:

1. **Slide Generation Stage**:
   - Use `relevant_chunks` as input to ChatGPT 4o
   - Each chunk contains highly relevant content
   - Relevance scores help prioritize content

2. **Evaluation Stage**:
   - Compare generated slides against retrieved chunks
   - Validate that slides cover relevant content
   - Check for accuracy and completeness

## Benefits

✅ **Automatic Processing**: No manual intervention needed  
✅ **Intelligent Chunking**: Preserves context with overlap  
✅ **Semantic Understanding**: Finds related content even with different wording  
✅ **Relevance Ranking**: Prioritizes most important content  
✅ **Graph Structure**: Maintains relationships between chunks  
✅ **Flexible**: Works with or without advanced ML libraries  

## Troubleshooting

### "No PDF library found"
Install PyPDF2 or pdfplumber:
```bash
pip install PyPDF2
```

### "sentence-transformers not available"
System will use keyword matching instead. For better results:
```bash
pip install sentence-transformers numpy
```

### Large PDFs take too long
- Reduce `chunk_size` parameter
- Reduce `top_k` parameter
- Increase `similarity_threshold` to create fewer edges

## File Locations

- **Retrieval Module**: `utils/retrieval_gnn.py`
- **Output Directory**: `retrieval_output/`
- **Example Script**: `example_retrieval.py`

The retrieval system is now fully operational and ready to feed data to the Slide Generation stage!

