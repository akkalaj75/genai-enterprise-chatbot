"""
Authentication and security module with JWT
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TokenData:
    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username

def create_access_token(user_id: str, username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "user_id": user_id,
        "username": username,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> TokenData:
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return TokenData(user_id=user_id, username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

class AuthService:
    """Service for user authentication"""
    
    def __init__(self):
        # In production, use a real database
        self.users = {
            "admin": "admin123",
            "user": "user123"
        }
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user credentials"""
        if username not in self.users:
            logger.warning(f"Authentication failed: user {username} not found")
            return None
        
        if self.users[username] != password:
            logger.warning(f"Authentication failed: incorrect password for user {username}")
            return None
        
        logger.info(f"User {username} authenticated successfully")
        return {
            "user_id": f"user_{username}",
            "username": username,
            "is_admin": username == "admin"
        }
    
    def create_token(self, username: str, password: str) -> Optional[str]:
        """Create token for authenticated user"""
        user = self.authenticate_user(username, password)
        if user:
            token = create_access_token(user["user_id"], user["username"])
            return token
        return None

def get_current_user(token_data: TokenData = Depends(verify_token)) -> TokenData:
    """Get current authenticated user"""
    return token_data
