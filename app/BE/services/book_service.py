from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database

async def add_book_to_user(book_db: Database, user_db: Database, username: str, book_id: str):
    """
    주어진 username에 해당하는 사용자의 book 필드에,
    books 컬렉션에서 book_name에 해당하는 책의 _id를 추가합니다.
    """
    # books 컬렉션에서 book_name에 해당하는 책을 조회합니다.
    book = await book_db["books"].find_one({"_id": book_id})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 사용자의 문서에서 book 필드에 책의 _id를 추가합니다.
    # $addToSet은 이미 존재하는 값은 추가하지 않습니다.
    result = await user_db["users"].update_one(
        {"name": username},
        {"$addToSet": {"book": book_id}}
    )
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사용자 상태 업데이트에 실패하였습니다."
        )
    return result

async def get_book_info(db: Database, book_id: str):
    """
    주어진 book_id(ObjectId)에 해당하는 책 정보를 MongoDB에서 조회하여 반환합니다.
    """
    try:
        object_id = ObjectId(book_id)  # 문자열을 ObjectId로 변환
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid book ID format")

    book = await db["books"].find_one({"_id": object_id})
    
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if "embedding" in book:
        del book["embedding"]
    if "reviews" in book:
        del book["reviews"]
    # MongoDB의 ObjectId를 문자열로 변환하여 반환
    book["_id"] = str(book["_id"])
    return book