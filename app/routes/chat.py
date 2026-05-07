import json
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from google import genai

from app.database import get_db
from app.models import Chat, Message, MessageRole, User
from app.schemas import ChatMessageRequest
from app.auth import get_current_user
from app.config import get_settings

router = APIRouter(tags=["chat"])
settings = get_settings()

BEARING_SYSTEM_PROMPT = """You are an expert bearing selection assistant specializing in SKF, NSK, FAG, Timken, and other major bearing manufacturers.

Your expertise includes:
- Ball bearings, roller bearings, needle bearings, thrust bearings, spherical bearings
- Bearing selection based on load, speed, temperature, and environment
- Bearing maintenance, lubrication, and failure analysis
- Industry applications: automotive, aerospace, industrial machinery, wind energy
- SKF product catalog knowledge including deep groove ball bearings, angular contact, cylindrical roller, tapered roller, and self-aligning bearings
- Bearing designations and nomenclature (e.g., 6205, 7208, NU 210, 32008)
- Performance metrics: dynamic load rating (C), static load rating (C0), limiting speed, reference speed
- Bearing life calculations (L10, L10a)

When answering:
- Provide specific bearing model numbers when relevant
- Include technical specifications (dimensions, load ratings, speed limits)
- Suggest alternatives when appropriate
- Use markdown tables for comparisons
- Format code/calculations clearly

If a question is not related to bearings or mechanical engineering, you can still help but gently remind the user this is a bearing-focused assistant."""


def get_gemini_client():
    return genai.Client(api_key=settings.GEMINI_API_KEY)


async def generate_title(client, message: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"Generate a short title (max 6 words) for a conversation that starts with this message. Return ONLY the title, nothing else:\n\n{message}",
        )
        return response.text.strip()[:100]
    except Exception:
        return "New Chat"


@router.post("/chat")
async def chat(
    data: ChatMessageRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Chat).where(Chat.id == data.chat_id, Chat.user_id == user.id))
    chat = result.scalar_one_or_none()
    if not chat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    user_message = Message(chat_id=chat.id, role=MessageRole.user, content=data.message)
    db.add(user_message)
    await db.flush()

    result = await db.execute(
        select(Message).where(Message.chat_id == chat.id).order_by(Message.created_at)
    )
    messages = result.scalars().all()

    conversation_history = [
        {"role": "user", "parts": [{"text": BEARING_SYSTEM_PROMPT}]},
        {"role": "model", "parts": [{"text": "Understood. I'm ready to help with bearing selection, specifications, and technical guidance. How can I assist you?"}]},
    ]
    for msg in messages:
        role = "model" if msg.role.value == "assistant" else msg.role.value
        conversation_history.append({"role": role, "parts": [{"text": msg.content}]})

    # Auto-generate title on first message
    is_first_message = len(messages) == 1
    client = get_gemini_client()

    if is_first_message:
        title = await generate_title(client, data.message)
        chat.title = title
        chat.updated_at = datetime.utcnow()
        await db.flush()

    chat.updated_at = datetime.utcnow()
    await db.commit()

    async def stream_response():
        full_response = ""
        try:
            response = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=conversation_history,
            )
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    yield f"data: {json.dumps({'content': chunk.text})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        # Save assistant message
        async with async_session_factory() as save_db:
            assistant_message = Message(
                chat_id=chat.id, role=MessageRole.assistant, content=full_response
            )
            save_db.add(assistant_message)
            await save_db.commit()

        yield "data: [DONE]\n\n"

    # We need a separate session for saving after streaming
    from app.database import async_session as async_session_factory

    return StreamingResponse(stream_response(), media_type="text/event-stream")
