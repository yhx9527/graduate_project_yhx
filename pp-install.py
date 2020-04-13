#用于下载chromium
import asyncio
from pyppeteer import launch
async def main():
    browser = await launch(headless = True, args=['--no-sandbox'])   # headless = False，默认ture，为无头模式
    page = await browser.newPage()
    await page.goto('https://www.baidu.com')
    await page.screenshot({'path': 'example.png'})
    await browser.close()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())