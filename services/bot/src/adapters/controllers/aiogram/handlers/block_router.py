from domain.ports.input import AbstractUserBlockedBotUseCase

from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, KICKED
from aiogram.types import ChatMemberUpdated

from structlog.stdlib import BoundLogger

block_router = Router()


@block_router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def handle_block(event: ChatMemberUpdated, uc: AbstractUserBlockedBotUseCase, log: BoundLogger):
    tg_id = event.from_user.id

    await uc.handle(tg_id)
    log.info(f"user {tg_id} deleted")
