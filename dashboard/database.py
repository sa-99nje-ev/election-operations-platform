import os
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use DATABASE_URL from .env with proper fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://election_user:sanjeev@localhost:5432/election_db"
)

# Convert asyncpg URL to sync psycopg URL for pandas
sync_db_url = DATABASE_URL.replace(
    "postgresql+asyncpg://",
    "postgresql+psycopg://"
)

# Create sync engine for pandas
engine = create_engine(sync_db_url, echo=False)

def fetch_safe(query, fallback_df):
    """
    Execute a SQL query safely with fallback.
    If database is unreachable, returns fallback DataFrame.
    """
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        print(f"?? Database query failed: {e}")
        return fallback_df
