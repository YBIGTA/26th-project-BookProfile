"""리뷰 데이터 확인 스크립트"""

import asyncio
from ..database.mongodb import get_crawling_db

async def check_reviews():
    db = await get_crawling_db()
    
    # 리뷰어별 리뷰 수 확인
    pipeline = [
        {"$group": {
            "_id": "$reviewer_name",
            "unique_books": {"$addToSet": "$book_id"},
            "review_count": {"$sum": 1}
        }},
        {"$project": {
            "reviewer_name": "$_id",
            "unique_book_count": {"$size": "$unique_books"},
            "review_count": 1,
            "_id": 0
        }},
        {"$sort": {"review_count": -1}},
        {"$limit": 10}
    ]
    
    results = await db.reviews.aggregate(pipeline).to_list(length=None)
    
    print("\n상위 10명의 리뷰어:")
    print("리뷰어명 | 리뷰한 책 수 | 전체 리뷰 수")
    print("-" * 40)
    for r in results:
        print(f"{r['reviewer_name']} | {r['unique_book_count']} | {r['review_count']}")

if __name__ == "__main__":
    asyncio.run(check_reviews())
