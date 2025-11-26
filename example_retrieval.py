"""
Example script demonstrating the GNN Retrieval system
Shows how the retrieval system processes PDFs and creates graph structures
"""

from utils.retrieval_gnn import GNNRetrieval
import os

def main():
    print("=" * 60)
    print("GNN Retrieval System Example")
    print("=" * 60)
    print()
    
    # Initialize retrieval system
    print("Initializing GNN Retrieval system...")
    retrieval = GNNRetrieval()
    print()
    
    # Check if there are any PDFs in uploads folder
    uploads_dir = 'uploads'
    pdf_files = [f for f in os.listdir(uploads_dir) if f.endswith('.pdf')] if os.path.exists(uploads_dir) else []
    
    if not pdf_files:
        print("No PDF files found in 'uploads' directory.")
        print("Please upload a PDF through the web interface first.")
        print()
        print("Example usage in code:")
        print("-" * 60)
        print("""
from utils.retrieval_gnn import GNNRetrieval

# Initialize
retrieval = GNNRetrieval()

# Process a PDF
output = retrieval.process_document(
    pdf_path='path/to/document.pdf',
    description='Create slides about computer systems',
    audience_type='students',
    chunk_size=500,
    overlap=50,
    top_k=20
)

# Save to JSON
retrieval.save_to_json(output, 'output.json')
        """)
        return
    
    # Use the first PDF found
    pdf_path = os.path.join(uploads_dir, pdf_files[0])
    print(f"Processing PDF: {pdf_files[0]}")
    print()
    
    # Example processing
    description = "Create slides about the main topics and key concepts"
    audience_type = "students"
    
    print(f"Description: {description}")
    print(f"Audience: {audience_type}")
    print()
    
    try:
        # Process document
        output = retrieval.process_document(
            pdf_path=pdf_path,
            description=description,
            audience_type=audience_type,
            chunk_size=500,
            overlap=50,
            similarity_threshold=0.5,
            top_k=20
        )
        
        print()
        print("=" * 60)
        print("Retrieval Results:")
        print("=" * 60)
        print(f"Total chunks created: {len(output['graph_structure']['nodes'])}")
        print(f"Total edges created: {len(output['graph_structure']['edges'])}")
        print(f"Relevant chunks retrieved: {len(output['relevant_chunks'])}")
        print()
        
        # Show top 3 relevant chunks
        print("Top 3 Most Relevant Chunks:")
        print("-" * 60)
        for i, chunk in enumerate(output['relevant_chunks'][:3], 1):
            print(f"\n{i}. Chunk ID: {chunk['id']}")
            print(f"   Relevance Score: {chunk.get('relevance_score', 0):.4f}")
            print(f"   Word Count: {chunk['word_count']}")
            print(f"   Preview: {chunk['text'][:200]}...")
        
        # Save to JSON
        output_path = 'example_retrieval_output.json'
        retrieval.save_to_json(output, output_path)
        print()
        print(f"Full output saved to: {output_path}")
        
    except Exception as e:
        print(f"Error processing PDF: {e}")
        print("\nMake sure you have installed required dependencies:")
        print("  pip install PyPDF2")
        print("  # Optional for better results:")
        print("  pip install sentence-transformers numpy")

if __name__ == '__main__':
    main()

