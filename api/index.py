import json
import os
import urllib.request

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def handler(request):
    if request.method == "GET":
        return {
            "statusCode": 200,
            "body": "Bot is running"
        }
    
    try:
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        
        data = json.loads(body)
        
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            
            # Groq
            req = urllib.request.Request(
                "https://api.groq.com/openai/v1/chat/completions",
                data=json.dumps({
                    "model": "llama3-8b-8192",
                    "messages": [{"role": "user", "content": text}]
                }).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                reply = result["choices"][0]["message"]["content"]
            
            # Telegram
            urllib.request.urlopen(urllib.request.Request(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data=json.dumps({"chat_id": chat_id, "text": reply}).encode('utf-8'),
                headers={"Content-Type": "application/json"},
                method='POST'
            ), timeout=10)
        
        return {"statusCode": 200, "body": "OK"}
        
    except Exception as e:
        return {"statusCode": 200, "body": f"Error: {str(e)}"}
