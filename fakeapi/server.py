""" fakeapi http server """
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

class FakeAPIHTTPHandler(BaseHTTPRequestHandler):
    """ Class handler for HTTP """

    def _set_response(self, status_code, data):
        """ set response """
        self.send_response(status_code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(str(data).encode())

    def do_ALL(self):
        """ do http calls """
        self.log_message(f"{self.command} {self.headers['Host']}{self.path}")
        self.log_message(f'=> {self.command} {self.server.http_prefix}{self.path}')
        content_length = int(self.headers['Content-Length'])
        text = self.rfile.read(content_length).decode('utf-8')
        self.log_message(text)
        payload = json.loads(text)
        call = getattr(self.server.fakeapi, f'{self.command.lower()}')
        response = call(f'{self.server.http_prefix}{self.path}', data=payload)
        self._set_response(response.status_code, response.text)

    do_GET    = do_ALL
    do_POST   = do_ALL
    do_PUT    = do_ALL
    do_DELETE = do_ALL

class FakeAPIServer(HTTPServer):
    """ HTTPServer with fakeapi """
    def __init__(self, fakeapi, http_prefix, start, *args, **kwargs):
        """ add fakeapi property """
        self.fakeapi = fakeapi
        self.http_prefix = http_prefix
        super().__init__(*args, **kwargs)
        if start:
            self.serve_forever()
