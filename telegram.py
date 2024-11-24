import requests
import os
import datetime
import logging
import sys


class TelegramBot:
    def __init__(self, api_token, chat_id):
        self.api_token = api_token
        self.chat_id = chat_id


    def send_message(self, message, print_terminal=True):
        api_url = f'https://api.telegram.org/bot{self.api_token}/sendMessage'

        try:
            response_1 = requests.post(api_url, json={'chat_id': self.chat_id, 'text': message})
            # # print(response.text)
            # print(response_1.status_code)
            # print(response_2.status_code)
        except Exception as e:
            self.logger.error("Exception! Telegram Bot.", e)
