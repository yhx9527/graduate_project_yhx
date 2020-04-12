from sqlalchemy import create_engine
from config import MYSQL_URL
import pandas as pd
import os
import sys

def fresh(table='stars', cover=False):
    cur_path = os.path.join(sys.path[0], '{}.csv'.format(table))
    exist = os.path.exists(cur_path)
    if (not exist or (exist and cover)):
        db = create_engine(MYSQL_URL, pool_recycle=2400, pool_size=20, max_overflow=10)
        print('正在收集'+table+'表数据...')
        df = pd.read_sql_query('select * from {}'.format(table), db)
        print(table+'文件正在写入...')
        df.to_csv(cur_path)
        print(table+'文件已写入')
        db.dispose()
    else:
        print('文件已存在')

if __name__ == '__main__':
    table = ['stars', 'comments', 'posts', 'users']
    for item in table:
        fresh(item)
    # data = pd.read_csv('./stars.csv')
    # print(data)
    # print(sys.path[0])