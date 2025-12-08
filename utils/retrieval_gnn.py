"""
GNN-based Retrieval System
Decomposes PDF documents into relevant nodes (chunks) and creates a graph structure
Returns JSON file containing relevant chunks for slide generation
"""

import json
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import fitz  # PyMuPDF
    PDF_IMAGE_LIB = 'pymupdf'
except ImportError:
    PDF_IMAGE_LIB = None
    print("Warning: PyMuPDF not available. Image extraction disabled.")

# PDF processing imports with fallbacks
try:
    import PyPDF2
    PDF_LIBRARY = 'PyPDF2'
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY = 'pdfplumber'
    except ImportError:
        PDF_LIBRARY = None
        print("Warning: No PDF library found. Install PyPDF2 or pdfplumber for PDF processing.")

# Embedding imports (for semantic similarity) - optional
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    np = None
    print("Warning: sentence-transformers not available. Using basic keyword matching.")


class GNNRetrieval:
    """GNN-based retrieval system for document processing"""
    
    def __init__(self, embedding_model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the retrieval system
        
        Args:
            embedding_model_name: Name of the sentence transformer model to use
        """
        self.embedding_model = None
        self.embedding_available = EMBEDDING_AVAILABLE
        
        if self.embedding_available:
            try:
                self.embedding_model = SentenceTransformer(embedding_model_name)
                print(f"Embedding model '{embedding_model_name}' loaded successfully")
            except Exception as e:
                print(f"Warning: Could not load embedding model: {e}")
                self.embedding_available = False
    
    def extract_images_from_pdf(self, pdf_path: str, images_dir: str) -> List[Dict[str, Any]]:
        """
        Extract images from the PDF and save them to images_dir.
        Returns a list of {id, page, path, bbox?, caption?} dicts.
        """
        if PDF_LIBRARY is None:
            print("[WARN] No PDF library for image extraction. Skipping images.")
            return []

        os.makedirs(images_dir, exist_ok=True)
        images_meta = []

        if PDF_LIBRARY == 'pdfplumber':
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    # pdfplumber gives you page.images with bbox info
                    for img_idx, img_obj in enumerate(page.images):
                        # bounding box in PDF coordinates
                        x0 = img_obj["x0"]
                        top = img_obj["top"]
                        x1 = img_obj["x1"]
                        bottom = img_obj["bottom"]

                        # crop & save
                        bbox = (x0, top, x1, bottom)
                        page_img = page.crop(bbox).to_image(resolution=150)

                        img_filename = f"page{page_idx+1}_img{img_idx+1}.png"
                        img_path = os.path.join(images_dir, img_filename)
                        page_img.save(img_path, format="PNG")

                        images_meta.append({
                            "id": f"page{page_idx+1}_img{img_idx+1}",
                            "page": page_idx + 1,
                            "path": img_path.replace("\\", "/"),
                            "bbox": [x0, top, x1, bottom],
                            # optional placeholder; you can improve this by scanning
                            # nearby text for "Figure 1:" etc.
                            "caption": ""
                        })

        elif PDF_LIBRARY == 'PyPDF2':
            # PyPDF2 image extraction is more painful; you can leave this as a TODO
            print("[WARN] Image extraction with PyPDF2 not implemented yet.")
            return []

        return images_meta
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        if PDF_LIBRARY is None:
            raise ImportError("No PDF library available. Please install PyPDF2 or pdfplumber.")
        
        text = ""
        
        if PDF_LIBRARY == 'PyPDF2':
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                print(f"Error extracting text with PyPDF2: {e}")
                raise
        
        elif PDF_LIBRARY == 'pdfplumber':
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                print(f"Error extracting text with pdfplumber: {e}")
                raise
        
        return text
    
    def chunk_document(self, text: str, chunk_size: int = 500, overlap: int = 3) -> List[Dict[str, Any]]:
        """
        Break down document into chunks (nodes for GNN)
        Each chunk becomes a node in the graph
        
        Args:
            text: Document text to chunk
            chunk_size: Target number of words per chunk
            overlap: Number of words to overlap between chunks
            
        Returns:
            List of chunk dictionaries (nodes)
        """
        # Clean and split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return []
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    'id': len(chunks),
                    'text': chunk_text,
                    'word_count': current_length,
                    'char_count': len(chunk_text),
                    'start_sentence': len(chunks) == 0,
                    'end_sentence': False
                })
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s.split()) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                'id': len(chunks),
                'text': chunk_text,
                'word_count': current_length,
                'char_count': len(chunk_text),
                'start_sentence': len(chunks) == 0,
                'end_sentence': True
            })
        
        return chunks
    
    def create_graph_edges(self, chunks: List[Dict[str, Any]], 
                           similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Create edges between chunks based on semantic similarity (GNN structure)
        This simulates a Graph Neural Network where chunks are nodes and edges represent relationships
        
        Args:
            chunks: List of chunk dictionaries (nodes)
            similarity_threshold: Minimum similarity score to create an edge
            
        Returns:
            List of edge dictionaries
        """
        edges = []
        
        if self.embedding_available and self.embedding_model and np is not None:
            # Use embeddings for semantic similarity
            texts = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
            
            # Calculate cosine similarity between chunks
            for i in range(len(chunks)):
                for j in range(i + 1, len(chunks)):
                    # Cosine similarity
                    dot_product = np.dot(embeddings[i], embeddings[j])
                    norm_i = np.linalg.norm(embeddings[i])
                    norm_j = np.linalg.norm(embeddings[j])
                    
                    if norm_i > 0 and norm_j > 0:
                        similarity = dot_product / (norm_i * norm_j)
                        
                        if similarity > similarity_threshold:
                            edges.append({
                                'source': chunks[i]['id'],
                                'target': chunks[j]['id'],
                                'weight': float(similarity),
                                'type': 'semantic_similarity'
                            })
        else:
            # Fallback: Create edges based on sequential proximity and keyword overlap
            for i in range(len(chunks)):
                # Connect adjacent chunks
                if i < len(chunks) - 1:
                    edges.append({
                        'source': chunks[i]['id'],
                        'target': chunks[i + 1]['id'],
                        'weight': 0.8,
                        'type': 'sequential'
                    })
                
                # Connect chunks with keyword overlap
                words_i = set(chunks[i]['text'].lower().split())
                for j in range(i + 1, min(i + 3, len(chunks))):
                    words_j = set(chunks[j]['text'].lower().split())
                    overlap = len(words_i & words_j) / max(len(words_i | words_j), 1)
                    if overlap > 0.2:
                        edges.append({
                            'source': chunks[i]['id'],
                            'target': chunks[j]['id'],
                            'weight': float(overlap),
                            'type': 'keyword_overlap'
                        })
        
        return edges
    
    def retrieve_relevant_chunks(self, chunks: List[Dict[str, Any]], 
                                 description: str, 
                                 audience_type: str,
                                 top_k: int = 20) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant chunks based on user description and audience type
        Uses GNN-like approach with semantic similarity
        
        Args:
            chunks: List of all chunks (nodes)
            description: User's description of desired content
            audience_type: Target audience type
            top_k: Number of top chunks to return
            
        Returns:
            List of relevant chunks with relevance scores
        """
        if not chunks:
            return []
        
        if self.embedding_available and self.embedding_model and np is not None:
            # Use embeddings for semantic search
            query_text = f"{description} Audience: {audience_type}"
            query_embedding = self.embedding_model.encode([query_text])[0]
            
            chunk_texts = [chunk['text'] for chunk in chunks]
            chunk_embeddings = self.embedding_model.encode(chunk_texts, show_progress_bar=False)
            
            # Calculate similarity scores
            similarities = []
            for i, chunk_embedding in enumerate(chunk_embeddings):
                dot_product = np.dot(query_embedding, chunk_embedding)
                norm_query = np.linalg.norm(query_embedding)
                norm_chunk = np.linalg.norm(chunk_embedding)
                
                if norm_query > 0 and norm_chunk > 0:
                    similarity = dot_product / (norm_query * norm_chunk)
                    similarities.append((i, float(similarity)))
            
            # Sort by similarity and get top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            relevant_indices = [idx for idx, _ in similarities[:top_k]]
            
            # Return relevant chunks with scores
            relevant_chunks = []
            for idx in relevant_indices:
                chunk = chunks[idx].copy()
                chunk['relevance_score'] = next(score for i, score in similarities if i == idx)
                relevant_chunks.append(chunk)
            
            return relevant_chunks
        
        else:
            # Fallback: Keyword-based matching
            query_words = set((description + " " + audience_type).lower().split())
            scores = []
            
            for i, chunk in enumerate(chunks):
                chunk_words = set(chunk['text'].lower().split())
                overlap = len(query_words & chunk_words) / max(len(query_words | chunk_words), 1)
                scores.append((i, overlap))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            relevant_indices = [idx for idx, _ in scores[:top_k]]
            
            # Return relevant chunks with scores
            relevant_chunks = []
            for idx in relevant_indices:
                chunk = chunks[idx].copy()
                chunk['relevance_score'] = next(score for i, score in scores if i == idx)
                relevant_chunks.append(chunk)
            
            return relevant_chunks


    def process_document(self, pdf_path: str,
        description: str,
        audience_type: str,
        chunk_size: int = 500,
        overlap: int = 3,
        similarity_threshold: float = 0.5,
        top_k: int = 20,
        images_output_dir: str = "extracted_images",
        include_images: bool = True, ) -> Dict[str, Any]:
        print(f"Starting GNN retrieval for: {pdf_path}")

        # Step 1: Extract text from PDF
        print("Extracting text from PDF...")
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            raise ValueError("Failed to extract text from PDF")

        print(f"Extracted {len(text)} characters from PDF")

        # Step 1b: Extract images
        images_dir = os.path.join(os.path.dirname(pdf_path), "extracted_images")
        images = self.extract_images_from_pdf(pdf_path, images_dir)

        # Step 2: Break down into chunks (nodes)
        print("Chunking document into nodes...")
        chunks = self.chunk_document(text, chunk_size=chunk_size, overlap=overlap)
        print(f"Created {len(chunks)} chunks")

        # Step 3: Create graph edges (GNN structure)
        print("Creating graph edges...")
        edges = self.create_graph_edges(chunks, similarity_threshold=similarity_threshold)
        print(f"Created {len(edges)} edges")

        # Step 4: Retrieve relevant chunks based on description
        print("Retrieving relevant chunks...")
        relevant_chunks = self.retrieve_relevant_chunks(
            chunks, description, audience_type, top_k=top_k
        )
        print(f"Retrieved {len(relevant_chunks)} relevant chunks")

        # Step 5: Create output structure
        output_data = {
            "metadata": {
                "pdf_path": pdf_path,
                "description": description,
                "audience_type": audience_type,
                "total_chunks": len(chunks),
                "relevant_chunks_count": len(relevant_chunks),
                "total_edges": len(edges),
                "num_images": len(images),
                "timestamp": datetime.now().isoformat(),
                "processing_method": "embedding"
                if self.embedding_available and self.embedding_model
                else "keyword",
            },
            "graph_structure": {
                "nodes": chunks,
                "edges": edges,
            },
            # NEW: top-level images array
            "images": images,
            "relevant_chunks": relevant_chunks,
        }

        return output_data
        
    def save_to_json(self, output_data: Dict[str, Any], output_path: str) -> str:
        """
        Save retrieval output to JSON file
        
        Args:
            output_data: Dictionary containing retrieval results
            output_path: Path where JSON file should be saved
            
        Returns:
            Path to saved JSON file
        """
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Retrieval output saved to: {output_path}")
        return output_path

