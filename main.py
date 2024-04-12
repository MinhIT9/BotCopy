from telethon import TelegramClient, events 
from dotenv import load_dotenv
import asyncio, os, requests, aiohttp

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

async def save_message_relation(original_message_id, forwarded_message_id, channel_id):
    # Hàm này lưu trữ mối quan hệ giữa tin nhắn gốc và tin nhắn được chuyển tiếp
    async with aiohttp.ClientSession() as session:
        response = await session.get(mockapi_endpoint)
        if response.status == 200:
            data = await response.json()
            current_mapping = data[0]["message_id_mapping"]

            if str(original_message_id) not in current_mapping:
                current_mapping[str(original_message_id)] = {}
            current_mapping[str(original_message_id)][str(channel_id)] = forwarded_message_id

            update_data = {"message_id_mapping": current_mapping}
            update_endpoint = f"{mockapi_endpoint}/1"
            await session.put(update_endpoint, json=update_data)
        else:
            print("Không thể lấy dữ liệu từ mock API:", await response.text())

@client.on(events.NewMessage(chats=channel_0, pattern='#12'))
async def handler(event):
    # Hàm này xử lý việc chuyển tiếp tin nhắn
    original_message_id = event.message.id
    modified_message_text = event.message.text.replace('#12', '').strip() if event.message.text else ''

    for channel in target_channels:
        if event.message.media:
            sent_message = await client.send_file(channel, event.message.media, caption=modified_message_text)
        else:
            sent_message = await client.send_message(channel, modified_message_text)
        await save_message_relation(original_message_id, sent_message.id, channel)

@client.on(events.MessageEdited(chats=channel_0))
async def edit_handler(event):
    original_message_id = event.message.id
    # Loại bỏ "#12" khỏi nội dung tin nhắn đã chỉnh sửa
    modified_message_text = (event.message.text.replace('#12', '').strip() 
                             if event.message.text else '')

    async with aiohttp.ClientSession() as session:
        response = await session.get(mockapi_endpoint)
        if response.status == 200:
            data = await response.json()
            message_id_mapping = data[0]["message_id_mapping"]

            for channel in target_channels:
                forwarded_message_id = message_id_mapping.get(str(original_message_id), {}).get(channel)
                if forwarded_message_id:
                    if not event.message.media:
                        # Đối với tin nhắn chỉ chứa văn bản
                        await client.edit_message(channel, int(forwarded_message_id), modified_message_text)
                    else:
                        # Đối với tin nhắn chứa media, chỉnh sửa caption
                        await client.edit_message(channel, int(forwarded_message_id), modified_message_text)
                else:
                    print(f"Không tìm thấy ID tin nhắn chuyển tiếp: {original_message_id}")


async def main():
    await client.start(bot_token=bot_token)
    print("BOT đã khởi động!")
    await client.run_until_disconnected()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()