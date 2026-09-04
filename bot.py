import requests
import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def chat_with_groq(message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": message}]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

async def handle_message(update: Update, context):
    reply = await chat_with_groq(update.message.text)
    await update.message.reply_text(reply)

async def webhook(request):
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    update = Update.de_json(json.loads(request.body), application.bot)
    await application.process_update(update)
    return {"statusCode": 200}

# Vercel handler
def handler(request):
    import asyncio
    return asyncio.run(webhook(request))


