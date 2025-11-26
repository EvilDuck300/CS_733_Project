# ppt4web Dataset - Purpose and Usage

## Overview

The `ppt4web_01.jsonl` file contains **3,647 real presentation examples** scraped from ppt4web.ru. Each line is a JSON object containing:

- **url**: Original presentation URL
- **title**: Presentation title
- **text**: Extracted text content from all slides
- **download_url**: URL to download the original PPT file
- **filepath**: Local file path reference

## Purpose in the Presentation Generator System

This dataset serves multiple important roles in your system:

### 1. **Slide Generation Stage** (ChatGPT 4o)
   - **Few-shot Learning**: Provide examples to ChatGPT to help it understand:
     - Presentation structure and formatting
     - How to organize content into slides
     - Appropriate slide length and detail level
     - Audience-appropriate language and style
   
   - **Format Reference**: Show the AI what good presentations look like
   - **Style Guidance**: Help match the style to the selected audience type

### 2. **Evaluation Stage**
   - **Quality Benchmark**: Compare generated slides against real presentations
   - **Structure Validation**: Ensure generated slides follow proper presentation structure
   - **Content Quality**: Assess if content matches the quality of real presentations

### 3. **Retrieval Stage** (Optional Enhancement)
   - **Semantic Similarity**: Find similar presentations to guide content selection
   - **Topic Matching**: Identify relevant examples based on user description

## How It Works

### Integration Flow

```
User Input → Retrieval → Slide Generation (with dataset examples) → Evaluation
```

1. **User submits form** with PDF, audience type, and description
2. **Retrieval system** extracts relevant content from PDF
3. **Slide Generation** uses dataset to:
   - Find similar presentation examples
   - Generate few-shot prompts for ChatGPT
   - Guide the AI on format and style
4. **Evaluation** compares output against dataset examples

### Example Usage in Slide Generation

When generating slides, the system can:

```python
from utils.dataset_loader import get_dataset

dataset = get_dataset()

# Get relevant examples based on user input
examples = dataset.get_few_shot_examples(
    description="Create slides about computer hardware",
    audience_type="students",
    num_examples=3
)

# Use in ChatGPT prompt
prompt = f"""
Generate presentation slides based on the following content:
{retrieved_content}

Target audience: students
Description: Create slides about computer hardware

Here are example presentations to guide the format and style:
{examples}

Create slides following a similar structure and style.
"""
```

## Dataset Statistics

- **Total Presentations**: 3,647
- **Format**: JSONL (one JSON object per line)
- **Content**: Extracted text from PowerPoint presentations
- **Topics**: Various educational and professional topics

## Files Created

1. **`utils/dataset_loader.py`**: 
   - `PresentationDataset` class for loading and querying the dataset
   - Methods to find examples by keywords, audience type, etc.
   - Few-shot example generation

2. **`example_dataset_usage.py`**: 
   - Demonstrates how to use the dataset
   - Shows integration examples

## Next Steps

To fully integrate the dataset:

1. **In Slide Generation Module**: 
   - Import `get_dataset()` from `utils.dataset_loader`
   - Use `get_few_shot_examples()` to enhance ChatGPT prompts
   - Pass examples as context to improve slide quality

2. **In Evaluation Module**:
   - Compare generated slides against dataset examples
   - Use for quality scoring and validation

3. **Optional Enhancements**:
   - Fine-tune models on this dataset
   - Create embeddings for semantic search
   - Build a recommendation system based on similar presentations

## Benefits

✅ **Better Slide Quality**: AI learns from real examples  
✅ **Consistent Formatting**: Follows proven presentation structures  
✅ **Audience-Appropriate**: Examples match target audience  
✅ **Evaluation Baseline**: Compare against real presentations  
✅ **Few-shot Learning**: Improves AI output without training  

The dataset is ready to use and will significantly improve the quality of generated presentations!

