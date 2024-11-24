import requests
import os
import threading
import configparser
import json
import time
import base64
from datetime import datetime
import hmac
import hashlib
from telegram import TelegramBot
import pytz
from kucoin.client import Client
from kucoin_futures.client import Trade, Market

config = configparser.ConfigParser(inline_comment_prefixes=";")
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "setting.ini")
config.read(config_path)

api_key = config["kucoin"]["KUCOIN_KEY"]
api_secret = config["kucoin"]["KUCOIN_SECRET"]
api_passphrase = config["kucoin"]["KUCOIN_PASSPHRASE"]
telegram_token = config["telegram"]["TELEGRAM_TOKEN"]
telegram_chatid = config["telegram"]["TELEGRAM_CHATID"]

def get_all_positions():
     
    
    # client = Client(api_key, api_secret, api_passphrase)
    client= Trade(key= api_key, secret = api_secret, passphrase = api_passphrase, url='')
    with open("2.txt","a") as file:
        all_positions = client.get_all_position()
        print(all_positions)

def close_all_positions():
    
    api_key = config["kucoin"]["KUCOIN_KEY"]
    api_secret = config["kucoin"]["KUCOIN_SECRET"]
    api_passphrase = config["kucoin"]["KUCOIN_PASSPHRASE"]

    
    # client = Client(api_key, api_secret, api_passphrase)
    client= Trade(key= api_key, secret = api_secret, passphrase = api_passphrase, url='')
    all_positions = client.get_all_position()
    # if all_positions
    for position in all_positions:
        currentQty = position['currentQty']
        opposite_side = "sell" if int(currentQty)>=0 else  "buy"
        order_id  = client.create_market_order(position['symbol'], opposite_side, size = str(abs(int(currentQty))), lever = position['leverage'], marginMode = "CROSS")
        print(f"{position['symbol']}  => {order_id}")
    # print(all_positions)
if __name__ == "__main__" :
    try : 
        # bot_thread = threading.Thread(target = run_bot)
        # bot_thread.start()
        # telegrambot =TelegramBot(telegram_token, telegram_chatid)
        # test_value = 1
        # telegrambot.send_message(f"test => {test_value}")
        # close_all_positions()
        # get_all_positions()
        timezone = pytz.timezone('Israel')
        time = datetime.now(timezone)
        if time.day !=20:
            print("NOT 21")
        print(time)
        print("This is main.")
    except KeyboardInterrupt:
        print("Excepting...")