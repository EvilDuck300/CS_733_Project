# VLM (Vision Language Model) Analysis Guide

## Overview

After generating a PowerPoint presentation, you can analyze it using a Vision Language Model (VLM) to get visual feedback, content analysis, and quality assessment.

**🎉 NO API KEYS REQUIRED!** The system supports local/open-source models that run completely free on your machine.

## 🎯 What is VLM Analysis?

VLM analysis uses AI vision models to:
- **Visual Design Analysis**: Evaluate layout, colors, fonts, and visual elements
- **Content Extraction**: Extract and summarize key information from slides
- **Readability Assessment**: Check if text is clear and well-organized
- **Quality Evaluation**: Rate professional appearance and provide improvement suggestions
- **Comprehensive Review**: Get detailed feedback on the entire presentation

## 🚀 How to Run VLM Analysis

### Option 1: Local Models (FREE - No API Keys Required!) ⭐ RECOMMENDED

Run VLM analysis completely locally using open-source models:

#### Using Hugging Face Local Models (BLIP-2, LLaVA)

```bash
# Install dependencies
pip install transformers torch Pillow

# Run analysis with local model (auto-detects best model)
python run_vlm_analysis.py presentations/file.pptx --backend local

# Or specify a model
python run_vlm_analysis.py presentations/file.pptx --backend local --model Salesforce/blip-image-captioning-base
```

**Available Local Models:**
- `Salesforce/blip-image-captioning-base` - Lightweight, fast (recommended)
- `Salesforce/blip-image-captioning-large` - Better quality, slower
- `llava-hf/llava-1.5-7b-hf` - Advanced vision-language model

#### Using Ollama (FREE - Easy Setup)

1. **Install Ollama**: https://ollama.ai/
2. **Pull a vision model**:
   ```bash
   ollama pull llava
   ```
3. **Run analysis**:
   ```bash
   python run_vlm_analysis.py presentations/file.pptx --backend ollama --model llava
   ```

**Benefits:**
- ✅ **100% FREE** - No API costs
- ✅ **Privacy** - Data stays on your machine
- ✅ **No API keys** - Works offline
- ✅ **Fast** - No network latency

### Option 2: Using Gemini Website (No API Key Needed)

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

### Option 3: Using the Script (Auto-Detection)

The script automatically detects the best available backend:

```bash
# Auto-detect best backend (tries local -> ollama -> gemini -> text)
python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx
```

#### With Specific Backend

```bash
# Use local model
python run_vlm_analysis.py presentations/file.pptx --backend local

# Use Ollama
python run_vlm_analysis.py presentations/file.pptx --backend ollama --model llava

# Use Gemini API (requires API key)
GEMINI_API_KEY=key python run_vlm_analysis.py presentations/file.pptx --backend gemini

# Text-based only (no vision)
python run_vlm_analysis.py presentations/file.pptx --backend text
```

### Option 4: With Gemini API Key (Optional)

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

### Option 5: Using the Web API Endpoint

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

### Complete Workflow with Local VLM (No API Keys!)

1. **Install Local Model Dependencies**:
   ```bash
   pip install transformers torch Pillow
   ```

2. **Upload PDF and Generate Presentation**:
   ```bash
   # Use the web interface or API
   # This generates: presentations/submission_id_final_presentation.pptx
   ```

3. **Run VLM Analysis with Local Model**:
   ```bash
   python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx --backend local
   ```

4. **Review Analysis Results**:
   - Results displayed in console
   - Results saved to: `submission_id_final_presentation_vlm_analysis.json`
   - No API calls, completely local!

### Alternative: Using Ollama

1. **Install Ollama**: https://ollama.ai/
2. **Download Vision Model**:
   ```bash
   ollama pull llava
   ```
3. **Run Analysis**:
   ```bash
   python run_vlm_analysis.py presentations/file.pptx --backend ollama --model llava
   ```

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

**For Local Models (FREE, No API Keys):**
```bash
pip install transformers torch Pillow
```

**For Ollama (FREE, No API Keys):**
- Install Ollama from https://ollama.ai/
- Then: `ollama pull llava`
- Python: `pip install requests Pillow` (usually already installed)

**For Gemini API (Optional, Requires API Key):**
```bash
pip install google-generativeai Pillow
```

## 📝 Notes

- **✅ NO API KEYS REQUIRED**: Use local models (BLIP-2, LLaVA) or Ollama - completely FREE!
- **Local Models**: Run on your machine, no internet needed, privacy guaranteed
- **Ollama**: Easy-to-use local models, great performance
- **Gemini Website**: Alternative option - just upload and ask questions (no API key needed)
- **Gemini API**: Optional - provides programmatic access if API key is set
- **Analysis Results**: Saved as JSON files next to the PowerPoint file
- **File Size Limits**: Only apply to Gemini website (typically 20MB), local models have no limits

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

