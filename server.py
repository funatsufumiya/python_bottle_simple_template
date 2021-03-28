
# pip install bottle
# pip install python-osc

import signal, sys
from bottle import route, run, template, Bottle, ServerAdapter
from pythonosc import osc_message_builder
from pythonosc import udp_client

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

osc_host = "127.0.0.1" # WORKAROUND: localhost does not work well on Windows
osc_port = 6000

def send_osc(addr):
    client = udp_client.UDPClient(osc_host, osc_port)
    msg = osc_message_builder.OscMessageBuilder(address=addr)
    msg = msg.build()
    client.send(msg)

app = Bottle()

@app.route('/test')
def test():
    address = "/test"
    send_osc(address)
    return template('OSC {{address}} was sent to {{osc_host}}:{{osc_port}}!',
        address=address,
        osc_host=osc_host,
        osc_port=osc_port
        )

@app.route('/is_alive')
def is_alive():
    return "alive"

#run(host='127.0.0.1', port=8080)
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