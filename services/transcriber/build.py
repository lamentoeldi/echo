import os

from whisper import load_model

model = os.getenv("MODEL")
load_model(model)
