"""Create a test user directly in the database."""
import asyncio
import sys
sys.path.insert(0, ".")

from app.database import async_session
from app.models import User
from app.auth import hash_password


async def create_user():
    async with async_session() as db:
        user = User(
            username="akhil",
            email="akhil@example.com",
            hashed_password=hash_password("password123"),
        )
        db.add(user)
        await db.commit()
        print("User created successfully!")
        print("  Username: akhil")
        print("  Password: password123")


if __name__ == "__main__":
    asyncio.run(create_user())
