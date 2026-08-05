from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.factories import ServiceFactory
from app.schemas.domain import CandidateCreate, CandidateResponse

router = APIRouter()

@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def register_candidate(payload: CandidateCreate, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_candidate_service(db)
    candidate = await service.register_candidate(payload)
    return candidate

@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: int, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_candidate_service(db)
    candidate = await service.get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate