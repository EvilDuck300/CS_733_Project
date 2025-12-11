"""
Evaluation Module
Grades slides for clarity, accuracy, visual balance, and audience fit
Uses Gemini API for evaluation
"""

import json
import os
from typing import Dict, Any, List, Optional

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    types = None

# Separate API call counter for evaluation
_EVALUATION_CALL_COUNT = 0
_MAX_EVALUATION_CALLS = 6

def get_evaluation_call_count() -> int:
    """Get current evaluation API call count"""
    global _EVALUATION_CALL_COUNT
    return _EVALUATION_CALL_COUNT

def increment_evaluation_call_count() -> bool:
    """Increment evaluation API call count. Returns True if under limit, False if limit reached."""
    global _EVALUATION_CALL_COUNT
    if _EVALUATION_CALL_COUNT < _MAX_EVALUATION_CALLS:
        _EVALUATION_CALL_COUNT += 1
        return True
    return False

def reset_evaluation_call_count():
    """Reset evaluation API call count (useful for testing or new sessions)"""
    global _EVALUATION_CALL_COUNT
    _EVALUATION_CALL_COUNT = 0


class SlideEvaluator:
    """Evaluate generated slides on multiple criteria using the Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the evaluator
        
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
            print("Warning: Gemini API key not provided. Evaluation will not be available.")
            print("Set GEOGRAPHY_KEY environment variable.")
        else:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("✓ SlideEvaluator initialized with Gemini API")
            except Exception as e:
                self.client = None
                print(f"Warning: Failed to initialize Gemini client: {e}")
    
    def _load_source_content(self, retrieval_json_path: str) -> str:
        """Load source content from retrieval output for accuracy checking"""
        try:
            with open(retrieval_json_path, 'r', encoding='utf-8') as f:
                retrieval_data = json.load(f)
            
            relevant_chunks = retrieval_data.get('relevant_chunks', [])
            source_text = "\n\n".join([chunk.get('text', '') for chunk in relevant_chunks[:5]])
            return source_text
        except Exception as e:
            print(f"Warning: Could not load source content: {e}")
            return ""
    
    
    def evaluate_slides(self, slides_data: Dict[str, Any], 
                        retrieval_json_path: str,
                        description: str,
                        audience_type: str,
                        model: str = "gemini-1.5-pro",
                        max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Evaluate slides on all criteria using the Gemini API
        
        Args:
            slides_data: Dictionary containing generated slides
            retrieval_json_path: Path to retrieval output JSON file
            description: User's description of desired content
            audience_type: Target audience type
            model: Gemini model to use (default: gemini-1.5-pro - free tier available)
            max_tokens: Maximum tokens for the response (default: 2000)
            
        Returns:
            Dictionary with evaluation scores and feedback
        """
        if not self.client or not self.api_key:
            print("Gemini API key not available. Returning default evaluation.")
            return self._default_evaluation()
        
        # Load source content for accuracy checking
        source_content = self._load_source_content(retrieval_json_path)
        
        # Format slides for evaluation
        slides_text = self._format_slides_for_evaluation(slides_data)
        
        # Build evaluation prompt
        prompt = f"""Evaluate the following presentation slides on 4 criteria. Provide scores from 0-100 for each criterion and brief feedback.

TARGET AUDIENCE: {audience_type}
USER REQUEST: {description}

SOURCE CONTENT (for accuracy checking):
{source_content[:2000]}

GENERATED SLIDES:
{slides_text}

EVALUATION CRITERIA:
1. CLARITY (0-100): How clear and understandable is the content?
   - Is the language clear and appropriate?
   - Are concepts explained well?
   - Is the structure logical and easy to follow?
   - Are bullet points concise and well-organized?

2. ACCURACY (0-100): How accurate is the information?
   - Does it match the source content?
   - Are facts correct?
   - Is information not misrepresented?
   - Are there any errors or inconsistencies?

3. VISUAL BALANCE (0-100): How well-balanced is the visual presentation?
   - Is content distributed evenly across slides?
   - Is there appropriate amount of text per slide (not too much, not too little)?
   - Are slides well-structured?
   - Is the layout visually appealing?

4. AUDIENCE FIT (0-100): How well does it match the target audience?
   - Is the language appropriate for {audience_type}?
   - Is the complexity level suitable?
   - Does it address the audience's needs?
   - Is the style appropriate?

OUTPUT FORMAT (JSON only):
{{
  "scores": {{
    "clarity": 85,
    "accuracy": 90,
    "visual_balance": 80,
    "audience_fit": 88
  }},
  "overall_score": 86,
  "feedback": {{
    "clarity": "Clear and well-structured, but could use more examples",
    "accuracy": "Accurate and matches source content well",
    "visual_balance": "Good distribution, but slide 2 has too much text",
    "audience_fit": "Well-suited for the target audience"
  }},
  "strengths": ["Clear structure", "Accurate information"],
  "weaknesses": ["Slide 2 too dense", "Could use more examples"],
  "recommendations": ["Reduce text on slide 2", "Add more visual examples"]
}}

Evaluate now: **Your entire response must be ONLY the valid JSON object.**"""
        
        # Define JSON schema for structured output
        evaluation_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "scores": types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "clarity": types.Schema(type=types.Type.NUMBER),
                        "accuracy": types.Schema(type=types.Type.NUMBER),
                        "visual_balance": types.Schema(type=types.Type.NUMBER),
                        "audience_fit": types.Schema(type=types.Type.NUMBER)
                    },
                    required=["clarity", "accuracy", "visual_balance", "audience_fit"]
                ),
                "overall_score": types.Schema(type=types.Type.NUMBER),
                "feedback": types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "clarity": types.Schema(type=types.Type.STRING),
                        "accuracy": types.Schema(type=types.Type.STRING),
                        "visual_balance": types.Schema(type=types.Type.STRING),
                        "audience_fit": types.Schema(type=types.Type.STRING)
                    },
                    required=["clarity", "accuracy", "visual_balance", "audience_fit"]
                ),
                "strengths": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING)
                ),
                "weaknesses": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING)
                ),
                "recommendations": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING)
                )
            },
            required=["scores", "overall_score", "feedback"]
        )
        
        # Check API call limit before making request
        if not increment_evaluation_call_count():
            print(f"⚠ Evaluation API call limit reached ({_MAX_EVALUATION_CALLS} calls). Using default evaluation.")
            print(f"Current evaluation API call count: {get_evaluation_call_count()}/{_MAX_EVALUATION_CALLS}")
            return self._default_evaluation()
        
        # Call Gemini API
        try:
            print(f"Calling Gemini API for evaluation (model={model}) [Evaluation Call {get_evaluation_call_count()}/{_MAX_EVALUATION_CALLS}]")
            
            config = types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
                response_schema=evaluation_schema
            )
            
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            
            print("✅ Gemini API Evaluation Request Successful!")
            
            # Extract text from response
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                response_text = response.candidates[0].content.parts[0].text
            else:
                print("Error: Unexpected response format from Gemini API")
                return self._default_evaluation()
            
            # Parse JSON response
            try:
                evaluation = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from text if wrapped
                cleaned = response_text.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.strip("`")
                    if cleaned.lower().startswith("json"):
                        cleaned = cleaned[4:].strip()
                if "{" in cleaned and "}" in cleaned:
                    cleaned = cleaned[cleaned.index("{"): cleaned.rindex("}") + 1]
                    evaluation = json.loads(cleaned)
                else:
                    print(f"Error: Could not parse JSON from response: {response_text[:500]}")
                    return self._default_evaluation()
            
            # Ensure all required fields exist
            if 'scores' not in evaluation or not isinstance(evaluation.get('scores'), dict):
                evaluation['scores'] = {}
            if 'feedback' not in evaluation or not isinstance(evaluation.get('feedback'), dict):
                evaluation['feedback'] = {}

            # Normalize numeric fields (avoid over-precision / invalid numbers)
            def normalize_score(val):
                try:
                    num = float(val)
                    if num != num:  # NaN check
                        return 0.0
                    return max(0.0, min(100.0, round(num, 2)))
                except Exception:
                    return 0.0

            scores = evaluation.get('scores', {})
            scores['clarity'] = normalize_score(scores.get('clarity'))
            scores['accuracy'] = normalize_score(scores.get('accuracy'))
            scores['visual_balance'] = normalize_score(scores.get('visual_balance'))
            scores['audience_fit'] = normalize_score(scores.get('audience_fit'))
            evaluation['scores'] = scores

            # Overall score: use provided if valid, else average
            if isinstance(evaluation.get('overall_score'), (int, float)):
                evaluation['overall_score'] = normalize_score(evaluation['overall_score'])
            else:
                numeric_scores = [v for v in scores.values() if isinstance(v, (int, float))]
                evaluation['overall_score'] = round(sum(numeric_scores) / len(numeric_scores), 2) if numeric_scores else 0.0

            # Ensure feedback text exists
            feedback = evaluation.get('feedback', {})
            for key in ['clarity', 'accuracy', 'visual_balance', 'audience_fit']:
                if not isinstance(feedback.get(key), str) or not feedback.get(key):
                    feedback[key] = "Evaluation unavailable"
            evaluation['feedback'] = feedback
            
            # Ensure optional fields exist
            if 'strengths' not in evaluation:
                evaluation['strengths'] = []
            if 'weaknesses' not in evaluation:
                evaluation['weaknesses'] = []
            if 'recommendations' not in evaluation:
                evaluation['recommendations'] = []
            
            return evaluation
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Exception in Gemini evaluate_slides: {error_details}")
            return self._default_evaluation()
    
    def _format_slides_for_evaluation(self, slides_data: Dict[str, Any]) -> str:
        """Format slides data for evaluation prompt"""
        formatted = []
        
        # Title slide
        if 'title_slide' in slides_data:
            title_slide = slides_data['title_slide']
            formatted.append(f"TITLE SLIDE:\nTitle: {title_slide.get('title', 'N/A')}\nSubtitle: {title_slide.get('subtitle', 'N/A')}\n")
        
        # Content slides
        slides = slides_data.get('slides', [])
        for slide in slides:
            slide_num = slide.get('slide_number', '?')
            title = slide.get('title', 'N/A')
            content = slide.get('content', [])
            
            formatted.append(f"\nSLIDE {slide_num}: {title}")
            if isinstance(content, list):
                for item in content:
                    formatted.append(f"  • {item}")
            else:
                formatted.append(f"  {content}")
        
        return "\n".join(formatted)
    
    def _default_evaluation(self) -> Dict[str, Any]:
        """Return default evaluation when API call fails"""
        return {
            "scores": {
                "clarity": 70,
                "accuracy": 70,
                "visual_balance": 70,
                "audience_fit": 70
            },
            "overall_score": 70,
            "feedback": {
                "clarity": "Evaluation unavailable",
                "accuracy": "Evaluation unavailable",
                "visual_balance": "Evaluation unavailable",
                "audience_fit": "Evaluation unavailable"
            },
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
    
    def check_threshold(self, evaluation: Dict[str, Any], threshold: float = 75.0) -> bool:
        """
        Check if evaluation scores meet threshold
        """
        overall_score = evaluation.get('overall_score', 0)
        return overall_score >= threshold
