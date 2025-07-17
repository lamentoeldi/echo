from io import BytesIO

from services.bot.domain.ports.input import AbstractVoiceMessageUseCase

from aiogram import Router, F, Bot
from aiogram.types import Message

vm_router = Router()


@vm_router.message(F.voice)
async def handle_vm(msg: Message, bot: Bot, uc_vm: AbstractVoiceMessageUseCase):
    f = await bot.get_file(msg.voice.file_id)

    stream = BytesIO()
    await bot.download_file(f.file_path, stream)

    stream.seek(0)
    await uc_vm.start_vm_handling(msg.from_user.id, stream)
