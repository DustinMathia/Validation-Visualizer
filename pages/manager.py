import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_ag_grid as dag  # AgGrid
from dash import (
    Dash,
    html,
    callback,
    Input,
    Output,
    State,
    ctx,
    ALL,
    no_update,
    dcc,
    page_container,
)
import pandas as pd
import json

dash.register_page(
    __name__,
    path="/data-manager",
)


layout = dbc.Container(
    children=[
        dcc.Store(id="manage-files-button-click"),
        dbc.Col(
            dcc.Upload(
                id="upload-data",
                multiple=True,
                children=html.Div([
                    "Drag and Drop or ",
                    html.A("Select Files", className="navlink")
                ]),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center'
                },
                className="my-2",
            ),
            width=12,
        ),
        dbc.Row(
            [
                dbc.Col(
                    dag.AgGrid(
                        id="manage-files",
                        className="ag-theme-balham",
                        defaultColDef = {
                            "sortable": False,
                            "filter": False,
                            "resizable": False,
                            "flex": False,
                            "autoHeight": True,
                        },
                        columnDefs = [
                            {"field": "filename", "sortable": True, "filter": True, "flex": True},
                            {"field": "view",
                             "width": 80,
                             "cellRenderer": "Button",
                             "cellRendererParams": {"className": "btn btn-info btn-sm"},
                             },
                            {"field": "download",
                             "width": 110,
                             "cellRenderer": "Button",
                             "cellRendererParams": {"className": "btn btn-success btn-sm"},
                             },
                            {"field": "delete",
                             "width": 85,
                             "cellRenderer": "Button",
                             "cellRendererParams": {"className": "btn btn-danger btn-sm"},
                             },
                            ],
                    ),
                    width=6,
                ),
                dbc.Col(
                    dag.AgGrid(
                        id="view-file",
                        className="ag-theme-balham",
                        columnSize="autoSize",
                        defaultColDef={
                            "resizable": True,
                            "sortable": True,
                            "filter": True,
                        },
                        # other props
                    ),
                    width=6,
                ),
            ],
        ),
    ]
)

@callback(
        Output("manage-files", "rowData"),
        Input("processed-files-list", "data"),
)
def add_files_to_grid(files):
    data = {
        "filename": files,
        "view": ["View" for f in files],
        "download": ["Download" for f in files],
        "delete": ["Delete" for f in files],
    }
    df = pd.DataFrame(data)
    return df.to_dict("records")

@callback(
    Output("manage-files-button-click", "data"),
    Input("manage-files", "cellRendererData"),
)
def showChange(n):
    if not n:
        return no_update
    print(json.dumps(n))
    return no_update


