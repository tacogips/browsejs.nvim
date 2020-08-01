BrowseJs
===

Read javascript snippet on current buffer and run it in the browser.

Intended to preview the tiny js scripts in browser (in the case using webpack is too heavy and copying and pasting to new html file is a bit pain in the neck).

Installation
----------
### Install with [vim-plug](https://github.com/junegunn/vim-plug)

```viml
Plug 'tacogips/browsejs.nvim', { 'do': ':UpdateRemotePlugins' }
```

## Requirements
- neovim with python3
- linux or mac

Usage
----------

Open javascript file and run `:BrowseJs` to open browser.

### Custom html tag and css
the default generated html file has a empty `<style>` tag and html body like below.

```html
<body>
<div id="app"></div>
</body>
```

You can custom these tags by write tags in js comment with special syntax.
<b>(not supported yet)</b>

### Optional variable
If you want to use specific browser to run js, you can specify the `g:browsejs_open_cmd`.

The html file will be created at `tmp dir` in default.
You can change the destination by setting the `g:browsejs_dest_dir`.
