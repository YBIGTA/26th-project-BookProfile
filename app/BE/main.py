from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware  # 세션 미들웨어 import
from .routers import router as main_router
from .database.mongodb import client


def create_app() -> FastAPI:
    app = FastAPI()

    # 세션 미들웨어 추가
    app.add_middleware(
    SessionMiddleware,
    secret_key = "fd9b8e7a6d5c4b3a2f1e0d9c8b7a6f5e", # 쿠키 서명에 사용되는 비밀키
    session_cookie="login_session", # 쿠키 이름
    max_age=3600, # 쿠키의 만료 시간, 1시간
    path="/", # 쿠키가 유효한 경로 설정
    same_site="lax", # SameSite 속성을 lax로 설정 (CSRF 공격 방지에 도움)
    https_only=False # HTTPS 연결이 아닐 경우에도 쿠키 전송 허용 (배포 시에는 True 권장)
    )

    # React 개발 서버와 연동하기 위한 CORS 설정
    origins = [
    "http://localhost:3001",  # 로컬 개발 환경
    "http://frontend:3001",  # Docker Compose 환경
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(main_router)  # __init__.py에서 합친 router
    try:
        # 서버 정보를 요청해서 연결 확인 (연결 실패 시 예외 발생)
        client.server_info()
        print("MongoDB 연결 성공!")
    except Exception as e:
        print("MongoDB 연결 오류:", e)
    
    return app

app = create_app()
