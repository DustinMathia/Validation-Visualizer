from dash import dcc, html
import dash_bootstrap_components as dbc # Import dash_bootstrap_components
import dash_ag_grid as dag # Import dash_ag_grid for the AgGrid component

colors = {
    'background': '#FFFFFF',
    'text': '#2E2D29'
}

header = html.H4(
    "Validation DataViewer", className="bg-primary p-2 mb-2 text-center"
)

layout = dbc.Container(style={'backgroundColor': colors['background']}, children=[ # Use dbc.Container

    html.Div(id='error-message'),  # Add a div to display error message

    # Top Row: Header and Upload
    dbc.Row([
        dbc.Col(header, width=12),
        dbc.Col(dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px'
            },
            multiple=True # Allow multiple files to be uploaded
        ), width=12),
    ]),

    dcc.Store(id='raw-file', data={}),
    dcc.Store(id='stored-data', data={}),
    dcc.Store(id='fit-params', data={}),
    dcc.Store(id='roc_curves', data={}),

    # Middle Row: Left Panel, Main Plot, Right Tabs
    dbc.Row([
        # Left Column: Buttons and Dropdowns
        dbc.Col([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        options=[],
                        placeholder='Select File',
                        id='file-select'
                    )
                ], className="mb-3"), # Add margin-bottom
                html.Label('Positive Stat Fit: ', htmlFor='pos-statfit-select'),
                dcc.Dropdown(
                    options=[{'label': 'None', 'value': 'none'},
                             {'label': 'Normal', 'value': 'norm'},
                             {'label': 'Gompertz', 'value': 'gompertz'},
                             {'label': 'Exponential', 'value': 'expon'},
                             {'label': 'Expon. Norm.', 'value': 'exponnorm'}],
                    value='norm',
                    placeholder='Positive Stat Fit',
                    id='pos-statfit-select', className="mb-3"
                ),
                html.Label('Negative Stat Fit: ', htmlFor='neg-statfit-select'),
                dcc.Dropdown(
                    options=[{'label': 'None', 'value': 'none'},
                             {'label': 'Normal', 'value': 'norm'},
                             {'label': 'Gompertz', 'value': 'gompertz'},
                             {'label': 'Exponential', 'value': 'expon'},
                             {'label': 'Expon. Norm.', 'value': 'exponnorm'}],
                    value='norm',
                    placeholder='Negative Stat Fit',
                    id='neg-statfit-select', className="mb-3"
                ),
                dcc.Dropdown(
                    id='column-select',
                    options=[],
                    placeholder='Select Column',
                    multi=False, # Graph only one column at a time, for now
                    className="mb-3"
                ),
                html.Div([
                    dcc.Checklist(
                        options=['Positive', 'Negative', 'Unknown'],
                        value=['Positive', 'Negative', 'Unknown'],
                        id='trace-select',
                        inline=True,
                        className="mb-3"
                    )
                ]),
                html.Div(children='Chart Type: ', className="mb-2"),
                dcc.RadioItems(['Line', 'Histogram'], 'Line', id='chart-type', className="mb-3"),
                html.Div(children='Unknown Chart Type: ', className="mb-2"),
                dcc.RadioItems(['Histogram', 'Line'], 'Histogram', id='unknown-chart', className="mb-3")
            ])
        ], width=3, className="p-2 border"), # Adjust width as needed, add some padding and border

        # Middle Column: Main Plot
        dbc.Col([
            dcc.Graph(
                id='graph',
                style={'width': '100%', 'height': '600px'} # Set a fixed height or make it responsive
            )
        ], width=5, className="p-2 border"), # Adjust width, add some padding and border

        # Right Column: Tabs (ROC Curve, ROC Table, AG-Grid)
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="ROC Curve", children=[
                    dcc.Graph(id='roc_plot', style={'height': '550px'}) # Set height for plot
                ]),
                dbc.Tab(label="ROC Matrix", children=[
                    dcc.Graph(id='roc_table', style={'height': '550px'}) # Set height for table
                ]),
                dbc.Tab(label="Raw Data", children=[
                    dag.AgGrid( # Correctly use dag.AgGrid
                        id='ag-grid',
                        columnDefs=[],
                        rowData=[],
                        columnSize="sizeToFit",
                        defaultColDef={"resizable": True, "sortable": True, "filter": True},
                        style={'height': '550px'} # Set height for the grid
                    )
                ]),
            ])
        ], width=4, className="p-2 border") # Adjust width, add some padding and border
    ], className="mb-3"), # Add margin-bottom to the middle row

    # Bottom Row: Sliders and Buttons
    dbc.Row([
        dbc.Col([
            html.Button('Reset', id='range-reset', n_clicks=0, className="me-2"), # Add Bootstrap margin-end
            dcc.RangeSlider(
                id='range-slider',
                min=0,
                max=100,
                value=[0, 100],
                className="mb-3" # Add margin-bottom
            )
        ], width=12),
        dbc.Col([
            html.Button('Auto', id='auto-slide', className="me-2"),
            dcc.Slider(
                id='slider-position',
                min=0,
                max=100,
                value=0
            )
        ], width=12)
    ], className="p-2 border"), # Add padding and border to the bottom row

    #### dcc.Store Debugger ####
    html.Div(id='output-data', className="mt-3"),  # Component to display the data
    html.Div(id='output-params', className="mt-3"),  # Component to display the data
    html.Div(id='output-roc', className="mt-3"),
    html.Div(id='output-raw', className="mt-3")
])
