import context  # noqa
import sys

import neovim
from browsejs import BrowseJs


def run(nvim_listner_socket_path):
    nvim = neovim.attach("socket", path=nvim_listner_socket_path)
    browse_js = BrowseJs(nvim)
    browse_js.open()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Need nvim socket file path that is set to $NVIM_LISTEN_ADDRESS")
        exit()

    run(sys.argv[1])
