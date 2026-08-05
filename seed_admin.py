"""
Admin Seeding Script for PostgreSQL.
"""

import asyncio
from sqlalchemy import select

# Import all models to configure the mapper registry completely
import app.models.user
import app.models.voter
import app.models.constituency
import app.models.candidate
import app.models.polling_booth
import app.models.voting_record
import app.models.audit_log
import app.models.refresh_token

from app.models.user import User
from app.database import AsyncSessionLocal
from app.core.security import get_password_hash


async def seed_admin():
    async with AsyncSessionLocal() as session:
        existing_user = await session.scalar(
            select(User).where(User.username == "admin_user")
        )
        if existing_user:
            print("✔ Admin user 'admin_user' already exists in PostgreSQL.")
            return

        admin_user = User(
            username="admin_user",
            hashed_password=get_password_hash("AdminPassword123"),
            role="admin",
            is_active=True
        )
        
        session.add(admin_user)
        await session.commit()
        print("✔ Successfully created 'admin_user' in PostgreSQL database.")


if __name__ == "__main__":
    asyncio.run(seed_admin())