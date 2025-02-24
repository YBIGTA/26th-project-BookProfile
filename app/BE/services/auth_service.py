from fastapi import HTTPException, Request, status
from pymongo.database import Database
from ..models.user import User

async def login(request: Request, db: Database, username: str, password: str):
    """
    주어진 username과 password로 사용자를 인증하고, 성공 시 세션에 사용자 정보를 저장합니다.
    """
    user = await db["users"].find_one({"name": username})
    if not user or user["password"] != password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    # 로그인 성공 시 세션에 사용자 이름 저장
    request.session["user"] = user["name"]
    
    return user

def require_login(request: Request):
    """
    세션에 사용자 정보가 있으면 반환하고, 없으면 401 에러를 발생시킵니다.
    """
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return user

async def register(db: Database, username: str, password: str):
    """
    새 사용자를 등록합니다.
    - 이미 존재하는 username이면 400 에러 발생.
    """
    # username 중복 검사
    existing_user = await db["users"].find_one({"name": username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists.")

    # 새 사용자 데이터 생성
    new_user = User(name=username, password=password)
    new_user_dict = new_user.model_dump()

    result = await db["users"].insert_one(new_user_dict)
    if result.inserted_id is None:
        raise HTTPException(status_code=500, detail="Failed to register user.")

    return new_user

async def logout(request: Request, db: Database):
    """
    로그아웃 서비스 함수:
    - 요청 객체의 세션 정보를 삭제하여 로그아웃 처리합니다.
    """
    # 세션을 초기화하여 로그아웃
    request.session.clear()

