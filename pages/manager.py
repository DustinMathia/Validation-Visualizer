import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_ag_grid as dag  # AgGrid

dash.register_page(
    __name__,
    path="/data-manager",
)

layout = dbc.Container(
    children=[
        dbc.Col(
            dcc.Upload(
                id="upload-data",
                children=html.Div(["Drag and Drop or ", html.A("Select Files")]),
                style={
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=True,  # Allow multiple files to be uploaded
            ),
            width=12,
        ),
        dag.AgGrid(
            id="manage-files",
            className="ag-theme-balham",
            columnDefs = [
                {"field": "Filename"},
                # {"field": "Download"},
                # {"field": "Delete"},
                ],
            # other props
        ),
    ]
)
