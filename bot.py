import os
import telebot
import json
from chatbot import *

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='Markdown')

knowledge_bases = ["pure mathematics", "statistics", "cryptography"]
doc_ids = []

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    text = "Hello, I am running on Llama3:8b with some knowledge bases to assist you, what are you looking for today?")
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, query_handler)

def query_handler(func=lambda message: message.text.lower() in knowledge_bases):
    json_data = get_doc_id(message.text)
    doc_ids = extract_id(json_data)
    text = "What would you like to find out?"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, response_handler)

def response_handler(message):
    query = message.text

def extract_id(json_package):
    parsed_data = json.loads(json_package)
    output = [doc["doc_id"] for doc in parsed_data["data"]["docs"]]
    return output


'''
@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)
'''

bot.infinity_polling()
