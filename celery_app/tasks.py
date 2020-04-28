'''
启动定时beat： celery -A celery_app.tasks beat -l info
启动worker： celery -A celery_app.tasks worker --loglevel=info

'''
from celery_app import celery
from douyin_crawler.crawl_post_pt import Douyin
from douyin_crawler.crawl_star import NewRank
from db.conn import Mymysql
from db.db_models import Urltask
import threading
from diggout.user_similar import gen_model, gen_MatrixSimilarity
conn = None
lock = threading.Lock()



@celery.task
def startDB():
    global conn
    conn = Mymysql()
    return True

# def start_crawling(url):
#     chain = get_conn.s() | crawling.s(url)
#     return chain()
#
# def start_addAnalyseCount(uid):
#     chain = get_conn.s() | addAnalyseCount.s(uid)
#     return chain()

def get_conn():
    global conn, lock
    lock.acquire()
    if not conn:
        print('conn不存在重新初始化', conn)
        conn = Mymysql()
    lock.release()
    return conn

@celery.task
def get_newrank():
    conn = get_conn()
    ranker = NewRank(conn)
    ranker.run()

@celery.task(bind=True)
def crawling(self, url):
    conn = get_conn()
    print('启动爬取任务: ')
    douyin = Douyin(conn)
    sum=0
    id=1
    data = []
    for item in douyin.getPost(url):
        info = handleItem(item)
        data.append(item)
        cur = len(item.get('aweme_list', []))
        sum+=cur
        self.update_state(state='PROGRESS',meta={'result': info, 'status': '爬取中...', 'end':0, 'id': id, 'cur': cur})
        id+=1
    result = '''
        共爬取{}条数据
    '''.format(sum)
    return {'result': [], 'status': '爬取结束！！！'+result, 'end': 1, 'id': id, 'cur':0, 'data': data}

def handleItem(item):
    aweme_list = item.get('aweme_list', [])
    info = [item.get('desc', '') for item in aweme_list]
    # info = ''
    # for post in aweme_list:
    #     desc = post.get('desc')
    #     info+='#{}'.format(desc)
    return info

@celery.task(ignore_result=True)
def addAnalyseCount(uid):
    conn = get_conn()
    session = conn.Session()
    res = session.query(Urltask).filter(Urltask.user_id==uid).first()
    print('增加分析次数', res)
    if res:
        print(res.analyse_count, ' ')
        res.analyse_count+=1
        print(res.analyse_count)
    conn.safeAction(session)

@celery.task(ignore_result=True)
def gen_model_task(model):
    print('生成模型', model)
    if model == 'sim':
        gen_MatrixSimilarity()
    elif model == 'd2v':
        gen_model()

# @celery.task(bind=True)
# def task_get_similar(self, uid, threshold=0.5):
#     print('正在加载数据...', uid)
#     id = 1
#     self.update_state(state='PROGRESS', meta={'result': '', 'status': '正在加载数据...', 'end': 0, 'id': id})
#     data = global_forUserWCdata(uid)
#     user_posts = data.get('similar_posts', None)
#     if len(user_posts)>0:
#         for item in get_similar_yield(user_posts):
#             print(item)
#             id+=1
#             if isinstance(item, str):
#                 self.update_state(state='PROGRESS', meta={'result': '', 'status': item, 'end': 0, 'id': id})
#             else:
#                 sims = [(uid1, degree) for uid1, degree in item if (degree > threshold) and (str(uid1) != str(uid))]
#                 result = []
#                 if len(sims)>0:
#                     self.update_state(state='PROGRESS', meta={'result': '', 'status': '正在查询相似用户信息...', 'end': 0, 'id': id})
#                     for sim in sims:
#                         user = global_user_data(sim[0])
#
#                         if user:
#                             xx = dict(
#                                 nickname=user.nickname,
#                                 user_id=user.user_id,
#                                 avatar=user.avatar,
#                                 degree=sim[1]
#                             )
#                             print('相似用户', xx)
#                             result.append(xx)
#                 else:
#                     self.update_state(state='PROGRESS', meta={'result': '', 'status': '无相似用户', 'end': 0, 'id': id})
#         return {'result': result, 'status': '数据加载完成', 'end': 1, 'id': id}
#     else:
#         print('数据加载失败')
#         id += 1
#         return {'result': '', 'status': '数据加载失败, 请重试...', 'end': 1, 'id': id}
#
#
#
#
#
#
#
