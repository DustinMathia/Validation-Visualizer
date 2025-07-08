import numpy as np
from scipy import stats
import plotly.graph_objects as go

def manipulate_data(data_list, column_names):
  manipulated_data = {}
  col_dtypes = data_list.dtype.fields
  numeric_cols = [col_name for col_name, col_type in col_dtypes.items()
                   if col_type[0] in (np.int_, np.float64) and col_name != 'reference_result']
  for col in numeric_cols:
    # Filter data based on reference_result
    positive_data_filtered = data_list[data_list['reference_result'] >  0][col]
    negative_data_filtered = data_list[data_list['reference_result'] <  0][col]
    unknown_data_filtered  = data_list[data_list['reference_result'] == 0][col]

    # Range Min, Max, Value, and Slider Initial Value
    range_min = 0 #min([positive_data_filtered.min(), negative_data_filtered.min(), unknown_data_filtered.min()])
    range_max = max([positive_data_filtered.max(), negative_data_filtered.max(), unknown_data_filtered.max()])
    range_value = [range_min, range_max]
    slider_value = range_min

    # Store data
    manipulated_data[col] = {
        'positive': {'data': np.sort(positive_data_filtered)},
        'negative': {'data': np.sort(negative_data_filtered)},
        'unknown' : {'data': np.sort(unknown_data_filtered)},
        'range_min': range_min, 'range_max': range_max, 'range_value': range_value, 'slider_value': slider_value
    }
  return manipulated_data

def calculate_bin_edges(column_data, graph_range, traces):
  if column_data is None:
    return []
  extended_data = []
  if 'Positive' in traces:
    extended_data.extend(column_data['positive']['data'])
  if 'Negative' in traces:
    extended_data.extend(column_data['negative']['data'])
  if 'Unknown' in traces:
    extended_data.extend(column_data['unknown']['data'])
  bin_edges = np.histogram_bin_edges(extended_data, bins='auto', range=graph_range)
  return bin_edges

def fit_params(file_data):
  fitted_data = {}
  for column in file_data:
    positive_data = file_data[column]['positive']['data']
    negative_data = file_data[column]['negative']['data']
    unknown_data  = file_data[column]['unknown'] ['data']

    pnl, pns = stats.norm.fit(positive_data)
    pel, pes = stats.expon.fit(positive_data)
    penk, penl, pens = stats.exponnorm.fit(positive_data)
    nnl, nns = stats.norm.fit(negative_data)
    nel, nes = stats.expon.fit(negative_data)
    nenk, nenl, nens = stats.exponnorm.fit(negative_data)
    unl, uns = stats.norm.fit(unknown_data)
    uel, ues = stats.expon.fit(unknown_data)
    uenk, uenl, uens = stats.exponnorm.fit(unknown_data)
    fitted_data[column] = {
                  'positive': {'norm': {'loc': pnl, 'scale': pns},#                'r-squared': None, 'aic': None, 'bic': None},
                              'expon': {'loc': pel, 'scale': pes},#                'r-squared': None, 'aic': None, 'bic': None},
                              'exponnorm': {'K': penk, 'loc': penl, 'scale': pens}},# 'r-squared': None, 'aic': None, 'bic': None}},
                  'negative': {'norm': {'loc': nnl, 'scale': nns},#                'r-squared': None, 'aic': None, 'bic': None},
                              'expon': {'loc': nel, 'scale': nes},#                'r-squared': None, 'aic': None, 'bic': None},
                              'exponnorm': {'K': nenk, 'loc': nenl, 'scale': nens}},# 'r-squared': None, 'aic': None, 'bic': None}},
                  'unknown':  {'norm': {'loc': unl, 'scale': uns},#                'r-squared': None, 'aic': None, 'bic': None},
                              'expon': {'loc': uel, 'scale': ues},#                'r-squared': None, 'aic': None, 'bic': None},
                              'exponnorm': {'K': uenk, 'loc': uenl, 'scale': uens}}#, 'r-squared': None, 'aic': None, 'bic': None}}
              }
  return fitted_data


def make_roc_curve(positive_data, negative_data, unknown_data):  # view confusion matrix chart @ https://en.wikipedia.org/wiki/Receiver_operating_characteristic
  total_positive = len(positive_data)
  total_negative = len(negative_data)
  total_unknown  = len(unknown_data)

  # make list of formated data values: tuple (value, True/False)
  positive_data = [(value, True) for value in positive_data]
  negative_data = [(value, False) for value in negative_data]
  unknown_data  = [(value, None) for value in unknown_data]

  #create a sorted master list of all categories
  population_data = sorted(positive_data + negative_data + unknown_data, key=lambda x: x[0])

  # accumulation for each population at index
  accumulated_positive = []
  accumulated_negative = []
  accumulated_unknown = []

  current_positive = 0
  current_negative = 0
  current_unknown = 0

  for value, label in population_data:
      if label is True:
          current_positive += 1
      elif label is False:
          current_negative += 1
      elif label is None:
          current_unknown += 1

      accumulated_positive.append(current_positive)
      accumulated_negative.append(current_negative)
      accumulated_unknown.append(current_unknown)


  # True positive at index
  TP = [total_positive - accumulated_positive[i] for i in range(len(accumulated_positive))]
  # False positive at index
  FP =  [total_negative - accumulated_negative[i] for i in range(len(accumulated_negative))] 
  # True negative at index
  TN = accumulated_negative
  # False negative at index
  FN = accumulated_positive

  # unknown labelled positive
  UP = [total_unknown - accumulated_unknown[i] for i in range(len(accumulated_unknown))]
  # unknown labelled negative
  UN = accumulated_unknown

  # True positive rate at index
  TPR = [TP[i] / total_positive if total_positive > 0 else 0 for i in range(len(TP))]
  # False positive rate at index
  FPR = [FP[i] / total_negative if total_negative > 0 else 0 for i in range(len(FP))]
  # True negative rate at index
  TNR = [1 - FPR[i] for i in range(len(TN))]
  # False negative rate at index
  FNR = [1 - TPR[i] for i in range(len(FN))]

  # accuracy at index
  ACC = [(TPR[i] + TNR[i]) / (total_positive + total_negative) if (total_positive + total_negative) > 0 else 0 for i in range(len(TP))]

  return {'population_data': population_data,
          'total_positive': total_positive,
          'total_negative': total_negative,
          'total_unknown': total_unknown,
          'accumulated_positive': accumulated_positive,
          'accumulated_negative': accumulated_negative,
          'accumulated_unknown': accumulated_unknown,
          'TP': TP,
          'FP': FP,
          'TN': TN,
          'FN': FN,
          'UP': UP,
          'UN': UN,
          'TPR': TPR,
          'FPR': FPR,
          'TNR': TNR,
          'FNR': FNR,
          'ACC': ACC}


def plot_roc(TPR, FPR, fig):

  #remove unknown from TPR and FPR
  TPR = [TPR[i] for i in range(len(TPR)) if TPR[i] != None]
  FPR = [FPR[i] for i in range(len(FPR)) if FPR[i] != None]
  #TPR = TPR.reverse()
  #FPR = FPR.reverse()

  #fig_roc = go.Figure(data=go.Scatter(x=FPR, y=TPR, mode='lines', line_shape='hv'))
  fig.add_trace(go.Scatter(x=FPR, y=TPR, mode='lines', line_shape='hv'), row=1, col=2)

  #fig.update_layout(
  #    title='ROC Curve',
  #    xaxis_title='False Positive Rate',
  #    yaxis_title='True Positive Rate',
  #    hovermode='closest'
  #)
  return fig
