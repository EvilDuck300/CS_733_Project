"""
VLM (Vision Language Model) Analyzer for PowerPoint Presentations
Analyzes generated PowerPoint presentations using Gemini Vision API
"""

import os
import json
import base64
from typing import Dict, Any, List, Optional
from pptx import Presentation
from io import BytesIO

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from PIL import Image
    import io
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None


class VLMAnalyzer:
    """Analyze PowerPoint presentations using Vision Language Model (Gemini)"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the VLM analyzer
        
        Args:
            api_key: Gemini API key (if None, will try to get from environment)
                    If not provided, VLM analysis will not be available
        """
        if not GEMINI_AVAILABLE:
            self.client = None
            self.api_key = None
            print("Warning: google-generativeai package not installed. VLM analysis will not be available.")
            print("Install with: pip install google-generativeai")
            return
        
        if not PIL_AVAILABLE:
            print("Warning: PIL/Pillow not available. Cannot convert slides to images.")
            print("Install with: pip install Pillow")
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            self.client = None
            print("Warning: Gemini API key not provided. VLM analysis will not be available.")
            print("Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        else:
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel('gemini-pro-vision')
            print("VLM Analyzer initialized with Gemini Vision API")
    
    def pptx_to_images(self, pptx_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Convert PowerPoint slides to images
        
        Args:
            pptx_path: Path to PowerPoint file
            output_dir: Directory to save images (default: same directory as PPTX)
            
        Returns:
            List of image file paths
        """
        if not PIL_AVAILABLE:
            raise ValueError("PIL/Pillow required for slide-to-image conversion")
        
        if not os.path.exists(pptx_path):
            raise FileNotFoundError(f"PowerPoint file not found: {pptx_path}")
        
        # Determine output directory
        if output_dir is None:
            base_dir = os.path.dirname(pptx_path)
            base_name = os.path.splitext(os.path.basename(pptx_path))[0]
            output_dir = os.path.join(base_dir, f"{base_name}_slides")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Load presentation
        prs = Presentation(pptx_path)
        image_paths = []
        
        print(f"Converting {len(prs.slides)} slides to images...")
        
        # Note: python-pptx doesn't directly support rendering to images
        # We'll need to use a workaround or external tool
        # For now, we'll create a placeholder that indicates this needs implementation
        # In production, you might use:
        # - LibreOffice headless mode
        # - comtypes (Windows COM automation)
        # - unoconv
        # - Or convert PPTX to PDF first, then PDF to images
        
        print("Note: Direct PPTX to image conversion requires additional tools.")
        print("Consider using: LibreOffice, unoconv, or convert PPTX->PDF->Images")
        
        return image_paths
    
    def analyze_slide_image(self, image_path: str, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze a single slide image using Gemini Vision
        
        Args:
            image_path: Path to slide image
            prompt: Analysis prompt (default: comprehensive slide analysis)
            
        Returns:
            Dictionary with analysis results
        """
        if not self.client:
            raise ValueError("Gemini API key not available. Cannot perform VLM analysis.")
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Load image
        if PIL_AVAILABLE:
            img = Image.open(image_path)
        else:
            raise ValueError("PIL/Pillow required for image processing")
        
        # Default prompt for comprehensive slide analysis
        if prompt is None:
            prompt = """Analyze this PowerPoint slide and provide:
1. Content Summary: What is the main content and key points?
2. Visual Design: Describe the layout, colors, fonts, and visual elements
3. Readability: Is the text clear and well-organized?
4. Visual Balance: Is the content well-distributed on the slide?
5. Professional Quality: Rate the overall professional appearance (1-10)
6. Suggestions: Any recommendations for improvement?

Provide a detailed analysis in JSON format."""
        
        try:
            # Use Gemini Vision API
            response = self.client.generate_content([prompt, img])
            analysis_text = response.text
            
            # Try to parse as JSON if possible
            try:
                # Extract JSON if wrapped in markdown
                if "```json" in analysis_text:
                    json_text = analysis_text.split("```json")[1].split("```")[0].strip()
                elif "```" in analysis_text:
                    json_text = analysis_text.split("```")[1].split("```")[0].strip()
                else:
                    json_text = analysis_text
                
                analysis_data = json.loads(json_text)
            except json.JSONDecodeError:
                # If not JSON, return as text
                analysis_data = {
                    "analysis": analysis_text,
                    "raw_response": True
                }
            
            return {
                "success": True,
                "image_path": image_path,
                "analysis": analysis_data
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def analyze_presentation(self, pptx_path: str, 
                           analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze entire PowerPoint presentation using VLM
        
        Args:
            pptx_path: Path to PowerPoint file
            analysis_type: Type of analysis ("comprehensive", "visual", "content", "quality")
            
        Returns:
            Dictionary with complete analysis results
        """
        if not self.client:
            raise ValueError("Gemini API key not available. Cannot perform VLM analysis.")
        
        if not os.path.exists(pptx_path):
            raise FileNotFoundError(f"PowerPoint file not found: {pptx_path}")
        
        # Load presentation to get metadata
        prs = Presentation(pptx_path)
        num_slides = len(prs.slides)
        
        print(f"Analyzing presentation with {num_slides} slides...")
        
        # For now, since we don't have direct PPTX->image conversion,
        # we'll provide instructions for manual upload
        result = {
            "success": True,
            "presentation_path": pptx_path,
            "num_slides": num_slides,
            "analysis_type": analysis_type,
            "message": "To analyze with VLM, upload the PowerPoint to Gemini website or convert slides to images first.",
            "instructions": {
                "option_1": "Upload PPTX directly to Gemini website for visual analysis",
                "option_2": "Convert PPTX to images using: LibreOffice, unoconv, or PPTX->PDF->Images",
                "option_3": "Use the analyze_slide_image() method after converting slides to images"
            }
        }
        
        return result
    
    def analyze_with_gemini_website(self, pptx_path: str) -> Dict[str, Any]:
        """
        Provide instructions for analyzing PowerPoint using Gemini website
        
        Args:
            pptx_path: Path to PowerPoint file
            
        Returns:
            Dictionary with instructions and file info
        """
        if not os.path.exists(pptx_path):
            raise FileNotFoundError(f"PowerPoint file not found: {pptx_path}")
        
        file_size = os.path.getsize(pptx_path) / (1024 * 1024)  # MB
        
        return {
            "success": True,
            "presentation_path": pptx_path,
            "file_size_mb": round(file_size, 2),
            "instructions": {
                "step_1": "Go to https://gemini.google.com/",
                "step_2": "Click on 'Upload' or drag and drop the PowerPoint file",
                "step_3": "Ask Gemini to analyze the presentation, for example:",
                "example_prompts": [
                    "Analyze this PowerPoint presentation and provide feedback on visual design, content organization, and readability.",
                    "Review this presentation and suggest improvements for professional quality.",
                    "Evaluate the slides for clarity, visual balance, and audience appropriateness.",
                    "Extract key information from each slide and summarize the presentation."
                ],
                "step_4": "Gemini will analyze the slides visually and provide detailed feedback"
            },
            "alternative": "You can also use the analyze_presentation() method if you have Gemini API key set up"
        }


def analyze_presentation_vlm(pptx_path: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to analyze a PowerPoint presentation with VLM
    
    Args:
        pptx_path: Path to PowerPoint file
        api_key: Optional Gemini API key
        
    Returns:
        Analysis results dictionary
    """
    analyzer = VLMAnalyzer(api_key=api_key)
    
    if analyzer.client:
        # Use API if available
        return analyzer.analyze_presentation(pptx_path)
    else:
        # Provide instructions for Gemini website
        return analyzer.analyze_with_gemini_website(pptx_path)

