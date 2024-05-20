import asyncio
import threading
import signal
from werkzeug.serving import make_server
from telethon import TelegramClient
from config import api_id, api_hash, bot_token, channel_mapping_api, channel_mapping_api_id, channel_mapping
from api_utils import fetch_channel_mapping
from message_utils import main as message_main
from App.flask_app import app

client = TelegramClient('bot', api_id, api_hash)
server = make_server('localhost', 5000, app)
server_thread = threading.Thread(target=server.serve_forever)
stop_event = threading.Event()

async def start_bot():
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
        
    await message_main(client)

async def stop_bot():
    print("Đang dừng Telegram Bot...")
    await client.disconnect()
    print("Telegram Bot đã dừng.")

def stop_flask():
    print("Đang dừng Flask...")
    server.shutdown()
    print("Flask đã dừng.")

def signal_handler(sig, frame):
    print("Đang dừng... vui lòng chờ")
    asyncio.create_task(stop_bot())
    stop_flask()
    stop_event.set()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    server_thread.start()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_bot())
    server_thread.join()
