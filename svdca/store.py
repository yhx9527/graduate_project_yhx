import os
import sys
cur_file_path = os.path.dirname(__file__)
sys.path.append(cur_file_path)

import pandas as pd
from sqlalchemy import create_engine, or_
from flask_caching import Cache
from config import MYSQL_URL, REDIS_URL, ENV
from app import server,app
from dash.dependencies import Input, Output
import time
from time import sleep
import sys
from datetime import datetime as dt
import numpy as np
from math import log

from db.conn import Mymysql
import json
from hyper import HTTPConnection
from urllib.parse import urlparse
import re
from db.db_models import Urltask, Post, User
import random
from db.conn import get_conn
import pickle

CACHE_CONFIG = {
        # try 'filesystem' if you don't want to setup redis
        'CACHE_TYPE': 'redis',
        'CACHE_REDIS_URL': REDIS_URL,
    }

cache = Cache()
cache.init_app(server, config=CACHE_CONFIG)
# server.db = Mymysql()
server.db = get_conn()


#stars, posts, users, comments, urltasks
def random_time(len):
    return int(random.random()*len)
@cache.memoize(timeout=random_time(300))
def global_store_rows(table):
    # simulate expensive query
    print('正在更新数量数据...')
    # engine = create_engine(MYSQL_URL, pool_recycle=2400, pool_size=20, max_overflow=10)
    engine = server.db.engine
    if table == 'urltasks':
        num = engine.scalar('select sum(analyse_count) from {}'.format(table))
    else:
        num = engine.scalar('select count(*) from {}'.format(table))

    print('更新完成，存入redis')
    return format(num, ',')

@cache.memoize(timeout=random_time(3600))
def global_uid(url):
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

@cache.memoize(timeout=random_time(3600))
def global_urltask(uid):
    Session = server.db.Session
    session = Session()
    data = session.query(Urltask).filter_by(user_id=uid).first()
    session.close()
    return data

@cache.memoize(timeout=random_time(1800))
def global_forUserWCdataCache(uid):
    print('重新查数据库', uid)
    post = pd.read_sql_query('select * from posts where user_id={}'.format(uid), server.db.engine)
    data = list(post['desc'])
    duration_posts = get_duration_posts(post)
    pie_posts = get_pie_posts(post)
    similar_posts = post.loc[:,['user_id', 'desc']]
    if (len(data)>0) and (len(duration_posts)>0) and (len(pie_posts)>0):
        return {
            'uid': uid,
            'data': data,
            'duration_posts': duration_posts,
            'pie_posts': pie_posts,
            'similar_posts': similar_posts
        }
@cache.memoize(timeout=random_time(3600))
def global_user_data(keyword):
    Session = server.db.Session
    session = Session()
    user = session.query(User).filter(or_(User.user_id == keyword, User.nickname.like("%{}%".format(keyword)))
                                      ).first()
    print('查询user', user)
    if user:
        return user
    else:
        return None

def global_forUserWCdata(keyword):
    user = global_user_data(keyword)
    if user:
        temp = global_forUserWCdataCache(user.user_id)
        temp['imageUrl'] = user.avatar
        temp['user']= user
        return temp
    else:
        return None


def delete_global_forUserWCdata(uid):
    temp = cache.delete_memoized(global_forUserWCdataCache, uid)
    print('删除结果', temp)
    return temp



data_dir = os.path.join(cur_file_path,'data')
city_geo = pd.read_csv(os.path.join(data_dir, 'city_geo.csv'))

@cache.memoize(timeout=random_time(3600))
def global_all_posts():
    print('加载文章数据到内存...')
    if ENV == 'production':
        posts = pd.read_sql_query('select * from posts', server.db.engine)
    else:
        posts = pd.read_csv(os.path.join(data_dir, 'posts.csv'))
    return pickle.dumps(posts)

@cache.memoize(timeout=random_time(3600))
def global_all_users():
    print('加载用户数据到内存...')
    if ENV == 'production':
        users = pd.read_sql_query('select * from users', server.db.engine)
    else:
        users = pd.read_csv(os.path.join(data_dir, 'users.csv'))

    return pickle.dumps(users)

@cache.memoize(timeout=random_time(3600))
def get_dataset_posts():
    posts = pickle.loads(global_all_posts())

    datalist = posts.loc[:, ['create_time', 'comment_count', 'digg_count', 'download_count', 'share_count']]
    datalist = datalist[datalist['create_time'].notnull()]
    datalist['create_time'] = datalist['create_time'].apply(
        lambda t: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
    )
    datalist['num'] = 1
    datalist['create_time'] = pd.to_datetime(datalist['create_time'])
    # Insert weekday and hour of checkin time
    datalist["Days of Wk"] = datalist["Check-In Hour"] = datalist["create_time"]
    datalist["Days of Wk"] = datalist["Days of Wk"].apply(
        lambda x: dt.strftime(x, "%A")
    )  # Datetime -> weekday string
    datalist["Check-In Hour"] = datalist["Check-In Hour"].apply(
        lambda x: dt.strftime(x, "%I %p")
    )  # Datetime -> int(hour) + AM/PM
    dataset_posts = datalist.fillna(0).set_index('create_time')
    return dataset_posts

@cache.memoize(timeout=random_time(3600))
def get_dataset_users():
    users = pickle.loads(global_all_users())
    temp_users = users[users['city'].notnull()].loc[:,['city', 'mplatform_followers_count', 'total_favorited', 'aweme_count']] #取值
    temp_users['lon'] = temp_users['lat'] = None #增加属性
    dataset_users = temp_users.apply(addGeo, axis='columns')  # 添加上
    dataset_users['count'] = 1
    dataset_users = dataset_users.groupby('city').agg({'count': np.sum,
                                                       'total_favorited': np.sum,
                                                       'mplatform_followers_count': np.sum,
                                                       'aweme_count': np.sum,
                                                       'lon': np.min,
                                                       'lat': np.min})
    dataset_users['city'] = dataset_users.index
    return dataset_users

def addGeo(row):
    temp = city_geo[city_geo.city.apply(lambda x: x.startswith(row.city))]
    res = temp[:1]
    res = np.array(res)
    if len(res)==0:
        print(row.city)
    else:
        row['lon'] = res[0][2]
        row['lat'] = res[0][3]
        row['city'] = res[0][1]
    return row

@cache.memoize(timeout=random_time(3600))
def get_sunburt_users():
    users = pickle.loads(global_all_users())
    tag = ['一万以下', '万级', '十万级', '百万级', '千万级', '亿级']
    area = [(0, 1e4), (0, 1e5), (1e5, 1e6), (1e6, 1e7), (1e7, 1e9)]
    sunburt_users = users.loc[:,['nickname', 'mplatform_followers_count']]
    sunburt_users['count'] = 1
    sunburt_users['tag'] = tag[0]
    sunburt_users['title'] = '用户粉丝量'
    def divide_user(row):
        for index, region in enumerate(area):
            if((row['mplatform_followers_count']>=region[0]) and
                    (row['mplatform_followers_count']<region[1])):
                row['tag'] = tag[index]
                break;
        return row
    sunburt_users = sunburt_users.apply(divide_user, axis='columns')
    return sunburt_users
# print(dataset_users)
# china_map = os.path.join(sys.path[0], 'data/geojson-map-china/china.json')
#
# gs_data = open(china_map, encoding='utf8').read()
# gs_data = json.loads(gs_data)
# print('中国地图', gs_data)
def get_duration_posts(posts):
    # print('生成dp', posts)
    kinds = ['0-15s', '15-30s', '30-60s', '1-5min', '5-10min', '10-30min', '30-60min', '60min～']
    area = [(0, 15), (15, 30), (30, 60), (60, 300), (300, 600), (600, 1800), (1800, 3600), (3600, 10000)]
    duration_posts = posts.loc[:, ['duration']]
    duration_posts = duration_posts[duration_posts['duration'].notnull()]
    duration_posts['count'] = 1
    duration_posts['tag'] = kinds[0]
    duration_posts['flag'] = -1

    def divide_duration(row):
        dura = row['duration'] / 1000
        for index, val in enumerate(area):
            if (dura >= val[0]) and (dura < val[1]):
                row['tag'] = kinds[index]
                row['flag'] = index
                break;
        return row

    duration_posts = duration_posts.apply(divide_duration, axis='columns')
    duration_posts = duration_posts.groupby('tag').agg({
        'count': np.sum,
        'flag': np.min,
    })
    duration_posts['tag'] = duration_posts.index
    duration_posts.index = range(len(duration_posts))
    duration_posts = duration_posts.sort_values(by='flag')
    return duration_posts

def get_pie_posts(posts):
    tag = ['小于1千👍', '1千～1万👍', '1万～10万👍', '10万～100万👍', '100万～1000万👍', '1千万～1亿万👍', '1亿万～10亿万👍', '十亿万～百亿万👍', '百亿万以上👍']
    pie_posts = posts.loc[:, ['digg_count']]
    pie_posts['tag'] = tag[0]
    pie_posts['count'] = 1

    def divide_posts(row):
        temp = row['digg_count']
        if temp > 0:
            num = int(log(temp, 10))
            if (num < len(tag)) and (num > 2):
                row['tag'] = tag[num - 2]
        return row

    pie_posts = pie_posts.apply(divide_posts, axis='columns')
    return pie_posts

@cache.memoize(timeout=random_time(3600))
def get_duration_posts_home():
    posts = pickle.loads(global_all_posts())
    return get_duration_posts(posts)

@cache.memoize(timeout=random_time(3600))
def get_pie_posts_home():
    posts = pickle.loads(global_all_posts())
    return get_pie_posts(posts)

print('数据预处理...')
dataset_posts = get_dataset_posts()
global_all_users()