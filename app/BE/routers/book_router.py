from fastapi import APIRouter, Depends
from pymongo.database import Database
from ..database.mongodb import get_crawling_db
from ..services.auth_service import require_login
from ..services.book_service import get_book_info

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