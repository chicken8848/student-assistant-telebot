from chatbot import *
import telebot
import requests
import logging
import json

# Telegram bot token
TELEGRAM_TOKEN = open('.teletoken', 'r').readline().rstrip()
bot = telebot.TeleBot(TELEGRAM_TOKEN)

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

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    res = create_conversation(user.first_name)
    session_id = res["data"]["id"]
    user_ids[user.first_name] = session_id
    bot.reply_to(message, "Hi! Send me a question, and I will try to answer it using RAGFlow.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user = message.from_user
    question = message.text
    response = query_ragflow(question, user)
    bot.reply_to(message, response)

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
            'messages': messages
            }
    print(data)
    try:
        response = requests.post(f"{RAGFLOW_API_URL}/completion", headers=headers, json=data)
        response.raise_for_status()
        print(response.json())
        return response.json().get('answer', 'No answer found')
    except requests.exceptions.RequestException as e:
        logger.error(f"RAGFlow API error: {e}")
        return 'Error querying RAGFlow'

def main():
    bot.polling()

if __name__ == '__main__':
    main()
