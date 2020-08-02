from .parser import Contents
import os
import webbrowser
import json

html_template = """<!DOCTYPE html>
<html>
<head>
	<meta charset="UTF-8">
	<title>{name}</title>
{custom_header_tags}
<style> {css} </style>
</head>
<body>
{tag}
</body>
{auto_reload_script}

<script>
{js}
</script>
</html>
"""

_default_tag = '<div id="app"></div>'

_auto_reload_script = """
<script>
(function(window, document, location){{

    var current_file_timestamp = "{current_file_timestamp}";
    var refresh_interval = 1000;

    function jsonp(url){{
        return new Promise(function(resolve, reject){{
            var callback_name = "refresh_callback"
            var script = document.createElement('script');
            script.src = url+"?callback=" + callback_name+"&t="+Date.now();
            script.async = "true";

            window[callback_name] = function(data){{
                resolve(data);
                script.parentNode.removeChild(script);
                delete window[callback_name];
            }};

            (document.getElementsByTagName('head')[0] || document.body || document.documentElement).appendChild(script)
        }});
    }}

    function checkUpdateAndReload(){{
        var refresh_metadata = jsonp("{file_metadata}")
        refresh_metadata.then((metadata) => {{
                if (current_file_timestamp  !==  metadata.timestamp){{
                    location.reload();
                }}
        }});
    }}

    setInterval(checkUpdateAndReload, refresh_interval);
}})(window, document, location);
</script>
"""


_metadata_file = """
(function(){{
refresh_callback({json_data});
}})();
"""


def save_metadata_script(body: dict, dest_path: str):
    contents = _metadata_file.format(json_data=json.dumps(body))
    with open(dest_path, "w") as f:
        f.write(contents)


def save_html(
    name,
    contents: Contents,
    dest_path: str,
    auto_reload: bool,
    timestamp: str,
    file_metadata: str,
):
    tag = "\n".join(contents.custom_tags)
    if not tag:
        tag = _default_tag

    auto_reload_script = _auto_reload_script.format(
        current_file_timestamp=str(timestamp), file_metadata=file_metadata
    )
    if not auto_reload:
        auto_reload_script = ""

    contents = html_template.format(
        name=name,
        custom_header_tags="\n".join(contents.custom_header_tags),
        js="\n".join(contents.js_lines),
        css="\n".join(contents.custom_styles),
        tag=tag,
        auto_reload_script=auto_reload_script,
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
            webbrowser.open("file://" + file_path)
