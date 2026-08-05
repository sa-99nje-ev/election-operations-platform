import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.factories import ServiceFactory
from app.schemas.domain import VoterCreate, VoterResponse

router = APIRouter()


@router.post("/", response_model=VoterResponse, status_code=status.HTTP_201_CREATED)
async def register_voter(payload: VoterCreate, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_voter_service(db)
    voter = await service.register_voter(payload)
    return voter


@router.get("/{voter_id}", response_model=VoterResponse)
async def get_voter(voter_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_voter_service(db)
    voter = await service.get_voter_by_id(voter_id)
    if not voter:
        raise HTTPException(status_code=404, detail="Voter not found")
    return voter
