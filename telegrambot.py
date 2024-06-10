from chatbot import *
import telebot
import requests
import logging
import json
import re
import time

# Telegram bot token
TELEGRAM_TOKEN = open('.teletoken', 'r').readline().rstrip()
bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode='MARKDOWN')

# RAGFlow API configuration
RAGFLOW_API_URL = "http://localhost:8080/v1/api/"
RAGFLOW_API_KEY = open('.chatapi', 'r').readline().rstrip()

# userid list
user_ids = {}

# Knowledge base list
knowledge_base = ["Programming", "Modern China"]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def escape_elasticsearch_query(query):
    output = re.sub(
        '(\+|\-|\=|&&|\|\||\>|\<|\!|\(|\)|\{|\}|\[|\]|\^|"|~|\*|\?|\:|\\\|\/)',
        "\\\\\\1",
        query,
    )
    return output

def escape_markdown(text):
    output = re.sub(r'(?<![\*\\])\*(?!\*)', r'', text)
    return output


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    res = create_conversation(user.first_name)
    session_id = res["data"]["id"]
    user_ids[user.first_name] = session_id
    first_message = "Hi! Send me a question, and I will try to answer to the best of my **knowledge**. \n\nCreator: @Eelauhsoj"
    bot.reply_to(message, escape_markdown(first_message))

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user = message.from_user
    question = message.text
    response = query_ragflow(escape_elasticsearch_query(question), user)
    print(escape_markdown(response))
    bot.reply_to(message, escape_markdown(response))

def query_ragflow(question: str, user: str) -> str:
    print(user_ids)
    headers = {
        'Authorization': f'Bearer {RAGFLOW_API_KEY}',
        'Content-Type': 'application/json'
    }
    messages = {
        'role': 'user',
        'content': question
    }
    data = {
            'conversation_id': user_ids[user.first_name],
            'messages': [messages],
            'stream': False
            }
    print(data)
    try:
        response = requests.post(f"{RAGFLOW_API_URL}completion", headers=headers, json=data)
        response.raise_for_status()
        print(response.json())
        if (response.json().get('data') is None):
            return "Error querying RAGFlow"
        return response.json().get('data', 'No answer Found')['answer'] 
    except requests.exceptions.RequestException as e:
        logger.error(f"RAGFlow API error: {e}")
        return 'Error querying RAGFlow'

def main():
    bot.polling()

if __name__ == '__main__':
    while True:
        try:
            main()
        except Exception as e:
            logger.error(f"Bot crashed with error: {e}")
            time.sleep(5)  # Wait for a few seconds before restarting
            logger.info("Restarting bot...")
