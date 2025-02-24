from fastapi import APIRouter, Form, Request, status, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pymongo.database import Database
from ..database.mongodb import get_user_db
from ..services.auth_service import login, register, require_login, logout
from ..services.survey_service import get_survey_status

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_login_page(
    request: Request,
    db: Database = Depends(get_user_db)
):
    """
    GET /:
      가입 후 최초 로그인이라면 return RedirectResponse(url="/survey")
      만약 로그인되어 있다면 return RedirectResponse(url="/home")
    - 로그인 안 되어 있으면 로그인 폼 노출
    """
    try:
        # 세션에 로그인 정보가 있는지 확인 (있으면 user 반환, 없으면 HTTPException 발생)
        username = require_login(request)
        if await get_survey_status(username, db):
            return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
        else:
            return RedirectResponse(url="/survey", status_code=status.HTTP_302_FOUND)
    except HTTPException:
        html_content = """
        <html>
            <head><title>Login</title></head>
            <body>
                <h2>Login</h2>
                <form action="/login" method="post">
                    <label>Username: <input type="text" name="username"/></label><br>
                    <label>Password: <input type="password" name="password"/></label><br>
                    <button type="submit">Login</button>
                </form>
                <a href="/register">Sign Up</a>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

@router.post("/login")
async def login_route(
    # JSON 형식으로 입력받으면 Pydantic 모델을 이용하기 위한 수정 필요
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Database = Depends(get_user_db)
):
    await login(request, db, username, password)
    if await get_survey_status(username, db):
            return RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    else:
        return RedirectResponse(url="/survey", status_code=status.HTTP_302_FOUND)

@router.get("/register", response_class=HTMLResponse)
def get_register_page():
    """
    GET /register:
    - 회원가입 폼을 노출
    """
    html_content = """
    <h2>Sign Up</h2>
    <form method="post" action="/register">
        <label>Username: <input type="text" name="username" /></label><br>
        <label>Password: <input type="password" name="password" /></label><br>
        <button type="submit">Register</button>
    </form>
    <a href="/">Go Back</a>
    """
    return html_content

@router.post("/register", response_class=HTMLResponse)
async def post_register(
    username: str = Form(...),
    password: str = Form(...),
    db: Database = Depends(get_user_db)
):
    try:
        await register(db, username, password)
    except HTTPException as e:
        error_html = f"""
        <html>
          <body>
            <h1>Error</h1>
            <p>{e.detail}</p>
            <a href="/register">Try Again</a>
          </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=e.status_code)
    
    # 회원가입 성공 시 로그인 페이지(또는 홈)로 리다이렉트
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)


@router.get("/logout")
async def logout_route(
    request: Request,
    db: Database = Depends(get_user_db),
    current_user: str = Depends(require_login)
):
    """
    로그아웃 처리:
    - 세션 정보를 삭제한 후 홈으로 리다이렉트합니다.
    """
    # 서비스 함수를 호출하여 로그아웃(세션 삭제) 처리
    await logout(request, db)
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)