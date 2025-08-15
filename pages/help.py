import dash
from dash import dcc, html
import os

dash.register_page(
    __name__,
    path="/help",
)


# current_script_dir = os.path.dirname(os.path.abspath(__file__))
# parent_dir = os.path.join(current_script_dir, os.pardir)
# parent_dir_absolute = os.path.abspath(parent_dir)
# file_name = "README.md"
# file_path = os.path.join(parent_dir_absolute, file_name)

try:
    with open(os.path.join("pages","help.md"), "r", encoding="utf-8") as f:
        readme_content = f.read()
except FileNotFoundError:
    readme_content = "README.md not found."

layout = html.Div([dcc.Markdown(children=readme_content)])
