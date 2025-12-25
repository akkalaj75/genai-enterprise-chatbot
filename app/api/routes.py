"""
API routes for the chatbot
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

router = APIRouter(prefix="/api", tags=["chat"])
logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    query: str
    conversation_history: List[Message] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    confidence: float
    hallucination_risk: float

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Integrate with RAG service
        response = "Response from RAG pipeline"
        sources = ["policy.txt"]
        confidence = 0.85
        hallucination_risk = 0.05
        
        return ChatResponse(
            response=response,
            sources=sources,
            confidence=confidence,
            hallucination_risk=hallucination_risk
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/info")
async def get_chatbot_info():
    """Get chatbot information"""
    return {
        "name": "Enterprise GenAI Chatbot",
        "version": "1.0.0",
        "model": "GPT-3.5-turbo",
        "capabilities": ["Q&A", "Document retrieval", "Hallucination detection"]
    }
