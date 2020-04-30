from sqlalchemy import create_engine, Table, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from config import MYSQL_URL,REDIS_URL
import threading
from sqlalchemy.exc import IntegrityError
class Mymysql(object):

    def __init__(self):
        print('连接数据库...')
        self.engine = create_engine(MYSQL_URL, pool_recycle=2400, pool_size=20, max_overflow=10, pool_pre_ping=True)
        metadata = MetaData(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.Post_table = Table("posts", metadata, autoload=True)  # autoload=True这个是关键
        self.UrlTask_table = Table("urltasks", metadata, autoload=True)
        self.User_table = Table("users", metadata, autoload=True)  # autoload=True这个是关键
        self.Star_table = Table("stars", metadata, autoload=True)  # autoload=True这个是关键
        print('已连接了')

    def insert(self, arr, table, session=None):
        print('插入数据库...')
        if not session:
            session = self.Session()
        try:
            session.execute(self.__dict__[table].insert(), arr)
            session.commit()
            print('数据已插入', table)
        except IntegrityError as e:
            session.rollback()
            print('重复插入,进行更新中...')
            if isinstance(e.params, tuple) or isinstance(e.params, list):
                temp = e.params
            else:
                temp = [e.params]
            self.update(temp, table, session)
        except Exception as e:
            print('数据插入异常,正在回滚', e)
            session.rollback()
        finally:
            print('关闭session')
            session.close()

    def update(self, arr, tablename, session=None):
        table = self.__dict__[tablename]
        primaryKeyColName = table.primary_key.columns.values()[0].name
        print(primaryKeyColName)
        print('更新数据库...')
        if not session:
            session = self.Session()
        try:
            for item in arr:
                up = dict()
                for k in item.keys():
                    if item[k] and k != primaryKeyColName:
                        up[k] = item[k]
                print('更新一行', up)
                session.execute(table.update()
                                .where(table.c[primaryKeyColName]==item[primaryKeyColName]), up)
            session.commit()
            print('数据已更新', tablename)
        except Exception as e:
            print('数据更新异常,正在回滚', e)
            session.rollback()
        finally:
            print('关闭session')
            session.close()


    #装饰器,用于获取数据库session
    def session_get(self, func):
        def wrapper(*args, **kw):
            try:
                print('获取session')
                ses = self.Session()
                result = func(ses, *args, **kw)
                ses.commit()
            except Exception as e:
                print('session_get异常', e)
                ses.rollback()
            finally:
                print('回收session')
                ses.close()
            return result
        return wrapper

    def safeAction(self, session):
        try:
            print('数据更新')
            session.commit()
        except Exception as e:
            print('safeAction数据插入异常,正在回滚', e)
            session.rollback()
        finally:
            print('关闭session')
            session.close()
    def close(self):
        print('关闭数据库引擎...')
        self.engine.dispose()

conn = None
lock = threading.Lock()

def get_conn():
    global conn, lock
    lock.acquire()
    if not conn:
        print('conn不存在重新初始化', conn)
        conn = Mymysql()
    lock.release()
    return conn