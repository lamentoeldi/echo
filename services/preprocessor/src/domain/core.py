import subprocess
from io import BytesIO
from typing import Tuple
from time import time_ns

import asyncio.subprocess

from src.application.usecases import AbstractCore
from src.domain.models import AudioRaw, AudioPreprocessed

import soundfile as sf


class Core(AbstractCore):
    async def preprocess_audio(self, md: AudioRaw, audio: BytesIO) -> Tuple[AudioPreprocessed, BytesIO]:
        audio.seek(0)

        ffmpeg_cmd = [
            '-i', 'pipe:0',
            '-f', 'wav',
            'pipe:1'
        ]

        ffmpeg_proc = await asyncio.create_subprocess_exec(
            'ffmpeg',
            *ffmpeg_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )

        ffmpeg_stdout, _ = await ffmpeg_proc.communicate(input=audio.read())

        if ffmpeg_proc.returncode != 0:
            raise RuntimeError("ffmpeg failed to decode input audio")

        sox_cmd = [
            'sox',
            '-t', 'wav', '-',
            '-t', 'wav', '-',
            'silence', '1', '0.1', '1%', '-1', '0.5', '1%',
            'rate', '16k',
            'channels', '1',
            'norm'
        ]

        sox_proc = await asyncio.create_subprocess_exec(
            *sox_cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL
        )

        sox_stdout, _ = await sox_proc.communicate(input=ffmpeg_stdout)

        if sox_proc.returncode != 0:
            raise RuntimeError("sox failed to process audio")

        out_audio = BytesIO(sox_stdout)
        out_audio.seek(0)

        with sf.SoundFile(out_audio) as f:
            out_md = AudioPreprocessed(
                id=md.id,
                user_id=md.user_id,
                size=len(sox_stdout),
                source=md.source,
                timestamp=time_ns(),
                duration=int(1000 * f.frames / f.samplerate),
                channels=f.channels
            )

        return out_md, out_audio
