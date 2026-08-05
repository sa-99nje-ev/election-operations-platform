"""
Database Schema Sync & Table Migration Script.
"""

import asyncio
from sqlalchemy import text
from app.database import engine, Base

# Import all models to register full metadata
import app.models.user
import app.models.voter
import app.models.constituency
import app.models.candidate
import app.models.polling_booth
import app.models.voting_record
import app.models.audit_log
import app.models.refresh_token


async def fix_schema():
    async with engine.begin() as conn:
        print("1. Adding missing columns to 'users' table...")
        await conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255),
            ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'admin',
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();
        """))
        
        print("2. Syncing remaining table metadata across PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)

    print("✔ Database schema fully synchronized!")


if __name__ == "__main__":
    asyncio.run(fix_schema())