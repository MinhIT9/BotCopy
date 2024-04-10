from telethon import TelegramClient, events 
from telethon.tl.custom import Button
from dotenv import load_dotenv
import os
import requests
import aiohttp
import asyncio

# Thêm dòng này để tải các biến môi trường từ file .env
load_dotenv('env.env')
# Thông tin cấu hình API - CL Nam
api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
bot_token = os.getenv('bot_token')

channel_0 = '@LogBotss1'

# Username của các channel đích
target_channels = ['@chanws1', '@chan9090s']

# Endpoint của mock API
mockapi_endpoint = "https://66069142be53febb857e308e.mockapi.io/message_tracker"


# Khởi tạo Telegram client
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Dictionary để theo dõi các message ID
message_id_mapping = {}

print("Đang khởi động...!")

# Hàm lưu trữ mối quan hệ tin nhắn
async def save_message_relation(original_message_id, forwarded_message_id, channel_id):
   async with aiohttp.ClientSession() as session:
        # Lấy dữ liệu hiện tại từ API
        response = await session.get(mockapi_endpoint)
        if response.status == 200:
            data = await response.json()
            message_id_mapping = data[0]["message_id_mapping"]  # Giả định rằng đây là entry đầu tiên

            # Cập nhật dữ liệu mới vào message_id_mapping
            if str(original_message_id) not in message_id_mapping:
                message_id_mapping[str(original_message_id)] = {}
            if str(forwarded_message_id) not in message_id_mapping[str(original_message_id)]:
                message_id_mapping[str(original_message_id)][str(forwarded_message_id)] = {}
            message_id_mapping[str(original_message_id)][str(forwarded_message_id)][str(channel_id)] = forwarded_message_id
            
            # Gửi yêu cầu PUT để cập nhật dữ liệu trên API
            update_data = {
                "message_id_mapping": message_id_mapping
            }
            # Sử dụng ID của entry để cập nhật nó, giả định là "1" như trong hình ảnh của bạn
            update_endpoint = f"{mockapi_endpoint}/1"  
            await session.put(update_endpoint, json=update_data)
        else:
            print("Không thể lấy dữ liệu từ mock API:", await response.text())


@client.on(events.NewMessage(chats=channel_0, pattern='#12'))
async def handler(event):
    original_message_id = event.message.id
    # Loại bỏ "#12" khỏi nội dung tin nhắn
    modified_message_text = event.message.text.replace('#12', '').strip()

    # Gửi và lưu trữ tin nhắn đã được chỉnh sửa nội dung
    for channel in target_channels:
        sent_message = await client.send_message(channel, modified_message_text)
        await save_message_relation(event.message.id, sent_message.id, channel)


@client.on(events.MessageEdited(chats=channel_0))
async def edit_handler(event):
    original_message_id = event.message.id
    # Kiểm tra xem tin nhắn được chỉnh sửa có chứa lệnh "/dl" hay không
    if '/rm' in event.raw_text:
        # Cờ hiệu để kiểm tra việc xóa tin nhắn thành công ở tất cả các channel đích
        all_deleted_successfully = True
        # Xóa các tin nhắn tương ứng
        for channel in target_channels:
            forwarded_message_id = message_tracker.pop((channel, original_message_id), None)
            if forwarded_message_id:
                delete_status = await client.delete_messages(channel, [forwarded_message_id])
                if not delete_status:
                    all_deleted_successfully = False
                    print(f"Không thể xóa tin nhắn từ channel {channel}")
            else:
                all_deleted_successfully = False
                print(f"Không tìm thấy tin nhắn trong message_tracker để xóa từ channel {channel}")

        # Nếu tất cả các tin nhắn đã được xóa thành công từ các channel đích, xóa tin nhắn gốc ở channel 0
        if all_deleted_successfully:
            await client.delete_messages(channel_0, [original_message_id])
    else:
        # Nếu không phải là lệnh xóa, cập nhật tin nhắn như bình thường
        for channel in target_channels:
            forwarded_message_id = message_tracker.get((channel, original_message_id))
            if forwarded_message_id:
                await client.edit_message(channel, forwarded_message_id, event.message.text)



# Bắt đầu bot
print("Khởi động BOT thành công!")
client.run_until_disconnected()
