import dash
from flask import _app_ctx_stack

meta_tags=[
    {
        'name': 'description',
        'content': '面向短视频流量爬取和分析系统(Short video data crawling and analysis)'
    },
    {
        'http-equiv': 'X-UA-Compatible',
        'content': 'IE=edge'
    },
    {
      'name': 'viewport',
      'content': 'width=device-width, initial-scale=1.0'
    }
    ]
# external JavaScript files
external_scripts = [
    # {
    #     'src': 'https://use.fontawesome.com/releases/v5.3.1/js/all.js',
    # }
]

# external CSS stylesheets
external_stylesheets = [
    'https://cdn.jsdelivr.net/npm/bulma@0.8.0/css/bulma.min.css',
    '/assets/font-awesome4/css/font-awesome.min.css'
]

app = dash.Dash(__name__, meta_tags=meta_tags, external_scripts=external_scripts, external_stylesheets=external_stylesheets)
server = app.server
app.config.suppress_callback_exceptions = True

# @server.teardown_appcontext
# def close_database_connection(error=None):
#     con = getattr(_app_ctx_stack, 'db', None)
#     if con:
#         con.close()