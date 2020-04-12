import asyncio
from pyppeteer import launch
from urllib.parse import urlparse, parse_qs
from functools import reduce
import requests
import json
from time import sleep
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from config import MYSQL_URL,REDIS_URL
from supply.proxy.items import PostItem
import threading
from random import random
import redis
import pickle

LARGE_WAIT = 3

map = {
    'a': 'K',
    'b': 'L',
    'c': 'M',
    'd': 'N',
    'e': 'O',
    'f': 'P',
    'g': 'w',
    'h': 'x',
    'i': 'y',
    'j': 'z',
    'k': '0',
    'l': '1',
    'm': '2',
    'n': '3',
    'o': '4',
    'p': '5',
    'q': '6',
    'r': '7',
    's': '8',
    't': '9',
    'u': '-',
    'v': '.',
    'w': 'g',
    'x': 'h',
    'y': 'i',
    'z': 'j',
    'A': 'Q',
    'B': 'R',
    'C': 'S',
    'D': 'T',
    'E': 'U',
    'F': 'V',
    'G': 'W',
    'H': 'X',
    'I': 'Y',
    'J': 'Z'
 }
def make(acc, cur):
    acc[cur[0]] = cur[1]
    acc[cur[1]] = cur[0]
    return acc
MAP = reduce(make, list(map.items()), {})

class Douyin():
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.post_url = 'http://www.iesdouyin.com/web/api/v2/aweme/post/'
        self.params = {
            'count': '21',
            'max_cursor': '0',
            'aid': '1128',
        }
        self.headers = {
            'Connection': 'keep-alive',
            # 'Host': 'www.iesdouyin.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
        }
        # self.db = Mymysql()
        # self.redis = MyRedis()

    async def getSignature(self, url):
        browser = await launch({'headless': True, 'args': ['--no-sandbox', '--disable-infobars',],})
        # browser = await launch()
        page = await browser.newPage()
        # await page.setUserAgent("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36")
        await page.setUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36")
        try:
            await page.evaluate(
                '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
            await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
            await page.evaluate(
                '''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
            await page.goto(url)  # 访问页面
            print('当前url',url)
            arr = urlparse(page.url)
            params = parse_qs(arr.query)
            self.params['sec_uid'] = params['sec_uid']
            uid = arr.path.split('/')[-1]
            script = '''
                ()=>{
                    var generate = window.__M.require('douyin_falcon:node_modules/byted-acrawler/dist/runtime');
                    var signature = generate.sign('''+uid+''');
                    return signature;
                    }'''
            signature = await page.evaluate(script)
            first1 = chr(ord(signature[-2:-1]) + 1)
            first2 = chr(ord(signature[-2:-1]) - 1)
            second = MAP[signature[-1]]
            sign1 = signature[:-2] + first1 + second
            sign2 = signature[:-2] + first2 + second
            print('获取签名: ', signature, sign1, sign2)
            return [sign1, sign2]
        except Exception as e:
            print('出错了', e)
        finally:
            print('关闭浏览器')
            await browser.close()



    def getPost(self, url):
        try:
            print('获取签名',url)
            signature = self.loop.run_until_complete(self.getSignature(url))  # 将协程注册到事件循环，并启动事件循环
            self.params['_signature'] = signature[0]
            count = 5
            sum = 0
            print('获取完毕')
            while True:
                res = requests.get(self.post_url, params=self.params, headers=self.headers)
                data = json.loads(res.text)
                print('响应数据', data)
                if not data.get('max_cursor', False):
                    print('更换签名')
                    count -= 1;
                    if count == 0:
                        break
                    self.params['_signature'] = signature[1]
                    continue
                sum += len(data.get('aweme_list', []))
                print('处理数据')
                # self.handle_post(data)
                # threading.Thread(target=self.handle_post, kwargs=dict(res=data)).start()
                if not data.get('has_more', False):
                    break

                self.params['max_cursor'] = data.get('max_cursor', 0)
                sleep(LARGE_WAIT*random())
            print('爬取结束,共爬取%s条数据' % str(sum))
        except Exception as e:
            print('协程出错', e)
        finally:
            pass
            # self.db.close()

    def handle_post(self, res):
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
                item['duration'] = post.get('video', {}).get('duration')
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

class Mymysql(object):
    def __init__(self):
        print('连接数据库...')
        self.engine = create_engine(MYSQL_URL, pool_recycle=2400, pool_size=20, max_overflow=10)
        metadata = MetaData(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.Post_table = Table("posts", metadata, autoload=True)  # autoload=True这个是关键
        print('已连接')
    def insert(self, arr, table):
        print('插入数据库...')
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
    def close(self):
        print('关闭数据库引擎...')
        self.engine.dispose()

class MyRedis():
    def __init__(self):
        self.conn = redis.Redis.from_url(REDIS_URL)

    # 将内存数据二进制通过序列号转为文本流，再存入redis
    def set_data(self, key, data, ex=None):
        self.conn.set(key, pickle.dumps(data), ex)

    def get_data(self, key):
        data = self.conn.get(key)
        if data is None:
            return None
        return pickle.loads(data)

if __name__ == '__main__':
    test = Douyin()
    test.getPost('https://v.douyin.com/WhmNnG/')