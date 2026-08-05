import uuid
from pydantic import BaseModel


class VotePayload(BaseModel):
    voter_id: uuid.UUID
    candidate_id: uuid.UUID
    booth_id: uuid.UUID


class VoteResponse(BaseModel):
    status: str
    transaction_id: str