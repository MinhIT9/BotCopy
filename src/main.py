# BOTCOPY/src/main.py

import asyncio
from telethon import TelegramClient # type: ignore
from config import api_id, api_hash, bot_token, channel_mapping_api, channel_mapping_api_id, channel_mapping
from message_utils import main as message_main
from api_utils import fetch_channel_mapping

async def start_bot():
    # Tạo một phiên client Telegram
    client = TelegramClient('bot', api_id, api_hash)
    await client.start(bot_token=bot_token)

    # Tải cấu hình channel mapping từ API
    new_channel_mapping = await fetch_channel_mapping(channel_mapping_api, channel_mapping_api_id)
    if new_channel_mapping:
        channel_mapping.clear()
        channel_mapping.update(new_channel_mapping)  # Cập nhật dữ liệu channel mapping mới
        # print("Channel mappings loaded successfully.")
        print("API Response main:", channel_mapping)
    else:
        print("Failed to load channel mappings.")
    
    # Khởi chạy các tác vụ chính của bot
    await message_main(client)

if __name__ == '__main__':
    # Lấy vòng lặp sự kiện hiện tại từ asyncio
    loop = asyncio.get_event_loop()
    
    # Chạy bot
    loop.run_until_complete(start_bot())
    
    # Đóng vòng lặp sự kiện sau khi các tác vụ đã hoàn thành
    loop.close()
