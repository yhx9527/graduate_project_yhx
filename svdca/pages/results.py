import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from .common import header

layout = html.Div([
    header.layout,
    # html.Div([
    #     html.Div('', className='tile is-3'),
    #     # html.Div([
    #     html.Div([
    #         html.Div([
    #             dcc.Input(className='input', type='text', placeholder='请输入需要分析的抖音用户名', id='analyseInput'),
    #         ], className='control is-expanded'),
    #         html.Div([
    #             html.Button('开始分析', id='startAnalyse', className='button is-primary'),
    #         ], className='control')
    #     ], className='field has-addons has-addons-centered tile is-6'),
    #     # ], className='tile is-8'),
    # ], className='tile is-ancestor', style={'marginTop': '4rem'}),
])