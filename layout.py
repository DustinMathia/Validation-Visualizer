from dash import Dash, dcc, html
import dash_ag_grid as dag

colors = {
    'background': '#FFFFFF',
    'text': '#2E2D29'
}



header = html.H4(
    "Validation DataViewer", className="bg-primary p-2 mb-2 text-center"
)

layout = html.Div(style={'backgroundColor': colors['background']}, children=[ # Use Calibri for now per recommended by stanford site

    html.Div(id='error-message'),  # Add a div to display error message

    dcc.Upload(
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
    ),


    dcc.Store(id='raw-file', data={}),                                                                         
    dcc.Store(id='stored-data', data={}),
    dcc.Store(id='fit-params', data={}),
    dcc.Store(id='roc_curves', data={}),

    html.Div([
        html.Div([
            dcc.Dropdown(
                options=[],
                placeholder='Select File',
                id='file-select'
            )
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'left'}),

        html.Div([
            html.Label('Positive Stat Fit: ', htmlFor='pos-statfit-select'),
            dcc.Dropdown(
                options=[{'label': 'None', 'value': 'none'},
                         {'label': 'Normal', 'value': 'norm'},
                         {'label': 'Gompertz', 'value': 'gompertz'},
                         {'label': 'Exponential', 'value': 'expon'},
                         {'label': 'Expon. Norm.', 'value': 'exponnorm'}],
                value='norm',
                placeholder='Positive Stat Fit',
                id='pos-statfit-select', style={'width': '100%'}
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
                id='neg-statfit-select', style={'width': '100%'}
            )
        ], style={'width': '48%', 'display': 'flex', 'flex-shrink': 0})
    ], style={'display': 'flex', 'width': '100%'}),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='column-select',
                options=[],
                # options=[{'label': col, 'value': col} for col in numeric_cols],
                # value=numeric_cols[0] if numeric_cols else None,  # Set default value if available
                placeholder='Select Column',
                #multi=True
                multi=False # Graph only one column at a time, for now
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
                dcc.Checklist(
                    options=['Positive', 'Negative', 'Unknown'],
                    value=['Positive', 'Negative', 'Unknown'],
                    id='trace-select',
                    inline=True
                )
        ], style={'width': '48%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.Div(children='Chart Type: ', style={'display': 'inline-block'}),
        html.Div([
            dcc.RadioItems(['Line', 'Histogram'], 'Line', id='chart-type'),
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div(children='Unknown Chart Type: ', style={'display': 'inline-block'}),
        html.Div([
            dcc.RadioItems(['Histogram', 'Line'], 'Histogram', id='unknown-chart')
        ], style={'width': '30%', 'display': 'inline-block'})
    ]),

    html.Div([
    dcc.Graph(
        id='roc_table'),

    dcc.Graph(
        id='graph',
        style={'display': 'block', 'width': 'auto', 'height': 'auto'}),
   
    dcc.Graph(id='roc_plot'),

    dag.AgGrid( # Replaced dcc.Graph with dag.AgGrid
        id='ag-grid',
        columnDefs=[], # Initial empty column definitions
        rowData=[],    # Initial empty row data
        columnSize="sizeToFit",
        defaultColDef={"resizable": True, "sortable": True, "filter": True},
    )

    ], style={'display': 'flex', 'flex-direction': 'column', 'gap': '0px'}),

html.Div([
    html.Button('Reset', id='range-reset', n_clicks=0),
    dcc.RangeSlider(
        id='range-slider',
        min=0,
        max=100,
        value=[0, 100]
    )
    ]),

html.Div([
    html.Button('Auto', id='auto-slide'),
    dcc.Slider(
        id='slider-position',
        #updatemode='drag',
        # Placeholder
        min=0,
        max=100,
        value=0
    )
    ]),



    #### dcc.Store Debugger ####
    html.Div(id='output-data'),  # Component to display the data
    html.Div(id='output-params'),  # Component to display the data
    html.Div(id='output-roc'),
    html.Div(id='output-raw')



])
