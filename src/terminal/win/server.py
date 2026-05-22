import os
import json
import tornado.web
import tornado.ioloop
import tornado.websocket
from winpty import PtyProcess

class MyTermSocket(tornado.websocket.WebSocketHandler):
    def initialize(self):
        # Use cmd.exe or powershell.exe for the Windows shell
        self.pty = PtyProcess.spawn('cmd.exe')
        self.term_manager = tornado.ioloop.PeriodicCallback(self.read_from_pty, 10)

    def check_origin(self, origin):
        return True

    def open(self):
        self.term_manager.start()

    def on_message(self, message):
        data = json.loads(message)
        if data[0] == 'stdin':
            self.pty.write(data[1])
        elif data[0] == 'set_size':
            self.pty.set_winsize(data[1], data[2])

    def read_from_pty(self):
        try:
            # Non-blocking read from the Windows terminal
            output = self.pty.read(1024)
            if output:
                self.write_message(json.dumps(['stdout', output]))
        except EOFError:
            self.term_manager.stop()
            self.close()

    def on_close(self):
        self.term_manager.stop()
        if self.pty.isalive():
            self.pty.terminate()

app = tornado.web.Application([
    (r"/term", MyTermSocket),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": ".", "default_filename": "index.html"}),
])

if __name__ == "__main__":
    port = 8888
    app.listen(port)
    print(f"Windows Terminal available at http://localhost:{port}")
    tornado.ioloop.IOLoop.current().start()