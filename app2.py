from logging import error
from dash import Dash, html, callback, Input, Output, State, ctx, ALL, no_update
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats
import base64
import io

import layout2
import utils

import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

dbc_css = (
    "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css"
)
custom_css = "/assets/custom.css"
SELECTED_BOOTSTRAP_THEME = dbc.themes.SPACELAB
load_figure_template(["spacelab"])

POSITIVE = "#cd0200"
NEGATIVE = "#446e9b"
UNKNOWN = "#999"

app = Dash(
    __name__,
    external_stylesheets=[
        SELECTED_BOOTSTRAP_THEME,
        dbc.icons.BOOTSTRAP,
        dbc_css,
        custom_css,
    ],
    external_scripts=["assets/dropdown_tooltips.js"],
)
app.layout = layout2.layout


# @app.callback(
#    Output("output-data", "children"),  # Output to display the data
#    Output("output-params", "children"),  # Output to store the data
#    Output("output-roc", "children"),
#    Output("output-raw", "children"),
#    Input("stored-data", "data"),  # Input from the Store component
#    Input("fit-params", "data"),  # view params
#    Input("roc_curves", "data"),
#    Input("raw-file", "data"),
# )
# def display_stored_data(stored_data, fitted_params, roc_curves, raw_files):
#    if stored_data and fitted_params and roc_curves and raw_files:
#        # Convert the data to a readable format (e.g., string)
#        data_string_data = str(stored_data)
#        data_string_params = str(fitted_params)
#        data_string_roc = str(roc_curves)
#        data_string_raw = str(raw_files)
#        # Return the data string
#        return data_string_data, data_string_params, data_string_roc, data_string_raw
#    else:
#        return (
#            "No data stored yet.",
#            "No parameters stored yet.",
#            "No ROC data stored yet.",
#            "No files stored yet.",
#        )


# Store data ready to graph
@callback(
    Output("stored-data", "data", allow_duplicate=True),  # Output to store the data
    Output("fit-params", "data", allow_duplicate=True),  # Output to store the data
    Output("roc_curves", "data", allow_duplicate=True),
    Output("raw-file", "data", allow_duplicate=True),
    Output("error-message", "children"),  # Output to display the error
    Input("upload-data", "contents"),  # Input from the upload component
    State("upload-data", "filename"),  # State to get the filename
    State("stored-data", "data"),  # State to get existing stored data
    State("fit-params", "data"),  # State to get existing fit params
    State("roc_curves", "data"),  # State to get existing roc curves
    State("raw-file", "data"),
    prevent_initial_call=True,  # Prevent the callback from firing on initial load
)
def store_file(
    list_of_contents,
    list_of_filenames,
    existing_stored_data,
    existing_fitted_params,
    existing_roc_curves,
    existing_raw,
):
    # Dictionary to store all file data
    all_files_data = existing_stored_data if existing_stored_data is not None else {}
    all_files_fit_params = (
        existing_fitted_params if existing_fitted_params is not None else {}
    )
    all_files_roc = existing_roc_curves if existing_roc_curves is not None else {}
    all_files_raw = existing_raw if existing_raw is not None else {}
    if list_of_contents is not None:
        error_messages = []
        for content, filename in zip(list_of_contents, list_of_filenames):
            if isinstance(content, str):  # Check if content is a string
                content_type, content_string = content.split(",")
                decoded = base64.b64decode(content_string)

                try:
                    # Read header to get column names
                    with io.StringIO(decoded.decode("utf-8")) as f:
                        header = f.readline().strip().split("\t")

                    # Load data with skip_header and names
                    data = np.genfromtxt(
                        io.BytesIO(decoded),
                        delimiter="\t",
                        dtype=None,
                        encoding="utf-8",
                        skip_header=1,
                        names=header,
                        missing_values="",
                        filling_values=0,
                    )

                    # Manipulate data
                    manipulated_data = utils.manipulate_data(data, header)

                    # make roc curve
                    roc_columns = {}
                    for column in manipulated_data:
                        roc_columns[column] = utils.make_roc_curve(
                            manipulated_data[column]["positive"]["data"],
                            manipulated_data[column]["negative"]["data"],
                            manipulated_data[column]["unknown"]["data"],
                        )

                    fitted_data = utils.fit_params(manipulated_data)

                    # Convert NumPy structured array to list of dictionaries for ag-grid
                    data_list_for_grid = []
                    for row in data:
                        data_list_for_grid.append(dict(zip(header, row)))

                    all_files_data[filename] = manipulated_data
                    all_files_fit_params[filename] = fitted_data
                    all_files_roc[filename] = roc_columns
                    all_files_raw[filename] = {
                        "header": header,
                        "data": data_list_for_grid,
                    }  # Store processed data for ag-grid

                except Exception as e:
                    error_messages.append(f"Error processing file '{filename}': {e}")
                    # Do not return None here, just append error and continue to process other files
            else:
                error_messages.append(f"Invalid content type for file '{filename}'.")

        if error_messages:
            return (
                all_files_data,
                all_files_fit_params,
                all_files_roc,
                all_files_raw,
                html.Div(error_messages, style={"color": "red"}),
            )
        else:
            return (
                all_files_data,
                all_files_fit_params,
                all_files_roc,
                all_files_raw,
                html.Div("", style={"color": "green"}),
            )
    # If list_of_contents is None (e.g., initial load if not prevented, or no files selected)
    return (
        all_files_data,
        all_files_fit_params,
        all_files_roc,
        all_files_raw,
        html.Div("No File Uploaded", style={"color": "green"}),
    )


# Update Stored Data
@app.callback(
    Output("stored-data", "data", allow_duplicate=True),
    Input("slider-position", "value"),
    Input("range-slider", "value"),
    State("stored-data", "data"),
    State("file-select", "label"),
    State("column-select", "label"),
    prevent_initial_call=True,  # Prevent the callback from firing on initial load
)
def update_stored_data(
    slider_position, range_slider_value, stored_data, selected_file, selected_column
):
    if stored_data and selected_file and selected_column:
        column_data = stored_data[selected_file][selected_column]
        column_data["slider_value"] = slider_position
        column_data["range_value"] = range_slider_value
        # Update stored data
        stored_data[selected_file].update({selected_column: column_data})
        return stored_data
    else:
        return stored_data


# Callback for range slider updates
@callback(
    Output("range-slider", "min"),
    Output("range-slider", "max"),
    Output("range-slider", "value"),
    Input("column-select", "label"),
    Input("range-reset", "n_clicks"),
    State("stored-data", "data"),
    State("file-select", "label"),
)
def update_range_slider_range(selected_column, button, stored_data, selected_file):
    if stored_data and selected_column in stored_data.get(selected_file, {}):
        column_data = stored_data[selected_file][selected_column]

        range_min = column_data["range_min"]
        range_max = column_data["range_max"]

        initial_range = column_data.get("range_value", [range_min, range_max])

        if "range-reset" == ctx.triggered_id:
            initial_range = [range_min, range_max]

        return range_min, range_max, initial_range  # Return updated stored data
    else:
        return 0, 100, [0, 100]  # Return default values if data is not available


# Callback for slider updates
@callback(
    Output("slider-position", "min"),
    Output("slider-position", "max"),
    Input("range-slider", "value"),
)
def update_slider_range(selected_range):
    slider_min = selected_range[0]
    slider_max = selected_range[1]
    return slider_min, slider_max


# roc figures
@app.callback(
    Output("roc_plot", "figure"),
    Output("roc_table", "figure"),
    Input("stored-data", "data"),
    Input("fit-params", "data"),
    Input("roc_curves", "data"),
    Input("file-select", "label"),
    Input("column-select", "label"),
    State("slider-position", "value"),
)
def update_roc_plot_and_table(
    stored_data, fitted_params, roc_data, selected_file, selected_column, pos_x
):
    # Only check for fundamental data needed for any graph
    if not (
        stored_data and selected_file and selected_column
    ):  # and fitted_params and roc_data:
        # Return empty figures and default slider values
        return go.Figure(), go.Figure()

    parameter_data = fitted_params.get(selected_file, {}).get(selected_column)
    roc_column = roc_data.get(selected_file, {}).get(selected_column)

    # Check if roc_column and its population_data are available and not empty
    if not roc_column or not roc_column.get("population_data"):
        return go.Figure(), go.Figure()
    else:
        roc_table, roc_table_header, roc_index = utils.gen_roc_table(
            roc_column, pos_x, parameter_data["positive"]["norm"]
        )
        roc_fig = utils.plot_roc_curve(roc_column, roc_index)
        roc_table = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=roc_table_header, fill_color="#f8f8f8", align="left"
                    ),
                    cells=dict(
                        values=[roc_table[0], roc_table[1], roc_table[2], roc_table[3]],
                        fill_color=[
                            ["#fcfcfc", "#f8f8f8", "#fcfcfc", "#f8f8f8", "#fcfcfc"] * 4
                        ],
                        align="left",
                    ),
                )
            ]
        )
        roc_fig.update_layout(
            showlegend=False,
            xaxis=dict(range=[-0.05, 1.05], title="1 - Specificty"),
            yaxis=dict(range=[-0.05, 1.05], title="Sensitivity"),
        )
        roc_table.update_layout(
            margin=dict(l=10, r=10, t=180, b=10), width=525  # Reduce overall margins
        )
    return roc_fig, roc_table


# data ag grid
@app.callback(
    Output("ag-grid", "rowData"),
    Output("ag-grid", "columnDefs"),
    Input("raw-file", "data"),
    Input("file-select", "label"),
)
def update_data_grid(raw_files, selected_file):
    # Ensure raw_files is a dictionary, even if it starts as None
    raw_files = raw_files if raw_files is not None else {}

    if raw_files and selected_file and selected_file in raw_files:
        file_data = raw_files[selected_file]
        header = file_data["header"]
        data = file_data["data"]  # This is already a list of dictionaries

        # Create column definitions for AgGrid
        column_defs = [{"field": col} for col in header]

        return data, column_defs
    return [], []  # Return empty lists if no data or file selected


@app.callback(
    Output("pos-btn-1", "outline"),
    Output("pos-btn-2", "outline"),
    Output("pos-btn-3", "outline"),
    Input("pos-btn-1", "n_clicks"),
    Input("pos-btn-2", "n_clicks"),
    Input("pos-btn-3", "n_clicks"),
    State("pos-btn-1", "outline"),
    State("pos-btn-2", "outline"),
    State("pos-btn-3", "outline"),
)
def update_positive_buttons(b1, b2, b3, o1, o2, o3):
    button_id = ctx.triggered_id
    if not button_id:
        return no_update, no_update, no_update

    new_o1, new_o2, new_o3 = o1, o2, o3

    if "pos-btn-1" == button_id:
        new_o1 = not o1
    elif "pos-btn-2" == button_id:
        new_o2 = not o2
    elif "pos-btn-3" == button_id:
        new_o3 = not o3

    return new_o1, new_o2, new_o3


@app.callback(
    Output("neg-btn-1", "outline"),
    Output("neg-btn-2", "outline"),
    Output("neg-btn-3", "outline"),
    Input("neg-btn-1", "n_clicks"),
    Input("neg-btn-2", "n_clicks"),
    Input("neg-btn-3", "n_clicks"),
    State("neg-btn-1", "outline"),
    State("neg-btn-2", "outline"),
    State("neg-btn-3", "outline"),
)
def update_negative_buttons(b1, b2, b3, o1, o2, o3):
    button_id = ctx.triggered_id
    if not button_id:
        return no_update, no_update, no_update

    new_o1, new_o2, new_o3 = o1, o2, o3

    if "neg-btn-1" == button_id:
        new_o1 = not o1
        return new_o1, o2, o3
    elif "neg-btn-2" == button_id:
        new_o2 = not o2
        return o1, new_o2, o3
    elif "neg-btn-3" == button_id:
        new_o3 = not o3
        return o1, o2, new_o3

    return new_o1, new_o2, new_o3


@app.callback(
    Output("unk-btn-1", "outline"),
    Output("unk-btn-2", "outline"),
    Output("unk-btn-3", "outline"),
    Input("unk-btn-1", "n_clicks"),
    Input("unk-btn-2", "n_clicks"),
    Input("unk-btn-3", "n_clicks"),
    State("unk-btn-1", "outline"),
    State("unk-btn-2", "outline"),
    State("unk-btn-3", "outline"),
)
def update_unknown_buttons(b1, b2, b3, o1, o2, o3):
    button_id = ctx.triggered_id
    if not button_id:
        return no_update, no_update, no_update

    new_o1, new_o2, new_o3 = o1, o2, o3

    if "unk-btn-1" == button_id:
        new_o1 = not o1
        return new_o1, o2, o3
    elif "unk-btn-2" == button_id:
        new_o2 = not o2
        return o1, new_o2, o3
    elif "unk-btn-3" == button_id:
        new_o3 = not o3
        return o1, o2, new_o3

    return new_o1, new_o2, new_o3


# Callback to populate the file-select dropdown menu
@app.callback(
    Output("file-select", "children"),
    Input("raw-file", "data"),
)
def update_file_dropdown(raw_file_data):
    if not raw_file_data:
        return []

    dropdown_items = []
    for filename in raw_file_data.keys():
        dropdown_items.append(
            dbc.DropdownMenuItem(filename, id={"type": "file-item", "index": filename})
        )

    return dropdown_items


# Callback to populate the column-select dropdown menu
@app.callback(
    Output("column-select", "children"),
    Input("stored-data", "data"),
    Input("file-select", "label"),
)
def update_column_dropdown(stored_data, filename):
    # Ensure stored_data is a non-empty dictionary and a filename is selected
    if not isinstance(stored_data, dict) or not stored_data or not filename:
        return []

    # Check if the selected file exists in the stored data
    if filename not in stored_data:
        return []

    # Get column names from the keys of the dictionary for the selected file
    columns = list(stored_data[filename].keys())

    dropdown_items = []
    for col in columns:
        dropdown_items.append(
            dbc.DropdownMenuItem(col, id={"type": "column-item", "index": col})
        )

    return dropdown_items


# Callback to capture file selection and update the label
@app.callback(
    Output("file-select", "label"),
    Input({"type": "file-item", "index": ALL}, "n_clicks"),
    State({"type": "file-item", "index": ALL}, "id"),
)
def select_file(n_clicks, item_ids):
    if not any(n_clicks):
        return no_update

    button_id = ctx.triggered_id
    return button_id["index"]


# Callback to capture column selection and update the label
@app.callback(
    Output("column-select", "label"),
    Input({"type": "column-item", "index": ALL}, "n_clicks"),
    State({"type": "column-item", "index": ALL}, "id"),
)
def select_column(n_clicks, item_ids):
    if not any(n_clicks):
        return no_update

    button_id = ctx.triggered_id
    return button_id["index"]


# Update Graph Callback
@app.callback(
    Output("graph", "figure"),
    [
        Input("stored-data", "data"),
        Input("fit-params", "data"),
        Input("roc_curves", "data"),
        Input("file-select", "label"),
        Input("column-select", "label"),  # Input from dropdown
        Input("pos-statfit-select", "value"),  # Select fit lines
        Input("neg-statfit-select", "value"),
        Input("unknown-statfit-select", "value"),
        Input("pos-btn-1", "outline"),
        Input("pos-btn-2", "outline"),
        Input("pos-btn-3", "outline"),
        Input("neg-btn-1", "outline"),
        Input("neg-btn-2", "outline"),
        Input("neg-btn-3", "outline"),
        Input("unk-btn-1", "outline"),
        Input("unk-btn-2", "outline"),
        Input("unk-btn-3", "outline"),
        State("slider-position", "value"),
        Input("range-slider", "value"),  # Input from range slider
    ],
    prevent_initial_call=True,  # Prevent the callback from firing on initial load
)
def update_graph(
    stored_data,
    fitted_params,
    roc_data,
    selected_file,
    selected_column,
    pos_fit_dist,
    neg_fit_dist,
    unknown_fit_dist,
    pos_btn1_outline,
    pos_btn2_outline,
    pos_btn3_outline,
    neg_btn1_outline,
    neg_btn2_outline,
    neg_btn3_outline,
    unk_btn1_outline,
    unk_btn2_outline,
    unk_btn3_outline,
    pos_x,
    range_value,
):
    # Convert the button classes to a list of selected options for each group
    pos_chart_types = []
    if not pos_btn1_outline:
        pos_chart_types.append(1)
    if not pos_btn2_outline:
        pos_chart_types.append(2)
    if not pos_btn3_outline:
        pos_chart_types.append(3)

    neg_chart_types = []
    if not neg_btn1_outline:
        neg_chart_types.append(1)
    if not neg_btn2_outline:
        neg_chart_types.append(2)
    if not neg_btn3_outline:
        neg_chart_types.append(3)

    unknown_chart_types = []
    if not unk_btn1_outline:
        unknown_chart_types.append(1)
    if not unk_btn2_outline:
        unknown_chart_types.append(2)
    if not unk_btn3_outline:
        unknown_chart_types.append(3)

    # Only check for fundamental data needed for any graph
    if not (
        stored_data and selected_file and selected_column
    ):  # and fitted_params and roc_data:
        # Return empty figures and default slider values
        return go.Figure()

    column_data = stored_data.get(selected_file, {}).get(selected_column)
    parameter_data = fitted_params.get(selected_file, {}).get(selected_column)
    roc_column = roc_data.get(selected_file, {}).get(selected_column)
    file_data = stored_data.get(selected_file, {})
    col_data = file_data.get(selected_column, {})

    positive_data = np.array(col_data.get("positive", {}).get("data", []))
    negative_data = np.array(col_data.get("negative", {}).get("data", []))
    unknown_data = np.array(col_data.get("unknown", {}).get("data", []))

    range_min = col_data.get("range_min", 0)
    range_max = col_data.get("range_max", 100)

    fig2 = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.93, 0.07],
        shared_xaxes="columns",
        vertical_spacing=0.01,
        specs=[[{"secondary_y": True}], [{"type": "xy"}]],
    )

    if column_data and parameter_data:
        # Calculate Histogram points depending of ranger slider
        bin_edges = utils.calculate_bin_edges(
            column_data,
            range_value,
            pos_chart_types,
            neg_chart_types,
            unknown_chart_types,
        )
        positive_hist, positive_bin_edges = np.histogram(
            column_data["positive"]["data"], bins=bin_edges, range=range_value
        )
        negative_hist, negative_bin_edges = np.histogram(
            column_data["negative"]["data"], bins=bin_edges, range=range_value
        )
        unknown_hist, unknown_bin_edges = np.histogram(
            column_data["unknown"]["data"], bins=bin_edges, range=range_value
        )

        positive_bar_widths = np.diff(positive_bin_edges)
        negative_bar_widths = np.diff(negative_bin_edges)
        unknown_bar_widths = np.diff(unknown_bin_edges)

        positive_bar_center = positive_bin_edges[:-1] + positive_bar_widths / 2
        negative_bar_center = negative_bin_edges[:-1] + negative_bar_widths / 2
        unknown_bar_center = unknown_bin_edges[:-1] + unknown_bar_widths / 2

        # Positive Trace
        if positive_data.size > 0:
            if 1 in pos_chart_types:  # Rug plot (represented by Box plot for jitter)
                fig2.add_trace(
                    go.Box(  # positive points  #draw original data points in boxplot below x axis
                        x=column_data["positive"]["data"],
                        marker_symbol="line-ns-open",
                        marker_color=POSITIVE,
                        boxpoints="all",
                        jitter=1,
                        fillcolor="rgba(255,255,255,0)",
                        line_color="rgba(255,255,255,0)",
                        hoveron="points",
                        showlegend=False,
                        name="Positives Rug",
                    ),
                    row=2,
                    col=1,
                )  # Plot on main graph area

            if 2 in pos_chart_types:  # Bar (Histogram)
                fig2.add_trace(
                    go.Bar(
                        x=positive_bar_center,
                        y=positive_hist,
                        name="Positives",
                        marker_color=POSITIVE,
                        width=positive_bar_widths,
                    ),
                    row=1,
                    col=1,
                    secondary_y=True,
                )

            if 3 in pos_chart_types and pos_fit_dist != "none":  # Stat. Fit (Line)
                pos_params = parameter_data["positive"][pos_fit_dist]
                positive_dist = getattr(stats, pos_fit_dist)
                x_range_for_pdf = np.linspace(range_value[0], range_value[1], 300)
                positive_pdf = positive_dist.pdf(x_range_for_pdf, **pos_params)
                fig2.add_trace(
                    go.Scatter(
                        x=x_range_for_pdf,
                        y=positive_pdf,
                        mode="lines",
                        name="Positives",
                        line_color=POSITIVE,
                    ),
                    row=1,
                    col=1,
                    secondary_y=True,
                )

        # Negative Trace
        if negative_data.size > 0:
            if 1 in neg_chart_types:  # Rug plot
                fig2.add_trace(
                    go.Box(
                        x=column_data["negative"]["data"],
                        marker_symbol="line-ns-open",
                        marker_color="blue",
                        boxpoints="all",
                        jitter=1,
                        fillcolor="rgba(255,255,255,0)",
                        line_color="rgba(255,255,255,0)",
                        hoveron="points",
                        showlegend=False,
                        name="Negatives Rug",
                    ),
                    row=2,
                    col=1,
                )

            if 2 in neg_chart_types:  # Bar (Histogram)
                fig2.add_trace(
                    go.Bar(
                        x=negative_bar_center,
                        y=negative_hist,
                        name="Negatives",
                        marker_color="green",
                        width=negative_bar_widths,
                    ),
                    row=1,
                    col=1,
                    secondary_y=True,
                )

            if 3 in neg_chart_types and neg_fit_dist != "none":  # Stat. Fit (Line)
                neg_params = parameter_data["negative"][neg_fit_dist]
                negative_dist = getattr(stats, neg_fit_dist)
                x_range_for_pdf = np.linspace(range_value[0], range_value[1], 300)
                negative_pdf = negative_dist.pdf(x_range_for_pdf, **neg_params)
                fig2.add_trace(
                    go.Scatter(
                        x=x_range_for_pdf,
                        y=negative_pdf,
                        mode="lines",
                        name="Negatives",
                        line_color=NEGATIVE,
                    ),
                    row=1,
                    col=1,
                    secondary_y=True,
                )

        # Unknown Trace
        if unknown_data.size > 0:
            if 1 in unknown_chart_types:
                fig2.add_trace(
                    go.Box(
                        x=column_data["unknown"]["data"],
                        marker_symbol="line-ns-open",
                        marker_color="gray",
                        boxpoints="all",
                        jitter=1,
                        fillcolor="rgba(255,255,255,0)",
                        line_color="rgba(255,255,255,0)",
                        hoveron="points",
                        showlegend=False,
                        name="Unknowns Rug",
                    ),
                    row=2,
                    col=1,
                )
            if 2 in unknown_chart_types:
                fig2.add_trace(
                    go.Bar(
                        x=unknown_bar_center,
                        y=unknown_hist,
                        name="Unknown",
                        marker_color="gray",
                        width=unknown_bar_widths,
                    ),
                    row=1,
                    col=1,
                    secondary_y=False,
                )
            if 3 in unknown_chart_types and unknown_fit_dist != "none":
                unknown_params = parameter_data["unknown"][unknown_fit_dist]
                unknown_dist = getattr(stats, unknown_fit_dist)
                x_range_for_pdf = np.linspace(range_value[0], range_value[1], 300)
                unknown_pdf = unknown_dist.pdf(x_range_for_pdf, **unknown_params)
                fig2.add_trace(
                    go.Scatter(
                        x=x_range_for_pdf,
                        y=unknown_pdf,
                        mode="lines",
                        name="Unknowns",
                        line_color="gray",
                    ),
                    row=1,
                    col=1,
                    secondary_y=False,
                )

        # Data points on the bottom axis (can be used for 'Rug' if not plotted above)
        #        if positive_data.size > 0:
        #            fig2.add_trace(
        #                go.Box(  # positive points  #draw original data points in boxplot below x axis
        #                    x=column_data["positive"]["data"],
        #                    marker_symbol="line-ns-open",
        #                    marker_color="red",
        #                    boxpoints="all",
        #                    jitter=1,
        #                    fillcolor="rgba(255,255,255,0)",
        #                    line_color="rgba(255,255,255,0)",
        #                    hoveron="points",
        #                    showlegend=False,
        #                ),
        #                row=2,
        #                col=1,
        #            )

        #        if negative_data.size > 0:
        #            fig2.add_trace(
        #                go.Box(  # negative points  #draw original data points in boxplot below x axis
        #                    x=column_data["negative"]["data"],
        #                    marker_symbol="line-ns-open",
        #                    marker_color="blue",
        #                    boxpoints="all",
        #                    jitter=1,
        #                    fillcolor="rgba(255,255,255,0)",
        #                    line_color="rgba(255,255,255,0)",
        #                    hoveron="points",
        #                    showlegend=False,
        #                ),
        #                row=2,
        #                col=1,
        #            )
        #
        #        if unknown_data.size > 0:
        #            fig2.add_trace(
        #                go.Box(  # unknown points  #draw original data points in boxplot below x axis
        #                    x=column_data["unknown"]["data"],
        #                    marker_symbol="line-ns-open",
        #                    marker_color="gray",
        #                    boxpoints="all",
        #                    jitter=1,
        #                    fillcolor="rgba(255,255,255,0)",
        #                    line_color="rgba(255,255,255,0)",
        #                    hoveron="points",
        #                    showlegend=False,
        #                ),
        #                row=2,
        #                col=1,
        #            )

        fig2.add_vline(
            x=pos_x,
            line_width=3,
            line_dash="dashdot",
            line_color="orange",
            annotation_text=pos_x,
            annotation_position="top right",  # Position above the line
            annotation_font=dict(size=18),
            row=1,
            col=1,
            secondary_y=True,
        )  # Customize font

        fig2.update_yaxes(showticklabels=False, row=2, col=1)
        fig2.update_xaxes(range=[range_value[0], range_value[1]], row=1, col=1)
        fig2.update_xaxes(range=[range_value[0], range_value[1]], row=2, col=1)
        fig2.update_layout(margin=dict(l=20, r=20, t=0, b=0), showlegend=False)

        return fig2  # , roc_table


if __name__ == "__main__":
    app.run(debug=True)
