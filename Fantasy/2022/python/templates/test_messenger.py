__author__ = 'chance'

# import html
import sys
import time

sys.path.append('../modules')
import os
import telebot

BOT_TOKEN = os.environ.get('TELEGRAM')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "hello from start")

#
# @bot.message_handler(func=lambda msg: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)

@bot.message_handler(commands=['hello'])
def hello(message):
    count = 1
    while True:
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        bot.send_message(message.chat.id, f"{current_time}")
        time.sleep(60)
        count += 1



bot.polling()

