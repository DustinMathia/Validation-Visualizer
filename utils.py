import numpy as np
from scipy import stats
import plotly.graph_objects as go
import pandas as pd
import bisect
import math
from dash import dash_table

# from app import THRESHOLD

THRESHOLD = "#d47500"


def label_data(df):
    labeled_data = {}
    numeric_cols = [
        col
        for col in df.columns
        if pd.api.types.is_numeric_dtype(df[col]) and col != "reference_result"
    ]

    for col in numeric_cols:

        # Filter data based on reference_result
        if "reference_result" in df.columns:
            df["reference_result"] = df["reference_result"].fillna(0)
            positive_data_filtered = df[df["reference_result"] > 0][col].to_numpy()
            negative_data_filtered = df[df["reference_result"] < 0][col].to_numpy()
            unknown_data_filtered = df[df["reference_result"] == 0][col].to_numpy()
        else:
            unknown_data_filtered = df[col].to_numpy()
            positive_data_filtered = np.array([])
            negative_data_filtered = np.array([])

        all_data = np.concatenate(
            [positive_data_filtered, negative_data_filtered, unknown_data_filtered]
        )
        if all_data.size > 0:
            range_min = math.floor(all_data.min() - 1)
            range_max = math.ceil(all_data.max() + 1)
        else:
            range_min = 0
            range_max = 100  # Default range if no data

        # Store data
        labeled_data[col] = {
            "positive": {"data": np.sort(positive_data_filtered)},
            "negative": {"data": np.sort(negative_data_filtered)},
            "unknown": {"data": np.sort(unknown_data_filtered)},
            "range_min": range_min,
            "range_max": range_max,
        }
    return labeled_data


def calculate_bin_edges(range_value, range_min, range_max):
    num_bins_on_screen = 100

    visible_range_width = range_value[1] - range_value[0]
    step = visible_range_width / num_bins_on_screen

    start = np.floor(range_min / step) * step
    stop = np.ceil(range_max / step) * step

    bin_edges = np.arange(start, stop + step, step)
    return bin_edges


def fit_params(labeled_data):
    fitted_data = {}
    for column, data in labeled_data.items():
        positive_data = data["positive"]["data"]
        negative_data = data["negative"]["data"]
        unknown_data = data["unknown"]["data"]

        # Initialize all parameters to None
        pnl, pns, pgc, pgl, pgs, pel, pes, penk, penl, pens = (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        nnl, nns, ngc, ngl, ngs, nel, nes, nenk, nenl, nens = (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
        unl, uns, ugc, ugl, ugs, uel, ues, uenk, uenl, uens = (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

        if positive_data.size > 0:
            pnl, pns = stats.norm.fit(positive_data)
            pgc, pgl, pgs = stats.gompertz.fit(positive_data)
            pel, pes = stats.expon.fit(positive_data)
            penk, penl, pens = stats.exponnorm.fit(positive_data)
        if negative_data.size > 0:
            nnl, nns = stats.norm.fit(negative_data)
            ngc, ngl, ngs = stats.gompertz.fit(negative_data)
            nel, nes = stats.expon.fit(negative_data)
            nenk, nenl, nens = stats.exponnorm.fit(negative_data)
        if unknown_data.size > 0:
            unl, uns = stats.norm.fit(unknown_data)
            ugc, ugl, ugs = stats.gompertz.fit(unknown_data)
            uel, ues = stats.expon.fit(unknown_data)
            uenk, uenl, uens = stats.exponnorm.fit(unknown_data)

        fitted_data[column] = {
            "positive": {
                "norm": {
                    "loc": pnl,
                    "scale": pns,
                },  #                'r-squared': None, 'aic': None, 'bic': None},
                "gompertz": {"c": pgc, "loc": pgl, "scale": pgs},
                "expon": {
                    "loc": pel,
                    "scale": pes,
                },  #                'r-squared': None, 'aic': None, 'bic': None},
                "exponnorm": {"K": penk, "loc": penl, "scale": pens},
            },  # 'r-squared': None, 'aic': None, 'bic': None}},
            "negative": {
                "norm": {
                    "loc": nnl,
                    "scale": nns,
                },  #                'r-squared': None, 'aic': None, 'bic': None},
                "gompertz": {"c": ngc, "loc": ngl, "scale": ngs},
                "expon": {
                    "loc": nel,
                    "scale": nes,
                },  #                'r-squared': None, 'aic': None, 'bic': None},
                "exponnorm": {"K": nenk, "loc": nenl, "scale": nens},
            },  # 'r-squared': None, 'aic': None, 'bic': None}},
            "unknown": {
                "norm": {
                    "loc": unl,
                    "scale": uns,
                },  #                'r-squared': None, 'aic': None, 'bic': None},
                "gompertz": {"c": ugc, "loc": ugl, "scale": ugs},
                "expon": {
                    "loc": uel,
                    "scale": ues,
                },  #                'r-squared': None, 'aic': None, 'bic': None},
                "exponnorm": {"K": uenk, "loc": uenl, "scale": uens},
            },  # , 'r-squared': None, 'aic': None, 'bic': None}}
        }
    return fitted_data


# mistitled, more like count labels at each point
def make_roc_curve(labeled_data):
    # view confusion matrix chart @ https://en.wikipedia.org/wiki/Receiver_operating_characteristic
    roc_curves = {}
    for column, data in labeled_data.items():
        positive_data = data["positive"]["data"]
        negative_data = data["negative"]["data"]
        unknown_data = data["unknown"]["data"]

        total_positive = len(positive_data)
        total_negative = len(negative_data)
        total_unknown = len(unknown_data)

        if total_positive == 0 and total_positive == 0:
            roc_curves[column] = {
                "population_data": [],
                "total_positive": 0,
                "total_negative": 0,
                "total_unknown": 0,
                "accumulated_positive_at_value": [],
                "accumulated_negative_at_value": [],
                "accumulated_unknown_at_value": [],
            }
            continue

        # make list of formated data values: tuple (value, True/False)
        positive_tuples = [(value, True) for value in positive_data]
        negative_tuples = [(value, False) for value in negative_data]
        unknown_tuples = [(value, None) for value in unknown_data]

        # create a sorted master list of all categories
        population_data = sorted(
            positive_tuples + negative_tuples + unknown_tuples, key=lambda x: x[0]
        )

        current_positive_count = 0
        current_negative_count = 0
        current_unknown_count = 0

        accumulated_positive_at_value = []
        accumulated_negative_at_value = []
        accumulated_unknown_at_value = []

        for value, label in population_data:
            if label is True:
                current_positive_count += 1
            elif label is False:
                current_negative_count += 1
            elif label is None:
                current_unknown_count += 1

            accumulated_positive_at_value.append(current_positive_count)
            accumulated_negative_at_value.append(current_negative_count)
            accumulated_unknown_at_value.append(current_unknown_count)

        roc_curves[column] = {
            "population_data": population_data,
            "total_positive": total_positive,
            "total_negative": total_negative,
            "total_unknown": total_unknown,
            "accumulated_positive_at_value": accumulated_positive_at_value,
            "accumulated_negative_at_value": accumulated_negative_at_value,
            "accumulated_unknown_at_value": accumulated_unknown_at_value,
        }
    return roc_curves


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


def plot_roc_curve(roc_data, threshold_index):
    population_data = roc_data["population_data"]
    total_positive = roc_data["total_positive"]
    total_negative = roc_data["total_negative"]
    acc_pos = roc_data["accumulated_positive_at_value"]
    acc_neg = roc_data["accumulated_negative_at_value"]

    TPR_plot = [1]
    FPR_plot = [0]
    threshold_plot = [population_data[0][0]]

    if total_positive == 0 and total_negative == 0:
        return no_fig

    for k, pop in enumerate(population_data):
        positives_less_than_current_value = acc_pos[k - 1] if k > 0 else 0
        negatives_less_than_current_value = acc_neg[k - 1] if k > 0 else 0

        tp_at_k = total_positive - positives_less_than_current_value
        fp_at_k = total_negative - negatives_less_than_current_value

        tpr_at_k = tp_at_k / total_positive if total_positive > 0 else 0
        fpr_at_k = 1 - (fp_at_k / total_negative) if total_negative > 0 else 0

        TPR_plot.append(tpr_at_k)
        FPR_plot.append(fpr_at_k)
        threshold_plot.append(pop[0])

    TPR_plot.append(0)
    FPR_plot.append(1)
    threshold_plot.append(population_data[-1][0])

    # TPR_plot.reverse()
    # FPR_plot.reverse()

    thresh_pt_x = 0
    thresh_pt_y = 0

    if total_positive == 0 and total_negative == 0:
        pass
    elif threshold_index == len(population_data):
        thresh_pt_x = 1
        thresh_pt_y = 0
    elif threshold_index == 0:
        thresh_pt_x = 0
        thresh_pt_y = 1
    else:
        thresh_pt_x = FPR_plot[threshold_index + 1]
        thresh_pt_y = TPR_plot[threshold_index + 1]

    threshold = population_data[threshold_index][0]

    fig = go.Figure()
    if FPR_plot and TPR_plot:  # Ensure lists are not empty
        fig.add_trace(
            go.Scatter(
                # i mixed up the fpr tpr naming dont fix its correct
                y=FPR_plot,
                x=TPR_plot,
                mode="lines",
                line_shape="hv",
                name="ROC Curve",
                customdata=threshold_plot,
                hovertemplate="Threshold: <b>%{customdata:.2f}</b><br>"
                + "Sensitivity (TPR): %{y:.2f}<br>"
                + "Specificity (FPR): %{x:.2f}",
            )
        )
        fig.add_trace(
            go.Scatter(
                y=[thresh_pt_x],
                x=[thresh_pt_y],
                mode="markers",
                marker=dict(color=THRESHOLD, size=15, symbol="circle"),
                name="Threshold Point",
                customdata=[threshold],
                hovertemplate="Threshold: <b>%{customdata:.2f}</b><br>"
                + "Sensitivity (TPR): %{y:.2f}<br>"
                + "Specificity (FPR): %{x:.2f}",
            )
        )
    return fig


def bisect_population_w_threshold(pop_data, threshold_value):
    # bisect_left returns an insertion point `i` such that all `a[k]` for `k < i` have `a[k] < x`.
    # And all `a[k]` for `k >= i` have `a[k] >= x`.
    # This `i` directly tells us how many elements are strictly less than `threshold_value`.
    index = bisect.bisect_left(pop_data, threshold_value)
    return index


def gen_roc_table(roc_data, threshold_value, norm_params):
    roc_table_header = ["TP", "FN", "FP", "TN"]
    if not roc_data:
        # Return an empty figure or a figure with a message if data is not available
        return (
            [
                [None, None, None, None],
                [None, None, None, None],
                [None, None, None, None],
            ],
            roc_table_header,
            0,
        )

    pop_data = [p[0] for p in roc_data["population_data"]]  #  if p[1] is not None]
    i = bisect_population_w_threshold(pop_data, threshold_value)
    pop_data = [p[0] for p in roc_data["population_data"] if p[1] is not None]
    i_without_unknown = bisect_population_w_threshold(pop_data, threshold_value)

    # Determine counts of samples *below* the threshold (classified as Negative)
    # If i is 0, no points are below the threshold.
    # Otherwise, accumulated_positive[i-1] gives the count of positives up to population_data[i-1].
    if i == 0:
        fn_val = 0
        tn_val = 0
        un_val = 0
    else:
        fn_val = roc_data["accumulated_positive_at_value"][i - 1]
        tn_val = roc_data["accumulated_negative_at_value"][i - 1]
        un_val = roc_data["accumulated_unknown_at_value"][i - 1]

    # Determine counts of samples *at or above* the threshold (classified as Positive)
    tp_val = (
        (roc_data["total_positive"] - fn_val)
        if roc_data["total_positive"] is not None
        else 0
    )
    fp_val = (
        (roc_data["total_negative"] - tn_val)
        if roc_data["total_negative"] is not None
        else 0
    )
    up_val = (
        (roc_data["total_unknown"] - un_val)
        if roc_data["total_unknown"] is not None
        else 0
    )

    tpr_val = (
        round(tp_val / roc_data["total_positive"], 2)
        if roc_data["total_positive"] > 0
        else 0
    )
    fpr_val = (
        round(fp_val / roc_data["total_negative"], 2)
        if roc_data["total_negative"] > 0
        else 0
    )
    tnr_val = (
        round(tn_val / roc_data["total_negative"], 2)
        if roc_data["total_negative"] > 0
        else 0
    )  # Specificity
    fnr_val = (
        round(fn_val / roc_data["total_positive"], 2)
        if roc_data["total_positive"] > 0
        else 0
    )  # Miss Rate

    total_classified = (roc_data["total_positive"] or 0) + (
        roc_data["total_negative"] or 0
    )
    acc_val = (
        round((tp_val + tn_val) / total_classified, 2) if total_classified > 0 else 0
    )

    mean = norm_params["loc"]
    std = norm_params["scale"]
    z_score = (threshold_value - mean) / std if std != 0 else float("nan")
    z_score = round(z_score, 2)
    try:
        ppv = tp_val / (tp_val + fp_val)
    except ZeroDivisionError:
        ppv = float('nan')

    # roc_table_for_df = [
    #     ["A", "B", "C", "D"],
    #     ["TP", "FN", "FP", "TN"],
    #     [tp_val, fn_val, fp_val, tn_val],
    #     [
    #         "Sensitivity (TPR)",
    #         "Miss Rate (FNR)",
    #         "False Alarm (FPR)",
    #         "Specificity (TNR)",
    #     ],
    #     [tpr_val, fnr_val, fpr_val, tnr_val],
    #     ["Unkn. as Pos.", "Unkn. as Neg.", "Accuracy", "Z-score"],
    #     [up_val, un_val, acc_val, z_score],
    # ]
    roc_table_for_df = [
        [
            "TP",
            "TN",
            "FN",
            "FP",
            "Sensitivity (TPR)",
            "Specificity (TNR)",
            "Positive Predictions",
            "Negative Predictions",
            "Accuracy",
            "PPV",
            "Z-score",
        ],
        [
            tp_val,
            tn_val,
            fn_val,
            fp_val,
            tnr_val, # again, tnr and tpr were switched
            tpr_val,
            up_val,
            un_val,
            acc_val,
            round(ppv, 2),
            z_score,
        ],
    ]

    df = pd.DataFrame(roc_table_for_df)
    new_header = df.iloc[0]
    df.columns = new_header
    df = df[1:].reset_index(drop=True)

    data = df.to_dict("records")
    columns = [{"name": i, "id": i} for i in df.columns]

    return data, columns, i
