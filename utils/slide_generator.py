"""
Slide Generation Module with Gemini API Integration
Generates intelligent, well-formatted slides from retrieval output
"""

import json
import os
import time
from typing import List, Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    types = None

from utils.dataset_loader import get_dataset

# Separate API call counters for slide generation and evaluation
_SLIDE_GENERATION_CALL_COUNT = 0
_MAX_SLIDE_GENERATION_CALLS = 6

def get_slide_generation_call_count() -> int:
    """Get current slide generation API call count"""
    global _SLIDE_GENERATION_CALL_COUNT
    return _SLIDE_GENERATION_CALL_COUNT

def increment_slide_generation_call_count() -> bool:
    """Increment slide generation API call count. Returns True if under limit, False if limit reached."""
    global _SLIDE_GENERATION_CALL_COUNT
    if _SLIDE_GENERATION_CALL_COUNT < _MAX_SLIDE_GENERATION_CALLS:
        _SLIDE_GENERATION_CALL_COUNT += 1
        return True
    return False

def reset_slide_generation_call_count():
    """Reset slide generation API call count (useful for testing or new sessions)"""
    global _SLIDE_GENERATION_CALL_COUNT
    _SLIDE_GENERATION_CALL_COUNT = 0


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
            print("Warning: google-genai package not installed. Install with: pip install google-genai")
            return
        
        # Use Gemini API. Check environment variable GEOGRAPHY_KEY
        self.api_key = api_key or os.getenv('GEOGRAPHY_KEY')
        if not self.api_key:
            self.client = None
            print("Warning: Gemini API key not provided. Slide generation will not be available.")
            print("Set GEOGRAPHY_KEY environment variable.")
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("✓ SlideGenerator initialized with Gemini API")
            except Exception as e:
                self.client = None
                print(f"Warning: Failed to initialize Gemini client: {e}")
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
    
    def _create_fallback_slides(self, description: str, audience_type: str, num_slides: int, retrieval_json_path: str = None) -> Dict[str, Any]:
        """Create a basic slide structure when API returns task object without content"""
        # Try to load retrieval data to create better slides
        relevant_chunks = []
        if retrieval_json_path and os.path.exists(retrieval_json_path):
            try:
                with open(retrieval_json_path, 'r', encoding='utf-8') as f:
                    retrieval_data = json.load(f)
                    relevant_chunks = retrieval_data.get('relevant_chunks', [])[:num_slides * 5]  # Get more chunks for better content
            except Exception as e:
                print(f"Warning: Could not load retrieval data for fallback slides: {e}")
        
        # Create slides from relevant chunks
        slides = []
        
        if relevant_chunks:
            chunks_per_slide = max(1, len(relevant_chunks) // num_slides)
            
            for i in range(num_slides):
                start_idx = i * chunks_per_slide
                end_idx = (i + 1) * chunks_per_slide if i < num_slides - 1 else len(relevant_chunks)
                slide_chunks = relevant_chunks[start_idx:end_idx]
                
                if slide_chunks:
                    # Extract key points from chunks
                    content_points = []
                    for chunk in slide_chunks[:4]:  # Use top 4 chunks per slide
                        text = chunk.get('text', '').strip()
                        if not text:
                            continue
                        
                        # Extract meaningful sentences (not too short, not too long)
                        sentences = [s.strip() for s in text.split('.') if s.strip()]
                        for sentence in sentences[:2]:  # Max 2 sentences per chunk
                            if 15 <= len(sentence) <= 200:  # Reasonable length
                                content_points.append(sentence)
                                if len(content_points) >= 5:  # Max 5 points per slide
                                    break
                        if len(content_points) >= 5:
                            break
                    
                    # Create title from first chunk
                    first_chunk_text = slide_chunks[0].get('text', '')
                    title = first_chunk_text.split('.')[0].strip()[:60] if first_chunk_text else f"Key Point {i + 1}"
                    if not title or len(title) < 10:
                        # Try to extract a better title
                        words = first_chunk_text.split()[:8]
                        title = ' '.join(words) if words else f"Slide {i + 1}"
                    
                    if not content_points:
                        content_points = [first_chunk_text[:200] + "..." if len(first_chunk_text) > 200 else first_chunk_text]
                else:
                    title = f"Slide {i + 1}"
                    content_points = [f"Content based on: {description}"]
                
                slides.append({
                    "slide_number": i + 1,
                    "title": title,
                    "content": content_points if content_points else [f"Key information for slide {i + 1}"],
                    "notes": f"Generated from retrieval data - Slide {i + 1}"
                })
        else:
            # No retrieval data, create basic structure
            for i in range(num_slides):
                slides.append({
                    "slide_number": i + 1,
                    "title": f"Slide {i + 1}: {description[:40] if description else 'Presentation Topic'}",
                    "content": [
                        f"Key point {i + 1}",
                        f"Based on: {description}",
                        f"Audience: {audience_type}"
                    ],
                    "notes": f"Fallback slide {i + 1} - API task polling unavailable"
                })
        
        return {
            "title_slide": {
                "title": description or "Presentation",
                "subtitle": f"For {audience_type} audience"
            },
            "slides": slides,
            "metadata": {
                "generation_method": "fallback_from_retrieval",
                "note": "Slides generated from retrieval data as Gemini API was unavailable"
            }
        }
    
    
    def generate_slides(self, retrieval_json_path: str, 
                       num_slides: int = 3,
                       model: str = "gemini-1.5-pro",
                       theme: Optional[str] = None,
                       max_tokens: int = 4000) -> Dict[str, Any]:
        """
        Generate slides from retrieval output using Gemini API
        
        Args:
            retrieval_json_path: Path to retrieval output JSON file
            num_slides: Number of slides to generate
            model: Gemini model to use (default: gemini-1.5-pro - free tier available)
            theme: Optional theme for slide generation
            max_tokens: Maximum tokens for the response (default: 4000)
            
        Returns:
            Dictionary with generated slides
        """
        if not self.client or not self.api_key:
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
        
        # Define JSON schema for structured output
        slides_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "title_slide": types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "title": types.Schema(type=types.Type.STRING),
                        "subtitle": types.Schema(type=types.Type.STRING)
                    },
                    required=["title", "subtitle"]
                ),
                "slides": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(
                        type=types.Type.OBJECT,
                        properties={
                            "slide_number": types.Schema(type=types.Type.INTEGER),
                            "title": types.Schema(type=types.Type.STRING),
                            "content": types.Schema(
                                type=types.Type.ARRAY,
                                items=types.Schema(type=types.Type.STRING)
                            ),
                            "notes": types.Schema(type=types.Type.STRING)
                        },
                        required=["slide_number", "title", "content"]
                    )
                )
            },
            required=["title_slide", "slides"]
        )
        
        # Check API call limit before making request
        if not increment_slide_generation_call_count():
            print(f"⚠ Slide generation API call limit reached ({_MAX_SLIDE_GENERATION_CALLS} calls). Using fallback slides.")
            print(f"Current slide generation API call count: {get_slide_generation_call_count()}/{_MAX_SLIDE_GENERATION_CALLS}")
            slides_data = self._create_fallback_slides(description, audience_type, num_slides, retrieval_json_path)
            slides_data['metadata'].update({
                'description': description,
                'audience_type': audience_type,
                'num_slides': num_slides,
                'model_used': model,
                'source_retrieval': retrieval_json_path,
                'api_limit_reached': True,
                'note': f'Fallback used - Slide generation API call limit ({_MAX_SLIDE_GENERATION_CALLS}) reached'
            })
            return slides_data
        
        # Call Gemini API
        try:
            print(f"Calling Gemini API for slide generation (model={model}) [Slide Gen Call {get_slide_generation_call_count()}/{_MAX_SLIDE_GENERATION_CALLS}]")
            
            config = types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
                response_schema=slides_schema
            )
            
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            
            print("✅ Gemini API Request Successful!")
            
            # Extract text from response
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                response_text = response.candidates[0].content.parts[0].text
            else:
                raise ValueError("Unexpected response format from Gemini API")
            
            # Parse JSON response
            try:
                slides_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from text if wrapped
                cleaned = response_text.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.strip("`")
                    if cleaned.lower().startswith("json"):
                        cleaned = cleaned[4:].strip()
                if "{" in cleaned and "}" in cleaned:
                    cleaned = cleaned[cleaned.index("{"): cleaned.rindex("}") + 1]
                    slides_data = json.loads(cleaned)
                else:
                    raise ValueError(f"Could not parse JSON from response: {response_text[:500]}")
            
            # Validate structure
            if not isinstance(slides_data, dict):
                raise ValueError(f"Expected dict from Gemini but got {type(slides_data)}")
            
            if 'title_slide' not in slides_data or 'slides' not in slides_data:
                print("⚠ Warning: Response does not contain expected slide structure. Using fallback.")
                slides_data = self._create_fallback_slides(description, audience_type, num_slides, retrieval_json_path)
            
            # Add metadata
            slides_data.setdefault('metadata', {})
            slides_data['metadata'].update({
                'description': description,
                'audience_type': audience_type,
                'num_slides': num_slides,
                'model_used': model,
                'source_retrieval': retrieval_json_path
            })
            
            print(f"Successfully processed slides from Gemini (keys: {list(slides_data.keys())})")
            return slides_data
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Exception in Gemini generate_slides: {error_details}")
            # Use fallback on error
            print("⚠ Using fallback slides due to API error")
            slides_data = self._create_fallback_slides(description, audience_type, num_slides, retrieval_json_path)
            slides_data['metadata'].update({
                'description': description,
                'audience_type': audience_type,
                'num_slides': num_slides,
                'model_used': model,
                'source_retrieval': retrieval_json_path,
                'error': str(e)
            })
            return slides_data
    
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
                # Add delay between requests to avoid rate limits (free tier: ~15 requests/minute)
                if i > 0:
                    delay_seconds = 5  # Wait 5 seconds between requests
                    print(f"Waiting {delay_seconds} seconds before next request to avoid rate limits...")
                    time.sleep(delay_seconds)
                
                print(f"Attempting to generate version {i+1}/{num_versions}...")
                slides = self.generate_slides(
                    retrieval_json_path=retrieval_json_path,
                    num_slides=num_slides,
                    model="gemini-1.5-pro"
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
                # If rate limited, wait longer before retrying
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    print("Rate limit hit. Waiting 20 seconds before continuing...")
                    time.sleep(20)
                continue
        
        print(f"Generated {len(versions)}/{num_versions} successful versions")
        return versions