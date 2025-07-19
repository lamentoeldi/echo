# Echo
Version: 0.1.0

Description: Echo is a voice transcription platform

## Table of Contents
- [Requirements](#requirements)
- [General Architecture](#general-architecture)
  - [Telegram Bot Frontend](#telegram-bot-frontend)
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

## Audio Preprocessor
Status: `unimplemented`<br/>
Version: `-`

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

## Audio Transcriber
Status: `unimplemented`<br/>
Version: `-`

### This service:
- Consumes [audio_preprocessed](api/async/api.yaml) messages from [audio_preprocessed](api/async/api.yaml) topic
- Downloads preprocessed voice messages from object storage
- Performs audio transcription (via extendable interface)
- Deletes preprocessed voice messages from object storage
- Produces [audio_transcribed](api/async/api.yaml) messages to corresponding topic based on source

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