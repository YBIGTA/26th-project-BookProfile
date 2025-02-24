"""
Book Embedding Generation Script
------------------------------
MongoDB의 book 컬렉션에서 책 데이터를 가져와 리뷰 기반 임베딩을 생성하고
해당 book 도큐먼트에 저장하는 스크립트
"""

import asyncio
from typing import Dict, List, Any
import numpy as np
from tqdm import tqdm

from ..database.mongodb import get_all_books, get_book_reviews, update_book_embedding
from .book_embedding import generate_book_embedding

async def process_book(book: Dict[str, Any]) -> bool:
    """
    단일 책에 대한 임베딩을 생성하고 저장

    Args:
        book: MongoDB의 book 도큐먼트

    Returns:
        bool: 임베딩 생성 및 저장 성공 여부
    """
    # 책의 모든 리뷰 가져오기
    reviews = await get_book_reviews(book["_id"])
    
    # 리뷰가 없으면 건너뛰기
    if not reviews:
        return False
        
    # 리뷰 데이터 포맷 변환
    book_data = {"reviews": reviews}
    
    # 임베딩 생성
    embedding = generate_book_embedding(book_data)
    
    # 임베딩 저장
    success = await update_book_embedding(book["_id"], embedding)
    return success

async def generate_all_embeddings():
    """
    모든 책에 대해 임베딩을 생성하고 저장
    """
    # 카운터 초기화
    total_books = 0
    processed_books = 0
    skipped_books = 0
    
    # 모든 책 가져오기
    books = await get_all_books()
    total_books = len(books)
    
    print(f"총 {total_books}권의 책을 처리합니다...")
    
    # 각 책에 대해 임베딩 생성
    for book in tqdm(books, desc="임베딩 생성 중"):
        success = await process_book(book)
        if success:
            processed_books += 1
        else:
            skipped_books += 1
    
    # 결과 출력
    print("\n처리 완료!")
    print(f"총 책 수: {total_books}")
    print(f"임베딩 생성된 책: {processed_books}")
    print(f"건너뛴 책 (리뷰 없음): {skipped_books}")

if __name__ == "__main__":
    asyncio.run(generate_all_embeddings())
