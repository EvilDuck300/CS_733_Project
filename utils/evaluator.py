"""
Evaluation Module
Grades slides for clarity, accuracy, visual balance, and audience fit
"""

import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI


class SlideEvaluator:
    """Evaluate generated slides on multiple criteria"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the evaluator
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
    
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
                        audience_type: str) -> Dict[str, Any]:
        """
        Evaluate slides on all criteria
        
        Args:
            slides_data: Generated slides dictionary
            retrieval_json_path: Path to retrieval output for accuracy checking
            description: Original user description
            audience_type: Target audience
            
        Returns:
            Dictionary with scores and feedback
        """
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

Evaluate now:"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert presentation evaluator. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            evaluation = json.loads(response_text)
            
            # Ensure all required fields exist
            if 'scores' not in evaluation:
                evaluation['scores'] = {}
            if 'overall_score' not in evaluation:
                scores = evaluation.get('scores', {})
                evaluation['overall_score'] = sum(scores.values()) / len(scores) if scores else 0
            
            return evaluation
            
        except json.JSONDecodeError as e:
            print(f"Error parsing evaluation JSON: {e}")
            # Return default evaluation
            return self._default_evaluation()
        except Exception as e:
            print(f"Error in evaluation: {e}")
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
        
        Args:
            evaluation: Evaluation dictionary
            threshold: Minimum overall score required
            
        Returns:
            True if scores meet threshold, False otherwise
        """
        overall_score = evaluation.get('overall_score', 0)
        return overall_score >= threshold

