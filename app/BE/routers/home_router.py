from fastapi import APIRouter, Form, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse
from pymongo.database import Database
from ..database.mongodb import get_user_db, get_crawling_db
from ..services.auth_service import require_login

router = APIRouter(
    prefix="/home",
    tags=["home"]
)

@router.get("/", response_class=HTMLResponse)
def get_home(
    db: Database = Depends(get_user_db),
    current_user: str = Depends(require_login)
):
    """
    GET /home:
    - 메인 홈페이지
    """
    html_content = f"""
    <h1>Home Page</h1>
    <ul>
      <li><a href="/user/{current_user}">내 프로필</a></li>
      <li><a href="/home/recommend">책 추천</a></li>
      <li><a href="/logout">로그아웃</a></li>
    </ul>
    """
    return html_content

@router.get("/recommend", response_class=HTMLResponse)
def get_recommend_form():
    """
    GET /home/recommend:
    - 텍스트 프롬프트 입력 폼
    """
    html_content = """
    <h2>추천받을 내용 입력</h2>
    <form method="post" action="/home/recommend">
        <input type="text" name="prompt" placeholder="Enter your prompt" />
        <button type="submit">Recommend</button>
    </form>
    """
    return html_content

@router.post("/recommend", response_class=HTMLResponse)
def post_recommend_result(prompt: str = Form(...)):
    """
    POST /home/recommend:
    - 챗봇(또는 RAG 모델)에 prompt를 넘겨 책을 추천받는다고 가정
    - 여기서는 단순히 placeholder 문자열만 반환
    """
    # 실제 구현: 챗봇 API 호출 → 결과 받아오기
    recommended_book = f"Recommended Book is 'The Great Gatsby' (예시)"
    html_content = f"""
    <h2>Book Recommendation Result</h2>
    <p>{recommended_book}</p>
    <a href="/home">Go Back to Home</a>
    """
    return html_content