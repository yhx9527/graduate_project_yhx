import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State
from dash.exceptions import PreventUpdate
from celery_app.tasks import addAnalyseCount
from app import app
from .common import header, info_analyse
import dash
from store import global_forUserWCdata, global_user_data, cache
from functools import reduce
import os
import time
from diggout import genLdaHtml, genCloudImg
from diggout.user_similar import get_similar
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame
import pickle
import visdcc
import threading

d = os.path.dirname(__file__)


layout = html.Div([
    header.layout,
    html.Div([
        html.Div('', className='tile is-3'),
        html.Div([
            html.Div([
                dcc.Input(className='input', type='text', placeholder='请输入抖音用户名或用户id', id='analyseInput'),
                # html.Datalist([
                #     html.Option(value='广东夫妇')
                # ],id='suggest'),
            ], className='control is-expanded'),
            html.Div([
                html.Button('开始分析', id='startAnalyse', className='button is-primary'),
            ], className='control')
        ], className='field has-addons has-addons-centered tile is-6 search_input'),
    ], className='tile is-ancestor', style={'marginTop': '4rem', 'marginBottom': '2rem'}),
    html.Div([
        html.P([
            html.Span([
                html.Span(id='similarPanel_title', className='similarPanel_title'),
                html.Small('|相似用户')
            ], style={'display': 'flex', 'alignItems': 'center'}),
            html.Button(className='delete', id='similarPanel_delete'),
        ], className='panel-heading simPanel_title'),
        dcc.Loading([
            html.Div([
            ], id='similarPanel_content', className='simPanel_content'),
        ],id='similarPanel_loading'),

    ],className='panel is-warning simPanel media-simPanel', id='similarPanel', style={'display': 'none'}),
    html.Div(id='hiddenParams', style={'display': 'none'}),
    dcc.Loading([
    ],id='waitUserWC',type='cube', style={'height': '60vh', 'marginTop': '10rem'}),
    info_analyse.layout,
    html.Div([
        '未查询到用户，请先进行',
        html.A('爬取', href='/crawling'),
    ], className='notification is-danger is-light nosearch', id='nosearch', style={'display': 'none'}),
    html.Div([
        html.Div(id='analyseResult1'),
        html.Div(id='analyseResult2'),
        html.Div(id='analyseResult3'),
        html.Div(id='analyseResult4'),
        html.Div(id='analyseResult5'),
    ],id='analyseResult'),
    visdcc.Run_js(id='similarScript'),
    visdcc.Run_js(id='addlistenScript'),
])
@app.callback(Output('info_analyse', 'style'),
              [Input('startAnalyse', 'n_clicks')],
              )
def hiddenInfo(n):
    return {'display': 'none'}


@app.callback([Output('addlistenScript', 'run'),
                Output('similarPanel', 'style')],
              [Input('similarPanel_delete', 'n_clicks'), Input('searchSimalar', 'n_clicks')],
              )
def searchSimilar(n, n1):
    print('看看', n, n1)
    origin = dash.callback_context.triggered[0].get('prop_id')
    appear = None
    hidden = {'display': 'none'}
    script = ''
    if origin == 'searchSimalar.n_clicks':
        # script = '''
        #             addSimilarEvent();
        #         '''
        return script, appear
    elif origin == 'similarPanel_delete.n_clicks':
        return script, hidden

@cache.memoize(timeout=3600)
def getSimilarPanel(uid):
    results = user_get_similar(uid)
    temp = None
    if len(results) > 0:
        temp = html.Div(children=[
            html.A([
                html.Span('Top{}.'.format(index + 1), style={'marginRight': 'auto'}),
                html.Strong(user['nickname'], style={'textOverflow': 'ellipsis', 'overflow': 'hidden', 'width': '50%',
                                                     'whiteSpace': 'nowrap'}),
                html.Small('相似度: {}'.format(round(float(user['degree']), 3)), style={'marginLeft': 'auto'}),
            ], className='panel-block', **{'data-uid': user['user_id'], 'data-nickname': user['nickname']})
            for index, user in enumerate(results)
        ])
    return temp

@app.callback([Output('similarPanel_title', 'children'),
               Output('similarPanel_content', 'children'),],
              [Input('similarPanel', 'style')],
              [State('recordUserId', 'children'),
               State('recordNickName', 'children')]
              )
def startSearchSimilar(st, uid, nickname):
    if (not st) and uid:
        # results = user_get_similar(uid)
        # temp = '未找到相似用户'
        # if len(results)>0:
        #     temp = html.Div(children=[
        #         html.A([
        #             html.Span('Top{}.'.format(index + 1), style={'marginRight': 'auto'}),
        #             html.Strong(user['nickname'], style={'textOverflow': 'ellipsis', 'overflow': 'hidden', 'width': '50%', 'whiteSpace': 'nowrap'}),
        #             html.Small('相似度: {}'.format(round(float(user['degree']), 3)), style={'marginLeft': 'auto'}),
        #         ], className='panel-block')
        #         for index, user in enumerate(results)
        #     ])
        # print(temp)
        # return temp
        fig = getSimilarPanel(uid)
        if fig:
            return nickname, fig
        else:
            return nickname, '未找到相似用户'
    return '', ''

# @app.callback(Output('similarScript', 'run'),
#               [Input('searchSimalar', 'n_clicks')],
#               [State('recordUserId', 'children')]
#               )
# def startScript(n, uid):
#     script = ''
#     if uid:
#         task = task_get_similar.apply_async(args=[uid])
#
#         script = '''
#             showSimilarDetail('{}');
#         '''.format(task.id)
#         print('执行脚本', uid, script)
#     return script


@app.callback(Output('analyseInput', 'value'),
              [Input('hiddenParams', 'children'),
               Input('example-analyse1', 'children'),
               Input('example-analyse2', 'children'),
               Input('example-analyse1', 'n_clicks'),
               Input('example-analyse2', 'n_clicks')]
              )
def setAnalyseInput(params, k1, k2, n1, n2):
    origin = dash.callback_context.triggered[0].get('prop_id')
    if origin =='hiddenParams.children':
        print('$$$$$$', params)
        par = doParams(params)
        if par:
            uid = par.get('uid')
            return uid
    elif origin == 'example-analyse1.n_clicks':
        return k1
    elif origin == 'example-analyse2.n_clicks':
        return k2
    return dash.no_update
def genTongji(duration_posts, pie_posts):

    fig_pie = px.pie(pie_posts, values='count', names='tag', title='视频获赞分类', height=600)

    fig_bar = go.Figure(data=[go.Bar(x=duration_posts['tag'], y=duration_posts['count'],
                                 text=duration_posts['count'], textposition='auto',
                                 )])

    fig_bar.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=1, opacity=0.6)
    fig_bar.update_layout(title_text='视频时长统计', xaxis={'title': '时长'},
                      yaxis={'title': '数量'})

    fig_tongji = html.Div([
        html.Div([
            html.Div([
                dcc.Graph(figure=fig_bar, style={'height': '50vh'}),
            ], className='tile is-child box'),
        ], className='tile is-parent'),
        html.Div([
            html.Div([
                dcc.Graph(figure = fig_pie, style={'height': '50vh'})
            ], className='tile is-child box'),
        ], className='tile is-parent'),
    ], className='tile is-ancestor', style={'margin': '0 1rem'}),
    # return dcc.Graph(style={'height': '600px'})
    return fig_tongji
def genResult(src, user, iframe, **kwargs):
    tabs = html.Div([
        html.Div('', className='tile is-3'),
        html.Div([
            html.Div([
                html.Ul([
                    html.Li([
                        html.A('视频词云'),
                    ], className='is-active', id='tabsCloud', ),
                    html.Li([
                        html.A('LDA主题分析'),
                    ], id='tabsLDA'),
                    html.Li([
                        html.A('文章统计', ),
                    ], id='tabsOther'),
                ])
            ], className='tabs is-centered is-medium', style={'width': '100%'}),
        ], className='tile is-6')
    ], className='tile is-ancestor', style={'marginBottom': '1rem'})
    # tabs = html.Div([
    #             html.Ul([
    #                 html.Li([
    #                     html.A('视频词云'),
    #                 ], className='is-active', id='tabsCloud', ),
    #                 html.Li([
    #                     html.A('LDA主题分析'),
    #                 ], id='tabsLDA'),
    #                 html.Li([
    #                     html.A('文章统计', ),
    #                 ],id='tabsOther'),
    #             ])
    #         ], className='tabs is-centered is-medium', style={'margin': '0 25% 2rem 25%'}),
    tabsColud = html.Div([
                html.Img(src=src, className='', style={'max-width': '600px', 'min-width':'300px'}),
            ], className='wcImg', id='userWC'),
    tabsLDA = html.Div([
        html.Iframe(src=iframe, style={'height': '130vh', 'width': '100%', 'overflow': 'hidden'}),
    ], className='wcImg', id='userLDA', style={'display': 'none'}),
    tabsOther = html.Div([
        html.Div(genTongji(**kwargs), style={'width': '100%'}),
    ], className='', id='userOther', style={'display': 'none', 'width': '100%'}),
    userInfo = html.Div([
        html.Div('', className='tile is-3'),
        html.Div([
            html.Div([
                html.Article([
                    html.Figure([
                        html.P([
                            html.Img(src=user.avatar)
                        ], className='image is-64x64')
                    ], className='media-left'),
                    html.Div([
                        html.Div([
                            html.P([
                                html.Strong(user.nickname, id='recordNickName'),
                                html.Small(' | ' + user.user_id, style={'whiteSpace': 'pre'}),
                                html.P(user.user_id, style={'display': 'none'}, id='recordUserId'),
                                html.Br(),
                                html.Div(user.signature)
                            ])
                        ], className='content'),
                        html.Div([
                            html.Div([
                                html.Div([
                                    html.Span('作品: ', style={'whiteSpace': 'pre'}),
                                    html.Span(format(user.aweme_count, ',') if user.aweme_count else '未知'),
                                ], className='level-item'),
                                html.Div([
                                    html.Span('获赞: ', style={'whiteSpace': 'pre'}),
                                    html.Span(format(user.total_favorited, ',') if user.total_favorited else '未知'),
                                ], className='level-item'),
                                html.Div([
                                    html.Span('粉丝: ', style={'whiteSpace': 'pre'}),
                                    html.Span(format(user.aweme_fans, ',') if user.aweme_fans else '未知'),
                                ], className='level-item'),
                            ], className='level-left')
                        ], className='level is-mobile')
                    ], className='media-content'),
                    html.Div([
                        html.Button('相似用户', className='button is-primary is-outlined is-small', id='searchSimalar')
                    ], className='media-right')
                ], className='media'),
            ], className='box', style={'width': '100%'}),
        ], className='tile is-6 search_input')
    ], className='tile is-ancestor', style={'marginBottom': '1rem'}),

    fig = [userInfo, tabs, tabsColud, tabsLDA, tabsOther]
    return fig

@app.callback([Output('analyseResult', 'style'), Output('startAnalyse', 'disabled')],
              [Input('startAnalyse', 'n_clicks'), Input('waitUserWC', 'className')],
              )
def setUserWC(n1, n2):
    origin = dash.callback_context.triggered[0].get('prop_id')
    print('@@@@@', origin)
    hidden = {'display': 'none'}
    appear = None
    if origin == 'startAnalyse.n_clicks':
        return hidden, True
    else:
        return appear, False


@app.callback([Output('waitUserWC', 'className'),
               Output('nosearch', 'style'),
               Output('analyseResult1', 'children'),
               Output('analyseResult2', 'children'),
               Output('analyseResult3', 'children'),
               Output('analyseResult4', 'children'),
               Output('analyseResult5', 'children'),
               ],
              [Input('startAnalyse', 'n_clicks')],
              [State('analyseInput', 'value')]
              )
def setUserWC(n, keyword):
    # return dash.no_update, dash.no_update
    print('分析关键字', keyword)
    hidden = {'display': 'none'}
    appear = None
    try:
        uidData = global_forUserWCdata(keyword)

        if not uidData:
            return ['',appear]+['' for i in range(5)]
        uid = uidData['uid']
        src = os.path.join('/assets', 'img', '{}.jpg'.format(uid))
        htmlSrc = os.path.join('/assets', 'html', '{}.html'.format(uid))

        temp = os.path.join(d, '..', 'assets', 'img', '{}.jpg'.format(uid))
        tempHtml = os.path.join(d, '..', 'assets', 'html', '{}.html'.format(uid))

        flagImg = os.path.isfile(temp)
        flagHtml = os.path.isfile(tempHtml)
        print('检查图片和html文件', flagImg, flagHtml)
        task = addAnalyseCount.apply_async(args=[uid])

        if flagImg and flagHtml:
            fig = genResult(src=src, user=uidData['user'], iframe=htmlSrc, duration_posts=uidData['duration_posts'], pie_posts = uidData['pie_posts'])
            return ['', hidden] + fig
        elif flagImg:
            t1 = threading.Thread(target=genLdaHtml, args=(uidData['data'], uid))
            t1.start()
            t1.join()
            # genLdaHtml(uidData['data'], uid)
            fig = genResult(src=src, user=uidData['user'], iframe=htmlSrc, duration_posts=uidData['duration_posts'], pie_posts = uidData['pie_posts'])
            return ['', hidden]+ fig
        elif flagHtml:
            t2 = threading.Thread(target=genCloudImg, args=(uidData['data'], uidData['imageUrl'], uid))
            t2.start()
            t2.join()
            # genCloudImg(uidData['data'], uidData['imageUrl'], uid)
            fig = genResult(src=src, user=uidData['user'], iframe=htmlSrc, duration_posts=uidData['duration_posts'], pie_posts = uidData['pie_posts'])
            return ['', hidden]+ fig
        else:
            t1 = threading.Thread(target=genLdaHtml, args=(uidData['data'], uid))
            t2 = threading.Thread(target=genCloudImg, args=(uidData['data'], uidData['imageUrl'], uid))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            # genCloudImg(uidData['data'], uidData['imageUrl'], uid)
            # genLdaHtml(uidData['data'], uid)
            fig = genResult(src=src, user=uidData['user'], iframe=htmlSrc, duration_posts=uidData['duration_posts'], pie_posts = uidData['pie_posts'])
            return ['', hidden] + fig
    except Exception as e:
        print('分析错误', e)
        return [dash.no_update for i in range(7)]


#
# @app.callback(Output('waitUserWC', 'loading_state'),
#               [Input('startAnalyse', 'n_clicks'), Input('waitUserWC', 'style'), Input('analyseResult', 'style')],
#               )
# def setUserWC(n1, n2, style):
#     origin = dash.callback_context.triggered[0].get('prop_id')
#     print('$$$$', dash.callback_context.triggered, origin, style)
#     if style:
#         return dict(is_loading=False)
#     if origin == 'startAnalyse.n_clicks':
#         print('检查style', style)
#         return dict(is_loading=True)
#     elif origin == 'waitUserWC.style':
#         return dict(is_loading=False)
#     raise PreventUpdate

@app.callback([Output('userWC', 'style'), Output('userLDA', 'style'), Output('userOther', 'style'),
               Output('tabsCloud', 'className'), Output('tabsLDA', 'className'), Output('tabsOther', 'className')],
              [Input('tabsCloud', 'n_clicks'), Input('tabsLDA', 'n_clicks'), Input('tabsOther', 'n_clicks')],
              )
def changeTabs(n1, n2, n3):
    origin = dash.callback_context.triggered[0].get('prop_id')
    hidden = {'display': 'none'}
    appear = {}
    active = 'is-active'
    inactive = ''
    if origin == 'tabsCloud.n_clicks':
        return appear, hidden, hidden, active, inactive, inactive
    elif origin == 'tabsLDA.n_clicks':
        return hidden, appear, hidden, inactive, active, inactive
    elif origin == 'tabsOther.n_clicks':
        return hidden, hidden, appear, inactive, inactive, active
    raise PreventUpdate

def doParams(params):
    if not params:
        return None
    arr = params[1:].split('&')
    def func(acc, cur):
        temp = cur.split('=')
        acc[temp[0]] = temp[1]
        return acc
    y = reduce(func, arr, {})
    return y

def user_get_similar(uid, threshold=0):
    print('正在加载数据...', uid)
    data = global_forUserWCdata(uid)
    user_posts = data.get('similar_posts', None)
    result = []
    if len(user_posts)>0:
        item = get_similar(user_posts)
        print(item)
        sims = [(uid1, degree) for uid1, degree in item if (degree > threshold) and (str(uid1) != str(uid))]

        for sim in sims:
            user = global_user_data(sim[0])
            if user:
                xx = dict(
                    nickname=user.nickname,
                    user_id=user.user_id,
                    degree=sim[1]
                )
                print('相似用户', xx)
                result.append(xx)

    return result