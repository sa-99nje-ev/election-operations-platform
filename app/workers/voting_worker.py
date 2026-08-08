"""
ARQ Background Worker for processing queued votes.
"""

import logging
import os

from arq.connections import RedisSettings
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import AsyncSessionLocal
from app.models.voting_record import VotingRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arq.worker")


async def process_vote_task(ctx, vote_data: dict):
    """
    Processes an enqueued vote, commits it to the database,
    and handles duplicate vote attempts.
    """

    request_id = vote_data.get("request_id")
    voter_id = vote_data.get("voter_id")
    candidate_id = vote_data.get("candidate_id")
    booth_id = vote_data.get("booth_id")

    async with AsyncSessionLocal() as session:
        try:
            existing_record = await session.scalar(
                select(VotingRecord).where(
                    VotingRecord.voter_id == voter_id
                )
            )

            if existing_record:
                logger.warning(
                    "Duplicate vote blocked for Voter ID: %s",
                    voter_id
                )
                return

            record = VotingRecord(
                voter_id=voter_id,
                candidate_id=candidate_id,
                booth_id=booth_id
            )

            session.add(record)
            await session.commit()

            logger.info(
                "Vote processed successfully for Request ID: %s",
                request_id
            )

            redis_pool = ctx.get("redis")

            if redis_pool:
                await redis_pool.hincrby(
                    "candidate_tallies",
                    str(candidate_id),
                    1
                )

        except IntegrityError:
            await session.rollback()

            logger.warning(
                "Duplicate vote blocked by DB constraint for Voter ID: %s",
                voter_id
            )

        except Exception as exc:
            await session.rollback()

            logger.error(
                "Vote processing failed: %s",
                exc,
                exc_info=True
            )
            raise


class WorkerSettings:
    functions = [process_vote_task]

    redis_settings = RedisSettings(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
    )
