FROM python:3.11-slim-bookworm

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY bot.py .

USER nodbody

ENTRYPOINT ["python", "bot.py"]
