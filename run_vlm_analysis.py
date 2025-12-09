"""
Script to run VLM analysis on generated PowerPoint presentations

Supports multiple backends (NO API KEYS REQUIRED):
- Local models (BLIP-2, LLaVA via Hugging Face) - FREE, runs locally
- Ollama (local models) - FREE, requires Ollama installation
- Gemini API (optional) - requires API key
- Text-based analysis (fallback) - FREE, no dependencies

Usage:
    python run_vlm_analysis.py <presentation_file.pptx> [--backend auto|local|ollama|gemini|text] [--model MODEL_NAME]
    
    Examples:
        # Auto-detect best available backend (no API keys needed!)
        python run_vlm_analysis.py presentations/file.pptx
        
        # Use local Hugging Face model (FREE, no API keys)
        python run_vlm_analysis.py presentations/file.pptx --backend local --model Salesforce/blip-image-captioning-base
        
        # Use Ollama (FREE, requires Ollama running)
        python run_vlm_analysis.py presentations/file.pptx --backend ollama --model llava
        
        # Use Gemini API (requires API key)
        MY_NEW_GEMINI_API_KEY=your-key python run_vlm_analysis.py presentations/file.pptx --backend gemini
        
        # Text-based analysis only (no vision, no dependencies)
        python run_vlm_analysis.py presentations/file.pptx --backend text

Requirements for local models:
    pip install transformers torch Pillow
    
Requirements for Ollama:
    Install Ollama from https://ollama.ai/
    Then: ollama pull llava
"""

import sys
import os
import json
import argparse
from utils.vlm_analyzer import analyze_presentation_vlm, VLMAnalyzer


def main():
    """Main function to run VLM analysis"""
    parser = argparse.ArgumentParser(
        description="Analyze PowerPoint presentations with VLM (no API keys required!)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect backend (no API keys needed)
  python run_vlm_analysis.py presentations/file.pptx
  
  # Use local model (FREE, no API keys)
  python run_vlm_analysis.py presentations/file.pptx --backend local
  
  # Use Ollama (FREE, requires Ollama)
  python run_vlm_analysis.py presentations/file.pptx --backend ollama --model llava
  
  # Use Gemini API (requires API key)
  MY_NEW_GEMINI_API_KEY=key python run_vlm_analysis.py presentations/file.pptx --backend gemini
        """
    )
    
    parser.add_argument('pptx_file', help='Path to PowerPoint file')
    parser.add_argument('--backend', 
                       choices=['auto', 'local', 'ollama', 'gemini', 'text'],
                       default='auto',
                       help='VLM backend to use (default: auto-detect)')
    parser.add_argument('--model', 
                       help='Model name for local/Ollama backends')
    parser.add_argument('--api-key',
                       help='API key (for Gemini backend)')
    parser.add_argument('--no-improve', 
                       action='store_true',
                       help='Only extract text, do not generate improved slides')
    
    args = parser.parse_args()
    
    pptx_path = args.pptx_file
    
    if not os.path.exists(pptx_path):
        print(f"Error: PowerPoint file not found: {pptx_path}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"VLM Analysis for: {os.path.basename(pptx_path)}")
    print(f"Backend: {args.backend}")
    print(f"{'='*60}\n")
    
    # Get API key if needed
    api_key = args.api_key or os.getenv('MY_NEW_GEMINI_API_KEY')
    
    try:
        result = analyze_presentation_vlm(
            pptx_path, 
            api_key=api_key,
            backend=args.backend,
            model_name=args.model,
            generate_improved=not args.no_improve  # Generate improved by default
        )
        
        if result.get('success'):
            print("✓ Analysis completed successfully!")
            print(f"\nBackend used: {result.get('backend', 'unknown')}")
            print(f"Number of slides: {result.get('num_slides', 0)}")
            
            # Check if improved slides were generated
            if result.get('has_improvements'):
                print("✓ Improved slide content generated!")
                print("\nImproved slides structure:")
                improved = result.get('improved_slides', {})
                if 'title_slide' in improved:
                    print(f"  Title: {improved['title_slide'].get('title', 'N/A')}")
                if 'slides' in improved:
                    print(f"  Content slides: {len(improved['slides'])}")
                    for slide in improved['slides']:
                        print(f"    - Slide {slide.get('slide_number')}: {slide.get('title', 'N/A')}")
                        print(f"      Bullet points: {len(slide.get('content', []))}")
            
            print(f"\nFull Results:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Save results
            base_name = os.path.splitext(os.path.basename(pptx_path))[0]
            output_file = f"{base_name}_vlm_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Results saved to: {output_file}")
            
            # If improved slides generated, save them separately for easy use
            if result.get('has_improvements'):
                improved_file = f"{base_name}_improved_slides.json"
                with open(improved_file, 'w', encoding='utf-8') as f:
                    json.dump(result.get('improved_slides', {}), f, indent=2, ensure_ascii=False)
                print(f"✓ Improved slides saved to: {improved_file}")
                print(f"\n💡 You can use this file to regenerate the presentation with improved content!")
                print(f"   Option 1: Use presentation builder")
                print(f"      from utils.presentation_builder import create_presentation_from_slides_data")
                print(f"      create_presentation_from_slides_data(result['improved_slides'], 'output.pptx')")
                print(f"   Option 2: Use the improved slides JSON in your app")
        else:
            print("⚠ Analysis completed with warnings")
            print(f"\nResults: {json.dumps(result, indent=2)}")
            
    except Exception as e:
        print(f"✗ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        
        # If auto backend failed, try text-based
        if args.backend == "auto":
            print("\nTrying text-based analysis as fallback...\n")
            try:
                result = analyze_presentation_vlm(pptx_path, backend="text")
                print(json.dumps(result, indent=2))
            except:
                pass




if __name__ == "__main__":
    main()

