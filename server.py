import http.server
import socketserver

# 서버 포트 설정
PORT = 8000

# 디렉토리를 HTTP로 제공
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    print(f"Access your files at http://localhost:{PORT}")
    httpd.serve_forever()
