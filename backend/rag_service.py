import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from models import KnowledgeDocument, DocumentChunk
from config import settings

class RAGService:
    def __init__(self):
        self.embedding_model = None
        self.vector_dimension = 384  # Default for sentence-transformers/all-MiniLM-L6-v2
        
    def _load_embedding_model(self):
        """Lazy load the embedding model"""
        if self.embedding_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(settings.embedding_model)
                print(f"Loaded embedding model: {settings.embedding_model}")
            except ImportError:
                print("Warning: sentence-transformers not available. Using mock embeddings.")
                self.embedding_model = "mock"
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text"""
        self._load_embedding_model()
        
        if self.embedding_model == "mock":
            # Mock embedding for development
            return [0.1] * self.vector_dimension
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return [0.1] * self.vector_dimension
    
    def chunk_text(self, text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """Split text into overlapping chunks"""
        chunk_size = chunk_size or settings.chunk_size
        overlap = overlap or settings.chunk_overlap
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks
    
    def process_document(self, db: Session, document_id: str, content: str) -> bool:
        """Process a document and store its chunks with embeddings"""
        try:
            # Get document
            document = db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()
            if not document:
                return False
            
            # Clear existing chunks
            db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).delete()
            
            # Split into chunks
            chunks = self.chunk_text(content)
            
            # Create chunks with embeddings
            for i, chunk_content in enumerate(chunks):
                embedding = self.generate_embedding(chunk_content)
                
                chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk_content,
                    chunk_index=i,
                    embedding=json.dumps(embedding),
                    chunk_metadata=json.dumps({
                        "chunk_size": len(chunk_content),
                        "processed_at": datetime.utcnow().isoformat()
                    })
                )
                
                db.add(chunk)
            
            # Mark document as processed
            document.is_processed = True
            db.commit()
            
            print(f"Processed document {document_id}: {len(chunks)} chunks created")
            return True
            
        except Exception as e:
            print(f"Error processing document {document_id}: {e}")
            db.rollback()
            return False
    
    def search_similar_chunks(self, db: Session, query: str, tenant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar document chunks based on query"""
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Get all chunks for the tenant
            chunks = db.query(DocumentChunk).join(KnowledgeDocument).filter(
                KnowledgeDocument.tenant_id == tenant_id,
                KnowledgeDocument.is_active == True,
                KnowledgeDocument.is_processed == True
            ).all()
            
            if not chunks:
                return []
            
            # Calculate similarities
            similarities = []
            for chunk in chunks:
                try:
                    chunk_embedding = json.loads(chunk.embedding)
                    similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                    similarities.append({
                        'chunk': chunk,
                        'similarity': similarity
                    })
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            results = []
            for item in similarities[:limit]:
                chunk = item['chunk']
                results.append({
                    'id': chunk.id,
                    'content': chunk.content,
                    'document_id': chunk.document_id,
                    'similarity': item['similarity'],
                    'metadata': json.loads(chunk.chunk_metadata) if chunk.chunk_metadata else {}
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching chunks: {e}")
            return []
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def generate_context_prompt(self, query: str, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Generate a context-aware prompt for the LLM"""
        if not relevant_chunks:
            return f"User question: {query}\n\nPlease provide a helpful response based on your knowledge."
        
        context = "Based on the following information:\n\n"
        for i, chunk in enumerate(relevant_chunks, 1):
            context += f"{i}. {chunk['content']}\n\n"
        
        context += f"User question: {query}\n\n"
        context += "Please provide a helpful response based on the information above. If the information doesn't contain the answer, say so and provide general guidance."
        
        return context

# Global RAG service instance
rag_service = RAGService() 