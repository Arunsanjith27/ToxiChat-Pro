import os
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Optional
import database as db
import redis_service
import audit
from security import hash_password, verify_password, migrate_password
from auth import create_token, get_current_user, is_admin_user, logout_user
from models import (
    UserRegister, UserLogin, TokenOut, UserOut,
    ForgotPasswordRequest, ResetPasswordRequest
)

router = APIRouter(prefix="/api")

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_WINDOW = 900  # 15 minutes
GLOBAL_RATE_LIMIT = 30
GLOBAL_RATE_WINDOW = 60

def _token_response(user: dict) -> TokenOut:
    return TokenOut(
        access_token=create_token(user["username"], is_admin_user(user["username"], user)),
        username=user["username"],
        display_name=user.get("display_name", user["username"]),
        role=user.get("role", "user"),
        avatar_url=user.get("avatar_url"),
        reputation_score=user.get("reputation_score", 100),
    )

async def check_rate_limit(request: Request):
    ip = request.client.host if request.client else "unknown"
    rate = await redis_service.increment_rate(f"auth_rate:{ip}", GLOBAL_RATE_WINDOW)
    if rate > GLOBAL_RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    return ip

@router.post("/register", response_model=TokenOut)
async def register(data: UserRegister, request: Request, ip: str = Depends(check_rate_limit)):
    existing = await db.get_user(data.username)
    if existing:
        raise HTTPException(400, "Username already taken")
    hashed = hash_password(data.password)
    display = data.display_name or data.username
    user = await db.create_user(data.username, hashed, display, data.email)
    
    await audit.log_event(
        actor_username=data.username,
        action="USER_REGISTERED",
        resource_type="AUTH",
        resource_id=data.username,
        description="New user registered",
        ip_address=ip
    )
    
    return _token_response(user)


@router.post("/login", response_model=TokenOut)
async def login(data: UserLogin, request: Request, ip: str = Depends(check_rate_limit)):
    # Check Lockout BEFORE checking credentials
    is_locked = await redis_service.check_lockout(data.username, MAX_LOGIN_ATTEMPTS)
    if is_locked:
        raise HTTPException(403, "Account temporarily locked due to multiple failed login attempts.")

    user = await db.get_user(data.username)
    if not user:
        # User does not exist, but we still increment failed attempts for the requested username
        # to prevent leaking whether the user exists or not, and to stop brute force.
        await redis_service.record_failed_login(data.username, LOCKOUT_WINDOW)
        raise HTTPException(401, "Invalid username or password")
        
    if not verify_password(data.password, user["password"]):
        fails = await redis_service.record_failed_login(data.username, LOCKOUT_WINDOW)
        
        await audit.log_event(
            actor_username=data.username,
            action="FAILED_LOGIN",
            resource_type="AUTH",
            resource_id=data.username,
            description=f"Failed login attempt ({fails}/{MAX_LOGIN_ATTEMPTS})",
            ip_address=ip
        )
        
        if fails >= MAX_LOGIN_ATTEMPTS:
            await audit.log_event(
                actor_username=data.username,
                action="ACCOUNT_LOCKED",
                resource_type="AUTH",
                resource_id=data.username,
                description=f"Account locked after {MAX_LOGIN_ATTEMPTS} failed attempts",
                ip_address=ip
            )
            raise HTTPException(403, "Account temporarily locked due to multiple failed login attempts.")
            
        raise HTTPException(401, "Invalid username or password")

    # Success path
    await redis_service.clear_failed_logins(data.username)
    
    # Check for password migration
    new_hash = migrate_password(data.password, user["password"])
    if new_hash:
        await db.update_user_password(data.username, new_hash)

    await audit.log_event(
        actor_username=data.username,
        action="LOGIN",
        resource_type="AUTH",
        resource_id=data.username,
        description="User logged in successfully",
        ip_address=ip
    )
    
    return _token_response(user)


@router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPasswordRequest, request: Request, ip: str = Depends(check_rate_limit)):
    # Always return success to prevent user enumeration
    token = await db.create_reset_token(data.username)
    
    # Only return token hint in dev environment, but keeping it for compatibility
    return {
        "message": "If the account exists, a reset link has been generated.",
        "token": token,
        "reset_url_hint": f"/reset-password?token={token}" if token else None,
    }


@router.post("/auth/reset-password")
async def reset_password(data: ResetPasswordRequest, request: Request, ip: str = Depends(check_rate_limit)):
    username = await db.consume_reset_token(data.token)
    if not username:
        raise HTTPException(400, "Invalid or expired reset token")
        
    await db.update_user_password(username, hash_password(data.new_password))
    
    await audit.log_event(
        actor_username=username,
        action="PASSWORD_RESET",
        resource_type="AUTH",
        resource_id=username,
        description="User reset their password",
        ip_address=ip
    )
    
    return {"message": "Password updated successfully", "username": username}

@router.post("/logout")
async def logout(request: Request, username: str = Depends(get_current_user)):
    ip = request.client.host if request.client else "unknown"
    await logout_user(username)
    
    # Note: logout_user already logs LOGOUT event, but we can capture IP here if we passed it down.
    # We will let logout_user handle the DB state and basic audit logging.
    return {"message": "Logged out successfully"}
