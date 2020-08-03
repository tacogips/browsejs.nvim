BrowseJs
===
![BrowseJs](https://github.com/tacogips/browsejs.nvim/blob/master/doc/screenshot.gif?raw=true)


Read javascript snippet on current buffer and run it in the browser.

Intended to run the tiny js scripts in browser on the fly.

Usecase:
- Webpack is too heavy.
- Copying and pasting to the html file is a bit pain in the neck.
- Write p5.js interactively
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

Open javascript file and run `:BrowseJs` to run js in browser.

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



```javscript

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
- custom tag lexer is a bit buggy.


### Optional variable
If you want to use specific browser to run js, you can specify the `g:browsejs_open_cmd`.

The html file will be created at `tmp dir` in default.
You can change the destination by setting the `g:browsejs_dest_dir`.

Auto refreshing the file will run on buffer write by default. set `g:browsejs_auto_reload=0` to unable it.


