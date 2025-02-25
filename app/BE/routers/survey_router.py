from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from fastapi.responses import RedirectResponse
from ..services.auth_service import require_login
from ..services.survey_service import get_survey_books, process_survey_completion
from ..database.mongodb import get_user_db, get_crawling_db
from ..schemas.survey import SurveyResponse

router = APIRouter(
    prefix="/survey",
    tags=["survey"]
)


@router.get("/", response_model=dict)
async def survey(
    db: Database = Depends(get_crawling_db),
    current_user: str = Depends(require_login)
):
    result = await get_survey_books(db)
    return {"books" : result}


@router.post("/", response_model=dict)
async def survey_completed(
    survey_data: SurveyResponse,
    current_user: str = Depends(require_login)
):
    """
    설문 완료 처리:
    - 임베딩 계산
    - 유사도 계산 및 저장
    - 설문 완료 상태 업데이트
    """
    await process_survey_completion(current_user, survey_data.ratings)
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
