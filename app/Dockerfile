# 베이스 이미지 선택
FROM python:3.13

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY BE/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# 프로젝트 전체 파일을 컨테이너로 복사
COPY . /app

# uvicorn으로 FastAPI 애플리케이션 실행 (main.py의 app 객체를 실행)
CMD ["uvicorn", "BE.main:app", "--host", "0.0.0.0", "--port", "80"]
