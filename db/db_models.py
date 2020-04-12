from sqlalchemy import create_engine
from sqlalchemy import Column, Date, Integer, String, ForeignKey, Boolean, Float, BLOB, TEXT,JSON,PickleType,TIMESTAMP,text,DateTime,func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import LONGTEXT

# LOCALHOST = ''
# USERNAME = ''
# PASSWORD = ''
# DB = 'douyin'
# # 连接数据库
# engine = create_engine("mysql+pymysql://%s:%s@%s:3306/%s?charset=UTF8MB4"%(USERNAME, PASSWORD, LOCALHOST, DB), max_overflow=5, echo=True)
# if not database_exists(engine.url):
#     create_database(engine.url)

#基本类
Base = declarative_base()

class Star(Base):
    __tablename__ = 'stars'
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }
    sid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50), unique=True)
    area = Column(String(30))
    if_crawl = Column(Integer, default=0)

class User(Base):
    __tablename__= 'users'
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }
    user_id = Column(String(50), primary_key=True, index=True)
    nickname = Column(TEXT, index=True)
    unique_id = Column(String(50)) #抖音号
    gender=Column(Integer, nullable=True)
    birthday = Column(String(50), nullable=True)
    signature = Column(TEXT, nullable=True, index=True)
    school_name = Column(TEXT, nullable=True)
    aweme_count = Column(Integer, nullable=True) #视频数量
    total_favorited = Column(Integer, nullable=True) #获赞总数
    following_count = Column(Integer, nullable=True) #关注别人数量
    aweme_fans = Column(Integer, nullable=True) # 抖音粉丝数量
    news_article_fans = Column(Integer,nullable=True, default=0) # 头条粉丝数量
    live_stream_fans = Column(Integer, nullable=True, default=0) # 抖音火山版粉丝数量
    mplatform_followers_count = Column(Integer, nullable=True) #各平台上粉丝数量总和
    country = Column(TEXT, nullable=True)
    province = Column(TEXT, nullable=True)
    city=Column(TEXT, nullable=True)
    location = Column(TEXT, nullable=True)
    district = Column(TEXT, nullable=True) #地区
    custom_verify = Column(TEXT, nullable=True) #官方称号
    with_fusion_shop_entry = Column(Boolean, default=False, nullable=True) #是否开启商品橱窗
    with_commerce_entry = Column(Boolean, default=False, nullable=True) #是否有商业合作
    avatar = Column(TEXT,nullable=True)
    share_url = Column(TEXT, nullable=True)

class Post(Base):
    __tablename__ = 'posts'
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }
    aweme_id = Column(String(100), primary_key=True)
    # user_id = Column(String(50), ForeignKey('users.user_id'))
    user_id = Column(String(50), index=True)
    create_time = Column(Integer) #发布时间
    desc = Column(TEXT, index=True) #视频描述
    music_author=Column(TEXT)
    music_author_uid = Column(String(50))
    music_url = Column(TEXT)
    duration = Column(Integer) #时长ms
    comment_count = Column(Integer) #评论数量
    digg_count = Column(Integer) #点赞数量
    download_count = Column(Integer) #下载数量
    share_count = Column(Integer) #分享数量
    forward_count = Column(Integer)
    text_extra = Column(PickleType, nullable=True)
    dynamic_cover = Column(TEXT, nullable=True)

# User.posts = relationship("Post", order_by=Post.create_time, back_populates="user")
# Post.user = relationship("User", back_populates="posts")

class Comment(Base):
    __tablename__='comments'
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }
    cid = Column(String(100), primary_key=True)
    # aweme_id = Column(String(100), ForeignKey('posts.aweme_id'))
    # user_id = Column(String(50), ForeignKey('users.user_id'))
    aweme_id = Column(String(100), index=True)
    user_id = Column(String(50), index=True)
    text = Column(TEXT, index=True)
    create_time = Column(Integer)  # 发布时间
    digg_count = Column(Integer) # 点赞数
    reply_id = Column(String(100), nullable=True, index=True)
    user_digged = Column(Integer)
    reply_comment_total = Column(Integer, default=0)

class Urltask(Base):
    __tablename__='urltasks'
    __table_args__ = {
        'mysql_charset': 'utf8mb4'
    }
    user_id = Column(String(50),primary_key=True, index=True)
    url=Column(String(100),nullable=False)
    crawl_count = Column(Integer, server_default=text('1'))
    analyse_count = Column(Integer, server_default=text('0'))
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='修改时间')
    num = Column(Integer, server_default=text('0'), comment='爬取数量')

# Post.comments = relationship("Comment", order_by=Comment.create_time, back_populates="post")
# Comment.post = relationship("Post", back_populates="comments")

# User.comments = relationship("Comment", order_by=Comment.create_time, back_populates="user")
# Comment.user = relationship("User", back_populates="comments")

# 创建表
# Base.metadata.create_all(engine)


