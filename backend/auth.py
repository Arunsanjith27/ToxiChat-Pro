import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import audit

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "toxichat-secret-key-change-in-prod")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))
ADMIN_USERNAMES = {
    u.strip().lower()
    for u in os.getenv("ADMIN_USERNAMES", "admin").split(",")
    if u.strip()
}

security = HTTPBearer(auto_error=False)


def create_token(username: str, is_admin: bool = False) -> str:
    expire = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = {"sub": username, "exp": expire}
    if is_admin:
        payload["role"] = "admin"
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def verify_token(token: str) -> str:
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    return verify_token(credentials.credentials)


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    if not credentials or not credentials.credentials:
        return None
    try:
        return verify_token(credentials.credentials)
    except HTTPException:
        return None


async def logout_user(username: str):
    import database as db
    await db.update_user_profile(username, {"is_online": False})
    
    # Async Audit Log
    await audit.log_event(
        actor_username=username,
        action="LOGOUT",
        resource_type="AUTH",
        resource_id=username,
        description="User logged out"
    )


def is_admin_user(username: str, user_doc: Optional[dict] = None) -> bool:
    if username.lower() in ADMIN_USERNAMES:
        return True
    if user_doc and user_doc.get("role") == "admin":
        return True
    return False


async def require_admin(username: str = Depends(get_current_user)) -> str:
    import database as db

    user = await db.get_user(username)
    if not is_admin_user(username, user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return username
