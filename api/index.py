import json
import os
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def chat_with_groq(message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": message}]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except:
        pass

def handler(request):
    if request.method == "GET":
        return {"statusCode": 200, "body": "Bot is running"}
    
    try:
        body = request.body
        if isinstance(body, bytes):
            body = body.decode("utf-8")
        data = json.loads(body)
        
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            reply = chat_with_groq(text)
            send_message(chat_id, reply)
        
        return {"statusCode": 200, "body": "OK"}
    except Exception as e:
        return {"statusCode": 200, "body": f"Error: {str(e)}"}

