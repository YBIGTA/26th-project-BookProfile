"""
Calculate Initial Similarities Script
----------------------------------
기존 유저들의 임베딩을 기반으로 유사도를 계산하고 저장하는 스크립트
"""

import asyncio
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from ..database.mongodb import get_user_db
from ..models.user_similarity import UserSimilarity

async def calculate_all_similarities():
    """모든 유저 쌍에 대해 유사도 계산 및 저장"""
    db = await get_user_db()
    
    # 임베딩이 있는 모든 유저 조회
    users = await db.users.find(
        {"embedding": {"$exists": True}},
        {"_id": 1, "embedding": 1}
    ).to_list(length=None)
    
    print(f"Found {len(users)} users with embeddings")
    
    # 각 유저에 대해 다른 모든 유저와의 유사도 계산
    for i, user in enumerate(users):
        user_id = str(user["_id"])
        user_embedding = np.array(user["embedding"])
        
        # 다른 유저들과의 유사도 계산
        similarities = {}
        for other_user in users:
            other_id = str(other_user["_id"])
            if other_id != user_id:  # 자기 자신은 제외
                other_embedding = np.array(other_user["embedding"])
                similarity = cosine_similarity(
                    user_embedding.reshape(1, -1),
                    other_embedding.reshape(1, -1)
                )[0][0]
                similarities[other_id] = float(similarity)
        
        # UserSimilarity 문서 생성
        similarity_doc = UserSimilarity(
            user_id=user_id,
            similarities=similarities
        )
        
        # MongoDB에 저장
        await db.user_similarities.update_one(
            {"user_id": user_id},
            {"$set": similarity_doc.model_dump()},
            upsert=True
        )
        
        print(f"Processed user {i+1}/{len(users)}: {user_id}")
        
        # 상위 5개 유사도 출력
        top_5 = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Top 5 similarities:")
        for other_id, score in top_5:
            print(f"- {other_id}: {score:.3f}")
        print()

if __name__ == "__main__":
    asyncio.run(calculate_all_similarities())
