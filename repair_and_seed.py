"""
Unified Database Schema Alignment & Admin Seeding Script.
"""

import asyncio
from sqlalchemy import text, select

# Import all ORM models
import app.models.user
import app.models.voter
import app.models.constituency
import app.models.candidate
import app.models.polling_booth
import app.models.voting_record
import app.models.audit_log
import app.models.refresh_token

from app.database import engine, AsyncSessionLocal, Base
from app.models.user import User
from app.core.security import get_password_hash


async def repair_and_seed():
    async with engine.begin() as conn:
        print("1. Aligning 'users' table columns in PostgreSQL...")
        
        # Add required columns
        await conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255),
            ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'admin',
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
        """))
        
        # Safely drop NOT NULL constraint on old password_hash column if it exists
        try:
            await conn.execute(text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;"))
            await conn.execute(text("""
                UPDATE users 
                SET hashed_password = password_hash 
                WHERE hashed_password IS NULL AND password_hash IS NOT NULL;
            """))
        except Exception:
            pass  # Ignore if password_hash column does not exist

        print("2. Syncing entire metadata schema across PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)

    print("3. Seeding admin account...")
    async with AsyncSessionLocal() as session:
        existing_user = await session.scalar(
            select(User).where(User.username == "admin_user")
        )
        if existing_user:
            print("✔ 'admin_user' already exists in database.")
            return

        admin_user = User(
            username="admin_user",
            hashed_password=get_password_hash("AdminPassword123"),
            role="admin",
            is_active=True
        )
        session.add(admin_user)
        await session.commit()
        print("✔ 'admin_user' successfully created in PostgreSQL!")


if __name__ == "__main__":
    asyncio.run(repair_and_seed())