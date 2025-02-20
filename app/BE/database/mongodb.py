from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

# MongoDB 클라이언트 생성
client = AsyncIOMotorClient(settings.MONGODB_URI)

# 데이터베이스 객체 생성
user_db = client.get_database("user")
crawling_db = client.get_database("crawling")

async def get_user_db():
    return user_db

async def get_crawling_db():
    return crawling_db
