import numpy as np
from scipy import stats

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

