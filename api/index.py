import json
import os
import urllib.request
import traceback

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def send_telegram(chat_id, text):
    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data=json.dumps({"chat_id": chat_id, "text": text}).encode('utf-8'),
            headers={"Content-Type": "application/json"},
            method='POST'
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        pass

def handler(request):
    if request.method == "GET":
        return {"statusCode": 200, "body": "Bot is running"}
    
    try:
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        
        data = json.loads(body)
        
        if "message" not in data:
            return {"statusCode": 200, "body": "No message"}
        
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        
        # أولاً: أرسل "تم الاستلام"
        send_telegram(chat_id, f"Received: {text}")
        
        # ثانياً: جرب Groq
        try:
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
            
            send_telegram(chat_id, reply)
            
        except Exception as groq_error:
            send_telegram(chat_id, f"Groq Error: {str(groq_error)}")
        
        return {"statusCode": 200, "body": "OK"}
        
    except Exception as e:
        error_msg = traceback.format_exc()
        # حاول إرسال الخطأ لو عرفنا chat_id
        try:
            data = json.loads(request.body.decode('utf-8'))
            if "message" in data:
                chat_id = data["message"]["chat"]["id"]
                send_telegram(chat_id, f"Main Error: {str(e)}")
        except:
            pass
        return {"statusCode": 200, "body": f"Error: {str(e)}"}

