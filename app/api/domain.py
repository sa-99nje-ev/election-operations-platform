"""
FastAPI Domain Routers for Constituencies, Polling Booths, Candidates, and Voters.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.utils.rbac import require_roles, admin_required, officer_required
from app.models.user import User
from app.models.constituency import Constituency
from app.models.polling_booth import PollingBooth
from app.models.candidate import Candidate
from app.models.voter import Voter

from app.repositories.constituency_repository import ConstituencyRepository
from app.repositories.polling_booth_repository import PollingBoothRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.voter_repository import VoterRepository

from app.schemas.domain import (
    ConstituencyCreate, ConstituencyResponse,
    BoothCreate, BoothResponse,
    CandidateCreate, CandidateResponse,
    VoterCreate, VoterResponse
)

# Standard error response dictionary for OpenAPI schema generation
AUTH_RESPONSES = {
    400: {"description": "Bad Request or Malformed Payload"},
    401: {"description": "Not authenticated"},
    403: {"description": "Insufficient permissions"},
    422: {"description": "Validation Error"},
}

# --- Constituency Router ---
constituency_router = APIRouter(
    prefix="/constituencies",
    tags=["Constituencies"],
    responses=AUTH_RESPONSES
)

@constituency_router.post("", response_model=ConstituencyResponse, status_code=status.HTTP_201_CREATED)
async def create_constituency(
    payload: ConstituencyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    repo = ConstituencyRepository(db)
    entity = Constituency(**payload.model_dump())
    created = await repo.create(entity)
    await db.commit()
    return created

@constituency_router.get("", response_model=List[ConstituencyResponse])
async def list_constituencies(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = ConstituencyRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


# --- Polling Booth Router ---
booth_router = APIRouter(
    prefix="/booths",
    tags=["Polling Booths"],
    responses=AUTH_RESPONSES
)

@booth_router.post("", response_model=BoothResponse, status_code=status.HTTP_201_CREATED)
async def create_booth(
    payload: BoothCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(officer_required)
):
    repo = PollingBoothRepository(db)
    entity = PollingBooth(**payload.model_dump())
    created = await repo.create(entity)
    await db.commit()
    return created

@booth_router.get("", response_model=List[BoothResponse])
async def list_booths(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = PollingBoothRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


# --- Candidate Router ---
candidate_router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
    responses=AUTH_RESPONSES
)

@candidate_router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    payload: CandidateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(officer_required)
):
    repo = CandidateRepository(db)
    entity = Candidate(**payload.model_dump())
    created = await repo.create(entity)
    await db.commit()
    return created

@candidate_router.get("", response_model=List[CandidateResponse])
async def list_candidates(
    skip: int = 0, limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = CandidateRepository(db)
    return await repo.get_all(skip=skip, limit=limit)


# --- Voter Router ---
voter_router = APIRouter(
    prefix="/voters",
    tags=["Voters"],
    responses=AUTH_RESPONSES
)

@voter_router.post("", response_model=VoterResponse, status_code=status.HTTP_201_CREATED)
async def register_voter(
    payload: VoterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(officer_required)
):
    repo = VoterRepository(db)
    entity = Voter(**payload.model_dump())
    created = await repo.create(entity)
    await db.commit()
    return created

@voter_router.get(
    "/{voter_id}",
    response_model=VoterResponse,
    responses={
        404: {"description": "Voter not found"},
        **AUTH_RESPONSES
    }
)
async def get_voter(
    voter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repo = VoterRepository(db)
    voter = await repo.get_by_id(voter_id)
    if not voter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voter not found")
    return voter