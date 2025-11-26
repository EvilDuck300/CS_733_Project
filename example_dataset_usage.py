"""
Example script showing how to use the ppt4web dataset
This demonstrates how the dataset can be used for slide generation
"""

from utils.dataset_loader import get_dataset

def main():
    # Load the dataset
    dataset = get_dataset()
    
    # Get dataset statistics
    stats = dataset.get_statistics()
    print("Dataset Statistics:")
    print(f"  Total presentations: {stats['total_presentations']}")
    print(f"  Average text length: {stats['average_text_length']:.0f} characters")
    print()
    
    # Example 1: Get examples by keywords (for slide generation)
    print("Example 1: Finding presentations about 'computers'")
    computer_examples = dataset.get_examples_by_keywords(['computer', 'technology'], limit=3)
    for i, example in enumerate(computer_examples, 1):
        print(f"  {i}. {example.get('title', 'N/A')[:60]}...")
    print()
    
    # Example 2: Get examples by audience type
    print("Example 2: Finding presentations for 'students' audience")
    student_examples = dataset.get_examples_by_audience('students', limit=3)
    for i, example in enumerate(student_examples, 1):
        print(f"  {i}. {example.get('title', 'N/A')[:60]}...")
    print()
    
    # Example 3: Get few-shot examples for AI prompt
    print("Example 3: Generating few-shot examples for slide generation")
    description = "Create slides about computer systems and hardware"
    audience = "students"
    few_shot = dataset.get_few_shot_examples(description, audience, num_examples=2)
    print(few_shot)
    print()
    
    # Example 4: Show how this would be used in slide generation
    print("Example 4: How to use in slide generation prompt")
    print("=" * 60)
    print("PROMPT FOR CHATGPT:")
    print("-" * 60)
    print(f"Generate presentation slides for: {description}")
    print(f"Target audience: {audience}")
    print("\nHere are some example presentations to guide the format:")
    print(few_shot)
    print("=" * 60)

if __name__ == '__main__':
    main()

