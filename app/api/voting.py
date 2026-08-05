"""
FastAPI Voting API Router with Singleton Redis Pool and Complete Schemas.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, UUID4, Field

# Standard OpenAPI response map for Schemathesis
VOTE_RESPONSES = {
    202: {"description": "Vote accepted and queued for processing"},
    400: {"description": "Malformed request payload"},
    401: {"description": "Not authenticated"},
    422: {"description": "Validation Error (Invalid UUID format)"},
}

router = APIRouter(prefix="/vote", tags=["Voting"], responses=VOTE_RESPONSES)


class VoteRequest(BaseModel):
    voter_id: UUID4 = Field(..., example="a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
    candidate_id: UUID4 = Field(..., example="b1fefd00-0d1c-4fa9-cc7e-7cc0ce491b22")
    booth_id: UUID4 = Field(..., example="c20f0e11-1e2d-40ba-dd8f-8dd1df502c33")

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

    # Get singleton Redis pool from FastAPI app state (initialized in main.py lifespan)
    redis = getattr(request.app.state, "redis_pool", None)
    
    if not redis:
        # Fallback if app.state isn't attached during quick isolated tests
        from arq import create_pool
        from arq.connections import RedisSettings
        redis = await create_pool(RedisSettings(host="localhost", port=6379))

    await redis.enqueue_job(
        "process_vote_task",
        vote_data={
            "request_id": request_id,
            "voter_id": str(payload.voter_id),
            "candidate_id": str(payload.candidate_id),
            "booth_id": str(payload.booth_id),
        },
        _job_id=request_id  # Native ARQ job idempotency
    )

    return {
        "success": True,
        "message": "Vote accepted for processing",
        "data": {
            "request_id": request_id,
            "status": "QUEUED"
        }
    }