import os
import sys
from subprocess import Popen
import signal


class HttpServer:
    def __init__(self, port: str, dir_path: str):
        self.port = port
        self.dir_path = dir_path

    def invoke(self,):
        with open(os.devnull) as devnull:
            p = Popen(
                ["python", "-m", "http.server", self.port],
                cwd=self.dir_path,
                stdout=devnull,
                stderr=devnull,
            )
            return p
