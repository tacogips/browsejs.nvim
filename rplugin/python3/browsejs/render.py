from .parser import Css, CustomTag, Js
import os
import webbrowser


html_template = """<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>{name}</title>
<style> {css} </style>

</head>
<body>
{tag}
</body>
<script>
{js}
</script>
</html>
"""

default_tag = '<div id="app"></div>'


def _get_lines(obj):
    if obj:
        return obj.lines
    return []


def save_html(name, js: Js, css: Css, custom_tag: CustomTag, dest_path: str):
    tag = "\n".join(_get_lines(custom_tag))
    if not tag:
        tag = default_tag

    contents = html_template.format(
        name=name,
        js="\n".join(_get_lines(js)),
        css="\n".join(_get_lines(css)),
        tag=tag,
    )

    dest_dir = os.path.dirname(dest_path)
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with open(dest_path, "w") as f:
        f.write(contents)


class Browser:
    def __init__(self, open_cmd=None):
        self.open_cmd = open_cmd

    def open(self, file_path: str):
        # TODO(tacogips) windows uncompatible now
        if self.open_cmd:
            os.system(open_cmd + " ", file_path)
        else:
            webbrowser.open("file:///" + file_path)
