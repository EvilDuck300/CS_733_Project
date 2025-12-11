# Recent changes (2025-12-10)

- Added local debugging guidance: make sure VS Code uses the repository virtual environment and that `pip install -r requirements.txt` is run inside that venv to avoid mismatched package imports.

# Gemini API Setup Guide

Your application has been updated to use **Google Gemini API** instead of OpenAI. This guide explains how to set it up.

## Installation

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

Or install the Gemini package directly:
```powershell
pip install google-genai>=0.3.0
```

## Getting Your Gemini API Key

### Step 1: Get API Key from Google AI Studio
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key" 
4. Copy the generated API key

### Step 2: Set Environment Variable

#### On Windows (PowerShell):
```powershell
# Set for current session only
$env:GEMINI_API_KEY = "your-api-key-here"

# Or set permanently in PowerShell profile:
Add-Content -Path $PROFILE -Value '$env:GEMINI_API_KEY = "your-api-key-here"'
```

#### Or create a `.env` file in your project root:
```
GEMINI_API_KEY=your-api-key-here
```

Then install python-dotenv and update `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Running the Application

```powershell
# Activate virtual environment (if using one)
.venv\Scripts\Activate.ps1

# Run the Flask app
python app.py
```

The app will start on `http://localhost:5000`

## What Uses Gemini

1. **Slide Generation** (`utils/slide_generator.py`)
   - Uses `gemini-2.5-flash` model
   - Generates 3 different versions of PowerPoint slides
   - Uses few-shot learning from dataset for better results

2. **Slide Evaluation** (`utils/evaluator.py`)
   - Uses `gemini-2.5-flash` model
   - Evaluates slides on 4 criteria:
     - Clarity
     - Accuracy
     - Visual Balance
     - Audience Fit

## Available Gemini Models

- **gemini-2.5-flash** (default) - Fast, efficient for most tasks
- **gemini-2.0-flash** - Stable model
- **gemini-1.5-pro** - More capable, higher cost

To use a different model, update the `model` parameter in:
- `utils/slide_generator.py` line 193
- `utils/evaluator.py` line 77

## API Quotas & Pricing

- **Free Tier**: 15 requests per minute, generous daily quotas
- **Paid Tier**: Pay-as-you-go pricing after free tier exhausted

Check usage at [Google AI Studio Usage](https://aistudio.google.com/app/apikey)

## Troubleshooting

### "Gemini API key not provided"
- Make sure `GEMINI_API_KEY` environment variable is set
- Restart your terminal/IDE after setting the variable
- Verify with: `echo $env:GEMINI_API_KEY`

### "Failed to parse JSON from Gemini response"
- Gemini model may have changed behavior
- Try using a different model (gemini-2.0-flash)
- Check that response schema is correct in code

### Rate Limiting
- If you hit rate limits, implement exponential backoff
- Free tier: max 15 requests/minute
- Space out requests or upgrade to paid tier

## Differences from OpenAI

| Aspect | Gemini | OpenAI |
|--------|--------|--------|
| API SDK | `google-genai` | `openai` |
| Response Format | JSON via schema | Manual JSON parsing |
| Model Names | gemini-* | gpt-* |
| Pricing | Free tier available | Pay-as-you-go |
| Rate Limits | 15 req/min (free) | Varies by plan |

## JSON Schema Validation

Gemini automatically validates responses against the schema defined in `GenerateContentConfig`. This ensures reliable JSON output without manual parsing workarounds.

Example from code:
```python
config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=types.Schema.from_dict({...}),
    temperature=0.7,
)
```

## Questions?

- Gemini Docs: https://ai.google.dev/docs
- API Reference: https://ai.google.dev/api/rest
- Support: https://support.google.com/gemini/

