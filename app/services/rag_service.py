"""
RAG Service - Retrieval Augmented Generation pipeline with FAISS
"""

import os
from typing import List, Tuple
import logging
import numpy as np
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available, using fallback retrieval")


class RAGService:
    """Service for Retrieval-Augmented Generation with Vector Search"""
    
    def __init__(self, embedding_service=None):
        self.documents = []
        self.chunks = []
        self.embeddings = []
        self.vector_store = None
        self.embedding_service = embedding_service
        self.index_path = "data/faiss_index.pkl"
        
    def load_documents(self, doc_path: str) -> List[str]:
        """Load documents from file path"""
        documents = []
        try:
            if os.path.isfile(doc_path):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    documents.append(f.read())
            elif os.path.isdir(doc_path):
                for file in os.listdir(doc_path):
                    if file.endswith(('.txt', '.md')):
                        filepath = os.path.join(doc_path, file)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            documents.append(f.read())
            
            self.documents = documents
            logger.info(f"Loaded {len(documents)} documents from {doc_path}")
            return documents
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return []
    
    def chunk_documents(self, chunk_size: int = 1000, overlap: int = 200) -> List[Tuple[str, str]]:
        """
        Split documents into overlapping chunks
        Returns list of (chunk_text, source_document) tuples
        """
        chunks = []
        for doc_idx, doc in enumerate(self.documents):
            for i in range(0, len(doc), chunk_size - overlap):
                chunk_text = doc[i:i + chunk_size]
                chunks.append((chunk_text, f"doc_{doc_idx}"))
        
        self.chunks = chunks
        logger.info(f"Created {len(chunks)} chunks from {len(self.documents)} documents")
        return chunks
    
    def build_vector_store(self) -> bool:
        """Build FAISS vector store from document chunks"""
        try:
            if not self.chunks:
                logger.warning("No chunks available. Call chunk_documents first.")
                return False
            
            if not FAISS_AVAILABLE:
                logger.warning("FAISS not available. Skipping vector store build.")
                return False
            
            if not self.embedding_service:
                logger.warning("No embedding service provided. Skipping vector store build.")
                return False
            
            # Extract chunk texts
            chunk_texts = [chunk[0] for chunk in self.chunks]
            
            # Generate embeddings
            logger.info("Generating embeddings for chunks...")
            embeddings = self.embedding_service.generate_embeddings(chunk_texts)
            
            if not embeddings:
                logger.error("Failed to generate embeddings")
                return False
            
            # Create FAISS index
            embeddings_array = np.array(embeddings).astype('float32')
            dimension = embeddings_array.shape[1]
            
            self.vector_store = faiss.IndexFlatL2(dimension)
            self.vector_store.add(embeddings_array)
            self.embeddings = embeddings
            
            # Save index
            os.makedirs("data", exist_ok=True)
            with open(self.index_path, 'wb') as f:
                pickle.dump((self.vector_store, self.chunks, self.embeddings), f)
            
            logger.info(f"Vector store built with {len(embeddings)} embeddings")
            return True
        except Exception as e:
            logger.error(f"Error building vector store: {str(e)}")
            return False
    
    def load_vector_store(self) -> bool:
        """Load pre-built FAISS index from disk"""
        try:
            if not os.path.exists(self.index_path):
                logger.warning(f"Vector store not found at {self.index_path}")
                return False
            
            with open(self.index_path, 'rb') as f:
                self.vector_store, self.chunks, self.embeddings = pickle.load(f)
            
            logger.info(f"Loaded vector store with {len(self.chunks)} chunks")
            return True
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Retrieve relevant documents for a query using vector similarity
        Returns list of (chunk_text, relevance_score) tuples
        """
        try:
            # Try vector-based retrieval first
            if self.vector_store and self.embedding_service:
                return self._vector_retrieve(query, top_k)
            else:
                # Fallback to keyword-based retrieval
                return self._keyword_retrieve(query, top_k)
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            return self._keyword_retrieve(query, top_k)
    
    def _vector_retrieve(self, query: str, top_k: int) -> List[Tuple[str, float]]:
        """Vector-based retrieval using FAISS"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embeddings([query])
            if not query_embedding:
                return []
            
            query_array = np.array(query_embedding).astype('float32')
            
            # Search in FAISS index
            distances, indices = self.vector_store.search(query_array, min(top_k, len(self.chunks)))
            
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx < len(self.chunks):
                    chunk_text = self.chunks[idx][0]
                    # Convert distance to similarity score (0-1)
                    similarity = 1 / (1 + distance)
                    results.append((chunk_text, similarity))
            
            logger.info(f"Retrieved {len(results)} chunks via vector search")
            return results
        except Exception as e:
            logger.error(f"Vector retrieval error: {str(e)}")
            return []
    
    def _keyword_retrieve(self, query: str, top_k: int) -> List[Tuple[str, float]]:
        """Keyword-based fallback retrieval"""
        relevant_docs = []
        query_words = set(query.lower().split())
        
        for chunk_text, source in self.chunks:
            chunk_words = set(chunk_text.lower().split())
            intersection = len(query_words & chunk_words)
            relevance = intersection / len(query_words) if query_words else 0
            
            if relevance > 0:
                relevant_docs.append((chunk_text, relevance))
        
        # Sort by relevance and return top_k
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        logger.info(f"Retrieved {len(relevant_docs[:top_k])} chunks via keyword search")
        return relevant_docs[:top_k]
    
    def generate_response(self, query: str, context: List[str], llm_service=None) -> str:
        """
        Generate response using context from retrieved documents
        """
        if not context:
            return "No relevant documents found to answer your question."
        
        context_str = "\n---\n".join(context)
        
        prompt = f"""You are a helpful enterprise assistant. Answer the following question based ONLY on the provided context.

Context:
{context_str}

Question: {query}

Answer:"""
        
        if llm_service:
            return llm_service.generate_completion(prompt)
        else:
            return "LLM service not configured"


class PromptTemplate:
    """Prompt templates for different scenarios"""
    
    @staticmethod
    def qa_template(context: str, question: str) -> str:
        """Question-answering prompt template"""
        return f"""You are a helpful enterprise assistant. Answer the following question based ONLY on the provided context. If the answer is not in the context, say "I don't have this information."

Context:
{context}

Question: {question}

Answer: """
    
    @staticmethod
    def summary_template(text: str) -> str:
        """Summarization prompt template"""
        return f"""Summarize the following text concisely in 2-3 sentences:

{text}

Summary:"""
    
    @staticmethod
    def entity_extraction_template(text: str) -> str:
        """Entity extraction prompt template"""
        return f"""Extract key entities (names, dates, amounts, policies) from the following text. Return as JSON.

{text}

Entities (JSON):"""
    
    @staticmethod
    def hallucination_check_template(response: str, sources: str) -> str:
        """Template for checking hallucinations"""
        return f"""Given the following response and sources, identify any claims in the response that are NOT supported by the sources.

Response: {response}

Sources:
{sources}

Unsupported claims (if any):"""
