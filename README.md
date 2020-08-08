BrowseJs
===
![BrowseJs](https://github.com/tacogips/browsejs.nvim/blob/master/doc/screenshot.gif?raw=true)


Read javascript snippet on current buffer and run it in the browser.

Intended to run the tiny js scripts in browser on the fly.

Usecase:
- Webpack is too heavy.
- Copying and pasting js code to the html file is a bit pain in the neck.
- Run js interactively
- etc

Installation
----------
### Install with [vim-plug](https://github.com/junegunn/vim-plug)

```viml
Plug 'tacogips/browsejs.nvim', { 'do': ':UpdateRemotePlugins' }
```

## Requirements
- Neovim with python3
- Linux or Mac
- Modern browser (IE is not included)

Usage
----------

Open javascript file and execute `:BrowseJs` to open local html file in browser.

If you need open the file on http server, run `BrowseJsServer`(http server mode).

It execute `pyton -m http.server` and open the url `http://localhost:8000/` in browser instead of local file path.

### Custom html tag and css
The generated html file has a body div tag like below in default.

```html
<html>
<head>
  <meta charset="UTF-8">
  <title>{your buffer name}</title>
  <style> </style>
</head>
<body>
  <div id="app"></div>
<script>
  // your js code
</script>
</body>
</html>

```

You can use special syntax in js comment to modify these tags. Like `{% start xxx %}` and `{% end %}`.

Availble commands:

- `header_tag` expand custom tags in `<header>`
- `custom_tag` body tag instead of `<div id="app"></div>`
- `style` inline css expand in `<style></style>`
- `copy` copy files to generated html dir. given `jsonl` lines that has `from` and `to` fields. `to` fields could be omitted if the destination is the top dir.

The codes between `{% start xxx %}` and `{% end %}` will be omitted(replaced with spaces) in generated html file.
So you can write any tags without escaping it.

```javascript

// e.g.  with p5.js
//
// {% start header_tag %}
// <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.1.9/p5.min.js"></script>
// {% end %}
//
// {% start custom_tag %}
// {% end %}
//
// {% start style  %}
// body {padding: 0; margin: 0;} canvas {vertical-align: top;}
// {% end %}

// {% start copy  %}
// {from:"path/to/icon"}
// {from:"path/to/image.jpg", to:"/images/image.jpg"}
// {% end %}

let stars = []; //star array

function setup() {
  createCanvas(800, 600);

  for (let i = 0; i < 800; i++) {
    //make a star array, and the array is a star function.
    stars[i] = new Star();
  }
}
...

```

Show `/example` dir for sample code.


#### Warning
- Custom tag lexer is a bit buggy.
- The detached python http server process might be made if nvim exits illegal way.

### Optional variable
#### browser command (g:browsejs_open_cmd)
If you want to use specific browser to run js, you can specify the `g:browsejs_open_cmd`.


#### Change output dir (g:browsejs_dest_dir)
The html file will be created at `tmp dir` in default.
You can change the destination by setting the `g:browsejs_dest_dir`.

Auto refreshing the file will run on buffer write by default. set `g:browsejs_auto_reload=0` to unable it.

#### Change http server port (g:browsejs_http_server_port)
If you need to change http server ports that `BrowseJsServer` invokes, add `g:browsejs_http_server_port=12345` (default:8000).


## TODO
- Gurantee to shutdown the python http server process safety(I tried to make pid file to write server process pid and kill the process on `VimLeave`, but I couldn't reference the value of `self.nvim.buffer` or `self.nvim.vars` to read the pid file for some reasons. It seems odd).
