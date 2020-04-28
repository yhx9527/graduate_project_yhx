import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from app import app,server
from .common import header, info_crawl
# from douyin_crawler.crawl_post_pt import Douyin, MyRedis
from celery_app.tasks import crawling
from flask import url_for
from hyper import HTTPConnection
from urllib.parse import urlparse
from db.db_models import Urltask
from store import global_uid, global_urltask, delete_global_forUserWCdata
import re
import requests
import visdcc
import time
import dash
import json
import uuid
from os import path, remove
layout = html.Div([
    header.layout,
    dcc.Store(id='sessionStore', storage_type='session'),
    html.Div([
        html.Div('', className='tile is-3'),
        html.Div([
            html.Div([
                dcc.Input(className='input', type='text', placeholder='请输入抖音用户链接', id='crawlInput'),
            ], className='control is-expanded'),
            html.Div([
                html.Button('立即爬取', id='crawlBtn', className='button is-info'),
            ], className='control')
        ], className='field has-addons has-addons-centered tile is-6 search_input'),

    ], className='tile is-ancestor', style={'marginTop': '4rem', 'marginBottom': '2rem'}),
    info_crawl.layout,
    # html.P('正在爬取...', className='has-text-centered'),
    html.Div([
        html.Div('', className='tile is-2'),
        html.Div([
            html.Div([
                html.Div([
                    html.P('爬取任务～', id='crawlingP'),
                    html.A('进入分析', href='/analysing', id='analyseBtn', target='_blank', style={'visibility': 'hidden'},
                           className='button is-link is-inverted is-outlined')
                ],
                    className='message-header'),
                html.Div('', className='message-body', id='crawlShow', style={'overflow': 'scroll', 'height': '60vh'})
            ], className='message is-link', style={'width': '100%'})
        ], className='tile is-8 search_input'),
        ],
    id='showPanel',className='tile is-ancestor',
    style={'display':'none'}),

    visdcc.Run_js(id = 'crawlScript'),
    visdcc.Run_js(id='crawlScript1'),
    dcc.ConfirmDialog(
        id='confirm',
        message='已爬取过该用户，是否重新爬取?'
    ),
    html.Div([
        html.Div('', className='tile is-4'),
        html.Div([
            html.Div([
                html.Header([
                    html.Div('查询结果',id='crawled-title',className='card-header-title')
                ],className='card-header'),
                html.Div([
                    html.Div([
                        html.Div('时间',id='crawledLasttime'),
                        html.Br(),
                        html.Div('次数',id='crawledCount')
                    ],className='content')
                ],className='card-content'),
                html.Footer([
                    html.A('进入分析', href='/analysing', target='_blank', className='card-footer-item', id='analysedBtn')
                ],className='card-footer'),
            ],className='card crawled-display', ),
        ], className='tile is-4 search_input')

    ], className='tile is-ancestor', id='crawledCard', style={'display': 'none'}),

])
@app.callback(Output('info_crawl', 'style'),
              [Input('crawlBtn', 'n_clicks')],
              )
def hiddenInfo(n):
    return {'display': 'none'}

@app.callback(Output('crawlInput', 'value'),
              [Input('example-crawl', 'n_clicks'),Input('example-crawl', 'children')],
              )
def fillInput(n,k):
    origin = dash.callback_context.triggered[0].get('prop_id')
    if origin == 'example-crawl.n_clicks':
        return k
    return dash.no_update

@app.callback([Output('crawlShow', 'children'),
               Output('sessionStore', 'data'), Output('crawlingP', 'children'),
               Output('crawledCard', 'style'),
               Output('crawledLasttime', 'children'),
               Output('crawledCount','children'),
               Output('showPanel', 'style'),
               Output('confirm', 'displayed'),
               Output('crawlBtn', 'disabled'),
               Output('analysedBtn', 'href'),
               Output('analyseBtn', 'href')],
              [Input('crawlBtn', 'n_clicks'), Input('confirm', 'submit_n_clicks'), Input('confirm', 'cancel_n_clicks')],
              [State('crawlInput', 'value')],
              )
def startCrawl(n,yes, no, url):
    print('!!!!!!',dash.callback_context.triggered)
    uid = global_uid(url)
    origin = dash.callback_context.triggered[0].get('prop_id')
    href = '/analysing?uid={}'.format(uid)
    if origin =='confirm.submit_n_clicks':
        print('重新爬取')
        task = crawling.apply_async(args=[url])
        removeAnalyseResult(uid)

        return '', url_for('taskstatus', task_id=task.id), '爬取任务～' + url, \
               {'display': 'none'},'','', \
               {}, False, False, href,href
    elif origin =='confirm.cancel_n_clicks':
        print('显示已爬取的结果')
        # uid = global_uid(url)
        data = global_urltask(uid)
        lasttime = '上次爬取时间：{}'.format(data.update_time)
        num = '共爬取了{}条数据'.format(data.num)
        return dash.no_update, dash.no_update, dash.no_update, \
               {}, lasttime, num, \
               {'display': 'none'}, dash.no_update, False, href, href
    elif origin == 'crawlBtn.n_clicks':
        # uid = global_uid(url)
        if uid:
            data = global_urltask(uid)
            if data:
                return dash.no_update,dash.no_update,dash.no_update,\
                       dash.no_update, dash.no_update,dash.no_update, \
                       dash.no_update, True, False, href, href
            else:
                print('未爬过,开始爬取')
                task = crawling.apply_async(args=[url])
                return '', url_for('taskstatus', task_id=task.id), '爬取任务～'+url, \
                       {'display': 'none'}, '','',\
                       {}, False, False, href, href
    # raise PreventUpdate
    return dash.no_update, dash.no_update, dash.no_update, \
           dash.no_update, dash.no_update, dash.no_update, \
           dash.no_update,dash.no_update, False, href, href


@app.callback(Output('crawlScript', 'run'),
              [Input('sessionStore', 'data')],
              )
def startScript(data):
    script = ''
    if data:
        script = '''
            showCrawlDetail();
        '''
    return script

def getUid(url):
    try:
        arr = urlparse(url)
        headers = {'User-Agent': 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14'}
        connection = HTTPConnection(arr.netloc+':443')
        connection.request('GET', arr.path, headers=headers)
        res = connection.get_response().read().decode('utf-8')
        temp = re.search(r'/(\d+)\?', res)
        print('匹配到', temp.group(1))
        return temp.group(1)
    except Exception as e:
        print(e)
        return None

d = path.dirname(__file__)
save_html_dir = path.join(d, '../', 'assets', 'html')
save_img_dir = path.join(d, '../', 'assets', 'img')

def removeAnalyseResult(uid):
    target_html = path.join(save_html_dir, '{}.html'.format(uid))
    target_img = path.join(save_img_dir, '{}.jpg'.format(uid))
    print('重新爬取时，删除已有的分析结果', target_img, target_html, path.exists(target_html))
    delete_global_forUserWCdata(uid)

    if path.exists(target_html):
        print('删除lda的html')
        remove(target_html)
    if path.exists(target_img):
        print('删除词云')
        remove(target_img)
    return True

@app.callback(Output('crawlScript1', 'run'),
              [Input('crawlBtn', 'n_clicks')],
              [State('crawlInput', 'value')],
              )
def refind(n, url):
    uid = global_uid(url)
    script = '''
        window.history.pushState({}, 'crawled', 'crawling?uid=%s')
    '''%uid
    return script