"""
Authentication and Role-Based Access Control (RBAC)
Provides token signing, verification, password hashing, and user authentication dependencies.
"""

import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Dict, Any
from fastapi import HTTPException, Header, Depends
from database.db_manager import execute_query_one

SECRET_KEY = "tripura_terra_jwt_secret_key_prod_2026"
TOKEN_EXPIRY_SECONDS = 86400 * 7  # 7 days

def hash_password(password: str) -> str:
    """Computes salted SHA-256 hash."""
    salt = "tripura_terra_secure_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def create_access_token(user_id: int, role: str, email: str, name: str) -> str:
    """Creates a secure HMAC-SHA256 signed JSON Web Token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "role": role,
        "email": email,
        "name": name,
        "exp": int(time.time()) + TOKEN_EXPIRY_SECONDS
    }
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    return f"{message}.{sig_b64}"

def verify_token(token: str) -> Dict[str, Any]:
    """Validates token signature and expiration."""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            raise HTTPException(status_code=401, detail="Malformed authorization token")
            
        header_b64, payload_b64, sig_b64 = parts
        message = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + '=' * (-len(sig_b64) % 4))
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            raise HTTPException(status_code=401, detail="Invalid token signature")
            
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + '=' * (-len(payload_b64) % 4))
        payload = json.loads(payload_bytes.decode())
        
        if payload.get("exp", 0) < int(time.time()):
            raise HTTPException(status_code=401, detail="Token has expired")
            
        return payload
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failure: {str(e)}")

def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Extracts and verifies the currently authenticated user from Bearer header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
        
    token = authorization.replace("Bearer ", "").strip()
    payload = verify_token(token)
    
    user = execute_query_one(
        "SELECT user_id, full_name, email, role, country FROM users WHERE user_id = ? AND is_active = 1;",
        (payload["sub"],)
    )
    if not user:
        raise HTTPException(status_code=401, detail="User account not found or disabled")
        
    return user

def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[Dict[str, Any]]:
    """Returns authenticated user if valid token present, else None."""
    if not authorization:
        return None
    try:
        token = authorization.replace("Bearer ", "").strip()
        payload = verify_token(token)
        return execute_query_one(
            "SELECT user_id, full_name, email, role FROM users WHERE user_id = ? AND is_active = 1;",
            (payload["sub"],)
        )
    except Exception:
        return None

def require_role(allowed_roles: list):
    """Enforces role-based permissions (e.g. ['admin', 'content_manager'])."""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Access forbidden: User role '{current_user['role']}' lacks required authority."
            )
        return current_user
    return role_checker
