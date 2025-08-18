import dash
from dash import dcc, html, Input, Output, callback, dash_table
import dash_bootstrap_components as dbc
import dash_ag_grid as dag  # AgGrid

dash.register_page(__name__, path="/")

POSITIVE = "#cd0200"
NEGATIVE = "#446e9b"
UNKNOWN = "#999"
THRESHOLD = "#d47500"

positive_buttons = html.Div(
    [
        html.Label("Positive: ", htmlFor="pos-statfit-select"),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Rug", id="pos-btn-1", n_clicks=0, color="danger", outline=False
                ),
                dbc.Button(
                    "Hist.",
                    id="pos-btn-2",
                    n_clicks=0,
                    color="danger",
                    outline=False,
                ),
                dbc.Button(
                    "Stat. Fit ↴",
                    id="pos-btn-3",
                    n_clicks=0,
                    color="danger",
                    outline=False,
                ),
            ],
            id="pos-btn-group",
            class_name="btn-group-sm",
        ),
        dcc.Dropdown(
            options=[
                {"label": "Normal", "value": "norm"},
                {"label": "Gompertz", "value": "gompertz"},
                {"label": "Exponential", "value": "expon"},
                {"label": "Expon. Norm.", "value": "exponnorm"},
            ],
            clearable=False,
            placeholder="Statistical Fit",
            id="pos-statfit-select",
            className="mb-3",
        ),
    ],
    className="positive-group",
)

negative_buttons = html.Div(
    [
        html.Label("Negative: ", htmlFor="neg-statfit-select"),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Rug", id="neg-btn-1", n_clicks=0, color="primary", outline=False
                ),
                dbc.Button(
                    "Hist.",
                    id="neg-btn-2",
                    n_clicks=0,
                    color="primary",
                    outline=False,
                ),
                dbc.Button(
                    "Stat. Fit ↴",
                    id="neg-btn-3",
                    n_clicks=0,
                    color="primary",
                    outline=False,
                ),
            ],
            id="neg-btn-group",
            class_name="btn-group-sm",
        ),
        dcc.Dropdown(
            options=[
                {"label": "Normal", "value": "norm"},
                {"label": "Gompertz", "value": "gompertz"},
                {"label": "Exponential", "value": "expon"},
                {"label": "Expon. Norm.", "value": "exponnorm"},
            ],
            clearable=False,
            placeholder="Statistical Fit",
            id="neg-statfit-select",
            className="mb-3",
        ),
    ],
    className="negative-group",
)

unknown_buttons = html.Div(
    [
        html.Label("Unknown: ", htmlFor="unknown-statfit-select"),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Rug",
                    id="unk-btn-1",
                    n_clicks=0,
                    color="secondary",
                    outline=False,
                ),
                dbc.Button(
                    "Hist.",
                    id="unk-btn-2",
                    n_clicks=0,
                    color="secondary",
                    outline=False,
                ),
                dbc.Button(
                    "Stat. Fit ↴",
                    id="unk-btn-3",
                    n_clicks=0,
                    color="secondary",
                    outline=False,
                ),
            ],
            id="unk-btn-group",
            class_name="btn-group-sm",
        ),
        dcc.Dropdown(
            options=[
                {"label": "Normal", "value": "norm"},
                {"label": "Gompertz", "value": "gompertz"},
                {"label": "Exponential", "value": "expon"},
                {"label": "Expon. Norm.", "value": "exponnorm"},
            ],
            clearable=False,
            placeholder="Statistical Fit",
            id="unknown-statfit-select",
            className="mb-3",
        ),
    ],
    className="unknown-group",
)

threshold_slider = html.Div(
    [
        dbc.Row(
            [
                html.Div(
                    "Threshold beyond which Positive",
                    id="threshold-slider-label",
                    style={
                        "textAlign": "center",
                        "padding": "0px",
                        "marginBottom": "5px",
                    },
                ),
            ]
        ),
        dbc.Row(
            [
                dcc.Slider(
                    id="slider-position",
                    min=0,
                    max=100,
                    value=0,
                    updatemode="drag",
                    tooltip={
                        "placement": "top",
                        "always_visible": True,
                        "style": {
                            "margin-top": "0px",
                            "margin-bottom": "-5px",
                        },
                    },
                ),
            ],
            align="center",
        ),
    ],
    className="p-2 border",
)

range_slider = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Button(
                        id="range-reset",
                        n_clicks=0,
                        class_name="bi bi-arrow-clockwise py-0 px-1",
                    ),
                    width="auto",
                    style={"align-self": "start"},
                ),  # Add Bootstrap margin-end
                dbc.Col(
                    dcc.RangeSlider(
                        id="range-slider",
                        min=0,
                        max=100,
                        updatemode="drag",
                        # dots=False,
                        value=[0, 100],
                        #            className="mb-3",  # Add margin-bottom
                    ),
                    width=True,
                    style={"padding": "0px"},
                ),
            ],
            align="center",
        ),
    ]
)


layout = dbc.Container(
    children=[
        html.Div(id="error-message"),  # Add a div to display error message
        # Top Row: Header and Upload
        dbc.Row(
            [
                threshold_slider,
            ]
        ),
        # Middle Row: Left Panel, Main Plot, Right Tabs
        dbc.Row(
            [
                # Left Column: Buttons and Dropdowns
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(
                                            "File:",
                                            style={"margin": "0", "padding": "0"},
                                        ),
                                        dcc.Dropdown(
                                            placeholder="Select File",
                                            clearable=False,
                                            id="file-select",
                                            className="wideDrop mb-3",  # "mb-3",
                                        ),
                                        html.P(
                                            "Column:",
                                            style={"margin": "0", "padding": "0"},
                                        ),
                                        dcc.Dropdown(
                                            placeholder="Select Column",
                                            value=None,
                                            clearable=False,
                                            id="column-select",
                                            className="wideDrop mb-3",
                                        ),
                                    ],
                                    style={"position": "relative"},
                                ),
                                html.Div(
                                    [
                                        positive_buttons,
                                    ],
                                    className="p-2 border",
                                ),
                                html.Div(
                                    [
                                        negative_buttons,
                                    ],
                                    className="p-2 border",
                                ),
                                html.Div(
                                    [
                                        unknown_buttons,
                                    ],
                                    className="p-2 border",
                                ),
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    dbc.Checklist(
                                                        options=[
                                                            {"label": "p=", "value": 1},
                                                        ],
                                                        value=[],
                                                        id="p-value",
                                                        switch=True,
                                                    ),
                                                    width=4,
                                                ),
                                                dbc.Col(
                                                    dbc.Input(
                                                        id="p-value-input", value="0.01", type="number", max=1, min=0.00, step=0.01,
                                                        style={"width": 80},
                                                    ),
                                                    width="auto",
                                                ),
                                            ],
                                            align="center",
                                            className="g-2",
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ],
                    width=2,
                    class_name="p-2 border dropdown-col",
                ),  # Adjust width as needed, add some padding and border
                # Middle Column: Main Plot
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Row(
                                            dcc.Graph(
                                                id="graph",
                                                # style={
                                                #     "width": "100%",
                                                #     "height": "450px",
                                                # },  # Set a fixed height or make it responsive
                                                config={
                                                    "doubleClick": False,
                                                    "displayModeBar": False,
                                                },
                                            )
                                        ),
                                        dbc.Row(
                                            [
                                                range_slider,
                                            ],
                                            align="start",
                                            class_name="g-0",
                                        ),
                                    ],
                                    width=6,
                                    class_name="p-2 border",
                                ),  # Adjust width, add some padding and border
                                # Right Column: Tabs (ROC Curve, ROC Table, AG-Grid)
                                dbc.Col(
                                    [
                                        dbc.Tabs(
                                            id="right-tabs",
                                            children=[
                                                dbc.Tab(
                                                    label="ROC Curve",
                                                    children=[
                                                        dcc.Graph(
                                                            id="roc_plot",
                                                            # style={"height": "525px"},
                                                            config={
                                                                "doubleClick": False,
                                                                "displayModeBar": False,
                                                            },
                                                        )  # Set height for plot
                                                    ],
                                                ),
                                                dbc.Tab(
                                                    label="File Viewer",
                                                    children=[
                                                        dag.AgGrid(
                                                            id="ag-grid",
                                                            className="ag-theme-balham",
                                                            columnDefs=[],
                                                            rowData=[],
                                                            columnSize="autoSize",
                                                            defaultColDef={
                                                                "resizable": True,
                                                                "sortable": True,
                                                                "filter": True,
                                                            },
                                                            # style={
                                                            #     "height": "525px"
                                                            # },  # Set height for the grid
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                    width=6,
                                    class_name="p-2 border",
                                ),  # Adjust width, add some padding and border
                            ],
                            style={"marginBottom": "0"},
                        ),
                        dbc.Row(
                            [
                                html.Div(
                                    [
                                        dash_table.DataTable(
                                            id="roc-table",
                                            columns=[],
                                            data=[],
                                            style_table={
                                                #   "border": "1px solid black",  # Example: 1px solid black border
                                                "width": "100%",  # Ensures the table fills the width of its parent container
                                                "height": "100%",  # Ensures the table fills the height of its parent container
                                                "overflowX": "auto",
                                            },
                                            style_cell={
                                                "whiteSpace": "normal",
                                                "overflow": "hidden",
                                                "textOverflow": "ellipsis",
                                                "fontSize": "12px",  # Adjust the font size as needed
                                                "minWidth": "0px",
                                                "width": "auto",
                                                "maxWidth": "100%",
                                            },
                                            style_data_conditional=[
                                                {
                                                    "if": {
                                                        "column_id": [
                                                            "TP",
                                                            "TN",
                                                            "Sensitivity (TPR)",
                                                            "Specificity (TNR)",
                                                        ]
                                                    },
                                                    "backgroundColor": "#ccffcc",
                                                    "color": "black",
                                                },
                                                {
                                                    "if": {
                                                        "column_id": [
                                                            "FP",
                                                            "FN",
                                                            "Miss Rate (FNR)",
                                                            "False Alarm (FPR)",
                                                        ]
                                                    },
                                                    "backgroundColor": "#ffdddd",
                                                    "color": "black",
                                                },
                                                {
                                                    "if": {
                                                        "column_id": "Positive Predictions"
                                                    },
                                                    "color": POSITIVE,
                                                },
                                                {
                                                    "if": {
                                                        "column_id": "Negative Predictions"
                                                    },
                                                    "color": NEGATIVE,
                                                },
                                            ],
                                            style_header_conditional=[
                                                {
                                                    "if": {
                                                        "column_id": [
                                                            "TP",
                                                            "TN",
                                                            "Sensitivity (TPR)",
                                                            "Specificity (TNR)",
                                                        ]
                                                    },
                                                    "backgroundColor": "#b5e6b5",
                                                    "color": "black",
                                                },
                                                {
                                                    "if": {
                                                        "column_id": [
                                                            "FP",
                                                            "FN",
                                                            "Miss Rate (FNR)",
                                                            "False Alarm (FPR)",
                                                        ]
                                                    },
                                                    "backgroundColor": "#e9c1c1",
                                                    "color": "black",
                                                },
                                                {
                                                    "if": {
                                                        "column_id": "Positive Predictions"
                                                    },
                                                    "color": "#892e2d",
                                                },
                                                {
                                                    "if": {
                                                        "column_id": "Negative Predictions"
                                                    },
                                                    "color": "#316296",
                                                },
                                            ],
                                        ),
                                    ],
                                    style={"margin-top": "0px", "padding": "0px"},
                                ),
                            ],
                            style={"marginTop": "0"},
                            class_name="p-2 border",
                        ),
                    ],
                    style={"marginBottom": "0"},
                ),
            ],
            class_name="mb-3",
        ),
    ],
)


@callback(
    Output("ag-grid", "columnSize"),
    Input("ag-grid", "columnDefs"),
    Input("right-tabs", "active_tab"),
    prevent_initial_call=True,
)
def trigger_autosize_after_data_update(_, __):
    return "autoSize"
