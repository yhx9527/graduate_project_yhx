import dash_core_components as dcc
import dash_html_components as html

nav_init= 'navbar-item'
# layout = html.Div([
#     html.Div([
#         html.Div([
#             html.Div('SVDCA', className="title is-1"),
#             html.Div('Short video data crawling and analysis', className="subtitle"),
#         ], className="navbar-item tile is-vertical"),
#         html.A([
#             html.Span(**{'aria-hidden': 'true'}),
#             html.Span(**{'aria-hidden': 'true'}),
#             html.Span(**{'aria-hidden': 'true'}),
#         ], className="navbar-burger burger", **{'data-target': 'navMenu'}),
#     ], className="navbar-brand"),
#     html.Div([
#         dcc.Link('首页', href='/', className=nav_init, id='nav1'),
#         dcc.Link('数据分析', href='/results', className=nav_init, id='nav2'),
#         dcc.Link('在线爬取', href='/crawling', className=nav_init, id='nav3'),
#     ], className="navbar-menu navbar-start", id="navMenu"),
#
# ], className="navbar is-spaced add_shadow")

# html.Div([
#     html.Div([
#         html.Div('SVDCA', className="level-item has-text-weight-medium is-size-5"),
#         html.Div('|  yhx', className="level-item has-text-weight-medium is-size-6")
#     ], className="level-left", style={'alignSelf': 'baseline'}),
#     dcc.Link([
#         html.Div([
#                 html.Div('Short video data crawling and analysis', className="title is-3"),
#                 html.Div('Data OverView', className='subtitle is-4')
#             ], className="has-text-centered"),
#     ],  href='/'),
#     html.Div([
#         html.A('用户分析', href='/results', className="button is-light",),
#         dcc.Link('在线爬取', href='/crawling', className="button"),
#     ], className='level-right buttons'),
#
# ], className="level is-mobile add_shadow", style={'padding': '1rem'})

layout = html.Div([
    html.Div([
        html.Div([
            html.Div('SVDCA |', className="has-text-weight-medium is-size-5"),
            html.Div(' yhx', className="has-text-weight-medium is-size-6", style={'whiteSpace': 'pre'})
        ], className='level')
    ], className="tile is-3", style={'alignSelf': 'baseline'}),
    dcc.Link([
        html.Div([
                html.Div('Short video data crawling and analysis', className="title"),
                html.Div('Achievement OverView', className='subtitle')
            ], className="has-text-centered"),
    ],  href='/', className='tile is-6 is-vertical'),
    html.Div([
        html.A('用户分析', href='/analysing', className="button is-light", target='_blank'),
        html.A('在线爬取', href='/crawling', className="button", target='_blank'),
    ], className='tile is-3 buttons', style={'justifyContent': 'flex-end','alignItems': 'center'}),

], className="tile is-ancestor add_shadow", style={'padding': '1.5rem 2rem'})