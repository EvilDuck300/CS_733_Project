# Guide: Generating 3 Themed Presentations from JSON

This guide explains how to generate 3 complete, distinct slide decks from the same JSON input, each with different themes and layouts.

## Quick Start

```bash
python generate_three_themed_presentations.py retrieval_output/your_file.json
```

## What It Does

The script generates **3 complete slide decks** from your JSON input:

1. **Executive Overview** - Business-focused, high-level impact, concise
2. **Technical Deep Dive** - Detailed methodology, architecture, implementation  
3. **Results & Impact** - Performance metrics, outcomes, visualizations

Each presentation:
- ✅ Is a **complete, standalone deck** (not split content)
- ✅ Covers the **same information** from your JSON
- ✅ Has a **different theme and layout**
- ✅ Includes **images** from the JSON when available
- ✅ Has **different slide counts** appropriate to the theme

## Two Modes

### 1. AI-Powered Generation (Recommended)
**Requires:** OpenAI API key

```bash
export OPENAI_API_KEY=your_key_here
python generate_three_themed_presentations.py retrieval_output/your_file.json
```

**Benefits:**
- Intelligent content organization
- Theme-appropriate language and structure
- Better slide flow and coherence
- Professional formatting

### 2. Content-Based Generation (No API Key)
**Requires:** No API key needed

```bash
python generate_three_themed_presentations.py retrieval_output/your_file.json
```

**How it works:**
- Extracts content from JSON chunks
- Organizes by theme using keyword matching
- Creates structured slides with extracted information
- Still produces 3 distinct presentations

## Output

The script creates 3 PowerPoint files in the `presentations/` directory:

```
presentations/
├── Presentation_executive_Executive_Overview.pptx
├── Presentation_technical_Technical_Deep_Dive.pptx
└── Presentation_results_Results_&_Impact.pptx
```

## Theme Differences

### Executive Overview
- **Focus:** Business impact, ROI, practical applications
- **Style:** Concise, strategic, decision-focused
- **Slides:** ~8 slides
- **Content:** Problem → Solution → Results → Impact → Conclusion

### Technical Deep Dive
- **Focus:** Methodology, architecture, algorithms, implementation
- **Style:** Detailed, analytical, comprehensive
- **Slides:** ~10 slides
- **Content:** Background → Methodology → Architecture → Implementation → Details → Evaluation

### Results & Impact
- **Focus:** Performance metrics, experimental results, comparisons
- **Style:** Data-driven, evidence-based
- **Slides:** ~9 slides
- **Content:** Overview → Setup → Results → Comparisons → Transferability → Conclusion

## Customization

### Change Output Directory
```bash
python generate_three_themed_presentations.py your_file.json --output-dir my_presentations
```

### Adjust Number of Slides
Edit the `num_slides` values in the `themes` dictionary in the script:
- Executive: `num_slides: 8`
- Technical: `num_slides: 10`
- Results: `num_slides: 9`

## Example Usage

```bash
# With API key (best results)
export OPENAI_API_KEY=sk-...
python generate_three_themed_presentations.py retrieval_output/aec9ee25-a657-47bc-b85e-a9a2c1049548_retrieval_output.json

# Without API key (still works, uses content extraction)
python generate_three_themed_presentations.py retrieval_output/aec9ee25-a657-47bc-b85e-a9a2c1049548_retrieval_output.json
```

## Image Support

The script automatically includes images from your JSON:
- Images are distributed across slides based on theme
- Executive: Key visualizations on results slides
- Technical: Diagrams on methodology/architecture slides
- Results: Visualizations on results/metrics slides

## Troubleshooting

### "OpenAI API key not provided"
- **Option 1:** Set `OPENAI_API_KEY` environment variable
- **Option 2:** Use without API key (content-based generation)

### "JSON file not found"
- Check the path to your JSON file
- Use relative path from project root or absolute path

### Images not appearing
- Check that image paths in JSON are correct
- Images should be in `uploads/extracted_images/` or path specified in JSON

## Next Steps

After generating the 3 presentations, you can:
1. Review each presentation
2. Use the iterative generator to improve them with VLM evaluation
3. Manually refine content if needed

## Integration with Iterative Generator

To use these presentations with the iterative VLM evaluation system:

```bash
python iterative_powerpoint_generator.py retrieval_output/your_file.json \
    --threshold 80 \
    --max-iterations 3
```

This will generate 3 themed presentations and evaluate them iteratively until they meet quality thresholds.

