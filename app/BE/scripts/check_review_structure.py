"""리뷰 문서 구조 확인 스크립트"""

import asyncio
from ..database.mongodb import get_crawling_db

async def check_review_structure():
    db = await get_crawling_db()
    
    # 첫 번째 리뷰 문서 가져오기
    review = await db.reviews.find_one()
    
    if review:
        print("\n리뷰 문서 구조:")
        for key in review:
            print(f"{key}: {type(review[key])}")
            if isinstance(review[key], (str, int, float)):
                print(f"  예시 값: {review[key]}")

if __name__ == "__main__":
    asyncio.run(check_review_structure())
