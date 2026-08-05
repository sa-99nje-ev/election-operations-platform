from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.factories import ServiceFactory
from app.schemas.domain import ConstituencyCreate, ConstituencyResponse

router = APIRouter()

@router.post("/", response_model=ConstituencyResponse, status_code=status.HTTP_201_CREATED)
async def create_constituency(payload: ConstituencyCreate, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_constituency_service(db)
    constituency = await service.create_constituency(payload)
    return constituency

@router.get("/{constituency_id}", response_model=ConstituencyResponse)
async def get_constituency(constituency_id: int, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_constituency_service(db)
    constituency = await service.get_constituency_by_id(constituency_id)
    if not constituency:
        raise HTTPException(status_code=404, detail="Constituency not found")
    return constituency