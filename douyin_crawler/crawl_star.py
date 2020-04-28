'''
用于采集新榜上的抖音号数据
'''

import asyncio
from pyppeteer import launch
from pyppeteer.errors import PageError
from db.conn import Mymysql
import threading

class NewRank(object):
    def __init__(self, conn):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        self.loop = asyncio.get_event_loop()
        self.db = conn
        self.targetUrl='https://www.newrank.cn/public/info/list.html?period=tiktok_day&type=data'

    async def main(self):
        browser = await launch({'headless': True, 'args': ['--no-sandbox', '--disable-infobars',],})
        page = await browser.newPage()
        await page.goto(url=self.targetUrl, waitUntil='networkidle0')  # 访问页面
        while True:
            try:
                arr = await page.querySelectorAll('.l_main.wx_main tr a')
                areadiv = await page.querySelector('.tiktok-type-selected')
                area = await (await areadiv.getProperty('textContent')).jsonValue()
                print('采集',area,'板块',len(arr),'人')
                for tr in arr:
                    try:
                        name = await (await tr.getProperty('text')).jsonValue()
                        item = dict(area=area, name=name)
                        threading.Thread(target=self.db.insert,
                                         kwargs=dict(arr=[item], table='Star_table')).start()
                    except Exception as e:
                        print('采集出错', e)
                    # result.append(item)
                await page.click('.tiktok-type-selected + span')
            except PageError as e:
                print('节点遍历完成', e)
                break
        await browser.close()
    def parseHtml(self, html):
        pass
    def run(self):
        self.loop.run_until_complete(self.main())  # 将协程注册到事件循环，并启动事件循环

if __name__=='__main__':
    conn = Mymysql()
    ranker = NewRank(conn)
    ranker.run()
    # sleep(60*60)