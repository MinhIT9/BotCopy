# BOTCOPY/src/message_utils.py

import asyncio, aiohttp, re
from telethon import events # type: ignore
from telethon.tl.types import MessageMediaWebPage # type: ignore
from config import channel_0, channel_mapping, bot_token, messageMaping_api,messageMaping_api_id , MAX_MESSAGES_PER_BATCH, MESSAGE_SEND_DELAY, channel_mapping_api, channel_mapping_api_id
from api_utils import fetch_message_relations, delete_message_relations, save_message_relations_bulk, fetch_channel_mapping

pinned_message_id = None

# biến đổi channel_mapping từ dạng lồng nhau thành một dictionary đơn giản
def simplify_channel_mapping(channel_mapping):
    simplified_mapping = {}
    for key, value_dict in channel_mapping.items():
        if isinstance(value_dict, dict):
            for channel, _ in value_dict.items():
                if channel.lstrip('-').isdigit():
                    simplified_mapping[key] = int(channel)  # Chuyển đổi thành số nguyên nếu là số
                else:
                    simplified_mapping[key] = channel  # Giữ nguyên nếu là tên kênh
    return simplified_mapping


async def main(client):
    # Đảm bảo rằng channel_mapping đã được cập nhật và đơn giản hóa trước khi gọi main
    simplified_channel_mapping = simplify_channel_mapping(channel_mapping)
    print("simplified_channel_mapping utlis: ", simplified_channel_mapping)
    
    # ------- Send START-------- #
    def modify_message_text(text):
        # Đoạn regex này tìm kiếm mẫu liên kết định dạng Markdown với **__ và __** bao quanh chữ được liên kết
        pattern = r"\[\*\*__(.*?)__\*\*\]\((https://[^)]+)\)"
        # Thay thế để đặt **__ và __** quanh phần chữ của liên kết, không bao gồm dấu ngoặc và URL
        new_text = re.sub(pattern, r"**__[\1]__**(\2) ", text)
        return new_text

    @client.on(events.NewMessage(chats=channel_0))
    async def handler(event):
        original_message_id = event.message.id
        message_text = event.message.text.strip()
        media = event.message.media
        
         # Kiểm tra xem tin nhắn có phải là lệnh bằng cách kiểm tra ký tự đầu tiên là '/'
        if message_text.startswith('/'):
            return  # Bỏ qua tin nhắn nếu bắt đầu bằng '/'

        command = message_text.split()[0]
        if command.startswith('#'):
            # Lấy danh sách kênh dựa trên các ký tự sau dấu #
            target_channels = [simplified_channel_mapping[char] for char in command[1:] if char in simplified_channel_mapping]
            modified_message_text = message_text.replace(command, '').strip()
        else:
            # Gửi đến tất cả các kênh nếu không có dấu #
            target_channels = list(simplified_channel_mapping.values())
            modified_message_text = message_text
            print("modified_message_text: ", modified_message_text)
        
        # Sử dụng hàm modify_message_text để thay đổi vị trí các dấu ** và __
        modified_message_text = modify_message_text(modified_message_text)
        print("modified_message_text sau khi gửi: ", modified_message_text)

        message_relations = {}
        # Gửi tin nhắn theo từng lô và áp dụng độ trễ
        for i in range(0, len(target_channels), MAX_MESSAGES_PER_BATCH):
            batch_channels = target_channels[i:i + MAX_MESSAGES_PER_BATCH]
            batch_relations = await send_message_to_multiple_channels(client, original_message_id, batch_channels, modified_message_text, media)
            message_relations.update(batch_relations)  # Thu thập tất cả mối quan hệ
            print("IDs of messages sent:", list(batch_relations.values()))
            await asyncio.sleep(MESSAGE_SEND_DELAY)  # Độ trễ giữa mỗi lô tin nhắn

        # Lưu toàn bộ mối quan hệ một lần sau khi tất cả tin nhắn đã được gửi
        if message_relations:
            await save_message_relations_bulk(original_message_id, message_relations)

                
    async def send_message_to_channel(client, original_message_id, channel_id, message_text, media=None):
        try:
            channel_entity = await get_channel_entity(client, channel_id)
            
            # Kiểm tra xem media có phải là MessageMediaWebPage không
            if isinstance(media, MessageMediaWebPage):
                print("Loại bỏ MessageMediaWebPage khỏi tin nhắn.")
                media = None  # Đặt lại media là None để loại bỏ nó

            if media:
                sent_message = await client.send_file(channel_entity, media, caption=message_text)
            else:
                sent_message = await client.send_message(channel_entity, message_text, link_preview=False)
            print(f"Đã gửi tin nhắn tới {channel_id}")

            return sent_message.id
        except Exception as e:
            print(f"Không thể gửi tin nhắn tới {channel_id}: {str(e)}")
            return None


        
    # Gửi tin nhắn đồng thời tới nhiều kênh
    async def send_message_to_multiple_channels(client, original_message_id, channels, message_text, media=None):
        tasks = []
        message_relations = {}

        # Tạo và lên lịch các coroutine gửi tin nhắn
        for channel_id in channels:
            task = send_message_to_channel(client, original_message_id, channel_id, message_text, media)
            tasks.append(task)
            if len(tasks) >= MAX_MESSAGES_PER_BATCH:
                # Đợi hoàn thành đợt hiện tại
                sent_message_ids = await asyncio.gather(*tasks)
                for channel_id, message_id in zip(channels, sent_message_ids):
                    if message_id is not None:
                        message_relations[str(channel_id)] = message_id
                # Xóa tasks để bắt đầu đợt mới
                tasks = []
                # Áp dụng độ trễ
                await asyncio.sleep(MESSAGE_SEND_DELAY)

        # Xử lý các tin nhắn còn lại nếu có
        if tasks:
            sent_message_ids = await asyncio.gather(*tasks)
            for channel_id, message_id in zip(channels, sent_message_ids):
                if message_id is not None:
                    message_relations[str(channel_id)] = message_id

        return message_relations
    # ------- Send End-------- #
    
    # ------- edit and remove handler START-------- #
    @client.on(events.MessageEdited(chats=channel_0))
    async def edit_handler(event):
        original_message_id = event.message.id
        text = event.message.text.strip()  # Loại bỏ khoảng trắng thừa
        media = event.message.media
        
        # Tìm command bắt đầu bằng "#"
        command_match = re.search(r'#\S*', text)
        if command_match:
            command = command_match.group(0)
        else:
            command = ''

        # Kiểm tra nếu lệnh là "/rm"
        if text.endswith("/rm"):
            # Cắt bỏ lệnh "/rm" khỏi nội dung
            message_relations = await fetch_message_relations(original_message_id)

            if not message_relations:
                print(f"Không tìm thấy mối quan hệ cho tin nhắn ID {original_message_id}")
                return

            for channel_handle, forwarded_message_id in message_relations.items():
                try:
                    if isinstance(channel_handle, str) and channel_handle.startswith('@'):
                        # Nếu channel_handle là username, sử dụng trực tiếp
                        await client.delete_messages(channel_handle, [int(forwarded_message_id)])
                    else:
                        # Nếu channel_handle là số, đảm bảo nó là số nguyên trước khi sử dụng
                        channel_handle = int(channel_handle)
                        await client.delete_messages(channel_handle, [int(forwarded_message_id)])
                    print(f"Deleted message ID {forwarded_message_id} in channel {channel_handle}")
                except Exception as e:
                    print(f"Failed to delete message {forwarded_message_id} in channel {channel_handle}: {e}")
            
            # Xóa tin nhắn gốc ở channel_0
            try:
                await client.delete_messages(channel_0, [original_message_id])
                print(f"Deleted original message ID {original_message_id} in channel_0.")
            except Exception as e:
                print(f"Failed to delete original message in channel_0: {e}")

            # Gọi hàm xóa mối quan hệ trên API
            await delete_message_relations(messageMaping_api, messageMaping_api_id, str(original_message_id))  # "1" là ID tài nguyên trên API
            return  # Dừng xử lý để không chỉnh sửa nếu là lệnh xóa

        else:
            # Nếu không phải lệnh "/rm", xử lý chỉnh sửa tin nhắn thông thường
            modified_message_text = text.replace(command, '').strip()
            modified_message_text = modify_message_text(modified_message_text)
            print("modified_message_text sau edit: ", modified_message_text)

            message_relations = await fetch_message_relations(original_message_id)
            if not message_relations:
                print(f"Không tìm thấy mối quan hệ cho tin nhắn ID {original_message_id}")
                return
            await edit_messages_in_batches(client, message_relations, modified_message_text, media)
                    
    async def edit_messages_in_batches(client, message_relations, modified_message_text, media):
        tasks = []
        for channel_handle, forwarded_message_id in message_relations.items():
            task = edit_message(client, channel_handle, forwarded_message_id, modified_message_text, media)
            tasks.append(task)
            if len(tasks) >= MAX_MESSAGES_PER_BATCH:
                await asyncio.gather(*tasks)
                tasks = []
                await asyncio.sleep(MESSAGE_SEND_DELAY)
        # Xử lý các task còn lại
        if tasks:
            await asyncio.gather(*tasks)
            
    async def edit_message(client, channel_handle, forwarded_message_id, modified_message_text, media):
        try:
            channel_entity = await get_channel_entity(client, channel_handle)
            if media:
                await client.edit_message(channel_entity, int(forwarded_message_id), file=media, text=modified_message_text)
            else:
                await client.edit_message(channel_entity, int(forwarded_message_id), text=modified_message_text, link_preview=False)
            print(f"Đã chỉnh sửa tin nhắn {forwarded_message_id} trên kênh {channel_handle}")
        except Exception as e:
            print(f"Không thể chỉnh sửa tin nhắn: {e}")
    # ------- edit and remove handler END-------- #
    
    # ------- ShowChannel handler START-------- #
    @client.on(events.NewMessage(chats=channel_0, pattern=r'/showChannel'))
    async def handle_show_channel_command(event):
        global pinned_message_id
        message_id = event.message.id  # Lưu ID của tin nhắn gửi lệnhmessage_id
        message_text = event.message.text.strip()
        if message_text == "/showChannel":
            # Kiểm tra và xóa tin nhắn ghim cũ nếu có
            if pinned_message_id:
                try:
                    await client.delete_messages(channel_0, [pinned_message_id])
                    print(f"Deleted pinned message ID {pinned_message_id}.")
                except Exception as e:
                    print(f"Failed to delete pinned message: {e}")
                    
            await client.delete_messages(channel_0, [message_id])
            
            channel_mapping = await fetch_channel_mapping(channel_mapping_api, channel_mapping_api_id)
            if channel_mapping:
                response_text = "Channel Mappings:\n" + "\n".join(f"{key}: {val}" for key, val in channel_mapping.items())
            else:
                response_text = "No channel mappings found."

            # Gửi phản hồi và ghim tin nhắn mới
            response_message = await event.reply(response_text)
            pinned_message_id = response_message.id  # Lưu ID của tin nhắn phản hồi
            with open("pinned_message_id.txt", "w") as file:
                file.write(f"{message_id},{pinned_message_id}")  # Lưu cả ID của tin nhắn gửi lệnh và tin nhắn phản hồi
            await client.pin_message(channel_0, response_message, notify=False)
    # ------- ShowChannel handler END-------- #
    
    async def get_channel_entity(client, channel_id):
        try:
            # Nếu channel_id là một chuỗi bắt đầu bằng '@', sử dụng trực tiếp
            if isinstance(channel_id, str) and channel_id.startswith('@'):
                return await client.get_entity(channel_id)
             # Chuyển đổi channel_id sang số nguyên nếu nó là một chuỗi số
            if isinstance(channel_id, str) and channel_id.lstrip('-').isdigit():
                channel_id = int(channel_id)
            # Đảm bảo channel_id là số nguyên hoặc bắt đầu bằng '@'
            return await client.get_entity(channel_id)
        except ValueError as e:
            print(f"Invalid channel ID: {channel_id} - {str(e)}")
            return None

    await client.start(bot_token=bot_token)
    print("BOT đã khởi động!")
    await client.run_until_disconnected()
