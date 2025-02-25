from fastapi import APIRouter
from .auth_router import router as auth_router
from .home_router import router as home_router
from .profile_router import router as profile_router
from .survey_router import router as survey_router
from .book_router import router as book_router
from .similar_users import router as similar_users_router



router = APIRouter()

router.include_router(auth_router)
router.include_router(home_router)
router.include_router(profile_router)
router.include_router(survey_router)
router.include_router(book_router)
router.include_router(similar_users_router)