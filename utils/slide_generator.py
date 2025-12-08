"""
Slide Generation Module with ChatGPT 4o Integration
Generates intelligent, well-formatted slides from retrieval output
"""

import json
import os
from typing import List, Dict, Any, Optional

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

from utils.dataset_loader import get_dataset


class SlideGenerator:
    """Generate slides using ChatGPT 4o with few-shot learning from dataset"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the slide generator
        
        Args:
            api_key: OpenAI API key (if None, will try to get from environment)
                    If not provided, slide generation will not be available
        """
        if not OPENAI_AVAILABLE:
            self.client = None
            self.api_key = None
            print("Warning: OpenAI package not installed. Slide generation will not be available.")
            print("You can upload the JSON retrieval output to Gemini website to generate PowerPoint.")
            return
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            self.client = None
            print("Warning: OpenAI API key not provided. Slide generation will not be available.")
            print("You can upload the JSON retrieval output to Gemini website to generate PowerPoint.")
        else:
            self.client = OpenAI(api_key=self.api_key)
        self.dataset = get_dataset()
    
    def _build_prompt(self, relevant_chunks: List[Dict[str, Any]], 
                     description: str, audience_type: str, 
                     num_slides: int = 3) -> str:
        """
        Build the prompt for ChatGPT 4o
        
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
        
        prompt = f"""You are an expert presentation designer. Create {num_slides} well-structured PowerPoint slides based on the following content.

TARGET AUDIENCE: {audience_type}
STYLE GUIDE: {style_guide}

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

Generate the slides now:"""
        
        return prompt
    
    def generate_slides(self, retrieval_json_path: str, 
                       num_slides: int = 3,
                       model: str = "gpt-4o") -> Dict[str, Any]:
        """
        Generate slides from retrieval output using ChatGPT 4o
        
        Args:
            retrieval_json_path: Path to retrieval output JSON file
            num_slides: Number of slides to generate
            model: OpenAI model to use (default: gpt-4o)
            
        Returns:
            Dictionary with generated slides
        """
        if not self.client:
            raise ValueError("OpenAI API key not available. Please upload the JSON retrieval output to Gemini website to generate PowerPoint.")
        
        # Load retrieval output
        with open(retrieval_json_path, 'r', encoding='utf-8') as f:
            retrieval_data = json.load(f)
        
        metadata = retrieval_data.get('metadata', {})
        relevant_chunks = retrieval_data.get('relevant_chunks', [])
        description = metadata.get('description', '')
        audience_type = metadata.get('audience_type', 'general')
        
        if not relevant_chunks:
            raise ValueError("No relevant chunks found in retrieval output")
        
        # Build prompt
        prompt = self._build_prompt(
            relevant_chunks=relevant_chunks,
            description=description,
            audience_type=audience_type,
            num_slides=num_slides
        )
        
        # Call ChatGPT 4o
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert presentation designer. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=3000
            )
            
            # Extract JSON from response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON if wrapped in markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            slides_data = json.loads(response_text)
            
            # Add metadata
            slides_data['metadata'] = {
                'description': description,
                'audience_type': audience_type,
                'num_slides': num_slides,
                'model_used': model,
                'source_retrieval': retrieval_json_path
            }
            
            return slides_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from ChatGPT response: {e}\nResponse: {response_text[:500]}")
        except Exception as e:
            raise RuntimeError(f"Error calling OpenAI API: {e}")
    
    def generate_multiple_versions(self, retrieval_json_path: str, 
                                   num_versions: int = 3,
                                   num_slides: int = 3) -> List[Dict[str, Any]]:
        """
        Generate multiple versions of slides for user selection
        
        Args:
            retrieval_json_path: Path to retrieval output JSON file
            num_versions: Number of different versions to generate
            num_slides: Number of slides per version
            
        Returns:
            List of slide dictionaries (one per version)
        """
        versions = []
        
        for i in range(num_versions):
            try:
                # Generate with slight variation by adjusting temperature
                slides = self.generate_slides(
                    retrieval_json_path=retrieval_json_path,
                    num_slides=num_slides,
                    model="gpt-4o"
                )
                slides['version_number'] = i + 1
                versions.append(slides)
            except Exception as e:
                print(f"Error generating version {i+1}: {e}")
                continue
        
        return versions

