from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from fastapi.responses import RedirectResponse
from ..services.auth_service import require_login
from ..services.survey_service import get_survey_books, update_survey_status
from ..database.mongodb import get_user_db, get_crawling_db
from ..schemas.survey import SurveyInput

router = APIRouter(
    prefix="/survey",
    tags=["survey"]
)


@router.get("/", response_model=dict)
async def survey(
    db: Database = Depends(get_crawling_db),
    current_user: str = Depends(require_login)
):
    return get_survey_books(db)


@router.post("/", response_model=dict)
async def survey_completed(
    survey_input: SurveyInput,
    user_db: Database = Depends(get_user_db),
    db: Database = Depends(get_crawling_db),
    current_user: str = Depends(require_login)
):
    # user 상태 변경
    await update_survey_status(current_user, user_db)
    """
    모델 호출 로직!!!
    """
    return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)


