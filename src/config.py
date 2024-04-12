# BOTCOPY/src/config.py

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'env.env')
load_dotenv(dotenv_path)

api_id = os.getenv('env_api_id')
api_hash = os.getenv('env_api_hash')
bot_token = os.getenv('env_bot_token')

messageMaping_api = os.getenv('env_messageMaping_api')
channel_mapping_api = os.getenv('env_channel_mapping_api')
channel_mapping_api_id = '1'


channel_0 = '@LogBotss1'

# Khởi tạo ban đầu
channel_mapping = {}