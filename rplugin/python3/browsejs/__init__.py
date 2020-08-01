import neovim


@neovim.plugin
class BrowseJS(object):
    def __init__(self, nvim):
        self.nvim = nvim

    @neovim.function("BrowseJS")
    def browse_js(self, args):
        print(args)
        self.vim.command('echo "hello"')
