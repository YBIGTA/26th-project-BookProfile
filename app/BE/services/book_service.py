from bson import ObjectId
from fastapi import HTTPException
from pymongo.database import Database

async def add_book_to_user(db: Database, username: str, book_name: str):
    """
    주어진 username에 해당하는 사용자의 books 필드에,
    books 컬렉션에서 book_name에 해당하는 책의 _id를 추가합니다.
    """
    # books 컬렉션에서 book_name에 해당하는 책을 조회합니다.
    book = await db["books"].find_one({"book_name": book_name})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # 책의 _id를 가져옵니다.
    book_id = book["_id"]
    
    # 사용자의 문서에서 books 필드에 책의 _id를 추가합니다.
    # $addToSet은 이미 존재하는 값은 추가하지 않습니다.
    result = await db["users"].update_one(
        {"name": username},
        {"$addToSet": {"book": book_id}}
    )
    
    # result.modified_count가 0이면 이미 추가되었거나 사용자가 존재하지 않을 수 있음.
    return book_id

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
    # MongoDB의 ObjectId를 문자열로 변환하여 반환
    book["_id"] = str(book["_id"])
    return book