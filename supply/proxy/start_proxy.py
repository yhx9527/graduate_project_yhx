import json
import pymongo
from mitmproxy import ctx
import re
from functools import reduce
from urllib.parse import urlparse
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from items import UserItem,PostItem, CommentItem
from sqlalchemy.pool import NullPool
# 启动 mitmdump -q -s ./start_proxy.py
MYSQL_URI='mysql+pymysql://root:mysql@12138@47.96.231.167:3306/douyin?charset=utf8mb4' #utf8mb4插入表情
import mitmproxy.addonmanager

class Mymysql(object):
    def __init__(self):
        print('proxy连接数据库...')
        self.engine = create_engine(MYSQL_URI, pool_recycle=2400, pool_size=20, max_overflow=10)
        metadata = MetaData(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.User_table = Table("users", metadata, autoload=True)  # autoload=True这个是关键
        self.Post_table = Table("posts", metadata, autoload=True)  # autoload=True这个是关键
        self.Comment_table = Table("comments", metadata, autoload=True)  # autoload=True这个是关键
    def insert(self, arr, table):
        try:
            self.session.execute(self.__dict__[table].insert(), arr)
            self.session.commit()
            print('数据已插入', table)
        except Exception as e:
            print('数据插入异常,正在回滚', e)
            self.session.rollback()
        finally:
            print('关闭session')
            self.session.close()
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     print('实例销毁,关闭数据库连接')
    #     self.session.close()
    # def __del__(self):
    #     print('实例销毁,关闭数据库连接')
    #     self.session.close()

class AddHeader:
    def __init__(self):
        self.db = Mymysql()

    def response(self, flow):
        curUrl = flow.request.url
        arr = urlparse(curUrl)
        # print('当前url-->',arr.scheme, '://',arr.netloc, arr.path)
        #reduce(lambda acc,cur:acc or cur.startswith('a'), ['c1','b1'], False)
        # url = ['https://api3-normal-c-lq.amemv.com/aweme/v2/comment/list/', 'https://aweme.snssdk.com/aweme/v2/comment/list/']
        # user_url = 'https://aweme-eagle.snssdk.com/aweme/v1/user'
        # post_url_aweme = 'https://aweme.snssdk.com/aweme/v1/aweme/post'
        # post_url_api = 'https://api.amemv.com/aweme/v1/aweme/post'
        # comment_url_api = 'https://api.amemv.com/aweme/v2/comment/list'
        # comment_url_aweme = 'https://aweme.snssdk.com/aweme/v2/comment/list'

        user_flag = '/aweme/v1/user'
        post_flag = '/aweme/v1/aweme/post'
        comment_flag = '/aweme/v2/comment/list'

        data = '{}'
        try:
            data = json.loads(flow.response.text)
        except Exception as e:
            pass
        if curUrl.find(user_flag)>-1:
            self.handle_user(data)
        if curUrl.find(post_flag)>-1:
            self.handle_post(data)
        if curUrl.find(comment_flag)>-1:
            self.handle_comment(data)
        # if curUrl.startswith(user_url):
        #     self.handle_user(data)
        # if curUrl.startswith(post_url_api):
        #     self.handle_post(data, 'api')
        # if curUrl.startswith(post_url_aweme):
        #     self.handle_post(data, 'aweme')
        # if curUrl.startswith(comment_url_api):
        #     self.handle_comment(data, 'api')
        # if curUrl.startswith(comment_url_aweme):
        #     self.handle_comment(data, 'aweme')

    def handle_user(self, res):
        print('拦截user接口')
        user = UserItem()
        if res.get('status_code') == 0:
            data = res.get('user', {})
            user['user_id'] = data.get('uid')
            user['nickname'] = data.get('nickname')
            user['unique_id'] = data.get('unique_id')
            user['gender'] = data.get('gender')
            user['birthday'] = data.get('birthday')
            user['signature'] = data.get('signature')
            user['school_name'] = data.get('school_name')
            user['aweme_count'] = data.get('aweme_count')
            user['total_favorited'] = data.get('total_favorited')
            user['following_count'] = data.get('follower_count')
            user['aweme_fans'] = data.get('follower_count')
            for item in data.get('followers_detail', []):
                temp = item.get('app_name', '')
                if temp == 'news_article':
                    user['news_article_fans'] = item.get('fans_count')
                if temp == 'live_stream':
                    user['live_stream_fans'] = item.get('fans_count')
            user['mplatform_followers_count'] = data.get('mplatform_followers_count')
            user['country'] = data.get('country')
            user['province'] = data.get('province')
            user['city'] = data.get('city')
            user['location'] = data.get('location', '')
            user['district'] = data.get('district')
            user['custom_verify'] = data.get('custom_verify')
            user['with_fusion_shop_entry'] = data.get('with_fusion_shop_entry')
            user['with_commerce_entry'] = data.get('with_commerce_entry')
            user['avatar'] = data.get('avatar_medium', {}).get('url_list', [''])[0]
            user['share_url'] = data.get('share_info', {}).get('share_url')
            self.db.insert([user], 'User_table')

    def handle_post(self, res, type=''):
        print('拦截%s_post接口' % (type))
        if res.get('status_code') == 0:
            result = []
            posts = res.get('aweme_list', [])
            for post in posts:
                item = PostItem()
                item['aweme_id'] = post.get('aweme_id')
                item['user_id'] = post.get('author', {}).get('uid')
                item['create_time'] = post.get('create_time')
                item['desc'] = post.get('desc')
                item['music_author'] = post.get('music', {}).get('author')
                item['music_author_uid'] = post.get('music', {}).get('owner_id')
                item['music_url'] = post.get('music', {}).get('play_url', {}).get('uri')
                item['duration'] = post.get('duration')
                statistics = post.get('statistics', {})
                item['comment_count'] = statistics.get('comment_count')
                item['digg_count'] = statistics.get('digg_count')
                item['download_count'] = statistics.get('download_count')
                item['share_count'] = statistics.get('share_count')
                item['forward_count'] = statistics.get('forward_count')
                item['text_extra'] = str(post.get('text_extra', [])).encode()
                item['dynamic_cover'] = post.get('video', {}).get('dynamic_cover', {}).get('url_list', [''])[0]
                result.append(item)
            self.db.insert(result, 'Post_table')

    def handle_comment(self, res, type=''):
        print('拦截%s_comment接口' % (type))
        result = []
        if res.get('status_code') == 0:
            comments = res.get('comments', [])
            for comment in comments:
                item = CommentItem()
                item['cid'] = comment.get('cid')
                item['aweme_id'] = comment.get('aweme_id')
                item['user_id'] = comment.get('user', {}).get('uid')
                item['text'] = comment.get('text')
                item['create_time'] = comment.get('create_time')
                item['digg_count'] = comment.get('digg_count')
                item['reply_id'] = comment.get('reply_id')
                item['user_digged'] = comment.get('user_digged')
                item['reply_comment_total'] = comment.get('reply_comment_total')
                result.append(item)
            self.db.insert(result, 'Comment_table')

    def load(self, entry: mitmproxy.addonmanager.Loader):
        print('load...........')

    def done(self):
        print('done......')
        print('关闭session')
        self.session.close()
addons = [
    AddHeader()
]


