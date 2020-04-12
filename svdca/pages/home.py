import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from .common import header,display
from datetime import datetime as dt
from controls import TIMESPAN,WEEK,CLOCK
import pandas as pd
import copy
from store import dataset_posts, get_duration_posts_home, get_pie_posts_home, get_dataset_posts, get_dataset_users, get_sunburt_users
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import datetime
import numpy as np
import plotly.express as px
from config import MAPBOX_TOKEN
import dash_daq as daq

mindate = dataset_posts.index.min()
maxdate = dataset_posts.index.max()

df = px.data.election()
df['district_id'] = df.index

layout = html.Div([
    header.layout,
    display.layout,
    html.Div(id='homeSignal', children='homeSignal', style={'display': 'none'}),
    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.P('时间单位:'),
                    dcc.Dropdown(
                            id="time-dropdown",
                            options=[{'label':key, 'value': value} for key,value in TIMESPAN.items()],
                            value='MS',
                            style={'width': '10rem'}
                        ),
                    html.P('日期范围:'),
                    dcc.DatePickerRange(
                        id='my-date-picker-range',
                        min_date_allowed=mindate,
                        max_date_allowed=maxdate,
                        start_date=mindate,
                        end_date=maxdate,
                        className='',
                        style={'width': '20rem'}
                    ),
                ], className='level'),

            ], className='tile is-child box'),
            html.Div([
                dcc.Graph(id='analyse_publish', className='tile is-12'),
            ], className='tile is-child box'),
        ], className='tile is-6 is-vertical is-parent'),
        html.Div([
            html.Div([
                dcc.Graph(id='analyse_count', className='tile is-12'),
            ], className='tile is-child box'),
        ], className='tile is-6 is-parent'),
    ], className='tile is-ancestor', style={'margin': '0 1rem'}),
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='analyse_heat', className='tile is-12'),
            ], className='tile is-child box'),
        ], className='tile is-parent is-8'),
        html.Div([
            html.Div([
                dcc.Graph(id='duration_bar'),
            ], className='tile is-child box')
        ], className='tile is-parent is-4'),
    ], className='tile is-ancestor', style={'margin': '0 1rem'}),
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='analyse_map', className='tile is-12'),
            ], className='tile is-child box'),
        ], className='tile is-parent'),
        html.Div([
            html.Div([
                # daq.ToggleSwitch(
                #     id='daq-heatmap',
                #     label=['点赞量', '粉丝量'],
                #     style={'width': '180px', 'margin': 'auto'},
                #     value=False,
                #     className='tile is-child'
                # ),
                dcc.Dropdown(
                    id="heatmap-dropdown",
                    options=[{'label':key, 'value': value} for key, value in [('视频数量',1), ('用户点赞量',2), ('用户粉丝量',3)]],
                    value=1,
                    style={'width': '10rem'}
                ),
                    dcc.Graph(id='analyse_heatmap', className='tile is-child is-12'),
            ], className='tile is-parent box is-vertical'),
        ], className='tile is-parent'),
    ], className='tile is-ancestor', style={'margin': '0 1rem'}),
    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='analyse_user_sunburst'),
            ], className='tile is-child box'),
        ], className='tile is-parent'),
        html.Div([
            html.Div([
                dcc.Graph(id='analyse_post_pie')
            ], className='tile is-child box'),
        ], className='tile is-parent'),
    ], className='tile is-ancestor', style={'margin': '0 1rem'}),
])


@app.callback(Output('analyse_publish', 'figure'),
              [Input('time-dropdown', 'value'),
               Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),])
def update_graph_analyse_publish(elem, start_date, end_date):
    dataset_posts = get_dataset_posts()
    temp = dataset_posts[(dataset_posts.index>=start_date) & (dataset_posts.index<=end_date)]
    temp = temp.resample(elem).sum()
    obj = {
        "data": [{
            "type": "bar",
            "x": temp.index,
            'y': temp['num'],
            'text': temp['num'],
            "textposition": "auto",
        }],
        "layout": dict(
            title={"text": "视频发布数量"},
            xaxis={'title': '时间'},
            yaxis={'title': '个数'},
            hovermode="closest",
        )
    }
    return obj

@app.callback(Output('analyse_count', 'figure'),
              [Input('time-dropdown', 'value'),
               Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),])
def update_graph_analyse_count(elem, start_date, end_date):
    dataset_posts = get_dataset_posts()
    temp = dataset_posts[(dataset_posts.index>=start_date) & (dataset_posts.index<=end_date)]
    temp = temp.resample(elem).sum()
    fig= make_subplots(specs=[[{"secondary_y": True}]], x_title='时间', y_title='数量', row_titles=[])
    fig.add_trace(
        go.Scatter(x=temp.index, y=temp['digg_count'], name="点赞量"),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(x=temp.index, y=temp['comment_count'], name="评论量"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=temp.index, y=temp['download_count'], name="下载量"),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=temp.index, y=temp['share_count'], name="分享量"),
        secondary_y=False,
    )
    fig.update_layout(title_text='视频数据量时间趋势',)
    return fig



x_axis = [datetime.time(i).strftime("%I %p") for i in range(24)]
day_list = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
y_axis = day_list


@app.callback(Output('analyse_heat', 'figure'),
              [Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),])
def update_graph_analyse_heat(start_date, end_date):
    dataset_posts = get_dataset_posts()
    temp = dataset_posts[(dataset_posts.index>=start_date) & (dataset_posts.index<=end_date)]
    z = np.zeros((7, 24))

    for ind_y, day in enumerate(y_axis):
        filtered_day = temp[temp["Days of Wk"] == day]
        for ind_x, x_val in enumerate(x_axis):
            sum_of_record = filtered_day[filtered_day["Check-In Hour"] == x_val]['num'].sum()
            z[ind_y][ind_x] = sum_of_record
    hovertemplate = "<b> %{y}  %{x} <br><br> %{z}个视频"

    data = [
        dict(
            x=CLOCK,
            y=WEEK,
            z=z,
            type="heatmap",
            name="",
            hovertemplate=hovertemplate,
            colorscale=[[0, "#caf3ff"], [1, "#005bdf"]],
        )
    ]

    layout = dict(
        # margin=dict(l=70, b=50, t=50, r=50),
        # modebar={"orientation": "v"},
        font=dict(family="Open Sans"),
        # annotations=annotations,
        # shapes=shapes,
        xaxis=dict(
            side="top",
            ticks="",
            ticklen=2,
            tickfont=dict(family="sans-serif"),
            tickcolor="#ffffff",
        ),
        yaxis=dict(
            side="left", ticks="", tickfont=dict(family="sans-serif"), ticksuffix=" "
        ),
        hovermode="closest",
        showlegend=False,
        title=dict(text="·抖音大V·时间上的发视频规律")
    )
    return {"data": data, "layout": layout}

@app.callback(Output('analyse_map', 'figure'),
              [Input('homeSignal', 'children'),])
def update_graph_analyse_map(value):
    df = get_dataset_users()
    df['text'] = df['city'] + '<br>' + (df['count']).astype(str) + ' 人'
    limits = [(0, 5), (5, 10), (10, 50), (50, 100), (100, 250)]
    colors = ["royalblue", "crimson", "lightseagreen", "orange", "lightgrey"]
    fig = go.Figure()
    scale = 20
    for i in range(len(limits)):
        lim = limits[i]
        df_sub = df[(df['count']>=lim[0]) & (df['count']<lim[1])]
        fig.add_trace(go.Scattermapbox(
            lon=df_sub['lon'],
            lat=df_sub['lat'],
            text=df_sub['text'],
            marker=dict(
                size=df_sub['count']*scale,
                color=colors[i],
                # line_color='rgb(40,40,40)',
                # line_width=0.5,
                sizemode='area'
            ),
            name='{0} - {1}'.format(lim[0], lim[1])))
    # fig = px.scatter_mapbox(dataset_users,
    #                         lat="lat", lon="lon", hover_name="city",
    #                         zoom=3, center={'lat': 36.3043, 'lon': 103.5901},
    #                         height=600,
    #                         width=750,
    #                         )
    fig.update_layout(
        title_text='用户分布图',
        # showlegend=True,
        # height=600, width=750,
        mapbox= dict(zoom=3, center={'lat': 36.3043, 'lon': 103.5901},)
    )
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=MAPBOX_TOKEN,)
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return fig
@app.callback(Output('analyse_heatmap', 'figure'),
              [Input('heatmap-dropdown', 'value'),])
def update_graph_analyse_heatmap(value):
    df = get_dataset_users()
    scale = 1e7
    if value==1:
        temp = df['aweme_count']
        statement = '视频数'
    elif value ==2:
        temp = df['total_favorited']/scale
        statement = '千万点赞量'
    else:
        temp = df['mplatform_followers_count'] / scale
        statement = '千万粉丝量'
    df['text'] = df['city'] + '<br>' + (temp).astype(str)

    fig = go.Figure(go.Densitymapbox(
        lon=df['lon'],
        lat=df['lat'],
        hovertemplate=df['text'],
        z=temp,
        colorbar_title=statement,
        name=statement
        # colorscale=[[0, "#ff0000"], [1, "#ffff00"]],
    ))
    fig.update_layout(
        # title_text='用户视频点赞/粉丝 热力图',
        # showlegend=True,
        # height=600, width=750,
        mapbox= dict(zoom=3, center={'lat': 36.3043, 'lon': 103.5901})
    )
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=MAPBOX_TOKEN)
    fig.update_layout(margin={"r": 0, "t": 20, "l": 0, "b": 0})
    return fig

@app.callback(Output('analyse_user_sunburst', 'figure'),
              [Input('homeSignal', 'children'),])
def update_graph_analyse_user_sunburst(value):
    sunburt_users = get_sunburt_users()
    fig = px.sunburst(sunburt_users, path=['title', 'tag', 'nickname'], values='count', title='用户粉丝量级别分类')

    return fig

@app.callback(Output('analyse_post_pie', 'figure'),
              [Input('homeSignal', 'children'),])
def update_graph_analyse_post_pie(value):
    pie_posts = get_pie_posts_home()
    fig = px.pie(pie_posts, values='count', names='tag', title='视频获赞分类')
    return fig

@app.callback(Output('duration_bar', 'figure'),
              [Input('homeSignal', 'children'),])
def update_graph_duration_bar(value):
    duration_posts = get_duration_posts_home()
    fig = go.Figure(data=[go.Bar(x=duration_posts['tag'], y=duration_posts['count'],
                                 text=duration_posts['count'],textposition='auto',
                                 )])
    # Customize aspect
    fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=1, opacity=0.6)
    fig.update_layout(title_text='视频时长统计',xaxis={'title': '时长'},
            yaxis={'title': '数量'})
    return fig
    # pass
    # country = ['Switzerland (2011)', 'Switzerland (2011)', 'Switzerland (2011)']
    # voting_pop = [40, 45.7, 52, 53.6, 54.1, 54.2, 54.5, 54.7, 55.1, 56.6]
    # reg_voters = [49.1, 42, 52.7, 84.3, 51.7, 61.1, 55.3, 64.2, 91.1, 58.9]
    # scale = 1000
    # fig = go.Figure()
    #
    # fig.add_trace(go.Scatter(
    #     x=duration_posts['duration']/scale,
    #     y=duration_posts['title'],
    #     name='Percent of estimated voting age population',
    #     marker=dict(
    #         color='rgba(156, 165, 196, 0.95)',
    #         line_color='rgba(156, 165, 196, 1.0)',
    #     )
    # ))
    #
    # fig.update_traces(mode='markers', marker=dict(line_width=1, symbol='circle', size=5))
    #
    # fig.update_layout(
    #     title="Votes cast for ten lowest voting age population in OECD countries",
    #     xaxis=dict(
    #         showgrid=False,
    #         showline=True,
    #         linecolor='rgb(102, 102, 102)',
    #         tickfont_color='rgb(102, 102, 102)',
    #         showticklabels=True,
    #         dtick=15,
    #         ticks='outside',
    #         tickcolor='rgb(102, 102, 102)',
    #     ),
    #     margin=dict(l=140, r=40, b=50, t=80),
    #     legend=dict(
    #         font_size=10,
    #         yanchor='middle',
    #         xanchor='right',
    #     ),
    #     paper_bgcolor='white',
    #     plot_bgcolor='white',
    #     hovermode='closest',
    # )
    # return fig
