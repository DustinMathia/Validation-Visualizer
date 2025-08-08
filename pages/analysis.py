import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import dash_ag_grid as dag  # AgGrid

dash.register_page(__name__, path="/")


positive_buttons = html.Div(
    [
        html.Label("Positive: ", htmlFor="pos-statfit-select"),
        dcc.Dropdown(
            options=[
                {"label": "None", "value": "none"},
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
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Rug", id="pos-btn-1", n_clicks=0, color="primary", outline=False
                ),
                dbc.Button(
                    "Hist.",
                    id="pos-btn-2",
                    n_clicks=0,
                    color="primary",
                    outline=False,
                ),
                dbc.Button(
                    "Stat. Fit",
                    id="pos-btn-3",
                    n_clicks=0,
                    color="primary",
                    outline=False,
                ),
            ],
            id="pos-btn-group",
            class_name="btn-group-sm",
        ),
    ],
    className="positive-group",
)

negative_buttons = html.Div(
    [
        html.Label("Negative: ", htmlFor="neg-statfit-select"),
        dcc.Dropdown(
            options=[
                {"label": "None", "value": "none"},
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
                    "Stat. Fit",
                    id="neg-btn-3",
                    n_clicks=0,
                    color="primary",
                    outline=False,
                ),
            ],
            id="neg-btn-group",
            class_name="btn-group-sm",
        ),
    ],
    className="negative-group",
)

unknown_buttons = html.Div(
    [
        html.Label("Unknown: ", htmlFor="unknown-statfit-select"),
        dcc.Dropdown(
            options=[
                {"label": "None", "value": "none"},
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
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Rug",
                    id="unk-btn-1",
                    n_clicks=0,
                    color="primary",
                    outline=True,
                ),
                dbc.Button(
                    "Hist.", id="unk-btn-2", n_clicks=0, color="primary", outline=False
                ),
                dbc.Button(
                    "Stat. Fit",
                    id="unk-btn-3",
                    n_clicks=0,
                    color="primary",
                    outline=False,
                ),
            ],
            id="unk-btn-group",
            class_name="btn-group-sm",
        ),
    ],
    className="unknown-group",
)

threshold_slider = html.Div(
    [
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
        dbc.Row(
            [
                html.Div(
                    "text",
                    id="threshold-slider-label",
                    style={
                        "textAlign": "center",
                        "padding": "0px",
                        "marginTop": "-5px",
                    },
                ),
            ]
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
                            ]
                        )
                    ],
                    width=2,
                    class_name="p-2 border dropdown-col",
                ),  # Adjust width as needed, add some padding and border
                # Middle Column: Main Plot
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="plot",
                                    children=[
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
                                ),
                                dbc.Tab(
                                    label="ROC 2x2 Table",
                                    children=[
                                        dcc.Graph(
                                            id="roc_table",
                                            # style={"height": "525px", "width": "525px"},
                                        )  # Set height for table
                                    ],
                                ),
                            ],
                        ),
                    ],
                    width=5,
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
                                        # TODO: dynamically size header minWidth
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
                    width=5,
                    class_name="p-2 border",
                ),  # Adjust width, add some padding and border
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
