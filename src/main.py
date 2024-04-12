# BOTCOPY/src/main.py

import asyncio , message_utils
from telethon import TelegramClient # type: ignore
from config import api_id, api_hash, bot_token

client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(message_utils.main(client))
    loop.close()