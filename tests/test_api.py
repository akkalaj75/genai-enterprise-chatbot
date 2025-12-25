"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

class TestHealthEndpoints:
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "Enterprise GenAI Chatbot" in data["service"]
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "Welcome" in data["message"]
        assert "docs" in data


class TestAuthenticationEndpoints:
    def test_login_success(self, client):
        """Test successful login"""
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "admin"
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401


class TestChatEndpoints:
    def test_chat_without_auth(self, client):
        """Test chat without authentication"""
        response = client.post(
            "/api/chat",
            json={"query": "What is the remote work policy?"}
        )
        
        assert response.status_code == 403  # Forbidden
    
    def test_chat_with_auth(self, client):
        """Test chat with valid authentication"""
        # First login
        login_response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Then chat
        response = client.post(
            "/api/chat",
            json={"query": "What is the remote work policy?"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "sources" in data
        assert "confidence" in data
        assert "hallucination_risk" in data
    
    def test_chat_empty_query(self, client):
        """Test chat with empty query"""
        login_response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        response = client.post(
            "/api/chat",
            json={"query": ""},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400


class TestInfoEndpoint:
    def test_get_info(self, client):
        """Test info endpoint"""
        response = client.get("/api/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "model" in data
        assert "capabilities" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
