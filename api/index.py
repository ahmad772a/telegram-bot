from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')
    
    def do_POST(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

