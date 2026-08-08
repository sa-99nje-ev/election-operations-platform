"""
ARQ Background Worker for processing queued votes.
"""

import logging
import uuid

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

    voter_id = uuid.UUID(vote_data["voter_id"])
    candidate_id = uuid.UUID(vote_data["candidate_id"])
    booth_id = uuid.UUID(vote_data["booth_id"])

    async with AsyncSessionLocal() as session:
        try:
            existing_record = await session.scalar(
                select(VotingRecord).where(
                    VotingRecord.voter_id == voter_id
                )
            )

            if existing_record:
                logger.warning(
                    f"Duplicate vote blocked for Voter ID: {voter_id}"
                )
                return {
                    "status": "DUPLICATE",
                    "request_id": request_id
                }

            record = VotingRecord(
                voter_id=voter_id,
                candidate_id=candidate_id,
                polling_booth_id=booth_id
            )

            session.add(record)
            await session.commit()

            logger.info(
                f"Vote processed successfully for Request ID: {request_id}"
            )

            redis_pool = ctx.get("redis")

            if redis_pool:
                await redis_pool.hincrby(
                    "candidate_tallies",
                    str(candidate_id),
                    1
                )

            return {
                "status": "SUCCESS",
                "request_id": request_id
            }

        except IntegrityError:
            await session.rollback()

            logger.warning(
                f"Duplicate vote blocked by DB constraint "
                f"for Voter ID: {voter_id}"
            )

            return {
                "status": "DUPLICATE",
                "request_id": request_id
            }

        except Exception as exc:
            await session.rollback()

            logger.exception(
                f"Vote processing failed for Request ID: {request_id}: {exc}"
            )

            raise


class WorkerSettings:
    functions = [process_vote_task]

    redis_settings = RedisSettings(
        host="localhost",
        port=6379
    )
