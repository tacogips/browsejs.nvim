import neovim
from neovim import Nvim
import os
import hashlib
from datetime import datetime

from .parser import Parser
from .render import save_html, save_metadata_script, Browser


@neovim.plugin
class BrowseJs(object):
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    def _hash_from_bufname(self):
        buf_name = self.nvim.current.buffer.name
        hash_length = 10
        hash_object = hashlib.md5(buf_name.encode())
        return hash_object.hexdigest()[0:hash_length]

    def _dest_dir(self):
        dest_dir = self.nvim.vars.get("browsejs_dest_dir")
        if not dest_dir:
            dest_dir = os.environ.get("TMPDIR")
        if not dest_dir:
            dest_dir = "/tmp"  # TODO(tacogips) windows uncompatible
        return os.path.join(dest_dir, "nvim_browsejs_" + self._hash_from_bufname())

    def _html_dest_file_path(self):
        dest_dir = self._dest_dir()
        return os.path.join(dest_dir, "index.html")

    def _file_metadata_script_file_path(self):
        dest_dir = self._dest_dir()
        return os.path.join(dest_dir, "refresh.js")

    def _do_autoreload(self):
        do_autoreload = self.nvim.vars.get("browsejs_auto_reload")
        if do_autoreload == "0":
            return False
        return True

    def save_files(self, contents):
        html_dest_path = self._html_dest_file_path()
        file_timestamp = str(int(datetime.utcnow().timestamp()))
        file_metadata_script_path = self._file_metadata_script_file_path()

        save_html(
            name=self.nvim.current.buffer.name,
            contents=contents,
            dest_path=html_dest_path,
            auto_reload=self._do_autoreload(),
            timestamp=file_timestamp,
            file_metadata=os.path.basename(file_metadata_script_path),
        )

        meta_body = {"timestamp": file_timestamp}
        save_metadata_script(body=meta_body, dest_path=file_metadata_script_path)

        return (html_dest_path, file_metadata_script_path)

    def _save_buffer_to_file(self):
        contents = Parser.parse(self.nvim.current.buffer[:])
        return self.save_files(contents)

    @neovim.command("BrowseJs")
    def open(self):
        (html_dest_path, _) = self._save_buffer_to_file()

        browser = Browser(self.nvim.vars.get("browsejs_open_cmd"))
        browser.open(html_dest_path)

    @neovim.autocmd("BufWritePost", pattern="*.js")
    def refresh(self):
        if not self._do_autoreload():
            return

        if not os.path.exists(self._html_dest_file_path()):
            return

        self._save_buffer_to_file()
