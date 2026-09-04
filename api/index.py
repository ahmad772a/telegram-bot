import json
import os
import urllib.request

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def make_request(url, data=None, headers=None):
    req = urllib.request.Request(url, method="POST" if data else "GET")
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    if data:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(data).encode('utf-8')
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode('utf-8'))

def handler(request):
    try:
        method = getattr(request, 'method', 'GET')
        
        if method == 'GET':
            return {"statusCode": 200, "body": "Bot is running"}
        
        body = getattr(request, 'body', b'{}')
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        
        data = json.loads(body)
        
        if "message" in data and "text" in data["message"]:
            chat_id = data["message"]["chat"]["id"]
            text = data["message"]["text"]
            
            # Groq
            result = make_request(
                "https://api.groq.com/openai/v1/chat/completions",
                data={"model": "llama3-8b-8192", "messages": [{"role": "user", "content": text}]},
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"}
            )
            
            reply = result["choices"][0]["message"]["content"]
            
            # Telegram
            make_request(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": chat_id, "text": reply}
            )
        
        return {"statusCode": 200, "body": "OK"}
        
    except Exception as e:
        return {"statusCode": 200, "body": f"Error: {str(e)}"}

