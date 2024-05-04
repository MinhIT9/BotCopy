import aiohttp
import json
import ssl
from config import messageMaping_api

# Khai báo biến toàn cục
session = None

# Tạo SSL context
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

async def get_session():
    global session
    if session is None:
        session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=ssl_context))
    return session


async def close_session():
    global session
    if session is not None:
        await session.close()
        session = None

async def fetch_data(api_url):
    session = await get_session()
    response = await session.get(api_url, ssl=ssl_context)
    return await response.text()

async def save_message_relations_bulk(original_message_id, message_relations):
    session = await get_session()
    response = await session.get(f"{messageMaping_api}/1", ssl=ssl_context)
    if response.status == 200:
        data = await response.json()
        current_mapping = data.get('message_id_mapping', {})

        # Cập nhật hoặc thiết lập mới mối quan hệ
        current_mapping[str(original_message_id)] = message_relations

        update_data = {'message_id_mapping': current_mapping}
        update_endpoint = f"{messageMaping_api}/1"
        update_response = await session.put(update_endpoint, json=update_data, ssl=ssl_context)
        if update_response.status == 200:
            print("All message relations have been saved successfully")
        else:
            print("Failed to update message relations:", await update_response.text())
    else:
        print("Failed to retrieve current message relations:", await response.text())

async def save_channel_mapping(api_url, channel_mapping):
    session = await get_session()
    payload = json.dumps({'channel_mapping': channel_mapping})
    response = await session.post(api_url, data=payload, headers={'Content-Type': 'application/json'}, ssl=ssl_context)
    if response.status in [200, 201]:
        print("Channel mapping has been saved successfully.")
    else:
        print("Failed to save channel mapping:", await response.text())

async def fetch_channel_mapping(api_url, api_url_id):
    session = await get_session()
    response = await session.get(api_url, ssl=ssl_context)
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
    session = await get_session()
    query_endpoint = f"{messageMaping_api}/1"
    response = await session.get(query_endpoint, ssl=ssl_context)
    if response.status in [200, 201]:
        data = await response.json()
        message_id_mapping = data["message_id_mapping"]
        return message_id_mapping.get(str(original_message_id), {})
    else:
        print("Không thể lấy dữ liệu từ API:", await response.text())
        return {}

async def delete_message_relations(api_url, resource_id, original_message_id):
    session = await get_session()
    endpoint = f"{api_url}/{resource_id}"
    response = await session.get(endpoint, ssl=ssl_context)
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
