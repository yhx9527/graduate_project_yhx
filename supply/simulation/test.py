import time

from sqlalchemy.engine import create_engine


MYSQL_URI='mysql+pymysql://root:mysql@12138@47.96.231.167:3306/douyin?charset=utf8mb4' #utf8mb4插入表情

engine = create_engine(MYSQL_URI, pool_recycle=13,pool_pre_ping=True, pool_size=20, max_overflow=10)

query = 'SELECT NOW();'

while True:
    print('Q1', engine.execute(query).fetchall())
    engine.execute('SET wait_timeout=2')
    time.sleep(3)
    print('Q2', engine.execute(query).fetchall())