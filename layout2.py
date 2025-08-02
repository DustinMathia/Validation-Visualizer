from dash import dcc, html
import dash_bootstrap_components as dbc
import dash_ag_grid as dag  # AgGrid

colors = {"background": "#FFFFFF", "text": "#2E2D29"}

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Analysis", class_name="text-light", href="#")),
        dbc.NavItem(dbc.NavLink("Data-Manager", class_name="text-light", href="#")),
        dbc.NavItem(dbc.NavLink("Help", class_name="text-light", href="#")),
    ],
    brand=html.A(
        dbc.Row(
            [
                dbc.Col(html.Img(src="/assets/100x100.svg", height="30px")),
            ],
            align="center",
            class_name="g-0",
        ),
        href="#",
    ),
    color="primary",
    dark=True,
    links_left=True,
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
            clearable=False,
            placeholder="Positive Stat. Fit",
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
                    outline=True,
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
            placeholder="Negative Stat. Fit",
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
                    outline=True,
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
                    outline=True,
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
                dbc.Col(
                    dbc.Button(
                        id="auto-slide", class_name="bi bi-calculator py-0 px-1"
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dcc.Slider(
                        id="slider-position",
                        min=0,
                        max=100,
                        value=0,
                        tooltip={"placement": "top", "always_visible": True},
                    ),
                    width=True,
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
                ),  # Add Bootstrap margin-end
                dbc.Col(
                    dcc.RangeSlider(
                        id="range-slider",
                        min=0,
                        max=100,
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

alert_fail = html.Div(
    [
        dbc.Alert(
            [
                html.I(className="bi bi-x-octagon-fill me-2"),
                "Hello! I am an alert",
            ],
            id="alert-fail",
            color="danger",
            dismissable=True,
            is_open=True,
        ),
    ],
)


alert_warning = html.Div(
    [
        dbc.Alert(
            [
                html.I(className="bi bi-exclamation-triangle-fill me-2"),
                "Hello! I am an alert",
            ],
            id="alert-warning",
            color="warning",
            dismissable=True,
            is_open=True,
        ),
    ],
)

layout = dbc.Container(
    style={"backgroundColor": colors["background"]},
    children=[  # Use dbc.Container
        html.Div(id="error-message"),  # Add a div to display error message
        # Top Row: Header and Upload
        dbc.Row(
            [
                navbar,
                alert_fail,
                alert_warning,
                threshold_slider,
                # dbc.Col(
                #     dcc.Upload(
                #         id="upload-data",
                #         children=html.Div(
                #             ["Drag and Drop or ", html.A("Select Files")]
                #         ),
                #         style={
                #             "height": "60px",
                #             "lineHeight": "60px",
                #             "borderWidth": "1px",
                #             "borderStyle": "dashed",
                #             "borderRadius": "5px",
                #             "textAlign": "center",
                #             "margin": "10px",
                #         },
                #         multiple=True,  # Allow multiple files to be uploaded
                #     ),
                #     width=12,
                # ),
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
                                        dbc.DropdownMenu(
                                            label="Select File",
                                            id="file-select",
                                            class_name="mb-3",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    [
                                        dbc.DropdownMenu(
                                            label="Select Column",
                                            id="column-select",
                                            class_name="mb-3",
                                        ),
                                    ]
                                ),
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
                    class_name="p-2 border",
                ),  # Adjust width as needed, add some padding and border
                # Middle Column: Main Plot
                dbc.Col(
                    [
                        dbc.Row(
                            dcc.Graph(
                                id="graph",
                                style={
                                    "width": "100%",
                                    "height": "525px",
                                },  # Set a fixed height or make it responsive
                            )
                        ),
                        dbc.Row(
                            range_slider,
                        ),
                    ],
                    width=5,
                    class_name="p-2 border",
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
                    class_name="p-2 border",
                ),  # Adjust width, add some padding and border
            ],
            class_name="mb-3",
        ),  # Add margin-bottom to the middle row
        # Bottom Rows: Sliders and Buttons
        #        dbc.Row(
        #            [
        #                dbc.Col(
        #                    dbc.Button(
        #                        id="range-reset",
        #                        n_clicks=0,
        #                        class_name="bi bi-arrow-clockwise py-0 px-1",
        #                    ),
        #                    width="auto",
        #                ),  # Add Bootstrap margin-end
        #                dbc.Col(
        #                    dcc.RangeSlider(
        #                        id="range-slider",
        #                        min=0,
        #                        max=100,
        #                        # dots=False,
        #                        value=[0, 100],
        #                        #            className="mb-3",  # Add margin-bottom
        #                    ),
        #                    width=True,
        #                ),
        #            ],
        #            align="center",
        #        ),
        #        dbc.Row(
        #            [
        #                dbc.Col(
        #                    dbc.Button(id="auto-slide", class_name="bi bi-graph-up py-0 px-1"),
        #                    width="auto",
        #                ),
        #                dbc.Col(
        #                    dcc.Slider(
        #                        id="slider-position",
        #                        min=0,
        #                        max=100,
        #                        value=0,
        #                        tooltip={"placement": "top", "always_visible": True},
        #                    ),
        #                    width=True,
        #                ),
        #            ],
        #            align="center",
        #        ),
        # class_name="p-2 border",
        #### dcc.Store Debugger ####
        # html.Div(id="output-data", class_name="mt-3"),  # Component to display the data
        # html.Div(id="output-params", class_name="mt-3"),  # Component to display the data
        # html.Div(id="output-roc", class_name="mt-3"),
        # html.Div(id="output-raw", class_name="mt-3"),
    ],
)
