"""
Script to create a new PowerPoint from VLM-improved slides

Usage:
    python create_improved_presentation.py <improved_slides.json> [output.pptx]
    
    Example:
        python create_improved_presentation.py file_improved_slides.json output.pptx
"""

import sys
import json
import os
from utils.presentation_builder import create_presentation_from_slides_data


def main():
    """Create PowerPoint from improved slides JSON"""
    if len(sys.argv) < 2:
        print("Usage: python create_improved_presentation.py <improved_slides.json> [output.pptx]")
        print("\nExample:")
        print("  python create_improved_presentation.py file_improved_slides.json")
        print("  python create_improved_presentation.py file_improved_slides.json output.pptx")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(json_file):
        print(f"Error: JSON file not found: {json_file}")
        sys.exit(1)
    
    print(f"Loading improved slides from: {json_file}")
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            improved_slides = json.load(f)
        
        # Determine output path
        if output_file is None:
            base_name = os.path.splitext(os.path.basename(json_file))[0]
            output_file = f"{base_name}_presentation.pptx"
        
        print(f"Creating PowerPoint: {output_file}")
        
        # Create presentation
        output_path = create_presentation_from_slides_data(improved_slides, output_file)
        
        print(f"\n✓ Success! Improved presentation created: {output_path}")
        print(f"  Title slide: {improved_slides.get('title_slide', {}).get('title', 'N/A')}")
        print(f"  Content slides: {len(improved_slides.get('slides', []))}")
        
    except Exception as e:
        print(f"\n✗ Error creating presentation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

