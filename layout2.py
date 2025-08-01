from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_ag_grid as dag  # AgGrid

colors = {"background": "#FFFFFF", "text": "#2E2D29"}

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Analysis", href="#")),
        dbc.NavItem(dbc.NavLink("Upload", href="#")),
        dbc.NavItem(dbc.NavLink("Help", href="#")),
    ],
    brand=html.A(
        dbc.Row(
            [
                dbc.Col(html.Img(src="/assets/100x100.svg", height="30px")),
            ],
            align="center",
            className="g-0",
        ),
        href="#",
    ),
    color="primary",
    dark=True,
)

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
            value="norm",
            placeholder="Positive Stat. Fit",
            id="pos-statfit-select",
            className="mb-3",
        ),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Rug", id="pos-btn-1", n_clicks=0, className="btn btn-primary"
                ),
                dbc.Button(
                    "Hist.",
                    id="pos-btn-2",
                    n_clicks=0,
                    className="btn btn-outline-primary",
                ),
                dbc.Button(
                    "Stat. Fit", id="pos-btn-3", n_clicks=0, className="btn btn-primary"
                ),
            ],
            id="pos-btn-group",
            className="btn-group-sm",
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
            value="norm",
            placeholder="Negative Stat. Fit",
            id="neg-statfit-select",
            className="mb-3",
        ),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Rug", id="neg-btn-1", n_clicks=0, className="btn btn-primary"
                ),
                dbc.Button(
                    "Hist.",
                    id="neg-btn-2",
                    n_clicks=0,
                    className="btn btn-outline-primary",
                ),
                dbc.Button(
                    "Stat. Fit", id="neg-btn-3", n_clicks=0, className="btn btn-primary"
                ),
            ],
            id="neg-btn-group",
            className="btn-group-sm",
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
            value="norm",
            placeholder="Unknown Stat. Fit",
            id="unknown-statfit-select",
            className="mb-3",
        ),
        dbc.ButtonGroup(
            [
                dbc.Button(
                    "Rug",
                    id="unk-btn-1",
                    n_clicks=0,
                    className="btn btn-outline-primary",
                ),
                dbc.Button(
                    "Hist.", id="unk-btn-2", n_clicks=0, className="btn btn-primary"
                ),
                dbc.Button(
                    "Stat. Fit",
                    id="unk-btn-3",
                    n_clicks=0,
                    className="btn btn-outline-primary",
                ),
            ],
            id="unk-btn-group",
            className="btn-group-sm",
        ),
    ],
    className="unknown-group",
)


layout = dbc.Container(
    style={"backgroundColor": colors["background"]},
    children=[  # Use dbc.Container
        html.Div(id="error-message"),  # Add a div to display error message
        # Top Row: Header and Upload
        dbc.Row(
            [
                navbar,
                dbc.Col(
                    dcc.Upload(
                        id="upload-data",
                        children=html.Div(
                            ["Drag and Drop or ", html.A("Select Files")]
                        ),
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
            ]
        ),
        dcc.Store(id="raw-file", data={}),
        dcc.Store(id="stored-data", data={}),
        dcc.Store(id="fit-params", data={}),
        dcc.Store(id="roc_curves", data={}),
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
                                        dcc.Dropdown(
                                            options=[],
                                            placeholder="Select File",
                                            id="file-select",
                                        ),
                                        dcc.Dropdown(
                                            id="column-select",
                                            options=[],
                                            placeholder="Select Column",
                                            multi=False,  # Graph only one column at a time, for now
                                            className="mb-3",
                                        ),
                                    ],
                                    className="mb-3",
                                ),  # Add margin-bottom
                                html.Hr(
                                    style={
                                        "width": "100%",
                                        "borderTop": "1px solid primary",
                                        "borderBottom": "1px solid primary",
                                        "opacity": "unset",
                                    }
                                ),
                                positive_buttons,
                                html.Hr(
                                    style={
                                        "width": "100%",
                                        "borderTop": "1px solid primary",
                                        "borderBottom": "1px solid primary",
                                        "opacity": "unset",
                                    }
                                ),
                                negative_buttons,
                                html.Hr(
                                    style={
                                        "width": "100%",
                                        "borderTop": "1px solid primary",
                                        "borderBottom": "1px solid primary",
                                        "opacity": "unset",
                                    }
                                ),
                                unknown_buttons,
                            ]
                        )
                    ],
                    width=2,
                    className="p-2 border",
                ),  # Adjust width as needed, add some padding and border
                # Middle Column: Main Plot
                dbc.Col(
                    [
                        dcc.Graph(
                            id="graph",
                            style={
                                "width": "100%",
                                "height": "525px",
                            },  # Set a fixed height or make it responsive
                        )
                    ],
                    width=5,
                    className="p-2 border",
                ),  # Adjust width, add some padding and border
                # Right Column: Tabs (ROC Curve, ROC Table, AG-Grid)
                dbc.Col(
                    [
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="ROC Curve",
                                    children=[
                                        dcc.Graph(
                                            id="roc_plot", style={"height": "525px"}
                                        )  # Set height for plot
                                    ],
                                ),
                                dbc.Tab(
                                    label="ROC Table",
                                    children=[
                                        dcc.Graph(
                                            id="roc_table",
                                            style={"height": "525px", "width": "525px"},
                                        )  # Set height for table
                                    ],
                                ),
                                dbc.Tab(
                                    label="Raw Data",
                                    children=[
                                        dag.AgGrid(  # Correctly use dag.AgGrid
                                            id="ag-grid",
                                            columnDefs=[],
                                            rowData=[],
                                            columnSize="sizeToFit",
                                            defaultColDef={
                                                "resizable": True,
                                                "sortable": True,
                                                "filter": True,
                                            },
                                            style={
                                                "height": "525px"
                                            },  # Set height for the grid
                                        )
                                    ],
                                ),
                            ]
                        )
                    ],
                    width=5,
                    className="p-2 border",
                ),  # Adjust width, add some padding and border
            ],
            className="mb-3",
        ),  # Add margin-bottom to the middle row
        # Bottom Row: Sliders and Buttons
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Button(
                            "Reset", id="range-reset", n_clicks=0, className="me-2"
                        ),  # Add Bootstrap margin-end
                        dcc.RangeSlider(
                            id="range-slider",
                            min=0,
                            max=100,
                            value=[0, 100],
                            className="mb-3",  # Add margin-bottom
                        ),
                    ],
                    width=12,
                ),
                dbc.Col(
                    [
                        html.Button("Auto", id="auto-slide", className="me-2"),
                        dcc.Slider(id="slider-position", min=0, max=100, value=0),
                    ],
                    width=12,
                ),
            ],
            className="p-2 border",
        ),  # Add padding and border to the bottom row
        #### dcc.Store Debugger ####
        html.Div(id="output-data", className="mt-3"),  # Component to display the data
        html.Div(id="output-params", className="mt-3"),  # Component to display the data
        html.Div(id="output-roc", className="mt-3"),
        html.Div(id="output-raw", className="mt-3"),
    ],
)
