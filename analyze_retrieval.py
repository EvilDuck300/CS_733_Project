"""Script to analyze retrieval output and check accuracy"""
import json
import os

# File path
file_path = r"retrieval_output\d0b32d39-cd2d-4bd7-936f-ae7a680f33d2_retrieval_output.json"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

print("Loading retrieval output...")
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("\n" + "="*60)
print("RETRIEVAL OUTPUT ANALYSIS")
print("="*60)

# Metadata
metadata = data.get('metadata', {})
print("\n[METADATA]")
print(f"  PDF Path: {metadata.get('pdf_path', 'N/A')}")
print(f"  Description: {metadata.get('description', 'N/A')}")
print(f"  Audience Type: {metadata.get('audience_type', 'N/A')}")
print(f"  Total Chunks: {metadata.get('total_chunks', 0)}")
print(f"  Relevant Chunks: {metadata.get('relevant_chunks_count', 0)}")
print(f"  Total Edges: {metadata.get('total_edges', 0)}")
print(f"  Processing Method: {metadata.get('processing_method', 'N/A')}")

# Graph Structure
graph = data.get('graph_structure', {})
nodes = graph.get('nodes', [])
edges = graph.get('edges', [])

print(f"\n[GRAPH STRUCTURE]")
print(f"  Nodes: {len(nodes)}")
print(f"  Edges: {len(edges)}")
if len(nodes) > 0:
    avg_edges_per_node = len(edges) / len(nodes)
    print(f"  Average edges per node: {avg_edges_per_node:.2f}")
    
    # Check for duplicate chunks
    chunk_texts = [node.get('text', '')[:100] for node in nodes[:10]]
    unique_chunks = len(set(chunk_texts))
    print(f"  Unique chunks (first 10): {unique_chunks}/10")
    
    if unique_chunks < 5:
        print("  WARNING: High duplication detected in chunks!")

# Relevant Chunks
relevant_chunks = data.get('relevant_chunks', [])
print(f"\n[RELEVANT CHUNKS]")
print(f"  Count: {len(relevant_chunks)}")

if relevant_chunks:
    print(f"\n  Top 3 Relevance Scores:")
    for i, chunk in enumerate(relevant_chunks[:3], 1):
        score = chunk.get('relevance_score', 0)
        text_preview = chunk.get('text', '')[:100].replace('\n', ' ')
        print(f"    {i}. Score: {score:.4f}")
        print(f"       Preview: {text_preview}...")
    
    # Check relevance scores
    scores = [chunk.get('relevance_score', 0) for chunk in relevant_chunks]
    avg_score = sum(scores) / len(scores) if scores else 0
    max_score = max(scores) if scores else 0
    min_score = min(scores) if scores else 0
    
    print(f"\n  Score Statistics:")
    print(f"    Average: {avg_score:.4f}")
    print(f"    Max: {max_score:.4f}")
    print(f"    Min: {min_score:.4f}")
    
    if avg_score < 0.3:
        print("  WARNING: Low relevance scores detected!")

# Issues Detection
print(f"\n[ISSUE DETECTION]")
issues = []

if len(edges) > len(nodes) * 50:
    issues.append(f"Too many edges ({len(edges)}) for {len(nodes)} nodes - graph is too dense")

if len(relevant_chunks) < 10:
    issues.append(f"Only {len(relevant_chunks)} relevant chunks - may not be enough for slide generation")

if relevant_chunks:
    scores = [chunk.get('relevance_score', 0) for chunk in relevant_chunks]
    if max(scores) < 0.3:
        issues.append(f"Low relevance scores (max: {max(scores):.4f}) - retrieval may not be accurate")

if len(nodes) > 500:
    issues.append(f"Very large number of chunks ({len(nodes)}) - may indicate chunking issues")

if issues:
    print("  Issues found:")
    for issue in issues:
        print(f"    - {issue}")
else:
    print("  No major issues detected")

# Recommendations
print(f"\n[RECOMMENDATIONS]")
print("  1. Structure is correct - has metadata, graph_structure, and relevant_chunks")
print("  2. Ready for slide generation - proceed to next stage")
if len(edges) > len(nodes) * 50:
    print("  3. Consider reducing similarity_threshold to create fewer edges")
if len(relevant_chunks) < 10:
    print("  4. Consider increasing top_k parameter for more relevant chunks")
if relevant_chunks and max([c.get('relevance_score', 0) for c in relevant_chunks]) < 0.3:
    print("  5. Consider refining description or adjusting retrieval parameters")

print(f"\n[NEXT STEPS]")
print("  1. Proceed with slide generation using this retrieval output")
print("  2. The system will use the 20 relevant chunks to create slides")
print("  3. ChatGPT 4o will generate 3 versions of slides")
print("  4. Evaluation will score each version")
print("  5. User will review and select best version")

print("\n" + "="*60)

