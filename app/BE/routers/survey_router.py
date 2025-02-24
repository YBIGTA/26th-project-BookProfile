from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from fastapi.responses import RedirectResponse
from ..services.auth_service import require_login
from ..services.survey_service import get_survey_books, update_survey_status
from ..database.mongodb import get_user_db, get_crawling_db
from ..schemas.survey import SurveyInput
from ..models.user import UserEmbedding

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
    survey_input: SurveyInput,
    user_db: Database = Depends(get_user_db),
    db: Database = Depends(get_crawling_db),
    current_user: str = Depends(require_login)
):
    # 1. 설문 완료 상태 업데이트
    await update_survey_status(current_user, user_db)
    
    # 2. 사용자 임베딩 생성
    user_embedding = UserEmbedding()
    embedding = await user_embedding.calculate_embedding(survey_input.ratings)
    
    # 3. 임베딩 저장 (유효한 임베딩이 생성된 경우에만)
    if embedding is not None:
        await user_embedding.save_embedding(current_user, embedding)
    
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
