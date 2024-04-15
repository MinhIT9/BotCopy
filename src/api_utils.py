# BOTCOPY/src/api_utils.py

import aiohttp, json
from config import messageMaping_api

async def save_message_relations_bulk(original_message_id, message_relations):
    async with aiohttp.ClientSession() as session:
        # Lấy dữ liệu hiện tại từ API
        response = await session.get(messageMaping_api + '/1')
        if response.status in [200, 201]:
            data = await response.json()
            current_mapping = data['message_id_mapping']

            # Lấy mối quan hệ tin nhắn hiện tại cho message_id, nếu không có tạo mới
            if str(original_message_id) in current_mapping:
                # Cập nhật các mối quan hệ hiện có bằng cách thêm hoặc cập nhật các giá trị mới
                for channel_id, message_id in message_relations.items():
                    current_mapping[str(original_message_id)][channel_id] = message_id
            else:
                # Nếu không có mối quan hệ nào trước đó, đặt mới
                current_mapping[str(original_message_id)] = message_relations

            update_data = {'message_id_mapping': current_mapping}
            update_endpoint = f"{messageMaping_api}/1"
            update_response = await session.put(update_endpoint, json=update_data)
            if update_response.status == 200:
                print("All message relations have been saved successfully")
            else:
                print("Failed to update message relations:", await update_response.text())
        else:
            print("Failed to retrieve current message relations:", await response.text())

async def save_channel_mapping(api_url, channel_mapping):
    async with aiohttp.ClientSession() as session:
        # Chuyển đổi dictionary thành string JSON để lưu trữ nếu cần
        payload = json.dumps({'channel_mapping': channel_mapping})
        response = await session.post(api_url, data=payload, headers={'Content-Type': 'application/json'})
        if response.status in [200 , 201]:
            print("Channel mapping has been saved successfully.")
        else:
            print("Failed to save channel mapping:", await response.text())
            
async def fetch_channel_mapping(api_url, api_url_id):
    async with aiohttp.ClientSession() as session:
        response = await session.get(api_url)
        if response.status == 200:
            data = await response.json()

            # Tìm và trả về ChannelMapping có id
            for item in data:
                if item.get('id') == '1' and 'ChannelMapping' in item:
                    channel_mapping = item['ChannelMapping']
                    # Chuyển đổi các giá trị chuỗi thành số nguyên nếu có thể
                    for key, value in channel_mapping.items():
                        if isinstance(value, str) and value.lstrip('-').isdigit():
                            channel_mapping[key] = int(value)
                    return channel_mapping
            # Nếu không tìm thấy ChannelMapping với id 
            print("No valid channel mapping found with id ")
            return {}
        else:
            print("Failed to fetch channel mapping:", await response.text())
            return {}

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