# Echo
Version: 0.1.0

Description: Echo is a voice transcription platform

## Table of Contents
- [Requirements](#requirements)
- [General Architecture](#general-architecture)
  - [Telegram Bot Frontend](#telegram-bot-frontend)
  - [Audio Preprocessor](#audio-preprocessor)
  - [Audio Transcriber](#audio-transcriber)
- [Scripts](#scripts)
  - [Set Webhook](#set-webhook)
  - [Delete Webhook](#delete-webhook)
- [Async API](api/async/api.yaml)
- [License](LICENSE)
- [Configuration Examples](.env.example)
- [Makefile](Makefile)
- [Docker Compose Configuration](docker-compose.yaml)

# Requirements
- Docker
- Docker compose

# General Architecture
This projects implements MSA and consists of the following services

## Telegram Bot Frontend
Status: `implemented`<br/>
Version: `0.1.0`

### This service:
- Manages telegram user accounts
- Receives user voice messages 
- Uploads voice messages to object storage
- Produces [audio_raw](api/async/api.yaml) messages to [audio_raw](api/async/api.yaml) topic to start processing
- Consumes [audio_transcribed_tg](api/async/api.yaml) messages from [audio_transcribed_tg] topic
- Sends voice message transcriptions to users

### Dependencies
- PostgreSQL
- Kafka
- S3

### Configuration
`S3_ACCESS_KEY_ID`: S3 Access Key ID (example: `moonfire`)

`S3_SECRET_ACCESS_KEY`: S3 Secret Access Key (example: `moonfire`)

`S3_URL`: S3 URL in [protocol://domain] format (example: `http://s3:9000`)

`PG_HOST`: Postgres host (example: `postgres`)

`PG_PORT`: Postgres port (example: `5432`)

`PG_USER`: Postgres user (example: `postgres`)

`PG_PASSWORD`: Postgres password (example: `postgres`)

`PG_DB`: Postgres DB (example: `postgres`)

`KAFKA_BOOTSTRAP_SERVERS`: Kafka bootstrap servers in ["host:port", "host:port"] format (example: ["kafka:9092"])

`KAFKA_CONSUMER_GROUP`: Kafak consumer group to join (example: `tg_bot`)

`DEFAULT_LOCALE`: Default locale language (example: `en`)

`BOT_API_MODE`: Telegram Bot API connection mode: long_polling | webhook (default: `long_polling`, example: `webhook`)

`BOT_TOKEN`: Telegram Bot API token (example: `7153357657:AFG613uy8BkBIskL8oGxQoDoJ-SC_Vs-Z3P`)

`WEBHOOK_SECRET`: Telegram Bot API webhook secret token (set in webhook mode only) (example: `webhook-super-secret`)

`METRICS_HOST`: Host to serve Prometheus metrics on (default: `0.0.0.0`, example: `0.0.0.0`)

`METRICS_PORT`: Port to server Prometheus metrics on (default: `9090`, example: `9090`)

## Audio Preprocessor
Status: `implemented`<br/>
Version: `0.1.0`

### This service:
- Consumes [audio_raw](api/async/api.yaml) messages from [audio_raw](api/async/api.yaml) topic
- Downloads raw audio messages from object storage
- Performs preprocessing stages
  - Silence Removal
  - Noice Cancellation
  - Volume Level Normalization
- Uploads preprocessed voice messages back to object storage
- Deletes raw audio messages from object storage
- Produces [audio_preprocessed](api/async/api.yaml) messages to [audio_preprocessed](api/async/api.yaml) topic for further processing

### Dependencies
- Kafka
- S3
- sox
- ffmpeg

### Configuration
`S3_ACCESS_KEY_ID`: S3 Access Key ID (example: `moonfire`)

`S3_SECRET_ACCESS_KEY`: S3 Secret Access Key (example: `moonfire`)

`S3_URL`: S3 URL in [protocol://domain] format (example: `http://s3:9000`)

`KAFKA_BOOTSTRAP_SERVERS`: Kafka bootstrap servers in ["host:port", "host:port"] format (example: ["kafka:9092"])

`KAFKA_CONSUMER_GROUP`: Kafka consumer group to join (example: `preprocessor`)

`METRICS_HOST`: Host to serve Prometheus metrics on (default: `0.0.0.0`, example: `0.0.0.0`)

`METRICS_PORT`: Port to server Prometheus metrics on (default: `9090`, example: `9090`)

## Audio Transcriber
Status: `implemented`<br/>
Version: `0.1.1`

### This service:
- Consumes [audio_preprocessed](api/async/api.yaml) messages from [audio_preprocessed](api/async/api.yaml) topic
- Downloads preprocessed voice messages from object storage
- Performs audio transcription (via extendable interface)
- Deletes preprocessed voice messages from object storage
- Produces [audio_transcribed](api/async/api.yaml) messages to corresponding topic based on source

### Dependencies
- Kafka
- S3
- ffmpeg
- OpenAI Whisper

### Configuration
`S3_ACCESS_KEY_ID`: S3 Access Key ID (example: `moonfire`)

`S3_SECRET_ACCESS_KEY`: S3 Secret Access Key (example: `moonfire`)

`S3_URL`: S3 URL in [protocol://domain] format (example: `http://s3:9000`)

`KAFKA_BOOTSTRAP_SERVERS`: Kafka bootstrap servers in ["host:port", "host:port"] format (example: ["kafka:9092"])

`KAFKA_CONSUMER_GROUP`: Kafka consumer group to join (example: `transcriber`)

`WHISPER_MODEL`: Whisper model ["tiny", "base", "small", "medium", "large"] (default: `base`, example: `base`)

`WHISPER_MAX_WORKERS`: Maximum whisper calls executed in the same time (default: `1`, example: `1`)

`METRICS_HOST`: Host to serve Prometheus metrics on (default: `0.0.0.0`, example: `0.0.0.0`)

`METRICS_PORT`: Port to server Prometheus metrics on (default: `9090`, example: `9090`)

# Scripts
In this section you may find description of '.sh' and 'Makefile' scripts

## Set Webhook
> [set_webhook.sh](scripts/set_webhook.sh) - Sets Telegram Bot API webhook URL
```shell
make set-webhook
```
This script requires following env variables to run
- `BOT_TOKEN`: Telegram Bot API token
- `WEBHOOK_URL`: Telegram Bot API webhook URL
- `WEBHOOK_SECRET`: Telegram Bot API webhook secret

## Delete Webhook
> [delete_webhook.sh](scripts/delete_webhook.sh) - Deletes Telegram Bot API webhook URL
```shell
make delete-webhook
```
This script requires following env variables to run
- `BOT_TOKEN`: Telegram Bot API token