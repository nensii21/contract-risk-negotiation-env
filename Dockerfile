FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app  

CMD ["python","-m","uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "7860"]