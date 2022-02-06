import dash_bootstrap_components as dbc
from dash import html

from constants import *

def render():
    return [
        html.Div([],
            id="attrs-hist-div",
            style={
                'overflowX': 'hidden',
                'overflowY': 'auto',
                'height': '100%',
                'marginLeft' : '1%', 
                'marginRight' : '1%',
            },
        )
    ]