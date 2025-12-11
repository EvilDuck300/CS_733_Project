# Recent changes (2025-12-10)

- Added a note to prefer running the Quickstart inside the project venv and using the workspace Python interpreter in VS Code. A `.vscode/launch.json` has been added to help run `app.py` with the venv active.

# Quick Start: Using Gemini with Your App

## 1. Get Your API Key (2 minutes)

1. Visit: **https://aistudio.google.com/apikey**
2. Sign in with Google
3. Click **"Create API Key"** 
4. Copy the key

## 2. Set Environment Variable

### PowerShell (Windows):
```powershell
$env:GEMINI_API_KEY = "paste-your-key-here"
```

### Or Create `.env` File:
Create a file named `.env` in your project root:
```
GEMINI_API_KEY=paste-your-key-here
```

## 3. Install Libraries

```powershell
pip install -r requirements.txt
```

This installs:
- `google-genai` (Gemini API)
- `Flask` (Web framework)
- `python-pptx` (PowerPoint generation)
- And other dependencies

## 4. Run the App

```powershell
# Activate virtual environment (if using one)
.venv\Scripts\Activate.ps1

# Start the Flask server
python app.py
```

Output will show:
```
* Running on http://localhost:5000
```

## 5. Use the App

Open your browser: **http://localhost:5000**

1. Upload a PDF
2. Select an audience type
3. Enter a description
4. Click "Submit"

The system will:
- Extract chunks using GNN retrieval
- Generate 3 slide versions using Gemini
- Automatically evaluate all versions
- Show results for review

## What Each Component Uses

| Component | Model | Purpose |
|-----------|-------|---------|
| **Slide Generator** | gemini-2.5-flash | Creates PowerPoint slides |
| **Evaluator** | gemini-2.5-flash | Grades slides on clarity, accuracy, etc. |
| **Retrieval (GNN)** | Local | Extracts relevant chunks from PDF |

## Free Tier Limits

- **15 requests/minute** (should be plenty for testing)
- **No payment required**
- **Upgrade later if needed**

Check usage: https://aistudio.google.com/app/apikey

## Troubleshooting

### "Gemini API key not provided"
```powershell
# Check if variable is set
echo $env:GEMINI_API_KEY

# If empty, set it again
$env:GEMINI_API_KEY = "your-key"
```

### "Module 'google' has no attribute 'genai'"
```powershell
# Reinstall google-genai
pip install --upgrade google-genai
```

### "Connection error"
- Check internet connection
- Verify API key is correct
- Check at https://aistudio.google.com/apikey

## API Key Security

⚠️ **Never share your API key!**

Never:
- Commit `.env` file to Git
- Share in Discord/Slack
- Put in public repositories
- Commit in code

If exposed:
1. Go to https://aistudio.google.com/apikey
2. Delete the compromised key
3. Create a new one

## File Structure

```
project/
├── app.py                    # Main Flask app
├── requirements.txt          # Dependencies
├── .env                      # Your API key (not in git!)
├── utils/
│   ├── slide_generator.py   # Uses Gemini to create slides
│   ├── evaluator.py         # Uses Gemini to grade slides
│   ├── retrieval_gnn.py     # Local: extracts chunks
│   └── presentation_builder.py # Creates PowerPoint files
├── templates/
│   ├── index.html           # Upload form
│   └── review.html          # Slide review page
├── static/
│   ├── css/style.css
│   └── js/main.js
└── GEMINI_SETUP.md          # Detailed setup guide
```

## Next Steps

- Upload a PDF to test
- Review generated slides
- Provide feedback to refine results
- Download final PowerPoint

## More Details

For detailed troubleshooting and advanced setup:
See **GEMINI_SETUP.md** in project root

---

**Questions?** Check Google's official docs: https://ai.google.dev/docs
