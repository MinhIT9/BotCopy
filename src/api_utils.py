# BOTCOPY/src/api_utils.py

import aiohttp
from config import messageMaping_api

async def save_message_relation(original_message_id, forwarded_message_id, channel_id):
    async with aiohttp.ClientSession() as session:
        response = await session.get(messageMaping_api + '/1')  # Giả sử bạn lưu tất cả mapping trong document có id là '1'
        if response.status in [200 , 201]:
            data = await response.json()
            current_mapping = data['message_id_mapping']  # Lấy mapping hiện tại

            if str(original_message_id) not in current_mapping:
                current_mapping[str(original_message_id)] = {}
            current_mapping[str(original_message_id)][str(channel_id)] = forwarded_message_id

            update_data = {'message_id_mapping': current_mapping}
            update_endpoint = f"{messageMaping_api}/1"
            await session.put(update_endpoint, json=update_data)  # Cập nhật toàn bộ mapping mới
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

async def delete_message_relations(api_url, resource_id, original_message_id):
    async with aiohttp.ClientSession() as session:
        # Đầu tiên, lấy dữ liệu hiện tại từ API
        endpoint = f"{api_url}/{resource_id}"
        response = await session.get(endpoint)
        if response.status == 200:
            data = await response.json()
            message_id_mapping = data['message_id_mapping']
            
            # Kiểm tra và xóa original_message_id
            if original_message_id in message_id_mapping:
                del message_id_mapping[original_message_id]  # Xóa key này khỏi dictionary

                # Cập nhật lại dữ liệu trên API
                updated_data = {"message_id_mapping": message_id_mapping}
                update_response = await session.put(endpoint, json=updated_data)
                if update_response.status == 200:
                    print("Successfully deleted the message relations from API.")
                else:
                    print("Failed to update the API after deletion.")
            else:
                print("Original message ID not found in the mapping.")
        else:
            print("Failed to fetch data from API.")