from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Chat, Message, User
from app.schemas import MessageResponse
from app.auth import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/{chat_id}", response_model=list[MessageResponse])
async def get_messages(
    chat_id: UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Chat).where(Chat.id == chat_id, Chat.user_id == user.id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at)
    )
    return [MessageResponse.model_validate(msg) for msg in result.scalars().all()]
