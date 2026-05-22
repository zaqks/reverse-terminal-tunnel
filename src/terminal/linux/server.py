import os
import tornado.web
import tornado.ioloop
import tornado.netutil
import tornado.httpserver
from terminado import UniqueTermManager  # Changed from SingleTermManager
from terminado.websocket import TermSocket

class MyTermSocket(TermSocket):
    def check_origin(self, origin):
        return True
    
    def on_close(self):
        # Optional: Clean up the terminal process immediately when tab closes
        super().on_close()

# Force a clean prompt
env = os.environ.copy()
env["PS1"] = r"\[\e[32m\]\u@\h\[\e[m\]:\[\e[34m\]\w\[\e[m\]\$ "

# UniqueTermManager spawns a new bash for every websocket connection
term_manager = UniqueTermManager(
    shell_command=["/bin/bash"],
    extra_env=env
)

app = tornado.web.Application([
    # TermSocket needs the manager to handle multiple terminals
    (r"/term", MyTermSocket, {"term_manager": term_manager}),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": ".", "default_filename": "index.html"}),
])

if __name__ == "__main__":
    port = 8888
    sockets = tornado.netutil.bind_sockets(port, '', reuse_port=True)
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    
    print(f"Terminal available at http://localhost:{port}")
    try:
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        term_manager.shutdown() # Clean up all child processes
        print("\nShutting down...")