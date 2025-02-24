from fastapi import APIRouter, Depends
from pymongo.database import Database
from ..database.mongodb import get_user_db, get_crawling_db
from ..services.profile_service import get_profile_info, get_friends_info, get_books_info
from ..services.auth_service import require_login

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.get("/{username}", response_model=dict)
async def read_profile(
    username: str,
    db: Database = Depends(get_user_db),
    current_user: str = Depends(require_login)
):
    """
    GET /user/{username}
    - 해당 username의 프로필 페이지
    """
    profile = await get_profile_info(db, username)
    return profile

@router.get("/{username}/friend", response_model=dict)
async def read_friend_list(
    username: str,
    db: Database = Depends(get_user_db),
    current_user: str = Depends(require_login)
):
    """
    GET /user/{username}/friend
    - username이 팔로잉/친구 관계인 사람들 리스트
    """
    friends = await get_friends_info(db, username)
    return friends

@router.get("/{username}/book", response_model=dict)
async def read_book_list(
    username: str,
    user_db: Database = Depends(get_user_db),
    crawling_db: Database = Depends(get_crawling_db),
    current_user: str = Depends(require_login)
):
    """
    GET /user/{username}/book
    - username이 읽은/추가한 책들 리스트
    """
    books = await get_books_info(user_db, crawling_db, username)
    return books