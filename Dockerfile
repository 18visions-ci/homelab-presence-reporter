FROM python:3.11-slim

ARG IMAGE_TAG
ENV IMAGE_TAG=${IMAGE_TAG}

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
