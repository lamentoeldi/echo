FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ARG MODEL=base

COPY ./build.py .
RUN pip install openai-whisper && python build.py

COPY requirements.txt .
RUN pip install -r ./requirements.txt

COPY . .

ENV PYTHONPATH=/app/src

ENTRYPOINT ["python", "main.py"]
EXPOSE 9090