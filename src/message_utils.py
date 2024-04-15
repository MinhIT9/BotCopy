# BOTCOPY/src/message_utils.py

import asyncio
from telethon import events # type: ignore
from telethon.tl.types import MessageMediaWebPage # type: ignore
from config import channel_0, channel_mapping, bot_token, messageMaping_api
from api_utils import save_message_relation, fetch_message_relations, delete_message_relations

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
    
    # ------- handler START-------- #
    @client.on(events.NewMessage(chats=channel_0, pattern=r'#\w+'))
    async def handler(event):
        original_message_id = event.message.id
        command = event.message.text.split()[0]
        modified_message_text = event.message.text.replace(command, '').replace('#', '').strip() if event.message.text else ''

        # Giả sử command có dạng "#1#2#3", bạn cần lấy tất cả các kênh từ simplified_channel_mapping
        target_channels = []
        for char in command[1:]:  # Bỏ qua ký tự đầu tiên là '#'
            if char in simplified_channel_mapping:
                target_channels.append(simplified_channel_mapping[char])

        # Gửi tin nhắn đến tất cả các channels và lưu trữ mối quan hệ
        sent_ids = await send_message_to_multiple_channels(client, original_message_id, target_channels, modified_message_text, event.message.media if event.message.media else None)
        print("IDs of messages sent:", sent_ids)


                
    async def send_message_to_channel(client, original_message_id, channel_id, message_text, media=None):
        try:
            channel_entity = await get_channel_entity(client, channel_id)
            
            # Kiểm tra xem media có phải là MessageMediaWebPage không
            if isinstance(media, MessageMediaWebPage):
                print("Loại bỏ MessageMediaWebPage khỏi tin nhắn.")
                media = None  # Đặt lại media là None để loại bỏ nó

            if media:
                sent_message = await client.send_file(channel_entity, media, caption=message_text, link_preview=False)
            else:
                sent_message = await client.send_message(channel_entity, message_text, link_preview=False)
            print(f"Đã gửi tin nhắn tới {channel_id}")

            # Lưu mối quan hệ tin nhắn
            await save_message_relation(original_message_id, sent_message.id, channel_id)

            return sent_message.id
        except Exception as e:
            print(f"Không thể gửi tin nhắn tới {channel_id}: {str(e)}")
            return None


        
    # Gửi tin nhắn đồng thời tới nhiều kênh
    async def send_message_to_multiple_channels(client, original_message_id, channels, message_text, media=None):
        # Tạo danh sách các coroutine gửi tin nhắn
        tasks = [
            send_message_to_channel(client, original_message_id, channel, message_text, media)
            for channel in channels
        ]
        # Chạy tất cả các coroutine đồng thời và trả về ID tin nhắn được gửi
        sent_message_ids = await asyncio.gather(*tasks)
        
        # Lưu tất cả các mối quan hệ tin nhắn một lần sau khi tất cả tin nhắn đã được gửi
        for channel_id, message_id in zip(channels, sent_message_ids):
            if message_id is not None:
                await save_message_relation(original_message_id, message_id, channel_id)
        
        return sent_message_ids

    # ------- handler End-------- #
    
    # ------- edit and remove handler START-------- #
    @client.on(events.MessageEdited(chats=channel_0))
    async def edit_handler(event):
        original_message_id = event.message.id
        text = event.message.text.strip()  # Loại bỏ khoảng trắng thừa
        command = text.split()[-1]  # Lấy từ cuối cùng của tin nhắn

        if command.lower() == "/rm":  # Kiểm tra nếu lệnh là "/rm"
            modified_message_text = text[:-len(command)].strip()  # Cắt bỏ lệnh "/rm" khỏi nội dung
            message_relations = await fetch_message_relations(original_message_id)

            if not message_relations:
                print(f"Không tìm thấy mối quan hệ cho tin nhắn ID {original_message_id}")
                return

            for channel_handle, forwarded_message_id in message_relations.items():
                print(f"Trying to delete message ID {forwarded_message_id} in channel {channel_handle}")
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
            await delete_message_relations(messageMaping_api, "1", str(original_message_id))  # "1" là ID tài nguyên trên API


            return  # Dừng xử lý để không chỉnh sửa nếu là lệnh xóa

        else:
            # Nếu không phải lệnh "/rm", xử lý chỉnh sửa tin nhắn thông thường
            command = event.message.text.split()[0]
            modified_message_text = text.replace(command, '').strip()
            message_relations = await fetch_message_relations(original_message_id)
            if not message_relations:
                print(f"Không tìm thấy mối quan hệ cho tin nhắn ID {original_message_id}")
                return

            for channel_handle, forwarded_message_id in message_relations.items():
                try:
                    channel_entity = await get_channel_entity(client, channel_handle)
                    if event.message.media:
                        await client.edit_message(channel_entity, int(forwarded_message_id), file=event.message.media, text=modified_message_text)
                    else:
                        await client.edit_message(channel_entity, int(forwarded_message_id), text=modified_message_text)
                    print(f"Đã chỉnh sửa tin nhắn {forwarded_message_id} trên kênh {channel_handle}")
                except Exception as e:
                    print(f"Không thể chỉnh sửa tin nhắn: {e}")
    # ------- edit and remove handler END-------- #
    
    async def get_channel_entity(client, channel_id):
        try:
            # Nếu channel_id là một chuỗi bắt đầu bằng '@', sử dụng trực tiếp
            if isinstance(channel_id, str) and channel_id.startswith('@'):
                return await client.get_entity(channel_id)
            # Nếu channel_id là một chuỗi số, chuyển đổi sang số nguyên
            elif isinstance(channel_id, str) and channel_id.isdigit():
                channel_id = int(channel_id)
            # Đảm bảo channel_id là số nguyên hoặc bắt đầu bằng '@'
            return await client.get_entity(channel_id)
        except ValueError as e:
            print(f"Invalid channel ID: {channel_id} - {str(e)}")
        except Exception as e:
            print(f"Error retrieving entity for channel {channel_id}: {str(e)}")

    await client.start(bot_token=bot_token)
    print("BOT đã khởi động!")
    await client.run_until_disconnected()
