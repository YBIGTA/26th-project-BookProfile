# 1️⃣ 베이스 이미지 선택 (최적화)
FROM python:3.11

# 2️⃣ 작업 디렉토리 설정
WORKDIR /app

# 3️⃣ 의존성 파일 복사 및 설치
COPY BE/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4️⃣ 프로젝트 전체 파일을 복사
COPY BE /app

# 5️⃣ FastAPI 실행
CMD ["uvicorn", "BE.main:app", "--host", "0.0.0.0", "--port", "80"]
