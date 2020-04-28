import os
from appium import webdriver
from appium.webdriver.common.touch_action import TouchAction
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from time import sleep
import sys
import os
cur_file_path = os.path.dirname(__file__)
sys.path.append(cur_file_path)
from config import *
import re
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
from db.db_models import Star, User
import time
SWIPER_TIMEOUT=10*60

class Douyin():
    def __init__(self):
        """
        初始化
        """
        # 驱动配置
        self.desired_caps = DESIRED_CAPS[1]
        print('启动webdriver...')
        self.driver = webdriver.Remote(DRIVER_SERVER, self.desired_caps)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        print('连接数据库...')
        self.engine = create_engine(MYSQL_URI, echo=False, encoding="utf-8", pool_recycle=2400, pool_size=20, max_overflow=10, pool_pre_ping=True)
        metadata = MetaData(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        # self.session = Session()
        # self.Star_table = Table("stars", metadata, autoload=True)
    def start(self):
        """
        进入抖音
        :return:
        """
        # 授权，引导初始化
        print('初始化...')
        el1 = self.wait.until(EC.presence_of_element_located((By.ID, "com.android.packageinstaller:id/permission_allow_button")))
        el1.click()
        el2 = self.wait.until(EC.presence_of_element_located((By.ID, "com.android.packageinstaller:id/permission_allow_button")))
        el2.click()
        # print(temp.find_element_by_xpath('.//following-sibing::*/following-sibing::*').get_attribute('class'))
        # print(temp.find_element_by_xpath('.//self::*/following-sibling::*').get_attribute('class'))
        if self.isElementExist('com.ss.android.ugc.aweme:id/qn', 'ID', True):
            agree = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/qn')
            agree.click()
        el3 = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/afx")))
        el3.click()
    def search(self):
        global over
        session = self.Session()
        print('进入搜索栏...')
        el4 = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/afs")))
        el4.click()
        print('搜索中...')
        while True:
            key = session.query(Star).filter(Star.if_crawl == None).first()
            session.close()
            if not key:
                break


        # keyword = self.get_data()
        # for ii, key in enumerate(keyword):
            print('正在爬取',key.name)
            key.if_crawl=1
            self.update_star(key)
            polling = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/jt")))
            polling.click()
            polling.send_keys(key.name)
            btn = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/a8w")))
            btn.click()
            chose_item = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@resource-id='com.ss.android.ugc.aweme:id/aaq']//*[contains(@text, '用户')]")))
            chose_item.click()
            first = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@resource-id='com.ss.android.ugc.aweme:id/lp']/android.widget.RelativeLayout[1]")))
            first.click()
            print('进入作者页面...')
            postBtn = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@resource-id='com.ss.android.ugc.aweme:id/a_t']//*[contains(@text, '作品')]")))
            print('点击作品')
            postBtn.click()
            # sleep(10)
            last_time=time.time()
            while True:
                flag = self.swipe_posts_outer(800)
                cur_time=time.time()
                if (cur_time-last_time>SWIPER_TIMEOUT) or flag:
                    break
            self.driver.back();
            self.driver.back();
            print(key.name,'爬取完成')
            key.if_crawl = 2
            self.update_star(key)
        over = True
            # print('作品总数')
            # self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/title")))
            # result = self.driver.find_element_by_id('com.ss.android.ugc.aweme:id/title').text
            # print(result)
            # count=0
            # try:
            #     count = int(re.search(r'(\d+)',result).group(1))
            #     first = self.wait.until(EC.presence_of_element_located(
            #         (By.XPATH, "//*[@resource-id='com.ss.android.ugc.aweme:id/jw']/android.widget.FrameLayout[1]")))
            # except Exception as e:
            #     self.driver.back()
            #     self.driver.back()
            #     print(e)
            #     continue
            # first.click()
            # print(count)
            # print('定位视频')
            #
            # for num in range(0, count):
            #     self.comment_get()
            #     sleep(2)
            #     self.swipe_video(1000) #真机
            #     # self.swipe_video(550) #模拟器
            #     print('第%s个视频'%(num))
            # self.driver.back();
            # self.driver.back();
            # self.driver.back();
            # print(key.name,'爬取完成')
            # key.if_crawl = 2
            # print(self.session.dirty)
            # print(key)
            # self.update_star(key)
            # if ii==len(keyword)-1:
            #     over = True
    def update_star(self,key):
        print('修改爬取状态')
        session = self.Session()
        try:
            usr = session.query(Star).filter(Star.name == key.name).first()
            usr.if_crawl = key.if_crawl
            session.add(usr)
        except Exception as e:
            print('插入出错,正在回滚...', e)
            session.rollback()
            raise
        finally:
            session.commit()
            session.close()


    def get_data(self):
        print('获取数据库数据...')
        session = self.Session()
        data = session.query(Star).order_by("area").filter(Star.if_crawl==None).all()
        print('数据长度:', len(data))
        session.close()
        return data
    def comment_get(self):
        TouchAction(self.driver).tap(x=985, y=1015, count=1).perform() # 真机位置
        # TouchAction(self.driver).tap(x=706, y=665, count=1).perform() #模拟器位置
        sleep(1)
        try:
            recycle = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/l_")))
            print('爬取评论...')
            count = 1
            while count>0:
                # 上滑
                count-=1;
                flag = self.swipe_comment(700) # 真机
                # flag = self.swipe_comment(500) # 模拟器
                if flag:
                    break
            print('该视频评论爬取结束')
        except Exception as e:
            print('评论为空', e)
        if self.isElementExist("com.ss.android.ugc.aweme:id/l_", 'ID'):
            self.driver.back()
    def swipe_comment(self, dis):
        flag = self.isElementExist('//*[contains(@text, "暂时没有更多了")]')
        if flag:
            print('plun滑动结束...')
            return True
        try:
            self.driver.swipe(FLICK_START_X, FLICK_START_Y + dis, FLICK_START_X, FLICK_START_Y)
            sleep(SCROLL_SLEEP_TIME)
            print('评论滑动...')
            return False
        except Exception as e:
            print('评论滑动失败', e)
            return True
    def swipe_posts_outer(self, dis):
        flag = self.isElementExist('//*[contains(@text, "暂时没有更多了")]')
        if flag:
            print('plun滑动结束...')
            return True
        try:
            self.driver.swipe(FLICK_START_X, FLICK_START_Y + dis, FLICK_START_X, FLICK_START_Y, 500)
            sleep(SCROLL_SLEEP_TIME)
            print('个人首页视频滑动...')
            return False
        except Exception as e:
            print('个人首页视频滑动', e)
            return True
    def swipe_video(self, dis):
        try:
            self.driver.swipe(FLICK_START_X, FLICK_START_Y + dis, FLICK_START_X, FLICK_START_Y, 500)
            sleep(SCROLL_SLEEP_TIME)
            print('视频滑动...')
        except Exception as e:
            print('视频滑动失败', e)
    def isElementExist(self, tag, type='XPATH', wait=False):
        flag = True
        try:
            if type=='XPATH':
                if not wait:
                    self.driver.find_element_by_xpath(tag)
                else:
                    self.wait.until(EC.presence_of_element_located((By.XPATH, tag)))
            elif type =='ID':
                if not wait:
                    self.driver.find_element_by_id(tag)
                else:
                    self.wait.until(EC.presence_of_element_located((By.ID, tag)))
            return flag
        except Exception as e:
            flag = False
            print('未到底部', e)
            return flag
    def login(self):
        print('进入登录...')
        mine = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@resource-id='com.ss.android.ugc.aweme:id/k0']/android.widget.FrameLayout[5]")))
        mine.click()
        print('密码登录...')
        el = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/af5")))
        el.click()
        # 手机前缀改成+86
        pre = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/aex")))
        pre.click()
        pre_86 = self.wait.until(EC.presence_of_element_located((By.XPATH, "//*[@resource-id='com.ss.android.ugc.aweme:id/lt']/android.widget.LinearLayout[1]/android.widget.RelativeLayout")))
        pre_86.click()

        phone = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/abx")))
        phone.send_keys('15520777630')
        pwd = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/af2")))
        pwd.send_keys('abcd1234')
        self.driver.hide_keyboard() #隐藏键盘
        submit = self.wait.until(EC.presence_of_element_located((By.ID, "com.ss.android.ugc.aweme:id/kq")))
        submit.click()
    
    def main(self):
        """
        入口
        :return:
        """
        # 进入，开启评论，滑动
        try:
            self.start()
            self.login()
            self.search()
        except Exception as e:
            print('模拟操作出错', e)
        finally:
            print('关闭数据库')
            # self.session.close()
over = False
if __name__ == '__main__':
    while True:
        douyin = Douyin()
        douyin.main()
        print('休息中...')
        sleep(300)
        if over:
            print('完全爬取，结束')
            break

