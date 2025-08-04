#!/bin/sh
MODEL="${1:-base}"

pip install --no-cache-dir --prefer-binary openai-whisper==20250625
python -c "import whisper; whisper.load_model('$MODEL')"
python main.py