import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from .common import header

layout = html.Div([
    header.layout,
    html.H3('about')
])