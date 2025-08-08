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
import os


SAVED_FILE_NAMES = {
    "roc curves": "roc_curves.pkl",
    "raw data": "raw_data.feather",
    "labeled data": "labeled_data.pkl",
    "parameter fitting": "fitted_params.pkl",
}

DATA_FOLDER = "data"


dash.register_page(
    __name__,
    path="/data-manager",
)


layout = dbc.Container(
    children=[
        dcc.Store(id="manage-files-button-click", data={}),
        dcc.Download(id="download-xlsx"),
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
                        # className="ag-theme-balham",
                        defaultColDef = {
                            "sortable": False,
                            "filter": False,
                            "resizable": False,
                            "flex": False,
                            "rowHeight": 500,
                        },
                        dashGridOptions={
                            "rowHeight": 35,  # Sets all rows to 50px height
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
                        id="file-viewer",
                        className="ag-theme-balham",
                        columnDefs=[],
                        rowData=[],
                        columnSize="autoSize",
                        defaultColDef = {
                            "sortable": True,
                            "filter": True,
                            "resizable": True,
                        },
                        # dashGridOptions={
                        #     "rowHeight": 20,
                        # },
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
def save_row_data(n):
    if not n:
        return no_update
    return n


@callback(
        Output("file-viewer", "columnDefs"),
        Output("file-viewer", "rowData"),
        Output("download-xlsx", "data"),
        Output("processed-files-list", "data", allow_duplicate=True),
        Input("manage-files-button-click", "data"),
        State("manage-files", "rowData"),
        State("processed-files-list", "data"),
        prevent_initial_call=True
)
def button_manager(button_data, row_data, processed_files):
    row      = button_data["rowIndex"]
    action   = button_data["colId"]
    filename = row_data[row]["filename"]
    filepath = os.path.join(DATA_FOLDER, filename, SAVED_FILE_NAMES["raw data"])

    out_columnDefs = None
    out_rowData = None
    out_download = None

    match action:
        case "view":
            df = pd.read_feather(filepath)
            out_rowData=df.to_dict("records")
            out_columnDefs=[
                        {
                            "headerName" : filename,
                            "children" : [{"field": i} for i in df.columns]
                        }
                    ]
        case "download":
            df = pd.read_feather(filepath)
            out_download = dcc.send_data_frame(df.to_excel, filename, sheet_name="Sheet1")
        case "delete":
            processed_files.remove(filename)
            os.remove(filepath)

    return out_columnDefs, out_rowData, out_download, processed_files

@callback(
    Output('file-viewer', 'columnSize'),
    Input('file-viewer', 'columnDefs'),
    prevent_initial_call=True
)
def trigger_autosize_after_data_update(_):
    return "autoSize"
