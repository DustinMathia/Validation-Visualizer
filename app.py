import dash
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
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from scipy import stats
import base64
import pickle
import io
import os
import shutil
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
THRESHOLD = "#d47500"

SAVED_FILE_NAMES = {
    "roc curves": "roc_curves.pkl",
    "raw data": "raw_data.feather",
    "labeled data": "labeled_data.pkl",
    "parameter fitting": "fitted_params.pkl",
}

DATA_FOLDER = "data"

app = Dash(
    __name__,
    external_stylesheets=[
        SELECTED_BOOTSTRAP_THEME,
        dbc.icons.BOOTSTRAP,
        dbc_css,
        custom_css,
    ],
    use_pages=True,
    suppress_callback_exceptions=True,
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Visualize", class_name="", href="/")),
        dbc.NavItem(dbc.NavLink("Data-Manager", class_name="", href="/data-manager")),
        dbc.NavItem(dbc.NavLink("Help", class_name="", href="/help")),
    ],
    brand=html.A(
        dbc.Row(
            [
                dbc.Col(
                    html.Img(
                        src="/assets/logo-white-validation-visualizer.png",
                        height="30px",
                    )
                ),
            ],
            align="center",
            class_name="g-0",
        ),
    ),
    color="primary",
    dark=True,
    links_left=True,
    style={"paddingTop": "0px", "paddingBottom": "0px"},
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
            is_open=False,
            className="d-flex align-items-center",
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
            is_open=False,
            className="d-flex align-items-center",
        ),
    ],
)


app.layout = html.Div(
    [
        html.Div(id="loadup-dummy"),
        dcc.Store(id="uploaded-files-list", data=[], storage_type="memory"),
        dcc.Store(id="processed-files-list", data=[], storage_type="memory"),
        dcc.Store(id="raw-data-for-grid", data={}, storage_type="memory"),
        dcc.Store(id="labeled-data", data={}, storage_type="memory"),
        dcc.Store(id="fit-params", data={}, storage_type="memory"),
        dcc.Store(id="roc-curves", data={}, storage_type="memory"),
        dcc.Store(id="range-value", data=[None, None], storage_type="memory"),
        dcc.Store(id="graph-cache", data={}, storage_type="memory"),
        navbar,
        alert_fail,
        alert_warning,
        dash.page_container,
    ]
)


@callback(
    Output("uploaded-files-list", "data", allow_duplicate=True),
    Output("alert-fail", "is_open", allow_duplicate=True),
    Output("alert-fail", "children", allow_duplicate=True),
    Output("alert-warning", "is_open", allow_duplicate=True),
    Output("alert-warning", "children", allow_duplicate=True),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("uploaded-files-list", "data"),
    prevent_initial_call=True,
)
# Checks if uploaded files are valid
def store_files(upload_contents, upload_filenames, uploaded_files_list):
    all_uploaded_files_list = uploaded_files_list if uploaded_files_list else []
    errors = []
    warnings = []

    if upload_filenames is not None:
        for content, filename in zip(upload_contents, upload_filenames):
            content_type, content_string = content.split(",")
            try:
                decoded = base64.b64decode(content_string)
            except base64.binascii.Error as e:
                errors.append(f"Error decoding Base64 string of file {filename}: {e}")

            try:
                if filename.endswith(".tsv"):
                    df_file = pd.read_csv(
                        io.StringIO(decoded.decode("utf-8")), sep="\t"
                    )
                else:
                    errors.append(
                        f"The filetype of {filename} is incorrect. Please upload a .tsv file."
                    )
                    continue

                # Check for required Column
                if "reference_result" not in df_file.columns:
                    warnings.append(f"Warning: No Column 'reference_result' in {filename}")
                else:
                    if (
                        not df_file["reference_result"]
                        .isin({float(-1), float(0), float(1), np.nan})
                        .all()
                    ):
                        errors.append(
                            f"Error: The column 'reference_result' in file {filename} has incorrect values, must be -1, 0, 1, or be empty."
                        )

            except pd.errors.EmptyDataError:
                errors.append(f"Error: The file {filename} is empty.")
            except Exception as e:
                errors.append(f"An unexpected Error occured: {e}")

            # If no errors, file is acceptable and save to /data/filename/
            file_dir = os.path.join("data", filename)
            if not errors:
                os.makedirs(file_dir, exist_ok=True)
                output_filepath = os.path.join(file_dir, filename)

                try:
                    with open(output_filepath, "wb") as file:
                        file.write(decoded)
                    all_uploaded_files_list.append(filename)
                except IOError as e:
                    errors.append(f"Error saving file {filename}: {e}")
            else:
                # delete file
                all_uploaded_files_list.remove(filename)
                if os.path.exists(file_dir):
                    try:
                        shutil.rmtree(file_dir)
                    except OSError as e:
                        errors.append(f"Error: {file_dir} - {e.strerror}.")

    # Logic for alerts
    fail_is_open = len(errors) > 0
    warning_is_open = len(warnings) > 0
    fail_children = html.Ul([html.Li(msg) for msg in errors]) if errors else ""
    warning_children = html.Ul([html.Li(msg) for msg in warnings]) if warnings else ""
    errors = []

    return (
        all_uploaded_files_list,
        fail_is_open,
        fail_children,
        warning_is_open,
        warning_children,
    )


# TODO: when files with same filename are uploaded they do not replace the existing file
@callback(
    Output("processed-files-list", "data", allow_duplicate=True),
    Output("labeled-data", "data", allow_duplicate=True),
    Output("roc-curves", "data", allow_duplicate=True),
    Output("fit-params", "data", allow_duplicate=True),
    Output("raw-data-for-grid", "data", allow_duplicate=True),
    Output("alert-fail", "is_open", allow_duplicate=True),
    Output("alert-fail", "children", allow_duplicate=True),
    Input("uploaded-files-list", "data"),
    State("processed-files-list", "data"),
    prevent_initial_call=True,
)
def data_processing(uploaded_files_list, processed_files_list):
    errors = []
    if not uploaded_files_list:
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
        )

    new_labeled_data = {}
    new_roc_curves = {}
    new_fit_params = {}
    new_raw_data_for_grid = {}
    last_processed_file = None

    finished_processed_files_list = processed_files_list if processed_files_list else []

    for filename in uploaded_files_list:
        if filename not in finished_processed_files_list:
            try:
                file_dir = os.path.join("data", filename)
                raw_file_path = os.path.join(file_dir, filename)

                if filename.endswith(".tsv"):
                    df = pd.read_csv(raw_file_path, sep="\t")

                labeled_data = utils.label_data(df)
                roc_curves = utils.make_roc_curve(labeled_data)
                fitted_params = utils.fit_params(labeled_data)

                labeled_data_filepath = os.path.join(
                    file_dir, SAVED_FILE_NAMES["labeled data"]
                )
                with open(labeled_data_filepath, "wb") as f:
                    pickle.dump(labeled_data, f)
                roc_curves_filepath = os.path.join(
                    file_dir, SAVED_FILE_NAMES["roc curves"]
                )
                with open(roc_curves_filepath, "wb") as f:
                    pickle.dump(roc_curves, f)
                fitted_params_filepath = os.path.join(
                    file_dir, SAVED_FILE_NAMES["parameter fitting"]
                )
                with open(fitted_params_filepath, "wb") as f:
                    pickle.dump(fitted_params, f)

                raw_grid_filepath = os.path.join(file_dir, SAVED_FILE_NAMES["raw data"])
                df.to_feather(raw_grid_filepath)

                new_labeled_data[filename] = labeled_data
                new_roc_curves[filename] = roc_curves
                new_fit_params[filename] = fitted_params
                new_raw_data_for_grid[filename] = df.to_dict("records")

                finished_processed_files_list.append(filename)
                last_processed_file = filename

            except Exception as e:
                errors.append(f"Error processing file {filename}: {e}")
                if os.path.exists(filename):
                    try:
                        shutil.rmtree(filename)
                    except OSError as e:
                        errors.append(f"Error: {filename} - {e.strerror}.")

    # Logic for alerts
    fail_is_open = len(errors) > 0
    fail_children = html.Ul([html.Li(msg) for msg in errors]) if errors else ""
    errors = []

    if last_processed_file:
        return (
            finished_processed_files_list,
            new_labeled_data.get(last_processed_file, {}),
            new_roc_curves.get(last_processed_file, {}),
            new_fit_params.get(last_processed_file, {}),
            new_raw_data_for_grid.get(last_processed_file, {}),
            fail_is_open,
            fail_children,
        )

    return (
        no_update,
        no_update,
        no_update,
        no_update,
        no_update,
        fail_is_open,
        fail_children,
    )


@app.callback(
    Output("labeled-data", "data"),
    Output("fit-params", "data"),
    Output("roc-curves", "data"),
    Output("raw-data-for-grid", "data"),
    Input("file-select", "value"),
    prevent_initial_call=True,
)
def load_data_into_stores(file_select_value):
    if file_select_value is None:
        return no_update, no_update, no_update, no_update

    file_dir = os.path.join("data", file_select_value)

    # Load labeled data from pickle
    labeled_data_path = os.path.join(file_dir, "labeled_data.pkl")
    with open(labeled_data_path, "rb") as f:
        labeled_data = pickle.load(f)

    # Load fitted params from pickle
    fit_params_path = os.path.join(file_dir, "fitted_params.pkl")
    with open(fit_params_path, "rb") as f:
        fit_params = pickle.load(f)

    # Load ROC curve data from pickle
    roc_curves_path = os.path.join(file_dir, "roc_curves.pkl")
    with open(roc_curves_path, "rb") as f:
        roc_curves = pickle.load(f)

    # Load raw data from feather and convert to dict for AG Grid
    raw_data_path = os.path.join(file_dir, "raw_data.feather")
    raw_data_df = pd.read_feather(raw_data_path)
    raw_data_for_grid = raw_data_df.to_dict("records")

    return labeled_data, fit_params, roc_curves, raw_data_for_grid


# Sliders #


@callback(
    Output("range-value", "data"),
    Output("range-slider", "value"),
    Output("range-slider", "min"),
    Output("range-slider", "max"),
    Input("column-select", "value"),
    Input("range-reset", "n_clicks"),
    State("range-slider", "value"),
    State("labeled-data", "data"),
    prevent_initial_call=False,
)
def reset_range_slider(selected_column, n_clicks, rangeslider_value, labeled_data):
    if not selected_column:
        raise dash.exceptions.PreventUpdate

    range_min = labeled_data.get(selected_column, {}).get("range_min", 0)
    range_max = labeled_data.get(selected_column, {}).get("range_max", 0)

    rangeslider_value = [range_min, range_max]

    return rangeslider_value, rangeslider_value, range_min, range_max


@callback(
    Output("slider-position", "value", allow_duplicate=True),
    Output("slider-position", "min", allow_duplicate=True),
    Output("slider-position", "max", allow_duplicate=True),
    Input("range-slider", "value"),
    State("slider-position", "value"),
    prevent_initial_call=True,
)
def update_threshold_slider(rangeslider_value, slider_value):
    # If the current value is outside the new range, reset it to the new min
    if slider_value <= rangeslider_value[0]:
        slider_value = rangeslider_value[0]
    if slider_value >= rangeslider_value[1]:
        slider_value = rangeslider_value[1]

    return slider_value, rangeslider_value[0], rangeslider_value[1]


# @callback(
#     Output("threshold-slider-label", "children"),
#     Input("column-select", "value"),
# )
# def update_threshold_slider_label(selected_column):
#     return selected_column


# roc figures #


no_fig = go.Figure()
no_fig.add_annotation(
    text="No Data",
    xref="paper",
    yref="paper",
    x=0.5,
    y=0.5,
    showarrow=False,
    font=dict(size=24, color="grey"),
)
no_fig.update_layout(xaxis={"visible": False}, yaxis={"visible": False})


@app.callback(
    Output("roc_plot", "figure"),
    Output("roc-table", "data"),
    Output("roc-table", "columns"),
    Input("column-select", "value"),
    Input("slider-position", "value"),
    State("fit-params", "data"),
    State("roc-curves", "data"),
    prevent_inital_call=False,
)
def update_roc_plot_and_table(selected_column, pos_x, fitted_params, roc_curves):
    if not roc_curves or not selected_column:
        return no_fig, None, None

    roc_column = roc_curves.get(selected_column)

    # Check if roc_column and its population_data are available and not empty
    if not roc_column or not roc_column.get("population_data"):
        return no_fig, None, None
    else:
        ROCDataTable_data, ROCDataTable_columns, roc_index = utils.gen_roc_table(
            roc_column, pos_x, fitted_params[selected_column]["positive"]["norm"]
        )
        roc_fig = utils.plot_roc_curve(roc_column, roc_index)
        roc_fig.update_layout(
            showlegend=False,
            xaxis=dict(range=[1.05, -0.05], title="Specificty (FPR)"),
            yaxis=dict(range=[-0.05, 1.05], title="Sensitivity (TPR)"),
        )
        # roc_table.update_layout(
        #     margin=dict(l=10, r=10, t=10, b=10), width=525  # Reduce overall margins
        # )
    return roc_fig, ROCDataTable_data, ROCDataTable_columns


@app.callback(
    Output("slider-position", "value", allow_duplicate=True),
    Input("roc_plot", "clickData"),
    prevent_initial_call=True,
)
def set_threshold_on_click_rocplot(clickData):
    if clickData:
        threshold = clickData["points"][0]["customdata"]
        return threshold
    return no_update


# data ag grid #


@app.callback(
    Output("ag-grid", "rowData"),
    Output("ag-grid", "columnDefs"),
    Input("raw-data-for-grid", "data"),
    Input("file-select", "value"),
    prevent_inital_call=True,
)
def update_data_grid(raw_data_for_grid, selected_file):
    # Ensure raw_files is a dictionary, even if it starts as None
    raw_data_for_grid = (
        raw_data_for_grid if raw_data_for_grid is not None else pd.DataFrame()
    )

    if raw_data_for_grid and selected_file:
        row_Data = raw_data_for_grid
        column_names = list(raw_data_for_grid[0].keys())
        column_Defs = [{"field": i} for i in column_names]

        return row_Data, column_Defs
    return [], []  # Return empty lists if no data or file selected


# buttons #


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


# dropdowns #


@app.callback(
    Output("file-select", "options"),
    Output("file-select", "value"),
    Input("processed-files-list", "data"),
    prevent_initial_call=False,
)
def update_file_dropdown(processed_files_list):  # , current_page):
    if not processed_files_list:
        return [], None

    options = [
        {"label": filename, "value": filename} for filename in processed_files_list
    ]
    default_value = processed_files_list[-1]

    return options, default_value


@app.callback(
    Output("column-select", "options"),
    Output("column-select", "value"),
    Input("labeled-data", "data"),
    prevent_initial_call=True,
)
def update_column_dropdown(labeled_data):
    if not labeled_data:
        return [], None

    column_names = list(labeled_data.keys())
    # try:
    #     column_names.remove("reference_result")
    # except ValueError:
    #     pass
    options = [{"label": column, "value": column} for column in column_names]
    default_value = column_names[0] if column_names else None

    return options, default_value


@app.callback(
    Output("pos-statfit-select", "value"),
    Output("neg-statfit-select", "value"),
    Output("unknown-statfit-select", "value"),
    Input("column-select", "value"),
    State("pos-statfit-select", "value"),
    State("neg-statfit-select", "value"),
    State("unknown-statfit-select", "value"),
)
def init_statfit_select(selected_column, pos, neg, unk):
    if not pos:
        pos = "gompertz"
    if not neg:
        neg = "gompertz"
    if not unk:
        unk = "gompertz"
    return pos, neg, unk


# main graph #


@app.callback(
    Output("slider-position", "value", allow_duplicate=True),
    Input("graph", "clickData"),
    State("range-value", "data"),
    # State
    prevent_initial_call=True,
)
def set_threshold_on_click_maingraph(clickData, range_value):
    if clickData:
        point_data = clickData["points"][0]
        x_coord = point_data["x"]
        if range_value[0] <= x_coord <= range_value[1]:
            return x_coord
    return no_update


@app.callback(
    # Output("graph-cache", "data"),
    Output("graph", "figure", allow_duplicate=True),
    [
        Input("pos-statfit-select", "value"),
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
        Input("slider-position", "value"),
        Input("range-slider", "value"),
        Input("p-value", "value"),
        Input("p-value-input", "value"),
        State("labeled-data", "data"),
        State("fit-params", "data"),
        State("roc-curves", "data"),
        State("column-select", "value"),
    ],
    prevent_initial_call=True,
)
def update_graph_and_cache(
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
    slider_value,
    range_value,
    p_value,
    p_value_input,
    labeled_data,
    fitted_params,
    roc_data,
    selected_column,
):
    if not labeled_data or not selected_column:
        raise dash.exceptions.PreventUpdate

    pos_chart_types = []
    if not pos_btn1_outline:
        pos_chart_types.append("rug")
    if not pos_btn2_outline:
        pos_chart_types.append("hist")
    if not pos_btn3_outline:
        pos_chart_types.append("stat")

    neg_chart_types = []
    if not neg_btn1_outline:
        neg_chart_types.append("rug")
    if not neg_btn2_outline:
        neg_chart_types.append("hist")
    if not neg_btn3_outline:
        neg_chart_types.append("stat")

    unknown_chart_types = []
    if not unk_btn1_outline:
        unknown_chart_types.append("rug")
    if not unk_btn2_outline:
        unknown_chart_types.append("hist")
    if not unk_btn3_outline:
        unknown_chart_types.append("stat")

    column_data = labeled_data.get(selected_column)
    parameter_data = fitted_params.get(selected_column)

    if pos_fit_dist:
        pos_params = parameter_data["positive"][pos_fit_dist]
    if neg_fit_dist:
        neg_params = parameter_data["negative"][neg_fit_dist]
    if unknown_fit_dist:
        unknown_params = parameter_data["unknown"][unknown_fit_dist]

    positive_data = np.array(column_data.get("positive", {}).get("data", []))
    negative_data = np.array(column_data.get("negative", {}).get("data", []))
    unknown_data = np.array(column_data.get("unknown", {}).get("data", []))
    range_min = column_data.get("range_min", 0)
    range_max = column_data.get("range_max", 100)

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.93, 0.07],
        shared_xaxes="columns",
        vertical_spacing=0.01,
        specs=[[{"type": "xy"}], [{"type": "xy"}]],
    )

    if column_data and parameter_data:
        # Calculate Histogram points depending of ranger slider
        bin_edges = utils.calculate_bin_edges(range_value, range_min, range_max)
        positive_hist, positive_bin_edges = np.histogram(
            column_data["positive"]["data"],
            bins=bin_edges,
            density=True,
        )
        negative_hist, negative_bin_edges = np.histogram(
            column_data["negative"]["data"],
            bins=bin_edges,
            density=True,
        )
        unknown_hist, unknown_bin_edges = np.histogram(
            column_data["unknown"]["data"],
            bins=bin_edges,
            density=True,
        )

        graph_max_height = 0

        positive_bar_widths = np.diff(positive_bin_edges)
        negative_bar_widths = np.diff(negative_bin_edges)
        unknown_bar_widths = np.diff(unknown_bin_edges)

        positive_bar_center = positive_bin_edges[:-1] + positive_bar_widths / 2
        negative_bar_center = negative_bin_edges[:-1] + negative_bar_widths / 2
        unknown_bar_center = unknown_bin_edges[:-1] + unknown_bar_widths / 2

        # Unknown Trace
        if unknown_data.size > 0:
            if "rug" in unknown_chart_types:
                fig.add_trace(
                    go.Box(
                        x=column_data["unknown"]["data"],
                        marker_symbol="line-ns-open",
                        marker_color=UNKNOWN,
                        boxpoints="all",
                        jitter=0.5,
                        fillcolor="rgba(255,255,255,0)",
                        line_color="rgba(255,255,255,0)",
                        hoveron="points",
                        showlegend=False,
                        name="Unknown",
                        hovertemplate="Threshold: <b>%{x:.2f}</b>",
                    ),
                    row=2,
                    col=1,
                )
            if "hist" in unknown_chart_types:
                if max(unknown_hist) > graph_max_height:
                    graph_max_height = max(unknown_hist)
                fig.add_trace(
                    go.Bar(
                        x=unknown_bar_center,
                        y=unknown_hist,
                        name="Unknown",
                        marker_color=UNKNOWN,
                        width=unknown_bar_widths,
                        opacity=0.7,
                        hoverinfo="none",
                    ),
                    row=1,
                    col=1,
                    secondary_y=False,
                )
            if (
                "stat" in unknown_chart_types
                and unknown_fit_dist != "none"
                and unknown_fit_dist
            ):
                unknown_params = parameter_data["unknown"][unknown_fit_dist]
                unknown_dist = getattr(stats, unknown_fit_dist)
                x_range_for_pdf = np.linspace(range_value[0], range_value[1], 300)
                unknown_pdf = unknown_dist.pdf(x_range_for_pdf, **unknown_params)
                if max(unknown_pdf) > graph_max_height:
                    graph_max_height = max(unknown_pdf)
                fig.add_trace(
                    go.Scatter(
                        x=x_range_for_pdf,
                        y=unknown_pdf,
                        mode="lines",
                        name="Unknown",
                        line_color=UNKNOWN,
                        hoverinfo="none",
                    ),
                    row=1,
                    col=1,
                )

        # Negative Trace
        if negative_data.size > 0:
            if "rug" in neg_chart_types:
                fig.add_trace(
                    go.Box(
                        x=column_data["negative"]["data"],
                        marker_symbol="line-ns-open",
                        marker_color=NEGATIVE,
                        boxpoints="all",
                        jitter=0.5,
                        fillcolor="rgba(255,255,255,0)",
                        line_color="rgba(255,255,255,0)",
                        hoveron="points",
                        showlegend=False,
                        name="Negative",
                        hovertemplate="Threshold: <b>%{x:.2f}</b>",
                    ),
                    row=2,
                    col=1,
                )

            if "hist" in neg_chart_types:
                if max(negative_hist) > graph_max_height:
                    graph_max_height = max(negative_hist)
                fig.add_trace(
                    go.Bar(
                        x=negative_bar_center,
                        y=negative_hist,
                        name="Negative",
                        marker_color=NEGATIVE,
                        width=negative_bar_widths,
                        opacity=0.7,
                        hoverinfo="none",
                    ),
                    row=1,
                    col=1,
                )

            if "stat" in neg_chart_types and neg_fit_dist != "none" and neg_fit_dist:
                neg_params = parameter_data["negative"][neg_fit_dist]
                negative_dist = getattr(stats, neg_fit_dist)
                x_range_for_pdf = np.linspace(range_value[0], range_value[1], 300)
                negative_pdf = negative_dist.pdf(x_range_for_pdf, **neg_params)
                if max(negative_pdf) > graph_max_height:
                    graph_max_height = max(negative_pdf)
                fig.add_trace(
                    go.Scatter(
                        x=x_range_for_pdf,
                        y=negative_pdf,
                        mode="lines",
                        name="Negative",
                        line_color=NEGATIVE,
                        hoverinfo="none",
                    ),
                    row=1,
                    col=1,
                )

        # Positive Trace
        if positive_data.size > 0:
            if "rug" in pos_chart_types:
                fig.add_trace(
                    go.Box(
                        x=column_data["positive"]["data"],
                        marker_symbol="line-ns-open",
                        marker_color=POSITIVE,
                        boxpoints="all",
                        jitter=0.5,
                        fillcolor="rgba(255,255,255,0)",
                        line_color="rgba(255,255,255,0)",
                        hoveron="points",
                        showlegend=False,
                        name="Positive",
                        hovertemplate="Threshold: <b>%{x:.2f}</b>",
                    ),
                    row=2,
                    col=1,
                )

            if "hist" in pos_chart_types:
                if max(positive_hist) > graph_max_height:
                    graph_max_height = max(positive_hist)
                fig.add_trace(
                    go.Bar(
                        x=positive_bar_center,
                        y=positive_hist,
                        name="Positive",
                        marker_color=POSITIVE,
                        width=positive_bar_widths,
                        opacity=0.7,
                        hoverinfo="none",
                    ),
                    row=1,
                    col=1,
                )

            if "stat" in pos_chart_types and pos_fit_dist != "none" and pos_fit_dist:
                pos_params = parameter_data["positive"][pos_fit_dist]
                positive_dist = getattr(stats, pos_fit_dist)
                x_range_for_pdf = np.linspace(range_value[0], range_value[1], 300)
                positive_pdf = positive_dist.pdf(x_range_for_pdf, **pos_params)
                if max(positive_pdf) > graph_max_height:
                    graph_max_height = max(positive_pdf)
                fig.add_trace(
                    go.Scatter(
                        x=x_range_for_pdf,
                        y=positive_pdf,
                        mode="lines",
                        name="Positive",
                        line_color=POSITIVE,
                        hoverinfo="none",
                    ),
                    row=1,
                    col=1,
                ),

        graph_yaxis_range = [0, graph_max_height * 1.1]

        if (
            "stat" in pos_chart_types
            and pos_fit_dist != "none"
            and pos_fit_dist
            and positive_data.size > 0
        ):
            if p_value:
                ppf_at_value = positive_dist.ppf(float(p_value_input), **pos_params)
                fig.add_shape(
                    type="line",
                    x0=ppf_at_value,
                    y0=0,
                    x1=ppf_at_value,
                    y1=graph_max_height,
                    line=dict(color=POSITIVE, width=1, dash="dash"),
                )
                fig.add_annotation(
                    x=ppf_at_value,
                    y=graph_max_height,
                    xref="x",
                    yref="y",
                    text="p=" + str(p_value_input),
                    showarrow=False,
                    yanchor="bottom",
                    font=dict(size=10, color=POSITIVE),
                    bgcolor="rgba(0, 0, 0, 0)",
                )

        # Comment for cache func
        if (slider_value is not None
            and pos_fit_dist != "none"
            and pos_fit_dist):
            fig.add_vline(
                x=slider_value,
                line_width=3,
                line_dash="dashdot",
                line_color=THRESHOLD,
                annotation_text=f"{slider_value:.2f}",
                annotation_position="top right",
                annotation_font=dict(size=18),
                row=1,
                col=1,
            ),

        fig.update_yaxes(showticklabels=False, row=2, col=1)
        fig.update_xaxes(range=[range_value[0], range_value[1]], showticklabels=True, ticks="inside", nticks=10, row=1, col=1)
        fig.update_xaxes(range=[range_value[0], range_value[1]], row=2, col=1)
        fig.update_layout(
            margin=dict(l=20, r=20, t=0, b=0),
            xaxis=dict(
                title=selected_column,
                fixedrange=True,
                side="top",
            ),
            yaxis=dict(
                title="Density",
                range=graph_yaxis_range,
            ),
            showlegend=False,
            dragmode=False,
            barmode="group",
            clickmode="event+select",
        )

        return fig  # .to_dict()


# @callback(
#     Output("graph", "figure", allow_duplicate=True),
#     Input("slider-position", "value"),
#     State("graph-cache", "data"),
#     prevent_initial_call=True,
# )
# def load_graph_add_vline(slider_position, graph_json):
#     if not graph_json:
#         raise dash.exceptions.PreventUpdate
#
#     graph = go.Figure(graph_json)
#
#     if slider_position is not None:
#         graph.add_vline(
#             x=slider_position,
#             line_width=3,
#             line_dash="dashdot",
#             line_color=THRESHOLD,
#             annotation_text=f"{slider_position:.2f}",
#             annotation_position="top right",
#             annotation_font=dict(size=18),
#             row=1,
#             col=1,
#         ),
#     return graph


# Init preprocessed data #


def check_for_processed_files(data):
    processed_files = []
    required_files = list(SAVED_FILE_NAMES.values())

    if not os.path.isdir(data):
        return False

    folders = [
        os.path.join(data, f)
        for f in os.listdir(data)
        if os.path.isdir(os.path.join(data, f))
    ]
    for folder in folders:
        if set(os.listdir(folder)) == set(required_files + [os.path.split(folder)[1]]):
            processed_files.append(os.path.split(folder)[1])
    return processed_files


@callback(
    Output("processed-files-list", "data"),
    Input("loadup-dummy", "children"),
    prevent_initial_call=False,
)
def load_data(dummy):
    return check_for_processed_files(DATA_FOLDER)


if __name__ == "__main__":
    app.run(debug=False)
