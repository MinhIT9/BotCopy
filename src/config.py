# BOTCOPY/src/config.py

import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'env.env')
load_dotenv(dotenv_path)

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
bot_token = os.getenv('bot_token')

messageMaping_api = os.getenv('messageMaping_api')

channel_0 = '@LogBotss1'
target_channels = ['@chanws1', '@chan9090s', '-1002133340256']
channel_mapping = {
    '1': '@chanws1',
    '2': '@chan9090s',
    '3': '-1002133340256',
    'a': '@chan9090s' 
}

