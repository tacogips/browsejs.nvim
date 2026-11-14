import neovim
from neovim import Nvim
import os
import hashlib
from datetime import datetime

from .parser import Parser
from .render import save_html, copy_files, save_metadata_script, Browser
from .server import HttpServer


@neovim.plugin
class BrowseJs(object):
    def __init__(self, nvim: Nvim):
        self.nvim = nvim

    def _hash_from_bufname(self, buf_name):
        hash_length = 10
        hash_object = hashlib.md5(buf_name.encode())
        return hash_object.hexdigest()[0:hash_length]

    def _parent_dest_dir(self):
        dest_dir = self.nvim.vars.get("browsejs_dest_dir")
        if not dest_dir:
            dest_dir = os.environ.get("TMPDIR")
        if not dest_dir:
            dest_dir = "/tmp"  # TODO(tacogips) windows uncompatible

        return dest_dir

    def _dest_dir(self, buf_name):
        parent_dir = self._parent_dest_dir()

        return os.path.join(
            parent_dir, "nvim_browsejs_" + self._hash_from_bufname(buf_name)
        )

    def _html_dest_file_path(self, buf_name):
        dest_dir = self._dest_dir(buf_name)
        return os.path.join(dest_dir, "index.html")

    def _file_metadata_script_file_path(self, buf_name):
        dest_dir = self._dest_dir(buf_name)
        return os.path.join(dest_dir, "refresh.js")

    def _do_autoreload(self):
        do_autoreload = self.nvim.vars.get("browsejs_auto_reload")
        if do_autoreload == "0":
            return False
        return True

    def save_files(self, contents, buf_name):
        html_dest_path = self._html_dest_file_path(buf_name)
        file_timestamp = str(int(datetime.utcnow().timestamp()))
        file_metadata_script_path = self._file_metadata_script_file_path(buf_name)

        save_html(
            name=self.nvim.current.buffer.name,
            contents=contents,
            dest_path=html_dest_path,
            auto_reload=self._do_autoreload(),
            timestamp=file_timestamp,
            file_metadata=os.path.basename(file_metadata_script_path),
        )

        copy_files(contents=contents, dest_path=file_metadata_script_path)

        meta_body = {"timestamp": file_timestamp}
        save_metadata_script(body=meta_body, dest_path=file_metadata_script_path)

        return (html_dest_path, file_metadata_script_path)

    def _save_buffer_to_file(self, buf_name):
        contents = Parser.parse(self.nvim.current.buffer[:])
        return self.save_files(contents, buf_name)

    @neovim.command("BrowseJs")
    def open_local(self):
        buf_name = self.nvim.current.buffer.name
        (html_dest_path, _) = self._save_buffer_to_file(buf_name)

        browser = Browser(self.nvim.vars.get("browsejs_open_cmd"))
        browser.open(html_dest_path)

    def _get_server_port(self):
        return str(self.nvim.vars.get("browsejs_http_server_port", "8000"))

    def _get_http_server(self, buf_name):
        return HttpServer(
            port=self._get_server_port(), dir_path=self._dest_dir(buf_name),
        )

    @neovim.command("BrowseJsServer")
    def open_server(self):
        buf_name = self.nvim.current.buffer.name
        (html_dest_path, _) = self._save_buffer_to_file(buf_name)

        server = self._get_http_server(buf_name)
        server.invoke()

        browser = Browser(self.nvim.vars.get("browsejs_open_cmd"))
        url = f"http://localhost:{server.port}"
        browser.open_url(url)
        return server

    @neovim.command("BrowseJsStopServer")
    def stop_server(self):
        buf_name = self.nvim.current.buffer.name
        server = self._get_http_server(buf_name)
        server.kill_process()

    @neovim.autocmd("BufWritePost", pattern="*.js")
    def refresh(self):
        if not self._do_autoreload():
            return

        buf_name = self.nvim.current.buffer.name
        if not os.path.exists(self._html_dest_file_path(buf_name)):
            return

        self._save_buffer_to_file(buf_name)
