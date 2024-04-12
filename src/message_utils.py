# BOTCOPY/src/message_utils.py

from telethon import events # type: ignore
from config import channel_0, channel_mapping, bot_token
from api_utils import save_message_relation, fetch_message_relations
import aiohttp

async def main(client):
    @client.on(events.NewMessage(chats=channel_0, pattern=r'#\w+'))
    async def handler(event):
        original_message_id = event.message.id
        command = event.message.text.split()[0]  # Lấy lệnh đầu tiên (ví dụ: #123, #12a4, #14)
        modified_message_text = event.message.text.replace(command, '').strip() if event.message.text else ''
        
        # Xác định các channels dựa trên từ khoá
        target_channels = [channel_mapping[char] for char in command[1:] if char in channel_mapping]

        for channel in target_channels:
            if event.message.media:
                sent_message = await client.send_file(channel, event.message.media, caption=modified_message_text)
            else:
                sent_message = await client.send_message(channel, modified_message_text)
            print("Đã gửi tin nhắn tới Channel", channel)
            await save_message_relation(original_message_id, sent_message.id, channel)

    @client.on(events.MessageEdited(chats=channel_0))
    async def edit_handler(event):
        original_message_id = event.message.id
        command = event.message.text.split()[0]  # Lấy lệnh đầu tiên để xác định kênh mục tiêu
        modified_message_text = event.message.text.replace(command, '').strip() if event.message.text else ''

        # Lấy thông tin về các tin nhắn đã chuyển tiếp từ message_id của tin nhắn gốc
        message_relations = await fetch_message_relations(original_message_id)
        print("message_relations: utlis", message_relations)
        if not message_relations:
            print(f"Không tìm thấy mối quan hệ cho tin nhắn ID {original_message_id}")
            return

        for channel_handle, forwarded_message_id in message_relations.items():
        # Sử dụng trực tiếp `channel_handle` vì nó đã là handle của kênh
            try:
                if event.message.media:
                    # Chỉnh sửa tin nhắn với media
                    await client.edit_message(channel_handle, int(forwarded_message_id), file=event.message.media, text=modified_message_text)
                else:
                    # Chỉnh sửa tin nhắn văn bản
                    await client.edit_message(channel_handle, int(forwarded_message_id), text=modified_message_text)
                print(f"Đã chỉnh sửa tin nhắn {forwarded_message_id} trên kênh {channel_handle}")
            except Exception as e:
                print(f"Không thể chỉnh sửa tin nhắn: {e}")




    await client.start(bot_token=bot_token)
    print("BOT đã khởi động!")
    await client.run_until_disconnected()
