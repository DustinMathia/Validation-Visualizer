from dash import Dash, dcc, html

colors = {
    'background': '#FFFFFF',
    'text': '#2E2D29'
}

layout = html.Div(style={'backgroundColor': colors['background']}, children=[ # Use Calibri for now per recommended by stanford site
    html.H1(
        children='Hello Dash',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Dash: A web application framework for your data.',
        style={
          'textAlign': 'center',
          'color': colors['text']
    }),

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

    dcc.Store(id='stored-data', data={
        'filename': {
            'column_name': {
                'positive': {'data': [], 'hist': [], 'bin_edges': [], 'bar_widths': []},
                'negative': {'data': [], 'hist': [], 'bin_edges': [], 'bar_widths': []},
                'unknown': {'data': [], 'hist': [], 'bin_edges': [], 'bar_widths': []},
                'range_min': 0, 'range_max': 100, 'range_value': [0,100], 'slider_value': 0
            }
        }
    }),


    dcc.Store(id='fit-params', data={
          'filename': {
            'column_name': {
                'positive': {'norm': {'loc': 0, 'scale': 0},  #               'r-squared': None, 'aic': None, 'bic': None},
                             'expon': {'loc': 0, 'scale': 0},  #              'r-squared': None, 'aic': None, 'bic': None},
                             'exponnorm': {'K': 0, 'loc': 0, 'scale': 0}},  # 'r-squared': None, 'aic': None, 'bic': None}},
                'negative': {'norm': {'loc': 0, 'scale': 0},    #             'r-squared': None, 'aic': None, 'bic': None},
                             'expon': {'loc': 0, 'scale': 0}},     #           'r-squared': None, 'aic': None, 'bic': None},
                             'exponnorm': {'K': 0, 'loc': 0, 'scale': 0}}, # 'r-squared': None, 'aic': None, 'bic': None}},
                'unknown': {'norm': {'loc': 0, 'scale': 0}, #                 'r-squared': None, 'aic': None, 'bic': None},
                             'expon': {'loc': 0, 'scale': 0}, #               'r-squared': None, 'aic': None, 'bic': None},
                             'exponnorm': {'K': 0, 'loc': 0, 'scale': 0}}#, 'r-squared': None, 'aic': None, 'bic': None}}
            }
    }),

    dcc.Store(id='roc_curves', data={
        'filename': {
            'column_name': {
                'population_data': [],
                'total_positive': [],
                'total_negative': [],
                'total_unknown': [],
                'accumulated_positive': [],
                'accumulated_negative': [],
                'accumulated_unknown': [],
                'TP': [],
                'FP': [],
                'TN': [],
                'FN': [],
                'UP': [],
                'UN': [],
                'TPR': [],
                'FPR': [],
                'TNR': [],
                'FNR': [],
                'ACC': []
            }}}),

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
    # html.Div([
    #     dcc.RadioItems(['Line', 'Histogram'], 'Line', inline=True, id='chart-type')
    # ]),
    # html.Div([
    #     dcc.RadioItems(['Raw', 'Logarithmic'], 'Line', inline=True, id='unknown-scale')
    # ]),


    dcc.Graph(
        id='graph'
    ),

html.Div([
    html.Button('Reset', id='range-reset'),
    dcc.RangeSlider(
        id='range-slider',
        #updatemode='drag',
        # Placeholder
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
    html.Div(id='error-message'),  # Add a div to display error message



])
