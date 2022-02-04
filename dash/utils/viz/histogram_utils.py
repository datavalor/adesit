import plotly.graph_objects as go
import numpy as np

from utils.viz.figure_utils import convert_from_numpy_edges
from constants import *

def compute_1d_histogram(
    session_infos, 
    columnn_name, 
    resolution, 
    minmax=None,
    data_key = 'df',
    df = None
):  
    attr = session_infos['user_columns'][columnn_name]
    if df is None: df=session_infos['data'][data_key]

    if attr.is_categorical():
        bins = attr.sorted_classes
        unique_values, count = np.unique(df[columnn_name], return_counts=True)
        count_dict = {}
        for i in range(len(unique_values)): count_dict[unique_values[i]]=count[i]
        bins_counts = [count_dict.get(label,0) for label in bins]
    else:
        if minmax is None: min, max = attr.get_minmax()
        else: min, max = minmax
        data = df[columnn_name]
        if attr.is_datetime():
            min, max = min.to_datetime64().view("int64"), max.to_datetime64().view("int64")
            data = data.astype("datetime64[ns]").view("int64")
        bins_counts, bins_edges = np.histogram(
            data, 
            bins=resolution,
            range=(min, max)
        )
        bins = convert_from_numpy_edges(bins_edges)
        if attr.is_datetime():
            for i in range(len(bins)):
                bins[i]=pd.Timestamp(bins[i])
    return [bins, bins_counts]

def add_basic_histograms(
    fig, 
    session_infos, 
    column_name,
    resolution,
    minmax=None,
    orientation = 'v',
    add_trace_args = {},
    bar_args = {},
    df=None
):
    bins, bins_counts = compute_1d_histogram(session_infos, column_name, resolution, minmax=minmax, df=df)
    if orientation=='h': bins, bins_counts = bins_counts, bins
    fig.add_trace(
        go.Bar(x=bins, y=bins_counts, marker_color=NON_ANALYSED_COLOR, orientation=orientation, **bar_args), 
        **add_trace_args
    )
    return fig

def add_advanced_histograms(
    fig,
    session_infos,
    column_name, 
    resolution, 
    orientation = 'v',
    add_trace_args = {},
    minmax=None
):
    if minmax is None: minmax=session_infos['user_columns'][column_name].get_minmax()
    bins_free, bins_counts_free = compute_1d_histogram(session_infos, column_name, resolution, minmax=minmax, data_key='df_free')
    bins_prob, bins_counts_prob = compute_1d_histogram(session_infos, column_name, resolution, minmax=minmax, data_key='df_prob')
    
    if orientation=='h': 
        bins_free, bins_counts_free = bins_counts_free, bins_free
        bins_prob, bins_counts_prob = bins_counts_prob, bins_prob

    fig.add_trace(
        go.Bar(x=bins_free, y=bins_counts_free, name='Free tuples', offsetgroup=0, marker_color=FREE_COLOR, orientation=orientation),
        **add_trace_args
    )
    fig.add_trace(
        go.Bar(x=bins_prob, y=bins_counts_prob, name='Involved tuples', offsetgroup=1, marker_color=CE_COLOR, orientation=orientation),
        **add_trace_args
    )

    return fig