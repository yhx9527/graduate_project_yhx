import dash_core_components as dcc
import dash_html_components as html
from store import global_store_rows
from dash.dependencies import Input, Output
from app import app

layout = html.Div([
    html.Div([
        html.P('累计采集', className='title is-size-5', id='display'),
        html.Div([
            html.Div([
                html.Div([
                    html.P('用户数', className='heading is-size-6'),
                    html.P(global_store_rows('users'), className='subtitle has-text-grey-darker')
                ])
            ], className='level-item has-text-centered'),
            html.Div([
                html.Div([
                    html.P('文章数', className='heading is-size-6'),
                    html.P(global_store_rows('posts'), className='subtitle has-text-grey-darker')
                ])
            ], className='level-item has-text-centered'),
            html.Div([
                html.Div([
                    html.P('评论数', className='heading is-size-6'),
                    html.P(global_store_rows('comments'), className='subtitle has-text-grey-darker')
                ])
            ], className='level-item has-text-centered'),
            html.Div([
                html.Div([
                    html.P('累计分析', className='heading is-size-6'),
                    html.P(global_store_rows('urltasks'), className='subtitle has-text-grey-darker')
                ])
            ], className='level-item has-text-centered'),
            html.Div(id='signal_num', style={'display': 'none'},children='')
        ], className='level is-mobile')
    ],className='hero-body', style={'paddingTop': '.5rem'})
], className='hero')
