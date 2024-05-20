# BOTCOPY/src/main.py

import asyncio, os, threading
from telethon import TelegramClient # type: ignore
from config import api_id, api_hash, bot_token, channel_mapping_api, channel_mapping_api_id, channel_mapping
from message_utils import main as message_main
from api_utils import fetch_channel_mapping
from App.flask_app import run_flask  # Nhập hàm khởi động Flask

print("Đang khởi động BOT ...")
client = TelegramClient('bot', api_id, api_hash)
async def start_bot():
    # Tạo một phiên client Telegram
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
    print("Khởi động BOT thành công!")

async def stop_bot():
    await client.disconnect()

def start_flask_app():
    # Chạy Flask trong một thread riêng biệt
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

if __name__ == '__main__':
    start_flask_app()  # Khởi động Flask app
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        loop.run_until_complete(stop_bot())