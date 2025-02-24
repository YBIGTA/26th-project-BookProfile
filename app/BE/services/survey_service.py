from fastapi import HTTPException, Request, status
from pymongo.database import Database
from ..models.user import User
from .book_service import get_book_info

async def get_survey_books(db: Database):
    documents = await db["survey"].find({}).to_list(length=None)
    result = []
    for doc in documents:
        # 각 도큐먼트에서 book_id 필드를 추출합니다.
        book_id = doc.get("book_id")
        if book_id is not None:
            # book_id를 이용해 get_book_info 함수를 호출합니다.
            # 만약 get_book_info가 비동기 함수라면 await을 사용하세요.
            book_info = await get_book_info(db, book_id)  # 비동기 함수인 경우
            result.append(book_info)
    
    return result

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