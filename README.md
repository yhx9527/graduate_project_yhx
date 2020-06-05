# Introduction

**此项目为本人毕设作品，设计实现了以抖音为数据源的短视频流量数据爬取和分析系统。**

## 系统演示

#### 1.系统首页

![演1](./introduction/演1.gif)

#### 2.在线爬取

![演2](./introduction/演2.gif)

#### 3.用户画像分析

![演3](./introduction/演3.gif)

## 系统设计概括

#### 1.系统架构图

![系统总体架构图](./introduction/系统总体架构图.png)

#### 2. 爬虫模块

![爬虫模块架构 (1)](./introduction/爬虫模块架构 (1).png)

#### 3.数据存储模块

![数据存储模块架构图](./introduction/数据存储模块架构图.png)

####4.数据挖掘模块

![数据挖掘模块架构图](./introduction/数据挖掘模块架构图.png)

#### 5.web服务模块

![web服务模块架构图](./introduction/web服务模块架构图.png)

## 项目目录

 - celery_app  
 后台任务模块，先启动该模块，再启动app  
 
 ```celery -A celery_app.tasks worker --loglevel=info```
 
 - db/  
 存放数据库模型
 
 - diggout/
 
 数据挖掘模块
 
 - douyin_alembic  
    alembic管理数据库

 - douyin_crawler  
    抖音用户分享链接web页面爬虫，”新榜“网页热门抖音号爬虫

 - supply  

    - proxy  
      mitmdump拦截抖音请求  

    - simulation  
      appium模拟操作

- svdca  
    web app模块  

    ```python svdca.index.py  ```