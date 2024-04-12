# BOTCOPY/src/api_utils.py

import aiohttp
from config import messageMaping_api

async def save_message_relation(original_message_id, forwarded_message_id, channel_id):
    # Hàm này lưu trữ mối quan hệ giữa tin nhắn gốc và tin nhắn được chuyển tiếp
    async with aiohttp.ClientSession() as session:
        response = await session.get(messageMaping_api)
        if response.status == 200:
            data = await response.json()
            current_mapping = data[0]["message_id_mapping"]

            if str(original_message_id) not in current_mapping:
                current_mapping[str(original_message_id)] = {}
            current_mapping[str(original_message_id)][str(channel_id)] = forwarded_message_id

            update_data = {"message_id_mapping": current_mapping}
            update_endpoint = f"{messageMaping_api}/1"
            await session.put(update_endpoint, json=update_data)
        else:
            print("Không thể lấy dữ liệu từ mock API:", await response.text())

async def fetch_message_relations(original_message_id):
    async with aiohttp.ClientSession() as session:
        # API endpoint với ID cụ thể (được lấy từ dữ liệu mẫu bạn cung cấp).
        query_endpoint = messageMaping_api + '/1'
        response = await session.get(query_endpoint)
        if response.status in [200 , 201]:
            data = await response.json()
            # Tìm trong `message_id_mapping` để lấy mối quan hệ cho `original_message_id`.
            message_id_mapping = data["message_id_mapping"]
            return message_id_mapping.get(str(original_message_id), {})
        else:
            print("Không thể lấy dữ liệu từ API:", await response.text())
            return {}

