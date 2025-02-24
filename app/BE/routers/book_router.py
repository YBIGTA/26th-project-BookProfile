from fastapi import APIRouter, Depends
from pymongo.database import Database
from ..database.mongodb import get_crawling_db, get_user_db
from ..services.auth_service import require_login
from ..services.book_service import get_book_info, add_book_to_user

router = APIRouter(
    prefix="/book",
    tags=["book"]
)

@router.get("/{book_id}", response_model=dict)
async def book_info(
    book_id : str,
    crawling_db: Database = Depends(get_crawling_db),
    current_user: str = Depends(require_login)
):
    book = await get_book_info(crawling_db, book_id)
    return book

@router.get("/{book_id}/add", response_model=dict)
async def add_book(
    book_id: str,
    crawling_db: Database = Depends(get_crawling_db),
    user_db: Database = Depends(get_user_db),
    current_user: str = Depends(require_login)
):
    result = add_book_to_user(crawling_db, user_db, current_user, book_id)
    return result