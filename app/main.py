"""
Updated main application with full integration
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

from app.services.rag_service import RAGService, PromptTemplate
from app.services.azure_openai import AzureOpenAIService
from app.services.auth import AuthService, get_current_user, TokenData, create_access_token

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
rag_service = RAGService()
llm_service = AzureOpenAIService()
auth_service = AuthService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    logger.info("Starting Enterprise GenAI Chatbot...")
    
    # Load documents and build vector store
    doc_path = os.getenv("DOCUMENT_PATH", "data/sample_docs")
    if os.path.exists(doc_path):
        rag_service.load_documents(doc_path)
        rag_service.chunk_documents(
            chunk_size=int(os.getenv("CHUNK_SIZE", 1000)),
            overlap=int(os.getenv("CHUNK_OVERLAP", 200))
        )
        # Attempt to build or load vector store
        if not rag_service.load_vector_store():
            rag_service.build_vector_store()
        logger.info(f"Loaded {len(rag_service.chunks)} document chunks")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Enterprise GenAI Chatbot...")

# Initialize FastAPI app
app = FastAPI(
    title="Enterprise GenAI Chatbot API",
    description="Production-ready RAG-based chatbot with Azure OpenAI",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class ChatRequest(BaseModel):
    query: str
    conversation_history: list = []

class ChatResponse(BaseModel):
    response: str
    sources: list
    confidence: float
    hallucination_risk: float


# Health & Info endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Enterprise GenAI Chatbot",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Enterprise GenAI Chatbot API v2.0",
        "docs": "/docs",
        "health": "/health",
        "auth": "/auth/login"
    }

# Authentication endpoints
@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    token = auth_service.create_token(request.username, request.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return LoginResponse(
        access_token=token,
        username=request.username
    )

# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Chat endpoint for querying the enterprise knowledge base
    Requires authentication
    """
    try:
        if not request.query or request.query.strip() == "":
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        logger.info(f"Query from {current_user.username}: {request.query[:50]}...")
        
        # Retrieve relevant documents
        top_k = int(os.getenv("TOP_K_RESULTS", 5))
        retrieved_docs = rag_service.retrieve(request.query, top_k=top_k)
        
        if not retrieved_docs:
            return ChatResponse(
                response="No relevant documents found to answer your question.",
                sources=[],
                confidence=0.0,
                hallucination_risk=0.0
            )
        
        # Extract context from retrieved documents
        context = [doc[0] for doc in retrieved_docs]
        sources = [f"chunk_{i}" for i in range(len(context))]
        confidence = sum(doc[1] for doc in retrieved_docs) / len(retrieved_docs)
        
        # Generate response using LLM
        response = rag_service.generate_response(request.query, context, llm_service)
        
        # Check for hallucination
        hallucination_risk = llm_service.detect_hallucination(response, context)
        
        logger.info(f"Response generated - Confidence: {confidence:.2f}, Hallucination: {hallucination_risk:.2f}")
        
        return ChatResponse(
            response=response,
            sources=sources,
            confidence=confidence,
            hallucination_risk=hallucination_risk
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate")
async def evaluate_rag(current_user: TokenData = Depends(get_current_user)):
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
        
        logger.info(f"Evaluation by {current_user.username} - P:{precision:.2f} R:{recall:.2f} F1:{f1:.2f}")
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info")
async def get_info():
    """Get chatbot information"""
    return {
        "name": "Enterprise GenAI Chatbot",
        "version": "2.0.0",
        "model": os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-35-turbo"),
        "capabilities": [
            "Question Answering",
            "Document Retrieval (Vector Search)",
            "Hallucination Detection",
            "Context-aware Responses"
        ],
        "loaded_chunks": len(rag_service.chunks),
        "authentication": "JWT"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
