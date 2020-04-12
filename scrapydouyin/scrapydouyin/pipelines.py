# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy import create_engine, Column, Integer, String, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

class mysqlPipeline(object):
    def __init__(self, mysql_uri):
        self.mysql_uri = mysql_uri

    @classmethod
    def from_crawler(cls, crawler):
        return cls(mysql_uri=crawler.settings.get('MYSQL_URI'))

    def open_spider(self, spider):
        engine = create_engine(self.mysql_uri, echo=False, encoding="utf-8")
        metadata = MetaData(engine)
        self.SessionClass = sessionmaker(bind=engine)  # 利用工厂模式获取SessionClass
        self.session_obj = self.SessionClass()  # 创建session对象,此时已绑定数据库引擎，但是未关联任何的对象模型

        self.Star_table = Table("stars", metadata, autoload=True)  # autoload=True这个是关键

    def process_item(self, item, spider):
        self.session_obj.execute(self.Star_table.insert(), [item])
        # self.User_table.insert(id=1, name="2")
        self.session_obj.commit()
        return item

    def close_spider(self, spider):
        self.session_obj.close()
        self.session_obj.commit()
