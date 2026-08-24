from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_db, get_current_user_payload
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db), _admin: dict = Depends(get_current_user_payload)):
    if body.role not in {"USER", "ADMIN"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    exists = (await db.execute(select(User).where(User.username == body.username))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Username exists")
    user = User(username=body.username, password_hash=hash_password(body.password), role=body.role)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.username == body.username))).scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(subject=user.id, role=user.role)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
async def me(payload: dict = Depends(get_current_user_payload), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, payload["sub"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
