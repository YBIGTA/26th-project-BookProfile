"""
Book Embedding Generation Module
--------------------------------
문서 리뷰 기반 책 임베딩 생성을 위한 유틸리티 모듈
"""

from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer

# 모델 상수 정의
_MODEL_NAME = "all-MiniLM-L6-v2"
_EMBEDDING_DIM = 384  # 사용 모델의 출력 차원

# 전역 모델 로드 (모듈 최초 임포트 시 단 한 번 실행)
_encoder = SentenceTransformer(_MODEL_NAME)

__all__ = ["generate_book_embedding"]

def generate_book_embedding(book_data: Dict[str, Any]) -> np.ndarray:
    """
    책 JSON 데이터에서 리뷰 임베딩의 평균 벡터 계산
    
    Parameters
    ----------
    book_data : Dict[str, Any]
        다음 키를 포함하는 책 데이터 딕셔너리:
        - reviews: List[Dict[str, str]] (필수)
        - 기타 메타데이터 필드 (옵션)

    Returns
    -------
    np.ndarray
        평균 임베딩 벡터 (shape: (_EMBEDDING_DIM,))

    Examples
    --------
    >>> book_data = {
    ...     "reviews": [
    ...         {"review": "Excellent book!", "rating": 5},
    ...         {"review": "Highly recommended", "rating": 4}
    ...     ]
    ... }
    >>> embedding = generate_book_embedding(book_data)
    >>> embedding.shape
    (384,)
    
    Notes
    -----
    - 리뷰가 없는 경우 zero vector 반환
    - 문자열이 아닌 리뷰는 자동 필터링
    """
    if not book_data or not isinstance(book_data, dict):
        return np.zeros(_EMBEDDING_DIM, dtype=np.float32)
        
    valid_reviews = [
        str(review.get('review', '')).strip()
        for review in book_data.get('reviews', [])
        if review is not None  # null 리뷰 필터링
    ]
    
    if valid_reviews:
        embeddings = _encoder.encode(valid_reviews, convert_to_numpy=True)
        return np.mean(embeddings, axis=0)
        
    return np.zeros(_EMBEDDING_DIM, dtype=np.float32)