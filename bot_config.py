# BOTCOPY/bot_config.py

import asyncio, json, os
from dotenv  import load_dotenv
from telegram import Bot

load_dotenv("env.env")

# Lấy giá trị biến môi trường
TOKEN_BOT = '7104369638:AAG1MG2mgoI-TAfNZ-hCbIsdeoVzlr-bFz4'

bot = Bot(token=TOKEN_BOT)