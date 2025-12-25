"""
Unit tests for RAG Service, Azure OpenAI, and Authentication
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from app.services.rag_service import RAGService, PromptTemplate
from app.services.azure_openai import AzureOpenAIService
from app.services.auth import AuthService, create_access_token, verify_token
import jwt

# Test RAG Service
class TestRAGService:
    @pytest.fixture
    def rag_service(self):
        return RAGService()
    
    def test_load_documents(self, rag_service, tmp_path):
        """Test loading documents"""
        # Create temporary file
        doc_file = tmp_path / "test.txt"
        doc_file.write_text("Test document content")
        
        docs = rag_service.load_documents(str(doc_file))
        
        assert len(docs) == 1
        assert "Test document content" in docs[0]
    
    def test_chunk_documents(self, rag_service):
        """Test chunking documents"""
        rag_service.documents = ["This is a long document. " * 100]
        chunks = rag_service.chunk_documents(chunk_size=100, overlap=20)
        
        assert len(chunks) > 1
        assert all(isinstance(chunk, tuple) for chunk in chunks)
    
    def test_keyword_retrieve(self, rag_service):
        """Test keyword-based retrieval"""
        rag_service.chunks = [
            ("Company policy about remote work", "doc_0"),
            ("Benefits information and details", "doc_1")
        ]
        
        results = rag_service._keyword_retrieve("remote work policy", top_k=5)
        
        assert len(results) > 0
        assert results[0][0] == "Company policy about remote work"
    
    def test_prompt_templates(self):
        """Test prompt templates"""
        context = "Test context"
        question = "Test question?"
        
        qa_prompt = PromptTemplate.qa_template(context, question)
        assert question in qa_prompt
        assert context in qa_prompt
        assert "Answer:" in qa_prompt


# Test Azure OpenAI Service
class TestAzureOpenAIService:
    @pytest.fixture
    def openai_service(self):
        return AzureOpenAIService()
    
    def test_hallucination_detection(self, openai_service):
        """Test hallucination detection"""
        response = "Company provides health insurance"
        sources = ["Health insurance is provided", "Coverage includes medical and dental"]
        
        hallucination_score = openai_service._simple_hallucination_check(response, sources)
        
        assert 0 <= hallucination_score <= 1
        assert hallucination_score < 0.5  # Should have low hallucination
    
    def test_hallucination_detection_high(self, openai_service):
        """Test hallucination detection with unsupported claims"""
        response = "The office has a swimming pool"
        sources = ["We have a gym facility", "Office located in downtown"]
        
        hallucination_score = openai_service._simple_hallucination_check(response, sources)
        
        assert hallucination_score > 0.5  # Should have high hallucination


# Test Authentication Service
class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    def test_authenticate_user_success(self, auth_service):
        """Test successful user authentication"""
        user = auth_service.authenticate_user("admin", "admin123")
        
        assert user is not None
        assert user["username"] == "admin"
        assert user["is_admin"] is True
    
    def test_authenticate_user_invalid_password(self, auth_service):
        """Test authentication with invalid password"""
        user = auth_service.authenticate_user("admin", "wrongpassword")
        
        assert user is None
    
    def test_authenticate_user_not_found(self, auth_service):
        """Test authentication with non-existent user"""
        user = auth_service.authenticate_user("nonexistent", "password")
        
        assert user is None
    
    def test_create_token(self, auth_service):
        """Test token creation"""
        token = auth_service.create_token("admin", "admin123")
        
        assert token is not None
        
        # Verify token
        from app.services.auth import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["username"] == "admin"


# Test Token Creation and Verification
class TestTokens:
    def test_create_access_token(self):
        """Test access token creation"""
        token = create_access_token("user_1", "testuser")
        
        assert token is not None
        assert isinstance(token, str)
    
    def test_token_contains_user_info(self):
        """Test that token contains user information"""
        token = create_access_token("user_1", "testuser")
        
        from app.services.auth import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        assert payload["user_id"] == "user_1"
        assert payload["username"] == "testuser"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
