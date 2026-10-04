from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen
import json


class AppHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/api/search':
            query = parse_qs(parsed_url.query).get('q', [''])[0].strip()
            if not query:
                self.send_json({'error': 'Falta la búsqueda'}, 400)
                return

            payload = json.dumps({
                'context': {
                    'client': {
                        'clientName': 'WEB',
                        'clientVersion': '2.20260902.01.00'
                    }
                },
                'query': query
            }).encode('utf-8')
            request = Request(
                'https://www.youtube.com/youtubei/v1/search?prettyPrint=false',
                data=payload,
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            try:
                with urlopen(request, timeout=15) as response:
                    result = response.read()
                self.send_json(json.loads(result))
            except Exception:
                self.send_json({'error': 'No se pudo consultar YouTube'}, 502)
            return

        super().do_GET()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == '__main__':
    import os

    port = int(os.environ.get('PORT', '5500'))
    ThreadingHTTPServer(('0.0.0.0', port), AppHandler).serve_forever()
