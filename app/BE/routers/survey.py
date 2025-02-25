"""
Survey Router
------------
설문 관련 엔드포인트를 처리하는 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict

from ..database.mongodb import get_crawling_db, get_user_db
from ..models.user import User
from ..schemas.survey import Rating, SurveyResponse
from ..services.survey_service import (
    get_survey_books,
    get_survey_status,
    process_survey_completion
)

router = APIRouter(
    prefix="/api",
    tags=["survey"]
)

@router.get("/survey/books")
async def get_books_for_survey():
    """설문에 사용될 책 목록을 조회"""
    db = await get_crawling_db()
    return await get_survey_books(db)

@router.get("/survey/status/{username}")
async def check_survey_status(username: str):
    """사용자의 설문 완료 상태를 조회"""
    db = await get_user_db()
    status = await get_survey_status(username, db)
    return {"survey_completed": status}

@router.post("/survey/complete")
async def complete_survey(survey_data: SurveyResponse):
    """
    설문 완료 처리
    - 사용자 임베딩 계산
    - 다른 사용자와의 유사도 계산 및 저장
    - 설문 완료 상태 업데이트
    """
    try:
        await process_survey_completion(
            user_id=survey_data.user_id,
            ratings=survey_data.ratings
        )
        return {
            "status": "success",
            "message": "설문이 성공적으로 처리되었습니다."
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"설문 처리 중 오류가 발생했습니다: {str(e)}"
        )
