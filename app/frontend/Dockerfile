# 1️⃣ 베이스 이미지 선택
FROM node:16-alpine

# 2️⃣ 작업 디렉토리 설정
WORKDIR /app

# 3️⃣ frontend 폴더 내부의 package.json 파일 복사
COPY frontend/package*.json ./

# 4️⃣ npm 패키지 설치
RUN npm install

# 5️⃣ frontend 코드 전체 복사
COPY frontend/ ./

# 6️⃣ static 폴더 복사
COPY static/ ./static

# (필요 시 CMD 또는 ENTRYPOINT 추가)
