import neovim
from neovim import Nvim
import os
import hashlib

from .parser import Parser, Js
from .render import save_html, Browser


@neovim.plugin
class BrowseJs(object):
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    def _hash_from_bufname(self):
        buf_name = self.nvim.current.buffer.name
        hash_length = 10
        hash_object = hashlib.md5(buf_name.encode())
        return hash_object.hexdigest()[0:hash_length]

    @neovim.command("BrowseJs")
    def open(self):
        parsed = Parser.parse(self.nvim.current.buffer[:])

        dest_dir = self.nvim.vars.get("browsejs_dest_dir")
        if not dest_dir:
            dest_dir = os.environ.get("TMPDIR")

        if not dest_dir:
            dest_dir = "/tmp"  # TODO(tacogips) windows uncompatible

        buf_dir_name = "nvim_browsejs_" + self._hash_from_bufname()
        dest_path = os.path.join(dest_dir, buf_dir_name, "index.html")

        save_html(
            name=self.nvim.current.buffer.name,
            js=parsed.js,
            css=parsed.css,
            custom_tag=parsed.custom_tag,
            dest_path=dest_path,
        )

        browser = Browser(self.nvim.vars.get("browsejs_open_cmd"))
        browser.open(dest_path)
