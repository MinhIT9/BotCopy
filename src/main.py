# BOTCOPY/src/main.py

import asyncio, os
from telethon import TelegramClient # type: ignore
from config import api_id, api_hash, bot_token, channel_mapping_api, channel_mapping_api_id, channel_mapping
from message_utils import main as message_main
from api_utils import fetch_channel_mapping

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
    # Xóa file session sau khi ngắt kết nối
    # session_file = 'bot.session'
    # if os.path.exists(session_file):
    #     os.remove(session_file)
    #     print("Session file removed!")
    # else:
    #     print("Session file does not exist.")

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        loop.run_until_complete(stop_bot())
