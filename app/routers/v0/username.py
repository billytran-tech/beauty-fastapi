from fastapi import APIRouter, status, Depends
from pydantic import ConfigDict, BaseModel
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database.database import get_db

router = APIRouter(
    prefix='/api/username',
    tags=['Username Management']
)


class UsernameAvailabilityResponse(BaseModel):
    username: str
    available: bool

    model_config = ConfigDict(populate_by_name=True,
                              arbitrary_types_allowed=True)


@router.get("/{username}", status_code=status.HTTP_200_OK, response_model=UsernameAvailabilityResponse)
async def get_username_availability(username: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    db_username = await db['usernames'].find_one({'username': username})
    if not db_username:
        return {
            "username": username,
            "available": True
        }
    else:
        return {
            "username": username,
            "available": False
        }
