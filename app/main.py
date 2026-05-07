from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.chats import router as chats_router
from app.routes.messages import router as messages_router
from app.routes.chat import router as chat_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(title="AI Chatbot API", version="1.0.0")

# Allow all origins in production (can restrict later)
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
]

# Add Vercel deployment URL if set
if settings.FRONTEND_URL:
    origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chats_router)
app.include_router(messages_router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
