from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Chat, User
from app.schemas import ChatCreate, ChatUpdate, ChatResponse
from app.auth import get_current_user

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=list[ChatResponse])
async def get_chats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Chat).where(Chat.user_id == user.id).order_by(Chat.updated_at.desc())
    )
    return [ChatResponse.model_validate(chat) for chat in result.scalars().all()]


@router.post("", response_model=ChatResponse)
async def create_chat(data: ChatCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    chat = Chat(user_id=user.id, title=data.title or "New Chat")
    db.add(chat)
    await db.flush()
    await db.refresh(chat)
    return ChatResponse.model_validate(chat)


@router.patch("/{chat_id}", response_model=ChatResponse)
async def update_chat(
    chat_id: UUID, data: ChatUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user.id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    chat.title = data.title
    chat.updated_at = datetime.utcnow()
    await db.flush()
    await db.refresh(chat)
    return ChatResponse.model_validate(chat)


@router.delete("/{chat_id}")
async def delete_chat(chat_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user.id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    await db.delete(chat)
    return {"detail": "Chat deleted"}
