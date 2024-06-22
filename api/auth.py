from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta
from pydantic import BaseModel

from core.config import jwt_settings
from core.security import verify_password, create_access_token, decode_access_token
from db.repositories.user_repository import get_user_by_username, create_user, delete_messages_by_sender
from api.models.requests import TokenRequest, RegisterRequest

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_user_by_username(payload.get("sub"))


@router.post("/token", response_model=Token)
async def login_for_access_token():
    # Generate a unique username using UUID
    unique_username = f"user_{uuid4()}"
    # For demonstration, we use a fixed password pattern, could be randomized similarly
    password = "defaultPassword123"

    # Create a new user with the generated unique username and password
    await create_user(unique_username, password)

    # Delete messages for this user, though they shouldn't have any
    await delete_messages_by_sender(unique_username)

    # Create token with short expiration for temporary access
    access_token_expires = timedelta(seconds=jwt_settings.EXPIRATION_SECONDS)
    access_token = create_access_token(data={"sub": unique_username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register")
async def register_user(register_request: RegisterRequest):
    user = await get_user_by_username(register_request.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    await create_user(register_request.username, register_request.password)
    return {"message": "User created successfully"}
