"""
Slide Generation Module with Gemini API Integration
Generates intelligent, well-formatted slides from retrieval output
"""

import json
import os
from typing import List, Dict, Any, Optional

try:
    # Import the Google GenAI SDK
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    types = None

from utils.dataset_loader import get_dataset


class SlideGenerator:
    """Generate slides using the Gemini API with few-shot learning from dataset"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the slide generator
        
        Args:
            api_key: Gemini API key (if None, will try to get from environment)
        """
        if not GEMINI_AVAILABLE:
            self.client = None
            self.api_key = None
            print("Warning: Google GenAI package not installed. Slide generation will not be available.")
            print("To enable, install: pip install google-genai")
            return
        
        # The genai.Client() constructor automatically looks for the GEMINI_API_KEY environment variable.
        # However, we explicitly pass the key here if provided from app.py
        self.api_key = api_key
        if not self.api_key:
            self.client = None
            print("Warning: Gemini API key not provided. Slide generation will not be available.")
        else:
            self.client = genai.Client(api_key=self.api_key)
        self.dataset = get_dataset()
    
    def _build_prompt(self, relevant_chunks: List[Dict[str, Any]], 
                     description: str, audience_type: str, 
                     num_slides: int = 3, theme: Optional[str] = None) -> str:
        """
        Build the prompt for the Gemini model
        
        Args:
            relevant_chunks: List of relevant chunks from retrieval
            description: User's description
            audience_type: Target audience
            num_slides: Number of slides to generate
            
        Returns:
            Formatted prompt string
        """
        # Get few-shot examples from dataset
        few_shot_examples = self.dataset.get_few_shot_examples(
            description=description,
            audience_type=audience_type,
            num_examples=3
        )
        
        # Combine relevant chunks into content
        content_text = "\n\n".join([
            f"Chunk {i+1} (Relevance: {chunk.get('relevance_score', 0):.2f}):\n{chunk.get('text', '')}"
            for i, chunk in enumerate(relevant_chunks[:10])  # Use top 10 chunks
        ])
        
        # Build audience-specific instructions
        # Ensure audience_type is not None and is a string
        if not audience_type or not isinstance(audience_type, str):
            audience_type = 'general'
        
        audience_instructions = {
            'students': 'Use clear, educational language. Include definitions and examples. Keep it simple and engaging.',
            'professionals': 'Use professional, concise language. Focus on key insights and actionable information.',
            'academic': 'Use formal, scholarly language. Include technical details and references where appropriate.',
            'business': 'Use business-focused language. Emphasize ROI, benefits, and practical applications.',
            'beginners': 'Use very simple language. Avoid jargon. Include lots of examples and explanations.',
            'advanced': 'Use technical language. Include detailed analysis and advanced concepts.',
            'general': 'Use clear, accessible language suitable for a general audience.'
        }
        
        style_guide = audience_instructions.get(audience_type.lower(), audience_instructions['general'])
        
        # Add theme-specific instructions
        theme_instructions = ""
        if theme:
            theme_configs = {
                "executive": {
                    "focus": "Business impact, high-level strategy, key metrics, ROI",
                    "style": "Concise, executive summary style, bullet points with key numbers",
                    "tone": "Strategic, results-oriented, decision-focused",
                    "layout": "Clean, minimal, emphasis on key takeaways"
                },
                "technical": {
                    "focus": "Methodology, architecture, implementation details, technical specifications",
                    "style": "Detailed, structured, includes technical terminology",
                    "tone": "Precise, analytical, comprehensive",
                    "layout": "Structured sections, technical diagrams, detailed explanations"
                },
                "results": {
                    "focus": "Performance metrics, outcomes, practical applications, visualizations",
                    "style": "Data-driven, metrics-focused, includes charts/graphs emphasis",
                    "tone": "Evidence-based, outcome-focused, practical",
                    "layout": "Metrics-heavy, visual data representation, impact-focused"
                }
            }
            
            if theme in theme_configs:
                config = theme_configs[theme]
                theme_instructions = f"""
THEME: {config['focus']}
THEME STYLE: {config['style']}
THEME TONE: {config['tone']}
THEME LAYOUT: {config['layout']}

Adapt the presentation to match this theme while maintaining accuracy to the source content.
"""
        
        prompt = f"""You are an expert presentation designer. Create {num_slides} well-structured PowerPoint slides based on the following content.

TARGET AUDIENCE: {audience_type}
STYLE GUIDE: {style_guide}
{theme_instructions}
USER REQUEST: {description}

SOURCE CONTENT:
{content_text}

FEW-SHOT EXAMPLES (for reference on structure and style):
{few_shot_examples}

INSTRUCTIONS:
1. Create exactly {num_slides} content slides (plus a title slide)
2. Each slide should have:
   - A clear, concise title
   - Well-organized bullet points or structured content
   - Appropriate amount of text (not too much, not too little)
   - Content that flows logically from one slide to the next
3. Adapt the language and complexity to the {audience_type} audience
4. Focus on the most relevant and important information from the source content
5. Ensure visual balance - distribute content evenly across slides
6. Make it engaging and easy to understand

OUTPUT FORMAT (JSON):
{{
  "title_slide": {{
    "title": "Main Title",
    "subtitle": "Subtitle or description"
  }},
  "slides": [
    {{
      "slide_number": 1,
      "title": "Slide Title",
      "content": [
        "Bullet point 1",
        "Bullet point 2",
        "Bullet point 3"
      ],
      "notes": "Brief notes about this slide"
    }},
    ...
  ]
}}

Generate the slides now. **Your entire response must be ONLY the valid JSON object.**"""
        
        return prompt
    
    def generate_slides(self, retrieval_json_path: str, 
                       num_slides: int = 3,
                       model: str = "gemini-2.5-flash",  # Updated to supported model name
                       theme: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate slides from retrieval output using Gemini API
        
        Args:
            retrieval_json_path: Path to retrieval output JSON file
            num_slides: Number of slides to generate
            model: Gemini model to use (default: gemini-2.5-flash)
            
        Returns:
            Dictionary with generated slides
        """
        if not self.client:
            raise ValueError("Gemini API key not available. Slide generation is disabled.")
        
        # Load retrieval output
        with open(retrieval_json_path, 'r', encoding='utf-8') as f:
            retrieval_data = json.load(f)
        
        metadata = retrieval_data.get('metadata', {}) or {}
        relevant_chunks = retrieval_data.get('relevant_chunks', [])
        description = metadata.get('description', '') or ''
        audience_type = metadata.get('audience_type', 'general') or 'general'
        
        # Ensure audience_type and description are strings
        if not isinstance(audience_type, str):
            audience_type = 'general'
        if not isinstance(description, str):
            description = ''
        
        if not relevant_chunks:
            raise ValueError("No relevant chunks found in retrieval output")
        
        # Build prompt
        try:
            prompt = self._build_prompt(
                relevant_chunks=relevant_chunks,
                description=description,
                audience_type=audience_type,
                num_slides=num_slides,
                theme=theme
            )
            
            if not prompt or not isinstance(prompt, str):
                raise ValueError(f"Invalid prompt generated. Type: {type(prompt)}, Value: {prompt[:100] if prompt else 'None'}")
        except Exception as e:
            raise ValueError(f"Error building prompt: {e}")
        
        # Call Gemini API
        try:
            print(f"Calling Gemini API with model: {model}")
            print(f"Prompt length: {len(prompt)} characters")
            
            # Configure the request to expect JSON output
            # The schema must be complete - arrays need items, objects need properties
            schema_dict = {
                "type": "object",
                "properties": {
                    "title_slide": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "subtitle": {"type": "string"}
                        }
                    },
                    "slides": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "slide_number": {"type": "integer"},
                                "title": {"type": "string"},
                                "content": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "notes": {"type": "string"}
                            }
                        }
                    }
                }
            }
            
            # Try to create config with schema - if Schema class exists, try to use it
            try:
                if hasattr(types, 'Schema'):
                    # Try different ways to create Schema
                    try:
                        # Method 1: Try direct instantiation
                        schema = types.Schema(schema_dict)
                    except:
                        try:
                            # Method 2: Try as keyword args
                            schema = types.Schema(**schema_dict)
                        except:
                            # Method 3: Use dict directly
                            schema = schema_dict
                else:
                    # No Schema class, use dict directly
                    schema = schema_dict
                
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.7,
                )
            except Exception as schema_error:
                print(f"Warning: Could not set response_schema: {schema_error}")
                print("Falling back to JSON mode without schema validation")
                # Fallback: JSON mode without schema
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7,
                )

            # Generate content
            print("Sending request to Gemini API...")
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )
            
            if not response:
                raise ValueError("Gemini API returned None response")
            
            # The response.text should be valid JSON thanks to the config
            if not hasattr(response, 'text') or not response.text:
                raise ValueError(f"Gemini API response has no text attribute. Response type: {type(response)}")
            
            response_text = response.text.strip()
            print(f"Received response from Gemini API (length: {len(response_text)} characters)")
            
            if not response_text:
                raise ValueError("Gemini API returned empty response")
            
            # Parse JSON
            try:
                slides_data = json.loads(response_text)
            except json.JSONDecodeError as json_err:
                print(f"JSON decode error. Response preview: {response_text[:500]}")
                raise ValueError(f"Failed to parse JSON from Gemini response: {json_err}\nResponse preview: {response_text[:500]}")
            
            # Validate the response structure
            if not isinstance(slides_data, dict):
                raise ValueError(f"Expected dict but got {type(slides_data)}")
            
            if 'slides' not in slides_data:
                raise ValueError(f"Response missing 'slides' key. Keys: {slides_data.keys()}")
            
            # Add metadata
            slides_data['metadata'] = {
                'description': description,
                'audience_type': audience_type,
                'num_slides': num_slides,
                'model_used': model,
                'source_retrieval': retrieval_json_path
            }
            
            print(f"Successfully parsed {len(slides_data.get('slides', []))} slides from response")
            return slides_data
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse JSON from Gemini response: {e}"
            if 'response_text' in locals():
                error_msg += f"\nResponse preview: {response_text[:500]}"
            raise ValueError(error_msg)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Exception in generate_slides: {error_details}")
            raise RuntimeError(f"Error calling Gemini API: {e}\nDetails: {error_details}")
    
    def generate_multiple_versions(self, retrieval_json_path: str, 
                                   num_versions: int = 3,
                                   num_slides: int = 3) -> List[Dict[str, Any]]:
        """
        Generate multiple versions of slides for user selection
        """
        versions = []
        
        # Use different models or slight variations for different versions if needed,
        # but for simplicity and consistency with the original code, we just call
        # generate_slides multiple times.
        for i in range(num_versions):
            try:
                print(f"Attempting to generate version {i+1}/{num_versions}...")
                slides = self.generate_slides(
                    retrieval_json_path=retrieval_json_path,
                    num_slides=num_slides,
                    model="gemini-2.5-flash"  # Updated to supported model name
                )
                if slides:
                    slides['version_number'] = i + 1
                    versions.append(slides)
                    print(f"✓ Successfully generated version {i+1}")
                else:
                    print(f"✗ Version {i+1} returned None/empty")
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"✗ Error generating version {i+1}: {str(e)}")
                print(f"Full traceback:\n{error_details}")
                continue
        
        print(f"Generated {len(versions)}/{num_versions} successful versions")
        return versions