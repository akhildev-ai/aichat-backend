from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"


class ChatUpdate(BaseModel):
    title: str


class ChatResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: UUID
    chat_id: UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageRequest(BaseModel):
    chat_id: UUID
    message: str
