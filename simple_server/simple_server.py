import http.server
import socketserver

#from https://docs.python.org/3/library/http.server.html

PORT = 8000

handler = http.server.SimpleHTTPRequestHandler

handler.extensions_map = {
	'.manifest': 'text/cache-manifest',
	'.html': 'text/html',
	'.png': 'image/png',
	'.jpg': 'image/jpg',
	'.css':	'text/css',
	'.js':	'application/x-javascript',
	'': 'application/octet-stream',
}

with socketserver.TCPServer(("", PORT), handler) as httpd:
	print("serving at port", PORT)
	httpd.serve_forever()

