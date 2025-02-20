from fastapi import HTTPException, Request, status
from pymongo.database import Database
from ..models.user import User

async def get_survey_books(db: Database):
    books = await db["survey"].find({}).to_list(length=None)
    return {"books": books}

async def get_survey_status(username: str, db: Database):
    user = await db["users"].find_one(
        {"name": username},
        {"survey_completed": 1}
    )
    return user["survey_completed"]

async def update_survey_status(username: str, db: Database):
    result = await db["users"].update_one(
        {"name": username},
        {"$set": {"survey_completed": True}}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 상태 업데이트에 실패하였습니다."
        )
    return result