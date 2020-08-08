import os
import sys
from subprocess import Popen
import signal


class HttpServer:
    def __init__(self, port: str, dir_path: str):
        self.port = port
        self.dir_path = dir_path

    def invoke(self, kill_process_if_any=True):
        if kill_process_if_any:
            self.kill_process()

        with open(os.devnull) as devnull:
            p = Popen(
                ["python", "-m", "http.server", self.port],
                cwd=self.dir_path,
                stdout=devnull,
                stderr=devnull,
            )

            with open(os.path.join(self.dir_path, "http_server.pid"), "w") as f:
                f.write(str(p.pid))

            return p

    def kill_process(self):
        pid_path = os.path.join(self.dir_path, "http_server.pid")
        if not os.path.exists(pid_path):
            return
        pid = None
        with open(pid_path) as f:
            pid = f.read()

        if not pid:
            return

        try:
            os.kill(int(pid), signal.SIGTERM)
            os.remove(pid_path)
        except ProcessLookupError:
            if os.path.exists(pid_path):
                os.remove(pid_path)
