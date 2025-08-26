FROM python:3.13-slim

ENV PYTHONPATH=/app/src\
    PYTHONUNBUFFERED=1\
    PIP_NO_CACHE_DIR=1\
    PIP_DEFAULT_TIMEOUT=600\
    PIP_RETRIES=20

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends ffmpeg &&  \
    apt-get clean &&  \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip &&  \
    pip install -r ./requirements.txt

COPY . .

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
EXPOSE 9090