import http.server
import socketserver
import os

PORT = 8080
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
BASE_PATH = "/e21-3yp-ReflectStudio"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOCS_DIR, **kwargs)

    def do_GET(self):
        # Redirect root to the base path (matches React Router basename)
        if self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", BASE_PATH + "/")
            self.end_headers()
            return

        # Strip the base path prefix so files are served from docs/
        if self.path.startswith(BASE_PATH):
            self.path = self.path[len(BASE_PATH):]
            if not self.path:
                self.path = "/"

        return super().do_GET()

if __name__ == "__main__":
    print(f"Serving {DOCS_DIR} at http://localhost:{PORT}{BASE_PATH}/")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
