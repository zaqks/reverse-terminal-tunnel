import os
import threading
import tornado.web
import tornado.ioloop
import tornado.netutil
import tornado.httpserver
from terminado import UniqueTermManager
from terminado.websocket import TermSocket

class MyTermSocket(TermSocket):
    def check_origin(self, origin):
        return True

# Global manager so main.py can access it for clean shutdown
term_manager = None
server = None

def start_terminal_server(port=8888):
    global term_manager, server
    
    # Configure clean bash environment
    env = os.environ.copy()
    env["PS1"] = r"\[\e[32m\]\u@\h\[\e[m\]:\[\e[34m\]\w\[\e[m\]\$ "

    term_manager = UniqueTermManager(
        shell_command=["/bin/bash"],
        extra_env=env
    )

    app = tornado.web.Application([
        (r"/term", MyTermSocket, {"term_manager": term_manager}),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": ".", "default_filename": "index.html"}),
    ])

    sockets = tornado.netutil.bind_sockets(port, '', reuse_port=True)
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    
    print(f"[+] Terminal backend listening on http://127.0.0.1:{port}")
    tornado.ioloop.IOLoop.current().start()

def stop_terminal_server():
    """Triggers terminal process cleanup and stops the IOLoop."""
    global term_manager, server
    print("[*] Stopping Tornado server and reaping processes...")
    
    if term_manager:
        term_manager.shutdown()
        
    if server:
        server.stop()
        
    loop = tornado.ioloop.IOLoop.current()
    loop.add_callback(loop.stop)