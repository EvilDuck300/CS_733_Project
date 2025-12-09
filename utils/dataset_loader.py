"""
Utility module for loading and using the ppt4web dataset
This dataset can be used for:
1. Providing examples to the slide generation model
2. Evaluating generated slides against real presentations
3. Understanding presentation structure and formatting
"""

import json
import os
from typing import List, Dict, Any, Optional


class PresentationDataset:
    """Loader and utility class for the ppt4web presentation dataset"""
    
    def __init__(self, jsonl_path: str = 'ppt4web_01.jsonl/ppt4web_01.jsonl'):
        """
        Initialize the dataset loader
        
        Args:
            jsonl_path: Path to the JSONL file
        """
        self.jsonl_path = jsonl_path
        self.presentations: List[Dict[str, Any]] = []
        self._load_dataset()
    
    def _load_dataset(self):
        """Load all presentations from the JSONL file"""
        if not os.path.exists(self.jsonl_path):
            print(f"Warning: Dataset file not found at {self.jsonl_path}")
            return
        
        try:
            with open(self.jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            presentation = json.loads(line)
                            self.presentations.append(presentation)
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON line: {e}")
                            continue
            
            print(f"Loaded {len(self.presentations)} presentations from dataset")
        except Exception as e:
            print(f"Error loading dataset: {e}")
    
    def get_examples_by_keywords(self, keywords: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get presentation examples that contain specific keywords
        
        Args:
            keywords: List of keywords to search for
            limit: Maximum number of examples to return
            
        Returns:
            List of matching presentations
        """
        if not self.presentations:
            return []
        
        keywords_lower = [kw.lower() for kw in keywords]
        matches = []
        
        for presentation in self.presentations:
            # Handle None values - .get() only returns default if key doesn't exist, not if value is None
            text = presentation.get('text') or ''
            title = presentation.get('title') or ''
            # Ensure they are strings before calling .lower()
            if not isinstance(text, str):
                text = str(text) if text is not None else ''
            if not isinstance(title, str):
                title = str(title) if title is not None else ''
            text = text.lower()
            title = title.lower()
            
            # Count keyword matches
            match_count = sum(1 for kw in keywords_lower if kw in text or kw in title)
            
            if match_count > 0:
                matches.append({
                    'presentation': presentation,
                    'match_score': match_count
                })
        
        # Sort by match score and return top results
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return [m['presentation'] for m in matches[:limit]]
    
    def get_examples_by_audience(self, audience_type: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get presentation examples that might be suitable for a specific audience
        
        Args:
            audience_type: Type of audience (students, professionals, etc.)
            limit: Maximum number of examples to return
            
        Returns:
            List of matching presentations
        """
        if not self.presentations:
            return []
        
        # Map audience types to relevant keywords
        audience_keywords = {
            'students': ['lesson', 'student', 'learn', 'education', 'class', 'course'],
            'professionals': ['business', 'corporate', 'professional', 'industry', 'work'],
            'academic': ['research', 'academic', 'study', 'paper', 'thesis', 'scholar'],
            'beginners': ['introduction', 'basic', 'beginner', 'first', 'start', 'learn'],
            'advanced': ['advanced', 'expert', 'complex', 'detailed', 'deep']
        }
        
        # Ensure audience_type is not None and is a string
        if not audience_type or not isinstance(audience_type, str):
            audience_type = 'general'
        keywords = audience_keywords.get(audience_type.lower(), [])
        return self.get_examples_by_keywords(keywords, limit)
    
    def get_random_examples(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get random presentation examples
        
        Args:
            limit: Number of examples to return
            
        Returns:
            List of random presentations
        """
        import random
        if not self.presentations:
            return []
        
        return random.sample(self.presentations, min(limit, len(self.presentations)))
    
    def get_example_slides_text(self, presentation: Dict[str, Any]) -> str:
        """
        Extract and format slide text from a presentation for use as examples
        
        Args:
            presentation: Presentation dictionary from dataset
            
        Returns:
            Formatted text suitable for use as examples in prompts
        """
        # Handle None values - .get() only returns default if key doesn't exist, not if value is None
        text = presentation.get('text') or ''
        title = presentation.get('title') or ''
        # Ensure they are strings
        if not isinstance(text, str):
            text = str(text) if text is not None else ''
        if not isinstance(title, str):
            title = str(title) if title is not None else ''
        
        # Format for use in prompts
        formatted = f"Example Presentation: {title}\n\n"
        formatted += f"Content:\n{text[:1000]}..."  # Limit length
        
        return formatted
    
    def get_few_shot_examples(self, description: str, audience_type: str, num_examples: int = 3) -> str:
        """
        Get formatted few-shot examples for use in slide generation prompts
        
        Args:
            description: User's description of desired presentation
            audience_type: Target audience type
            num_examples: Number of examples to include
            
        Returns:
            Formatted string with examples for use in AI prompts
        """
        # Extract keywords from description
        # Ensure description is not None and is a string
        if not description or not isinstance(description, str):
            description = ''
        keywords = description.lower().split()[:10]  # Top 10 words
        
        # Get relevant examples
        examples = self.get_examples_by_keywords(keywords, limit=num_examples)
        
        # If not enough keyword matches, supplement with audience-based examples
        if len(examples) < num_examples:
            audience_examples = self.get_examples_by_audience(audience_type, limit=num_examples - len(examples))
            examples.extend(audience_examples)
        
        # Format examples
        formatted_examples = []
        for i, example in enumerate(examples[:num_examples], 1):
            formatted_examples.append(
                f"Example {i}:\n"
                f"Title: {example.get('title', 'N/A')}\n"
                f"Content Preview: {example.get('text', '')[:500]}...\n"
            )
        
        return "\n".join(formatted_examples)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the dataset
        
        Returns:
            Dictionary with dataset statistics
        """
        if not self.presentations:
            return {
                'total_presentations': 0,
                'average_text_length': 0
            }
        
        text_lengths = [len(p.get('text', '')) for p in self.presentations]
        
        return {
            'total_presentations': len(self.presentations),
            'average_text_length': sum(text_lengths) / len(text_lengths) if text_lengths else 0,
            'min_text_length': min(text_lengths) if text_lengths else 0,
            'max_text_length': max(text_lengths) if text_lengths else 0
        }


# Global dataset instance (lazy loading)
_dataset_instance: Optional[PresentationDataset] = None


def get_dataset() -> PresentationDataset:
    """Get or create the global dataset instance"""
    global _dataset_instance
    if _dataset_instance is None:
        _dataset_instance = PresentationDataset()
    return _dataset_instance

