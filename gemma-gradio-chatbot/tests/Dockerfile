#Dockerfile
FROM python:3.10-slim

# 시스템 기본 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt .
COPY main.py .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# FastAPI 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
