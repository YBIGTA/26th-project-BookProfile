"""
Check Users Script
----------------
데이터베이스에 저장된 유저 정보를 확인하는 스크립트
"""

import asyncio
from ..database.mongodb import get_user_db

async def check_users():
    """유저 정보 확인"""
    db = await get_user_db()
    
    # 임베딩이 있는 유저 조회
    users = await db.users.find(
        {"embedding": {"$exists": True}},
        {"_id": 1, "name": 1}
    ).to_list(length=5)  # 처음 5명만 확인
    
    print("\n=== 임베딩이 있는 유저 목록 ===")
    for user in users:
        print(f"ID: {user['_id']}, Name: {user['name']}")
    
    # 유사도 정보 확인
    similarities = await db.user_similarities.find(
        {},
        {"user_id": 1, "similarities": 1}
    ).to_list(length=1)  # 첫 번째 문서만 확인
    
    if similarities:
        similarity = similarities[0]
        print("\n=== 유사도 정보 예시 ===")
        print(f"User ID: {similarity['user_id']}")
        sorted_similarities = sorted(
            similarity['similarities'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # 상위 5개만
        print("Top 5 Similar Users:")
        for other_id, score in sorted_similarities:
            print(f"- User {other_id}: {score:.3f}")
    else:
        print("\n유사도 정보가 없습니다.")

if __name__ == "__main__":
    asyncio.run(check_users())
