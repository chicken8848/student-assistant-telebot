from chatbot import *
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, Updater, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes, ConversationHandler
import requests
import logging
import json
import re
import time
import asyncio
import telegramify_markdown
import httpx

TALK = range(1)

# Telegram bot token
with open('.teletoken', 'r') as f:
    TELEGRAM_TOKEN = f.readline().rstrip()

# RAGFlow API configuration
RAGFLOW_API_URL = "http://localhost:8080/v1/api/"
with open('.chatapi', 'r') as f:
    RAGFLOW_API_KEY = f.readline().rstrip()

# User ID list
user_ids = {}

# Knowledge base list
knowledge_base = ["Programming", "Modern China"]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def escape_elasticsearch_query(query):
    output = re.sub(
        r'(\+|\-|\=|&&|\|\||\>|\<|\!|\(|\)|\{|\}|\[|\]|\^|"|~|\*|\?|\:|\\|\/)',
        r"\\\1",
        query,
    )
    return output

async def start(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    res = create_conversation(user.first_name)
    session_id = res["data"]["id"]
    user_ids[user.first_name] = session_id
    first_message = "Hi\\! Send me a question, and I will try to answer to the best of my *knowledge*\\. \n\nCreator: @Eelauhsoj"
    await update.message.reply_text(first_message, parse_mode=ParseMode.MARKDOWN_V2)
    return TALK

async def handle_message(update: Update, context: CallbackContext) -> int:
    user = update.effective_user
    question = update.message.text
    response = await query_ragflow(escape_elasticsearch_query(question), user)
    print(response)
    await update.message.reply_text(telegramify_markdown.markdownify(response), parse_mode=ParseMode.MARKDOWN_V2)
    return TALK
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def query_ragflow(question: str, user) -> str:
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
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{RAGFLOW_API_URL}completion", headers=headers, json=data, timeout=30.0)
            response.raise_for_status()
            print(response.json())
            if response.json().get('data') is None:
                return "Error querying RAGFlow"
            return response.json().get('data', 'No answer Found')['answer']
    except httpx.RequestError as e:
        logger.error(f"RAGFlow API error: {e}")
        return 'Error querying RAGFlow'

def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().read_timeout(30).connect_timeout(30).token(TELEGRAM_TOKEN).build()
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            TALK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, timeout=None)

if __name__ == '__main__':
    main()
