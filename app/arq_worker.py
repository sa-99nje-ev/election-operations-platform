import uuid
from app.database import AsyncSessionLocal
from app.models.voting_record import VotingRecord

async def process_vote_task(ctx, vote_payload: dict):
    session_factory = ctx.get("db_session") or AsyncSessionLocal
    req_id = vote_payload.get("request_id") or str(uuid.uuid4())
    tx_id = vote_payload.get("transaction_id") or f"TX-{uuid.uuid4().hex[:8].upper()}"
    
    async with session_factory() as db:
        async with db.begin():
            record = VotingRecord(
                id=uuid.UUID(req_id) if isinstance(req_id, str) else req_id,
                voter_id=uuid.UUID(vote_payload["voter_id"]) if isinstance(vote_payload.get("voter_id"), str) else vote_payload["voter_id"],
                candidate_id=uuid.UUID(vote_payload["candidate_id"]) if isinstance(vote_payload.get("candidate_id"), str) else vote_payload["candidate_id"],
                polling_booth_id=uuid.UUID(vote_payload["booth_id"]) if isinstance(vote_payload.get("booth_id"), str) else vote_payload["booth_id"],
                transaction_id=tx_id
            )
            db.add(record)
            
    return {
        "status": "SUCCESS",
        "request_id": req_id,
        "transaction_id": tx_id
    }
