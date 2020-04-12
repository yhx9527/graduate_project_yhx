# Introduction

## 目录简介
 - db/  
 存放数据库模型
 - douyin_alembic  
 alembic管理数据库
 - celery_app  
 后台任务模块，先启动该模块，再启动app  
 > celery -A celery_app.tasks worker --loglevel=info
 - svdca  
 web app模块  
 > python svdca.index.py  
 - douyin_crawler  
 抖音web分享页面爬虫
 - scrpaydouyin  
 爬取抖音号网页  
 - supply  
    - proxy  
    mitmdump拦截抖音请求  
    - simulation  
    appium模拟操作