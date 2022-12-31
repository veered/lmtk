import threading, socket
from http.server import HTTPServer, BaseHTTPRequestHandler

class RequestHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    """Handle a GET request by calling the handler function and returning the response."""
    self.send_response(200)
    self.end_headers()
    result = self.server.handler(self.request, self.path) or ''
    self.wfile.write(result.encode())

  def log_request(self, *args, **kwargs):
    pass
  def log_request_line(self, *args, **kwargs):
    pass
  # def log_error(self, *args, **kwargs):
  #   pass
  def log_message(self, *args, **kwargs):
    pass

class SimpleServer(threading.Thread):
  def __init__(self, handler, host='localhost', port=8080):
    """
    Initialize the threaded HTTP server with the specified host, port, and handler function.
    The handler function should take in a request object and return the response string.
    """
    self.handler = handler
    self.host = host
    self.port = port
    self.running = False

    super().__init__(daemon=True)

  def start(self):
    if self.is_port_used(self.port):
      return False

    self.httpd = HTTPServer((self.host, self.port), RequestHandler)
    self.httpd.handler = self.handler
    super().start()

    return True

  def run(self):
    """Start the HTTP server in a separate thread."""
    self.running = True
    self.httpd.serve_forever()

  def stop(self):
    """Stop the HTTP server."""
    if self.running:
      self.httpd.shutdown()
      self.httpd.socket.close()

  def is_port_used(self, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      return s.connect_ex(('localhost', port)) == 0
