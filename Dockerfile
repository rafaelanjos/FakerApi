FROM python:3.8-alpine
WORKDIR /app
COPY . .
RUN python -m pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]