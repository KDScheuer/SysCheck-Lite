import webbrowser
import tempfile
import os
from html import escape

def to_html(results: dict, host: str) -> None:
    html_lines = [
        "<html>",
        "<head>",
        f"<title>System Info: {escape(host)}</title>",
        "<style>",
        "body {",
        "  background: linear-gradient(to bottom, #1e1e1e, #000000);",
        "  color: #eeeeee;",
        "  font-family: 'Segoe UI', sans-serif;",
        "  padding: 40px;",
        "  line-height: 1.6;",
        "  text-align: center;",
        "}",
        "h1 {",
        "  color: #00FF00;",
        "  margin-bottom: 20px;",
        "  text-align: center;",
        "}",
        ".content-box {",
        "  display: inline-block;",      
        "  text-align: left;",            
        "  background-color: #111;",     
        "  padding: 20px 30px;",         
        "  border-radius: 10px;",        
        "  box-shadow: 0 0 10px #000;",  
        "  max-width: max-content;",     
        "  margin: auto;",               
        "}",
        "ul { list-style-type: none; padding-left: 0; }",
        "li { margin-bottom: 10px; }",
        "li > ul {",
        "  margin-top: 5px;",
        "  padding-left: 20px;",
        "  border-left: 2px solid #333;",
        "}",
        "strong { color: #00FF00; }",
        "code {",
        "  background-color: #222;",
        "  padding: 2px 4px;",
        "  border-radius: 4px;",
        "  font-family: monospace;",
        "}",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>System Info: {escape(host)}</h1>",
        "<div class='content-box'>",
        "<ul>"
    ]

    for key, value in results.items():
        html_lines.append(f"<li><strong>{escape(str(key))}</strong>:")
        if isinstance(value, dict):
            html_lines.append("<ul>")
            for sub_key, sub_value in value.items():
                html_lines.append(
                    f"<li><strong>{escape(str(sub_key))}</strong>: <code>{escape(str(sub_value))}</code></li>"
                )
            html_lines.append("</ul>")

        elif isinstance(value, list):
            html_lines.append("<pre style='background-color: #222; padding: 10px; border-radius: 5px; text-align: left;'>")
            for item in value:
                html_lines.append(escape(str(item)))
            html_lines.append("</pre>")

        else:
            html_lines.append(f" <code>{escape(str(value))}</code>")
        html_lines.append("</li>")

    html_lines.extend([
        "</ul>",
        "</div>",
        "</body>",
        "</html>"
    ])

    html_content = "\n".join(html_lines)

    # Save to a temporary file and open it
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as f:
        f.write(html_content)
        file_path = f.name

    webbrowser.open(f"file://{os.path.abspath(file_path)}")
