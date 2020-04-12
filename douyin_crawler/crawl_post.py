from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs
from requests import Session
import requests
import json
from functools import reduce
from time import sleep
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from supply.proxy.items import PostItem
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from config import MYSQL_URL

SELENIUM_TIMEOUT = 20
WAIT_TIME = 0.5
PHANTOMJS_SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']
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
    def __init__(self, share_url):
        self.share_url = share_url
        # self.browser = webdriver.PhantomJS()
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # chrome_options.binary_location=''
        # chrome_options.add_argument('--headless') #使用老版本的chromedriver和chrome，其没有navigator.webdriver,应该可实现无头抓取，
        capabilities = DesiredCapabilities.CHROME
        capabilities['loggingPrefs'] = {'browser': 'ALL'}
        self.browser = webdriver.Chrome(chrome_options=chrome_options, desired_capabilities=capabilities)
        # self.browser.set_window_size(1400, 700)
        # script = '''
        # Object.defineProperty(navigator, 'webdriver', {
        #     get: () => undefined
        # })
        # '''
        # self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": script})

        self.browser.set_page_load_timeout(SELENIUM_TIMEOUT)
        self.wait = WebDriverWait(self.browser, SELENIUM_TIMEOUT)
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
        self.db = Mymysql()

    def getSignature(self):
        self.browser.get(self.share_url)
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.nickname')))
        print('当前url: ', self.browser.current_url)
        arr = urlparse(self.browser.current_url)
        params = parse_qs(arr.query)
        uid = arr.path.split('/')[-1]
        print('当前爬取: ', uid)
        self.params['sec_uid'] = params['sec_uid']
        self.browser.execute_script(
            "var generate = window.__M.require('douyin_falcon:node_modules/byted-acrawler/dist/runtime');"
            "var signature = generate.sign("+uid+");"
            "console.log(signature);"
            "var div = document.createElement('div');div.innerText = signature;div.setAttribute('id','only');document.body.insertBefore(div, document.body.children[0])")
        only = self.browser.find_element_by_id('only')
        first1 = chr(ord(only.text[-2:-1]) + 1)
        first2 = chr(ord(only.text[-2:-1]) - 1)
        second = MAP[only.text[-1]]
        sign1 = only.text[:-2]+first1+second
        sign2 = only.text[:-2] + first2 + second
        print('获取签名: ', only.text, sign1, sign2)

        return [sign1, sign2]
    def getPost(self):
        signature = self.getSignature()
        self.params['_signature'] = signature[0]
        # res = self.session.get(self.post_url, params=self.params, headers=self.headers)
        # self.headers['Referer'] = self.browser.current_url
        # self.headers['User-Agent'] = USER_AGENT[4]
        count = 5
        sum=0

        while True:
            res = requests.get(self.post_url, params=self.params, headers=self.headers)
            data = json.loads(res.text)
            print('响应数据', data)
            if not data.get('max_cursor', False):
                print('更换签名')
                count-=1;
                if count==0:
                    break
                self.params['_signature'] = signature[1]
                continue
            sum += len(data.get('aweme_list', []))
            print('处理数据')
            self.handle_post(data)
            # yield data
            if not data.get('has_more', False):
                break

            self.params['max_cursor'] = data.get('max_cursor', 0)
            sleep(WAIT_TIME)
        print('爬取结束,共爬取%s条数据'%str(sum))
    def close(self):
        self.browser.close()
        self.db.close()

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

if __name__ == '__main__':
    douyin = Douyin('https://v.douyin.com/nW5NUF/')
    douyin.getPost()
    # douyin.close()


