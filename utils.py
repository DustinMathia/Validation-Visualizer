import numpy as np
from scipy import stats
import plotly.graph_objects as go
import bisect

def manipulate_data(data_list, column_names):
  manipulated_data = {}
  col_dtypes = data_list.dtype.fields
  numeric_cols = [col_name for col_name, col_type in col_dtypes.items()
                   if col_type[0] in (np.int_, np.float64) and col_name != 'reference_result'] 

  for col in numeric_cols:
    # Filter data based on reference_result
    print(data_list.dtype.names)
    if 'reference_result' in data_list.dtype.names:
        print("i did it")
        positive_data_filtered = data_list[data_list['reference_result'] >  0][col]
        negative_data_filtered = data_list[data_list['reference_result'] <  0][col]
        unknown_data_filtered  = data_list[data_list['reference_result'] == 0][col] 
    else:
        unknown_data_filtered  = data_list[col] 
        positive_data_filtered = np.array([])
        negative_data_filtered = np.array([])

    all_data = np.concatenate([positive_data_filtered, negative_data_filtered, unknown_data_filtered])
    if all_data.size > 0:
        range_min = all_data.min()
        range_max = all_data.max()
    else:
        range_min = 0
        range_max = 100 # Default range if no data

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

    # Initialize all parameters to None
    pnl, pns, pgc, pgl, pgs, pel, pes, penk, penl, pens = None, None, None, None, None, None, None, None, None, None
    nnl, nns, ngc, ngl, ngs, nel, nes, nenk, nenl, nens = None, None, None, None, None, None, None, None, None, None
    unl, uns, ugc, ugl, ugs, uel, ues, uenk, uenl, uens = None, None, None, None, None, None, None, None, None, None

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
                  'positive': {'norm': {'loc': pnl, 'scale': pns},#                'r-squared': None, 'aic': None, 'bic': None},
                              'gompertz': {'c': pgc, 'loc': pgl, 'scale': pgs},
                              'expon': {'loc': pel, 'scale': pes},#                'r-squared': None, 'aic': None, 'bic': None},
                              'exponnorm': {'K': penk, 'loc': penl, 'scale': pens}},# 'r-squared': None, 'aic': None, 'bic': None}},
                  'negative': {'norm': {'loc': nnl, 'scale': nns},#                'r-squared': None, 'aic': None, 'bic': None},
                              'gompertz': {'c': ngc, 'loc': ngl, 'scale': ngs},
                              'expon': {'loc': nel, 'scale': nes},#                'r-squared': None, 'aic': None, 'bic': None},
                              'exponnorm': {'K': nenk, 'loc': nenl, 'scale': nens}},# 'r-squared': None, 'aic': None, 'bic': None}},
                  'unknown':  {'norm': {'loc': unl, 'scale': uns},#                'r-squared': None, 'aic': None, 'bic': None},
                              'gompertz': {'c': ugc, 'loc': ugl, 'scale': ugs}, 
                              'expon': {'loc': uel, 'scale': ues},#                'r-squared': None, 'aic': None, 'bic': None},
                              'exponnorm': {'K': uenk, 'loc': uenl, 'scale': uens}}#, 'r-squared': None, 'aic': None, 'bic': None}}
              }
  return fitted_data


def make_roc_curve(positive_data, negative_data, unknown_data):  # view confusion matrix chart @ https://en.wikipedia.org/wiki/Receiver_operating_characteristic
  total_positive = len(positive_data)
  total_negative = len(negative_data)
  total_unknown  = len(unknown_data)

  if total_positive ==  0 and total_positive == 0: # usually if reference_result doesnt exist
     return {'population_data': None,
          'total_positive': None,
          'total_negative': None,
          'total_unknown': None,
          'accumulated_positive': None,
          'accumulated_negative': None,
          'accumulated_unknown': None,
          'TP': None,
          'FP': None,
          'TN': None,
          'FN': None,
          'UP': None,
          'UN': None,
          'TPR': None,
          'FPR': None,
          'TNR': None,
          'FNR': None,
          'ACC': None}
 
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
  TNR = [1 - FPR[i] if FPR[i] is not None else None for i in range(len(TN))] # Handle division by zero
  # False negative rate at index
  FNR = [1 - TPR[i] if TPR[i] is not None else None for i in range(len(FN))] # Handle division by zero
 
  # accuracy at index
  ACC = [(TPR[i] + TNR[i]) / (total_positive + total_negative) if (total_positive + total_negative) > 0 and TPR[i] is not None and TNR[i] is not None else 0 for i in range(len(TP))]

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


def plot_roc_curve(TPR, FPR, i):
  
  thresh_pt_x = FPR[i]
  thresh_pt_y = TPR[i]

  #remove unknown from TPR and FPR
  # Filter out None values before plotting
  filtered_tpr = [t for t in TPR if t is not None]
  filtered_fpr = [f for f in FPR if f is not None]

  fig = go.Figure()
  if filtered_tpr and filtered_fpr: # Only plot if there's data to plot
    fig.add_trace(go.Scatter(x=FPR, y=TPR, mode='lines', line_shape='hv'))
    # find two points where threshold is
    fig.add_trace(go.Scatter(x=[thresh_pt_x], y=[thresh_pt_y], mode='markers', marker=dict(color='orange', size=10, symbol='circle')))

  return fig


def bisect_population_w_threshold(roc_data, threshold_value):
    index = bisect.bisect_left(roc_data['population_data'], threshold_value, key=lambda x: x[0])
    if index >= len(roc_data['population_data']):
        index = len(roc_data['population_data']) - 1
    if index < 0:
        index = 0
    return index

def gen_roc_table(roc_data, threshold_value, norm_params):
    roc_table_labels = [['TP','FN','FP','TN'],
                        ['sensitivity (TPR)','miss rate (FNR)','prob. of false alarm (FPR)','specifity (TNR)'],
                        ['unkn. as pos.','unkn. as neg.','accuracy','z-score']]
    if not roc_data or not roc_data.get('population_data'):
        # Return an empty figure or a figure with a message if data is not available
        return roc_table_labels, [[None,None,None,None],[None,None,None,None],[None,None,None,None]]

    i = bisect_population_w_threshold(roc_data, threshold_value)
    # Check if any of the values are None before trying to access them
    tp_val = roc_data['TP'][i] if roc_data['TP'] else None
    fp_val = roc_data['FP'][i] if roc_data['FP'] else None
    tn_val = roc_data['TN'][i] if roc_data['TN'] else None
    fn_val = roc_data['FN'][i] if roc_data['FN'] else None
    up_val = roc_data['UP'][i] if roc_data['UP'] else None
    un_val = roc_data['UN'][i] if roc_data['UN'] else None
    tpr_val = round(roc_data['TPR'][i], 2) if roc_data['TPR'] and roc_data['TPR'][i] is not None else None
    fpr_val = round(roc_data['FPR'][i], 2) if roc_data['FPR'] and roc_data['FPR'][i] is not None else None
    tnr_val = round(roc_data['TNR'][i], 2) if roc_data['TNR'] and roc_data['TNR'][i] is not None else None
    fnr_val = round(roc_data['FNR'][i], 2) if roc_data['FNR'] and roc_data['FNR'][i] is not None else None
    acc_val = round(roc_data['ACC'][i], 2) if roc_data['ACC'] and roc_data['ACC'][i] is not None else None

    mean = norm_params['loc']
    std = norm_params['scale']
    z_score = (threshold_value - mean) / std
    z_score = round(z_score, 2)

    roc_table_header = ['TP', 'FN', 'FP', 'TN']
    roc_table = [[tp_val, 'sensitivity (TPR)', tpr_val, 'unkn. as pos.', up_val],
                 [fn_val, 'miss rate (FNR)', fnr_val, 'unkn. as neg.', un_val],
                 [fp_val, 'prob. of false alarm (FPR)', fpr_val, 'accuracy', acc_val],
                 [tn_val, 'specificity (TNR)', tnr_val, 'z-score', z_score]]
    return roc_table, roc_table_header, i

