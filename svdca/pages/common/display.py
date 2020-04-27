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
                    html.P('xxx', className='subtitle has-text-grey-darker',
                           id='display_users')

                ])
            ], className='level-item has-text-centered'),
            html.Div([
                html.Div([
                    html.P('文章数', className='heading is-size-6'),
                    html.P('xxx', className='subtitle has-text-grey-darker',
                           id='display_posts')
                ])
            ], className='level-item has-text-centered'),
            html.Div([
                html.Div([
                    html.P('评论数', className='heading is-size-6'),
                    html.P('xxx', className='subtitle has-text-grey-darker',
                           id='display_comments')
                ])
            ], className='level-item has-text-centered'),
            html.Div([
                html.Div([
                    html.P('累计分析', className='heading is-size-6'),
                    html.P('xxx', className='subtitle has-text-grey-darker',
                           id='display_urltasks')
                ])
            ], className='level-item has-text-centered'),
            html.Div(id='signal_num', style={'display': 'none'},children='')
        ], className='level is-mobile')
    ],className='hero-body', style={'paddingTop': '.5rem'})
], className='hero')

@app.callback([Output('display_users', 'children'),
               Output('display_posts', 'children'),
               Output('display_comments', 'children'),
               Output('display_urltasks', 'children'),],
              [Input('time-dropdown', 'value')])
def update_display(v):
    a = global_store_rows('users')
    b = global_store_rows('posts')
    c = global_store_rows('comments')
    d = global_store_rows('urltasks')
    return a,b,c,d