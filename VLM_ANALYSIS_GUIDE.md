# VLM (Vision Language Model) Analysis Guide

## Overview

After generating a PowerPoint presentation, you can analyze it using a Vision Language Model (VLM) like Gemini Vision to get visual feedback, content analysis, and quality assessment.

## 🎯 What is VLM Analysis?

VLM analysis uses AI vision models to:
- **Visual Design Analysis**: Evaluate layout, colors, fonts, and visual elements
- **Content Extraction**: Extract and summarize key information from slides
- **Readability Assessment**: Check if text is clear and well-organized
- **Quality Evaluation**: Rate professional appearance and provide improvement suggestions
- **Comprehensive Review**: Get detailed feedback on the entire presentation

## 🚀 How to Run VLM Analysis

### Option 1: Using Gemini Website (Recommended - No API Key Needed)

This is the easiest method and doesn't require any API keys:

1. **Generate your PowerPoint** using the system (or use an existing one)
2. **Go to Gemini Website**: https://gemini.google.com/
3. **Upload the PowerPoint file**:
   - Click on "Upload" or drag and drop your `.pptx` file
   - Wait for upload to complete
4. **Ask Gemini to analyze** using prompts like:
   - "Analyze this PowerPoint presentation and provide feedback on visual design, content organization, and readability."
   - "Review this presentation and suggest improvements for professional quality."
   - "Evaluate the slides for clarity, visual balance, and audience appropriateness."
   - "Extract key information from each slide and summarize the presentation."
5. **Get detailed analysis** from Gemini

### Option 2: Using the Script (With or Without API Key)

#### Without API Key (Gets Instructions)

```bash
python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx
```

This will provide step-by-step instructions for using Gemini website.

#### With Gemini API Key

1. **Get a Gemini API Key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key

2. **Set Environment Variable**:
   
   **Linux/Mac:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
   
   **Windows:**
   ```cmd
   set GEMINI_API_KEY=your-api-key-here
   ```

3. **Install Required Packages** (optional, for API usage):
   ```bash
   pip install google-generativeai Pillow
   ```

4. **Run the Analysis Script**:
   ```bash
   python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx
   ```

### Option 3: Using the Web API Endpoint

After generating a presentation, you can use the Flask API:

#### Get Instructions for Gemini Website:
```bash
curl http://localhost:5000/api/vlm-instructions/<submission_id>
```

#### Analyze with API (if API key is set):
```bash
curl -X POST http://localhost:5000/api/analyze-vlm/<submission_id> \
  -H "Content-Type: application/json" \
  -d '{"analysis_type": "comprehensive"}'
```

## 📋 Example Workflow

### Complete Workflow with VLM Analysis

1. **Upload PDF and Generate Presentation**:
   ```bash
   # Use the web interface or API
   # This generates: presentations/submission_id_final_presentation.pptx
   ```

2. **Run VLM Analysis**:
   ```bash
   python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx
   ```

3. **Follow Instructions**:
   - If no API key: Upload to Gemini website manually
   - If API key set: Analysis runs automatically

4. **Review Analysis Results**:
   - Results saved to: `slides_output/submission_id_vlm_analysis.json`
   - Or view directly in Gemini website

## 🔧 Using the VLM Analyzer Module Directly

You can also use the VLM analyzer in your own Python code:

```python
from utils.vlm_analyzer import VLMAnalyzer, analyze_presentation_vlm

# Simple usage
result = analyze_presentation_vlm("presentations/file.pptx")

# With API key
result = analyze_presentation_vlm("presentations/file.pptx", api_key="your-key")

# Get instructions for Gemini website
analyzer = VLMAnalyzer()
instructions = analyzer.analyze_with_gemini_website("presentations/file.pptx")
```

## 📊 Analysis Output

The VLM analysis provides:

- **Content Summary**: Main content and key points from each slide
- **Visual Design**: Layout, colors, fonts, visual elements
- **Readability**: Text clarity and organization
- **Visual Balance**: Content distribution on slides
- **Professional Quality**: Overall rating (1-10)
- **Suggestions**: Recommendations for improvement

## 🎨 Example Analysis Prompts for Gemini

When using Gemini website, try these prompts:

1. **Comprehensive Analysis**:
   ```
   Analyze this PowerPoint presentation comprehensively. Provide feedback on:
   - Visual design and layout
   - Content organization and clarity
   - Readability and text formatting
   - Professional quality
   - Specific improvement suggestions
   ```

2. **Content Extraction**:
   ```
   Extract and summarize all key information from each slide in this presentation.
   Organize the information by slide number.
   ```

3. **Visual Design Review**:
   ```
   Review the visual design of this presentation. Evaluate:
   - Color scheme and contrast
   - Font choices and sizes
   - Layout and spacing
   - Overall visual appeal
   ```

4. **Quality Assessment**:
   ```
   Rate this presentation on a scale of 1-10 for:
   - Professional appearance
   - Content quality
   - Visual design
   - Overall effectiveness
   Provide detailed justification for each rating.
   ```

## ⚙️ Configuration

### Environment Variables

- `GEMINI_API_KEY` (Optional): Gemini API key for programmatic analysis
  - If not set, the system provides instructions for Gemini website
  - Get key from: https://makersuite.google.com/app/apikey

### Dependencies

**Required:**
- `python-pptx` (already installed)

**Optional (for API usage):**
- `google-generativeai` - Gemini API client
- `Pillow` - Image processing (if converting slides to images)

Install optional dependencies:
```bash
pip install google-generativeai Pillow
```

## 📝 Notes

- **No API Key Required**: The system works without API keys by providing instructions for Gemini website
- **Gemini Website**: Easiest method - just upload and ask questions
- **API Integration**: Optional - provides programmatic access if API key is set
- **Analysis Results**: Saved to `slides_output/` directory as JSON files
- **File Size Limits**: Gemini website has file size limits (typically 20MB)

## 🐛 Troubleshooting

### "Gemini API key not available"
- This is normal if you haven't set `GEMINI_API_KEY`
- Use Gemini website instead (instructions will be provided)

### "PIL/Pillow not available"
- Only needed if converting slides to images
- For Gemini website upload, this is not required
- Install with: `pip install Pillow`

### "google-generativeai not installed"
- Only needed for API usage
- For Gemini website, this is not required
- Install with: `pip install google-generativeai`

## 🎉 Benefits of VLM Analysis

1. **Visual Quality Check**: Ensures presentations look professional
2. **Content Validation**: Verifies information is clear and accurate
3. **Design Feedback**: Gets suggestions for visual improvements
4. **Quality Assurance**: Automated quality assessment
5. **Comprehensive Review**: Detailed analysis of all aspects

---

For more information, see the main [README.md](README.md) file.

