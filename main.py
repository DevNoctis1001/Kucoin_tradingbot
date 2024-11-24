import requests
import os
import threading
import configparser
import json
import time
import pytz
import base64
import hmac
import hashlib
from datetime import datetime

from kucoin.client import Client
from kucoin_futures.client import Trade, Market

from telegram import TelegramBot

    
def run_bot():
    #Import config data
    config = configparser.ConfigParser(inline_comment_prefixes=";")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "setting.ini")
    config.read(config_path)

    coins=[
        [config['kucoin']['COIN1'], config['kucoin']['COIN1_SIZE'], config['kucoin']['COIN1_SIDE'], 0, None],
        [config['kucoin']['COIN2'], config['kucoin']['COIN2_SIZE'], config['kucoin']['COIN2_SIDE'], 0, None],
        [config['kucoin']['COIN3'], config['kucoin']['COIN3_SIZE'], config['kucoin']['COIN3_SIDE'], 0, None],
        [config['kucoin']['COIN4'], config['kucoin']['COIN4_SIZE'], config['kucoin']['COIN4_SIDE'], 0, None],
        [config['kucoin']['COIN5'], config['kucoin']['COIN5_SIZE'], config['kucoin']['COIN5_SIDE'], 0, None],
        [config['kucoin']['COIN6'], config['kucoin']['COIN6_SIZE'], config['kucoin']['COIN6_SIDE'], 0, None],
    ]
    invest_amount = int(config['kucoin']['INVEST_AMOUNT'])
    tp_amount = int(config['kucoin']['TAKE_PROFIT_AMOUNT'])
    sample_period = int(config['kucoin']['SAMPLE_PERIOD'])
    wait_time = int(config['kucoin']['WAIT_TIME'])
    max_profit = int(config['kucoin']['MAX_PROFIT'])
    leverage = int(config['kucoin']['LEVERAGE'])
    coin_count = int(config['kucoin']['COIN_COUNT'])
    margin_mode = config['kucoin']['MARGIN_MODE']

    api_key = config["kucoin"]["KUCOIN_KEY"]
    api_secret = config["kucoin"]["KUCOIN_SECRET"]
    api_passphrase = config["kucoin"]["KUCOIN_PASSPHRASE"]

    telegram_token = config["telegram"]["TELEGRAM_TOKEN"]
    telegram_chatid = config["telegram"]["TELEGRAM_CHATID"]

    telegram_bot = TelegramBot(telegram_token, telegram_chatid)

    timezone = pytz.timezone('Israel')
    # telegram_bot.send_message("Hi. This is testing.")
    # return
    month_array = ["January", "Febrary", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    # client = Client(api_key, api_secret, api_passphrase)
    client= Trade(key= api_key, secret = api_secret, passphrase = api_passphrase, url='')
    client1 = Market(url='https://api-futures.kucoin.com')
    with open("1.txt", "a") as file1:
        event_number = 0
        past_time = datetime.now(timezone)
        today_profit = 0
        today_profit_percent = 0
        while True:

            # open postions
            long_count = 0
            short_count = 0
            sum_invest_amount = 0
            for i in range(0, len(coins)):
                try:
                    price = float(client1.get_current_mark_price(coins[i][0])['value'])
                    temp_size = int(leverage*invest_amount/price/float(coins[i][1]))
                    if coins[i][2] == "buy" and temp_size>0: 
                        long_count += 1
                    if coins[i][2] == "sell" and temp_size>0: 
                        short_count += 1
                    coins[i][3]= temp_size
                    print(f'{coins[i][0]} {coins[i][1]} {coins[i][2]} {coins[i][3]}')
                except Exception as e:
                    print(f'Getting mark price error => {e}')
            min_count = short_count if long_count >= short_count else long_count
            print(f'{min_count} {short_count} {long_count}')
            long_count = 0
            short_count = 0 
            for i in range(0, len(coins)):
                try :
                    price = float(client1.get_current_mark_price(coins[i][0])['value'])
                    temp_size = int(leverage*invest_amount/price/float(coins[i][1]))
                except Exception as e :
                    print(f'Getting price => {e}')
                    continue
                # print(f'{coins[i][0]}  => {temp_size}')
                if temp_size == 0:
                    continue
                if coins[i][2] == "buy" and temp_size>0: 
                    long_count += 1
                    if long_count > min_count :
                        continue
                if coins[i][2] == "sell" and temp_size>0: 
                    short_count += 1
                    if short_count > min_count :
                        continue
                
                print(coins[i][0])
                try :
                    client.change_margin_mode(coins[i][0], margin_mode)
                    time.sleep(0.3)
                    client.change_cross_user_leverage(coins[i][0], leverage)
                    time.sleep(0.3)
                    price = float(client1.get_current_mark_price(coins[i][0])['value'])
                    sum_invest_amount += price * float(temp_size)*float(coins[i][1])/float(leverage)
                    print(f"invest - > {sum_invest_amount}")
                    order_id = client.create_market_order(coins[i][0], coins[i][2], size = str(temp_size), lever= leverage, marginMode = margin_mode)
                    time.sleep(0.3)
                    current_time = datetime.now(timezone)
                    print(f'Create order: {coins[i][0]}   Order ID:  {order_id}  current_time: {current_time}')

                    coins[i][4] = order_id
                except Exception as e:
                    print(f"Creating order => {e}")
            while True:
                try:
                    all_positions = client.get_all_position()
                    # print(f'sum_invest_amount=> {sum_invest_amount}')
                    sum = 0.0
                    for item in all_positions : 
                        sum+=float(item["unrealisedPnl"]) 
                        current_time = datetime.now(timezone)
                    print(f"Total TP => {sum}   current_time => {current_time }")
                    if sum > float(max_profit):
                        # close_all_positions()
                        for position in all_positions:
                            currentQty = position['currentQty']
                            opposite_side = "sell" if int(currentQty)>=0 else  "buy"
                            order_id  = client.create_market_order(position['symbol'], opposite_side, size = str(abs(int(currentQty))), lever = position['leverage'], marginMode = "CROSS")
                            print(f"{position['symbol']}  => {order_id}")
                        print(f"Every positions are finished.")
                        
                        current_time = datetime.now(timezone)
                        delay_time = current_time - past_time
                        if current_time.day != past_time.day : 
                            event_number = 0
                            today_profit = 0
                            today_profit_percentage = 0
                        days, remainder = divmod(delay_time.total_seconds(), 3600*24)
                        hours, remainder = divmod(remainder, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        event_number += 1 
                        past_time = current_time
                        elapsed_time = ""
                        if days > 0: elapsed_time = str(int(days)) + " day " + str(int(hours)) + " hour " + str(int(minutes)) + " minute"
                        else : elapsed_time = str(int(hours)) + " hour " + str(int(minutes)) + " minute"
                        today_profit += sum
                        today_profit_percentage += 100*sum/sum_invest_amount
                        telegram_bot.send_message(f"✨ Take Profit Event : Event {event_number}\n      Date : {month_array[int(current_time.month)-1]} {current_time.day}, {current_time.year}\n      Time : {current_time.hour}:{current_time.minute}:{current_time.second} (Tel Aviv)\n      Invest Amount: ${int(sum_invest_amount*100)/100.0}\n      Numbers of Coins: {min_count*2}\n      Profit Amount: ${int(sum*100)/100.0}\n      Percent Return: {int(sum/sum_invest_amount*10000)/100.0} %\n      Total Profit Today : ${int(today_profit*100)/100.0}\n      Total Profit Today : {int(today_profit_percentage*100)/100.0} %\n      Elapsed time: {elapsed_time}")
                        
                        print(f"Date/Time Timestamp : {current_time.year}.{current_time.month}.{current_time.day} {current_time.hour}:{current_time.minute}:{current_time.second}\nTake Profit Event : Event{event_number}\nInvest Amount: {sum_invest_amount}\nNumbers of Coins:{min_count*2}\nMargin % at Position Close: \nProfit Amount: {sum}\nPercent Return: {int(sum/sum_invest_amount*10000)/100.0}\nElalsed Time from Previous Event: {hours}:{minutes}:{seconds}\n--------------------------------------\n\n")
                        # file.write(f"Every positions are finished. TP => {sum}  current_time = {current_time}\n\n---------------------------------------------------------------------------\n")
                        break
                except Exception as e:
                    print(f"Error => {e}")
                time.sleep(1)
            time.sleep(1)
    



if __name__ == "__main__" :
    try : 
        bot_thread = threading.Thread(target = run_bot)
        bot_thread.start()
        print("This is main.")
    except KeyboardInterrupt:
        print("Excepting...")