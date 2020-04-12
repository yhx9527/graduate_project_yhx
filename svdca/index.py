import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sys
import os
cur_file_path = os.path.dirname(__file__)
sys.path.append(cur_file_path)
from app import app, server
import store
import api
from pages import home, results, crawling, analysing, about
import dash

def server_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
        html.Div(id='signal', style={'display': 'none'})
    ])

app.layout = server_layout


@app.callback([Output('page-content', 'children'),
               Output('nav1', 'className'),
                Output('nav2', 'className'),
                Output('nav3', 'className'),
               Output('hiddenParams', 'children')],
              [Input('url', 'pathname'), ],
              [State('url', 'search')])
def display_page(pathname, search):
    # origin = dash.callback_context.triggered[0].get('prop_id')
    active = 'navbar-item is-active has-text-info is-size-3'
    if pathname == '/':
        return home.layout, active, dash.no_update, dash.no_update, dash.no_update
    elif pathname == '/results':
        return results.layout, dash.no_update, active, dash.no_update, dash.no_update
    elif pathname == '/crawling':
        return crawling.layout, dash.no_update, dash.no_update, active, dash.no_update
    elif pathname == '/analysing':
        return analysing.layout, dash.no_update, dash.no_update, dash.no_update, search
    else:
        return home.layout, active, dash.no_update, dash.no_update,dash.no_update



if __name__ == '__main__':
    app.run_server(debug=False, port=8051)
    app.enable_dev_tools(dev_tools_hot_reload=False)