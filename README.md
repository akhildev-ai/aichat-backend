# AI Chatbot Backend

FastAPI backend for the AI Chatbot application.

## Deploy to Render

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Configure:
   - **Root Directory:** `.` (since this is its own repo)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Add environment variables:
   - `DATABASE_URL` = your Neon connection string (use `postgresql+asyncpg://...`)
   - `JWT_SECRET` = any random secret string
   - `GEMINI_API_KEY` = your Gemini API key
   - `FRONTEND_URL` = your Vercel frontend URL (e.g., `https://your-app.vercel.app`)

5. Deploy!

## Run Migrations (one-time)

After first deploy, open Render Shell and run:
```bash
alembic upgrade head
```

Or run locally pointing to Neon DB:
```bash
pip install -r requirements.txt
alembic upgrade head
```

## Local Development

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
