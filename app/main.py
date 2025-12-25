"""
Main application entry point for Enterprise GenAI Chatbot
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Enterprise GenAI Chatbot",
    description="RAG-based enterprise chatbot using Azure OpenAI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ChatRequest(BaseModel):
    query: str
    conversation_history: list = []

class ChatResponse(BaseModel):
    response: str
    sources: list
    confidence: float

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enterprise GenAI Chatbot",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Enterprise GenAI Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for querying the enterprise knowledge base
    """
    try:
        if not request.query or request.query.strip() == "":
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Placeholder response - integrate with actual RAG pipeline
        response = "This is a placeholder response. Integrate with your RAG pipeline."
        sources = ["company_policy.txt"]
        confidence = 0.85
        
        logger.info(f"Query: {request.query}")
        
        return ChatResponse(
            response=response,
            sources=sources,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate")
async def evaluate_rag():
    """
    Evaluate RAG system performance
    """
    try:
        from evaluation.metrics import EvaluationMetrics
        
        evaluator = EvaluationMetrics()
        
        # Simulate evaluation
        retrieved = ["doc1", "doc2", "doc3"]
        relevant = ["doc1", "doc2", "doc4"]
        
        precision = evaluator.calculate_precision(retrieved, relevant)
        recall = evaluator.calculate_recall(retrieved, relevant)
        f1 = evaluator.calculate_f1(precision, recall)
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "timestamp": str(os.popen('date').read().strip())
        }
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
