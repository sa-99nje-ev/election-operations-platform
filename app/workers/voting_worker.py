"""
ARQ Background Worker for processing queued votes.
"""

import logging
from arq.connections import RedisSettings
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.voter import Voter
from app.models.voting_record import VotingRecord

# Configure logging for ARQ execution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arq.worker")


async def process_vote_task(ctx, vote_data: dict):
    """
    Processes enqueued vote, commits to DB, and handles duplicate vote attempts.
    """
    request_id = vote_data.get("request_id")
    voter_id = vote_data.get("voter_id")
    candidate_id = vote_data.get("candidate_id")
    booth_id = vote_data.get("booth_id")

    async with AsyncSessionLocal() as session:
        try:
            # 1. Check if voter has already cast a vote (Application-level Idempotency Check)
            existing_record = await session.scalar(
                select(VotingRecord).where(VotingRecord.voter_id == voter_id)
            )
            if existing_record:
                logger.warning(f"🛡️ Duplicate vote blocked for Voter ID: {voter_id}")
                return

            # 2. Record Vote Entry in 'voting_records'
            record = VotingRecord(
                voter_id=voter_id,
                candidate_id=candidate_id,
                booth_id=booth_id
            )
            session.add(record)

            await session.commit()
            logger.info(f"✔ Vote processed successfully for Request ID: {request_id}")

            # 3. Increment Live Candidate Counter in Redis Cache
            redis_pool = ctx.get("redis")
            if redis_pool:
                await redis_pool.hincrby("candidate_tallies", str(candidate_id), 1)

        except IntegrityError:
            await session.rollback()
            logger.warning(f"🛡️ Duplicate vote blocked by DB constraint for Voter ID: {voter_id}")

        except Exception as exc:
            await session.rollback()
            logger.error(f"❌ Error processing vote task: {exc}")
            raise exc


class WorkerSettings:
    """ARQ Worker configuration settings."""
    functions = [process_vote_task]
    redis_settings = RedisSettings(host="localhost", port=6379)