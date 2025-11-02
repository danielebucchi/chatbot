FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r src/requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/app/src"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7373"]
