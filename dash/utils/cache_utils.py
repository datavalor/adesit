
import pandas as pd
import numpy as np
from sklearn import preprocessing
import logging
logging.basicConfig()

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None 
import base64
import io

import constants
from constants import *
from utils.data_utils import num_or_cat

import pydataset
dataset_names={
    'iris':'iris',
    'housing': 'Housing',
    'diamonds': 'diamonds',
    'kidney': 'kidney'
}

logger=logging.getLogger('adesit_callbacks')
cache = None

default_data = {
    "data_holder": None,
    "graphs": {},
    "thresolds_settings": {},
    "table_data": None,
    "selected_point": {
        "point": None,
        "in_violation_with": []
    }
}

def gen_data_holder(df):
    # Proprocessing dataframe
    df = df.dropna()
    cols_type = {}
    cols_minmax = {}
    cols_ncats = {}
    for c in df.columns:
        if c in ['id', 'Id', 'ID']:
            df = df.drop(columns=c)
        elif num_or_cat(c, df)==CATEGORICAL_COLUMN:
            cols_type[c] = CATEGORICAL_COLUMN
            le = preprocessing.LabelEncoder()
            df[c+SUFFIX_OF_ENCODED_COLS] = le.fit_transform(df[c])
            # print(le.transform(df[c]))
            cols_ncats[c] = {
                "unique_values": sorted(le.classes_),
                "label_encoder": le,
            }
        elif num_or_cat(c, df)==NUMERICAL_COLUMN:
            cols_type[c] = NUMERICAL_COLUMN
            cols_minmax[c] = [df[c].min(), df[c].max()]

    cols = list(cols_type.keys())
    df = df[cols]
    df = df.reset_index(drop=True)
    df.insert(0, ADESIT_INDEX, df.index)

    return {
        "data": df,
        "graph": None,
        "user_columns": cols,
        "user_columns_type": cols_type,
        "num_columns_minmax": cols_minmax,
        "cat_columns_ncats": cols_ncats,
        "X": [],
        "Y": []
    }

def get_data(session_id, pydata=False, clear=False, filename=None, contents=None, copy=None):    
    @cache.memoize()
    def handle_data(session_id):
        if copy is not None: return copy

        if pydata:
            df = pydataset.data(dataset_names[filename])
            if filename=="diamonds": df = df.sample(n=10000)
        elif filename is not None:
            _, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            try:
                if 'csv' in filename:
                    # Assume that the user uploaded a CSV file
                    df = pd.read_csv(
                        io.StringIO(decoded.decode('utf-8')))
                elif 'xls' in filename:
                    # Assume that the user uploaded an excel file
                    df = pd.read_excel(io.BytesIO(decoded))
            except Exception as e:
                logger.error(e)
                return None
            if constants.RESOURCE_LIMITED and (len(df.index)>MAX_N_TUPLES or len(df.columns)>MAX_N_ATTRS): 
                return None
        else:
            return None

        final_data = default_data
        final_data["data_holder"]=gen_data_holder(df)
        return final_data

    if clear: 
        cache.delete_memoized(handle_data, session_id)
        return None
    else:
        return handle_data(session_id)

def clear_session(session_id):
    get_data(session_id, clear=True)

def overwriters(name):
    def overwrite(session_id, data=default_data[name]):
        session_data=get_data(session_id)
        session_data[name]=data
        clear_session(session_id)
        get_data(session_id, copy=session_data)
    return overwrite

for k in default_data:
    exec(f"overwrite_session_{k}=overwriters('{k}')")