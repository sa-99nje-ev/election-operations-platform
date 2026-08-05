from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.factories import ServiceFactory
from app.schemas.voting import VotePayload, VoteResponse

router = APIRouter()

@router.post("/cast", response_model=VoteResponse, status_code=status.HTTP_200_OK)
async def cast_vote(payload: VotePayload, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_voting_service(db)
    result = await service.validate_and_enqueue_vote(
        voter_id=payload.voter_id,
        candidate_id=payload.candidate_id,
        booth_id=payload.booth_id
    )
    return result