# BOTCOPY/src/config.py

import os
from dotenv import load_dotenv

MAX_MESSAGES_PER_BATCH = 10 # Số lượng tin nhắn gửi tối đa đến Channel
MESSAGE_SEND_DELAY = 0.5  # Delay in seconds

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'env.env')
load_dotenv(dotenv_path)

api_id = os.getenv('env_api_id')
api_hash = os.getenv('env_api_hash')
bot_token = os.getenv('env_bot_token')

messageMaping_api = os.getenv('env_messageMaping_api')
messageMaping_api_id= os.getenv("env_messageMaping_api_id")
channel_mapping_api = os.getenv('env_channel_mapping_api')
channel_mapping_api_id = os.getenv('env_channel_mapping_api_id')

channel_0 = os.getenv('env_channel_main')

channel_mapping={}