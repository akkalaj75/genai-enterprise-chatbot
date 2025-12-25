"""
Azure OpenAI Service wrapper
"""

import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Service for Azure OpenAI integration"""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_DEPLOYMENT_NAME")
        self.model = "gpt-35-turbo"
        
        if not all([self.api_key, self.endpoint, self.deployment]):
            logger.warning("Azure OpenAI credentials not fully configured")
    
    def generate_completion(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Generate completion using Azure OpenAI
        """
        try:
            # Placeholder for actual Azure OpenAI call
            # In production, use: from openai import AzureOpenAI
            response = "Generated response from Azure OpenAI"
            return response
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            return "Error generating response"
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts
        """
        try:
            # Placeholder for actual embedding generation
            embeddings = [[0.1, 0.2, 0.3] for _ in texts]
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return []
    
    def detect_hallucination(self, response: str, sources: List[str]) -> float:
        """
        Detect hallucination score (0-1, where 0 = no hallucination)
        """
        if not sources:
            return 1.0
        
        source_text = " ".join(sources).lower()
        response_words = set(response.lower().split())
        source_words = set(source_text.split())
        
        supported_words = len(response_words & source_words)
        hallucination_score = 1 - (supported_words / len(response_words)) if response_words else 1.0
        
        return min(max(hallucination_score, 0), 1)  # Clamp between 0 and 1
