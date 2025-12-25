"""
RAG Service - Retrieval Augmented Generation pipeline
"""

import os
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class RAGService:
    """Service for Retrieval-Augmented Generation"""
    
    def __init__(self):
        self.documents = []
        self.embeddings = []
        self.vector_store = None
        
    def load_documents(self, doc_path: str) -> List[str]:
        """Load documents from file path"""
        documents = []
        try:
            if os.path.isfile(doc_path):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    documents.append(f.read())
            elif os.path.isdir(doc_path):
                for file in os.listdir(doc_path):
                    if file.endswith('.txt'):
                        with open(os.path.join(doc_path, file), 'r', encoding='utf-8') as f:
                            documents.append(f.read())
            
            self.documents = documents
            logger.info(f"Loaded {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            return []
    
    def chunk_documents(self, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split documents into overlapping chunks"""
        chunks = []
        for doc in self.documents:
            for i in range(0, len(doc), chunk_size - overlap):
                chunks.append(doc[i:i + chunk_size])
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Retrieve relevant documents for a query
        Returns list of (document, relevance_score) tuples
        """
        relevant_docs = []
        query_words = set(query.lower().split())
        
        for doc in self.documents:
            doc_words = set(doc.lower().split())
            intersection = len(query_words & doc_words)
            relevance = intersection / len(query_words) if query_words else 0
            
            if relevance > 0:
                relevant_docs.append((doc, relevance))
        
        # Sort by relevance and return top_k
        relevant_docs.sort(key=lambda x: x[1], reverse=True)
        return relevant_docs[:top_k]
    
    def generate_response(self, query: str, context: List[str]) -> str:
        """
        Generate response using context from retrieved documents
        """
        context_str = "\n".join(context)
        
        prompt = f"""Based on the following context, answer the question concisely.

Context:
{context_str}

Question: {query}

Answer:"""
        
        # Placeholder - integrate with Azure OpenAI
        return "Response generated based on context"

class PromptTemplate:
    """Prompt templates for different scenarios"""
    
    @staticmethod
    def qa_template(context: str, question: str) -> str:
        """Question-answering prompt template"""
        return f"""You are a helpful enterprise assistant. Answer the following question based ONLY on the provided context.

Context:
{context}

Question: {question}

Answer: """
    
    @staticmethod
    def summary_template(text: str) -> str:
        """Summarization prompt template"""
        return f"""Summarize the following text concisely:

{text}

Summary:"""
    
    @staticmethod
    def entity_extraction_template(text: str) -> str:
        """Entity extraction prompt template"""
        return f"""Extract key entities (names, dates, amounts) from the following text:

{text}

Entities:"""
