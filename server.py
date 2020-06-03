import cgi
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse

from WebHooksHandler import WebHooksHandler
from config import CONFIG


class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('ascii')
        body = parse.parse_qs(body, keep_blank_values=True)

        handler = WebHooksHandler()
        handler.handle(body['payload'][0])

        return self.ok_response()

    def ok_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"OK\n")


server = HTTPServer(('', CONFIG['server_port']), MyHandler)
print('Server listening port: ', CONFIG['server_port'])

try:
    server.serve_forever()
except KeyboardInterrupt:
    print('Shut down the web server...')
    server.socket.close()
print('Server stopped')
