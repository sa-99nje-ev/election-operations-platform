"""
FastAPI Voting API Router with Singleton Redis Pool and Complete Schemas.
"""

import os
import uuid

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, UUID4, Field


VOTE_RESPONSES = {
    202: {"description": "Vote accepted and queued for processing"},
    400: {"description": "Malformed request payload"},
    401: {"description": "Not authenticated"},
    422: {"description": "Validation Error (Invalid UUID format)"},
}


router = APIRouter(
    prefix="/vote",
    tags=["Voting"],
    responses=VOTE_RESPONSES
)


class VoteRequest(BaseModel):
    voter_id: UUID4 = Field(
        ...,
        example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
    )
    candidate_id: UUID4 = Field(
        ...,
        example="b1fefd00-0d1c-4fa9-cc7e-7cc0ce491b22"
    )
    booth_id: UUID4 = Field(
        ...,
        example="c20f0e11-1e2d-40ba-dd8f-8dd1df502c33"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "voter_id": "123e4567-e89b-12d3-a456-426614174000",
                "candidate_id": "123e4567-e89b-12d3-a456-426614174001",
                "booth_id": "123e4567-e89b-12d3-a456-426614174002"
            }
        }


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    responses=VOTE_RESPONSES
)
async def cast_vote(payload: VoteRequest, request: Request):
    request_id = str(uuid.uuid4())

    # Use the singleton Redis pool initialized by the FastAPI lifespan.
    redis = getattr(request.app.state, "redis_pool", None)

    # Fallback for isolated tests where app.state.redis_pool
    # has not been initialized.
    if redis is None:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", "6379"))

        redis = await create_pool(
            RedisSettings(
                host=redis_host,
                port=redis_port
            )
        )

    await redis.enqueue_job(
        "process_vote_task",
        vote_data={
            "request_id": request_id,
            "voter_id": str(payload.voter_id),
            "candidate_id": str(payload.candidate_id),
            "booth_id": str(payload.booth_id),
        },
        _job_id=request_id
    )

    return {
        "success": True,
        "message": "Vote accepted for processing",
        "data": {
            "request_id": request_id,
            "status": "QUEUED"
        }
    }
