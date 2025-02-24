from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

# MongoDB 클라이언트 생성
client = AsyncIOMotorClient(settings.MONGODB_URI)

# 데이터베이스 객체 생성
user_db = client.user
crawling_db = client.crawling

async def get_user_db():
    return user_db

async def get_crawling_db():
    return crawling_db

async def get_all_books():
    """Get all books from the crawling database"""
    db = await get_crawling_db()
    cursor = db.books.find({})
    return await cursor.to_list(length=None)

async def get_book_reviews(book_id):
    """Get all reviews for a specific book"""
    db = await get_crawling_db()
    cursor = db.reviews.find({"book_id": book_id})
    return await cursor.to_list(length=None)

async def update_book_embedding(book_id, embedding):
    """Update the embedding field of a book document"""
    db = await get_crawling_db()
    result = await db.books.update_one(
        {"_id": book_id},
        {"$set": {"embedding": embedding.tolist()}}
    )
    return result.modified_count > 0
