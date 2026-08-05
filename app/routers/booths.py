from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.factories import ServiceFactory
from app.schemas.domain import BoothCreate, BoothResponse

router = APIRouter()

@router.post("/", response_model=BoothResponse, status_code=status.HTTP_201_CREATED)
async def create_booth(payload: BoothCreate, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_polling_booth_service(db)
    booth = await service.create_polling_booth(payload)
    return booth

@router.get("/{booth_id}", response_model=BoothResponse)
async def get_booth(booth_id: int, db: AsyncSession = Depends(get_db)):
    service = ServiceFactory.get_polling_booth_service(db)
    booth = await service.get_booth_by_id(booth_id)
    if not booth:
        raise HTTPException(status_code=404, detail="Polling booth not found")
    return booth