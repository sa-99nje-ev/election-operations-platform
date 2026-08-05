import uuid
from datetime import date
from pydantic import BaseModel, ConfigDict


class ConstituencyBase(BaseModel):
    name: str
    region: str


class ConstituencyCreate(ConstituencyBase):
    pass


class ConstituencyResponse(ConstituencyBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class BoothBase(BaseModel):
    booth_code: str
    location: str
    capacity: int
    constituency_id: uuid.UUID
    status: str = "active"


class BoothCreate(BoothBase):
    pass


class BoothResponse(BoothBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class CandidateBase(BaseModel):
    national_id: str
    full_name: str
    party: str
    constituency_id: uuid.UUID


class CandidateCreate(CandidateBase):
    pass


class CandidateResponse(CandidateBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)


class VoterBase(BaseModel):
    national_id: str
    full_name: str
    dob: date
    constituency_id: uuid.UUID
    status: str = "active"


class VoterCreate(VoterBase):
    pass


class VoterResponse(VoterBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)