from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.candidate import Candidate
from app.models.constituency import Constituency
from app.models.voting_record import VotingRecord

router = APIRouter(prefix="/results", tags=["Results & Tallies"])


@router.get("/overall", response_model=List[dict])
async def get_overall_results(db: AsyncSession = Depends(get_db)):
    """Fetch total accumulated votes grouped by candidate across all constituencies."""
    stmt = (
        select(
            Candidate.id.label("candidate_id"),
            Candidate.full_name,
            Candidate.party,
            Constituency.name.label("constituency_name"),
            func.count(VotingRecord.id).label("total_votes"),
        )
        .join(Constituency, Candidate.constituency_id == Constituency.id)
        .outerjoin(VotingRecord, VotingRecord.candidate_id == Candidate.id)
        .group_by(Candidate.id, Candidate.full_name, Candidate.party, Constituency.name)
        .order_by(func.count(VotingRecord.id).desc())
    )
    results = await db.execute(stmt)
    return [
        {
            "candidate_id": row.candidate_id,
            "candidate_name": row.full_name,
            "party": row.party,
            "constituency": row.constituency_name,
            "total_votes": row.total_votes,
        }
        for row in results.all()
    ]


@router.get("/constituency/{constituency_id}", response_model=dict)
async def get_constituency_results(
    constituency_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """Fetch vote tallies broken down by candidate for a specific constituency."""
    constituency = await db.get(Constituency, constituency_id)
    if not constituency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Constituency not found"
        )

    stmt = (
        select(
            Candidate.id.label("candidate_id"),
            Candidate.full_name,
            Candidate.party,
            func.count(VotingRecord.id).label("votes"),
        )
        .where(Candidate.constituency_id == constituency_id)
        .outerjoin(VotingRecord, VotingRecord.candidate_id == Candidate.id)
        .group_by(Candidate.id, Candidate.full_name, Candidate.party)
        .order_by(func.count(VotingRecord.id).desc())
    )
    results = await db.execute(stmt)

    candidates_tally = [
        {
            "candidate_id": row.candidate_id,
            "candidate_name": row.full_name,
            "party": row.party,
            "votes": row.votes,
        }
        for row in results.all()
    ]

    total_constituency_votes = sum(c["votes"] for c in candidates_tally)

    return {
        "constituency_id": constituency.id,
        "constituency_name": constituency.name,
        "total_votes_cast": total_constituency_votes,
        "results": candidates_tally,
    }
