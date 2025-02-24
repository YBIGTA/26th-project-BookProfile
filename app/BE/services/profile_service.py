from fastapi import HTTPException
from pymongo.database import Database

async def get_profile_info(db: Database, username: str):
    """
    MongoDB에서 username에 해당하는 사용자 프로필 정보를 조회합니다.
    """
    user = await db["users"].find_one({"name": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile_info = {
        "user_id": str(user.get("_id")),
        "name": user.get("name"),
        # 추가 정보...
    }
    return profile_info

async def get_friends_info(db: Database, username: str):
    """
    MongoDB에서 username에 해당하는 사용자의 친구를 조회합니다.
    """
    user = await db["users"].find_one({"name": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 사용자 문서의 friend 필드 (ObjectId 목록)를 가져옴
    friend_ids = user.get("friend", [])
    friend_names = []
    
    # 각 friend_id에 대해 users 컬렉션에서 친구 문서를 조회하고 이름을 추출
    for friend_id in friend_ids:
        friend_doc = await db["users"].find_one({"_id": friend_id})
        if friend_doc:
            friend_names.append(friend_doc.get("name"))
    
    # 최종적으로 친구 이름 목록으로 friend 정보를 구성
    friend_info = {
        "user_id": str(user.get("_id")),
        "friend": friend_names,
        # 추가 정보...
    }
    return friend_info

async def get_books_info(user_db: Database, crawling_db: Database, username: str):
    """
    MongoDB에서 username에 해당하는 사용자의 책 정보를 조회합니다.
    각 책에 대해 _id와 book_name을 함께 반환합니다.
    """
    user = await user_db["users"].find_one({"name": username})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 사용자 문서에 저장된 book 필드 (ObjectId 목록)를 가져옴
    book_ids = user.get("book", [])
    books_info = []
    
    # 각 book id로 books 컬렉션에서 책 정보를 조회하여 _id와 book_name을 가져옴
    for book_id in book_ids:
        book_doc = await crawling_db["books"].find_one({"_id": book_id})
        if book_doc:
            books_info.append({
                "id": str(book_doc.get("_id")),
                "book_name": book_doc.get("book_name"),
                "book_image": book_doc.get("book_image")
            })
    
    # book 필드를 책 정보 목록으로 대체하여 프로필 정보를 구성
    user_info = {
        "user_id": str(user.get("_id")),
        "books": books_info,
        # 추가 정보...
    }
    return user_info