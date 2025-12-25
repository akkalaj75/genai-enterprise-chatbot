"""
Azure OpenAI Service wrapper with real API integration
"""

import os
import logging
from typing import List, Optional
from openai import AzureOpenAI

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Service for Azure OpenAI integration"""
    
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-35-turbo")
        self.model = "gpt-35-turbo"
        
        if not all([self.api_key, self.endpoint]):
            logger.warning("Azure OpenAI credentials not fully configured")
        else:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version="2024-02-15-preview",
                azure_endpoint=self.endpoint
            )
            logger.info("Azure OpenAI client initialized")
    
    def generate_completion(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
        """
        Generate completion using Azure OpenAI
        """
        try:
            if not hasattr(self, 'client'):
                logger.error("Azure OpenAI client not initialized")
                return "Azure OpenAI is not configured"
            
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            return f"Error: {str(e)}"
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for texts using Azure OpenAI
        """
        try:
            if not hasattr(self, 'client'):
                logger.error("Azure OpenAI client not initialized")
                return []
            
            embeddings = []
            for text in texts:
                # Use Azure OpenAI embedding endpoint
                response = self.client.embeddings.create(
                    input=text,
                    model="text-embedding-ada-002"
                )
                embeddings.append(response.data[0].embedding)
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return []
    
    def detect_hallucination(self, response: str, sources: List[str]) -> float:
        """
        Detect hallucination score (0-1, where 0 = no hallucination)
        Uses Azure OpenAI to evaluate factuality
        """
        try:
            if not hasattr(self, 'client'):
                return self._simple_hallucination_check(response, sources)
            
            source_text = "\n".join(sources)
            
            evaluation_prompt = f"""Given the following sources and response, evaluate if the response is supported by the sources.
Return a score from 0 to 1 where:
- 0 = completely supported by sources (no hallucination)
- 1 = completely unsupported (complete hallucination)

Sources:
{source_text}

Response:
{response}

Return ONLY a number between 0 and 1."""
            
            score_text = self.generate_completion(evaluation_prompt, temperature=0)
            
            try:
                score = float(score_text.strip())
                return min(max(score, 0), 1)
            except ValueError:
                return self._simple_hallucination_check(response, sources)
        except Exception as e:
            logger.error(f"Error detecting hallucination: {str(e)}")
            return self._simple_hallucination_check(response, sources)
    
    def _simple_hallucination_check(self, response: str, sources: List[str]) -> float:
        """Simple fallback hallucination check"""
        if not sources:
            return 1.0
        
        source_text = " ".join(sources).lower()
        response_words = set(response.lower().split())
        source_words = set(source_text.split())
        
        supported_words = len(response_words & source_words)
        hallucination_score = 1 - (supported_words / len(response_words)) if response_words else 1.0
        
        return min(max(hallucination_score, 0), 1)
