
# pip install bottle

import signal, sys
from bottle import route, run, template, Bottle, ServerAdapter

class CustomWSGIServer(ServerAdapter):
    server = None

    def run(self, handler):
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self):
        # self.server.server_close() <--- alternative but causes bad fd exception
        self.server.shutdown()

app = Bottle()

@app.route('/test')
def test():
    return "test"

@app.route('/is_alive')
def is_alive():
    return "alive"

server = CustomWSGIServer(host='127.0.0.1', port=8080)

def exit_gracefully(self,signum, frame):
    server.stop()

signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)
if hasattr(signal, 'SIGBREAK'):
    signal.signal(signal.SIGBREAK, exit_gracefully)

try:
    app.run(server=server)
except:
    print('Bye')