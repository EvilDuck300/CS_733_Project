"""
Script to run VLM analysis on generated PowerPoint presentations

Usage:
    python run_vlm_analysis.py <presentation_file.pptx>
    
    Examples:
        # Analyze a specific presentation
        python run_vlm_analysis.py presentations/0293f39f-566a-486d-a369-fe416c4f7b64_final_presentation.pptx
        
        # Analyze with Gemini API (if API key is set)
        GEMINI_API_KEY=your-key python run_vlm_analysis.py presentations/file.pptx
        
        # Get instructions for Gemini website (no API key needed)
        python run_vlm_analysis.py presentations/file.pptx

Requirements:
    Optional: pip install google-generativeai Pillow
    (If not installed, script will provide instructions for Gemini website)
"""

import sys
import os
import json
from utils.vlm_analyzer import analyze_presentation_vlm, VLMAnalyzer


def main():
    """Main function to run VLM analysis"""
    if len(sys.argv) < 2:
        print("Usage: python run_vlm_analysis.py <presentation_file.pptx>")
        print("\nExample:")
        print("  python run_vlm_analysis.py presentations/submission_id_final_presentation.pptx")
        sys.exit(1)
    
    pptx_path = sys.argv[1]
    
    if not os.path.exists(pptx_path):
        print(f"Error: PowerPoint file not found: {pptx_path}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"VLM Analysis for: {os.path.basename(pptx_path)}")
    print(f"{'='*60}\n")
    
    # Check if API key is available
    api_key = os.getenv('GEMINI_API_KEY')
    
    if api_key:
        print("✓ Gemini API key found. Using API for analysis...\n")
        try:
            result = analyze_presentation_vlm(pptx_path, api_key=api_key)
            
            if result.get('success'):
                print("✓ Analysis completed successfully!")
                print(f"\nResults:")
                print(json.dumps(result, indent=2))
            else:
                print("⚠ Analysis completed with warnings")
                print(f"\nResults: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"✗ Error during API analysis: {e}")
            print("\nFalling back to Gemini website instructions...\n")
            analyzer = VLMAnalyzer()
            result = analyzer.analyze_with_gemini_website(pptx_path)
            print_instructions(result)
    else:
        print("ℹ No Gemini API key found.")
        print("Providing instructions for Gemini website analysis...\n")
        analyzer = VLMAnalyzer()
        result = analyzer.analyze_with_gemini_website(pptx_path)
        print_instructions(result)


def print_instructions(result):
    """Print instructions for using Gemini website"""
    print(f"\n{'='*60}")
    print("HOW TO ANALYZE WITH GEMINI WEBSITE")
    print(f"{'='*60}\n")
    
    instructions = result.get('instructions', {})
    
    print(f"File: {result.get('presentation_path')}")
    print(f"Size: {result.get('file_size_mb', 'N/A')} MB\n")
    
    print("Steps:")
    for key, value in instructions.items():
        if key == 'example_prompts':
            print(f"\n  Example Prompts:")
            for i, prompt in enumerate(value, 1):
                print(f"    {i}. \"{prompt}\"")
        else:
            print(f"  {value}")
    
    print(f"\n{'='*60}")
    print("ALTERNATIVE: Use Gemini API")
    print(f"{'='*60}")
    print("\nTo use the API instead:")
    print("  1. Get a Gemini API key from: https://makersuite.google.com/app/apikey")
    print("  2. Set environment variable:")
    print("     export GEMINI_API_KEY='your-api-key-here'")
    print("  3. Run this script again")
    print("\nOr install required packages:")
    print("  pip install google-generativeai Pillow")
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()

