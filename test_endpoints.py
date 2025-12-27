#!/usr/bin/env python
"""
Quick test script to verify all endpoints work
Run with: python test_endpoints.py
"""

from fastapi.testclient import TestClient
from app.main import app

def main():
    client = TestClient(app)
    
    print("=" * 60)
    print("ENTERPRISE GENAI CHATBOT - ENDPOINT TESTS")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n[1/6] Testing /health endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ PASSED - Status: {data['status']}")
    print(f"  Service: {data['service']}")
    print(f"  Version: {data['version']}")
    
    # Test 2: Root Endpoint
    print("\n[2/6] Testing / endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ PASSED - {data['message']}")
    
    # Test 3: Info Endpoint
    print("\n[3/6] Testing /api/info endpoint...")
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    print(f"✓ PASSED - Model: {data['model']}")
    print(f"  Loaded chunks: {data['loaded_chunks']}")
    print(f"  Capabilities: {', '.join(data['capabilities'])}")
    
    # Test 4: Login
    print("\n[4/6] Testing /auth/login endpoint...")
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    token = data['access_token']
    print(f"✓ PASSED - Token: {token[:30]}...")
    print(f"  Token type: {data['token_type']}")
    print(f"  Username: {data['username']}")
    
    # Test 5: Chat with Authentication
    print("\n[5/6] Testing /api/chat endpoint...")
    response = client.post(
        "/api/chat",
        json={"query": "What is the company policy?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"✓ PASSED - Response received")
    print(f"  Answer: {data['response'][:60]}...")
    print(f"  Confidence: {data['confidence']:.2f}")
    print(f"  Hallucination Risk: {data['hallucination_risk']:.2f}")
    print(f"  Sources: {len(data['sources'])} document(s)")
    
    # Test 6: Authentication Required
    print("\n[6/6] Testing authentication requirement...")
    response = client.post(
        "/api/chat",
        json={"query": "What is the policy?"}
    )
    assert response.status_code == 401  # Should be unauthorized
    print(f"✓ PASSED - Authentication correctly required (401)")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nTo start the server, run:")
    print("  python -m uvicorn app.main:app --host 127.0.0.1 --port 5000")
    print("\nThen access the API at:")
    print("  http://127.0.0.1:5000/docs (Interactive API docs)")
    print("=" * 60)

if __name__ == "__main__":
    main()
