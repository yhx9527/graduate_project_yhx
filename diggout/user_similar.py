from sqlalchemy import create_engine
import pandas as pd
from config import MYSQL_URL
import jieba
import jieba.posseg as pseg
import re
import gensim
import os
from pandas import DataFrame
from diggout import stpwrdlst
from gensim import models, similarities, corpora
from os.path import join
from functools import reduce

d = os.path.dirname(__file__)
file = os.path.join(d, 'mymodel.d2v')
sim_dir = os.path.join(d, 'sims_data')

def get_data_from_db():
    # MYSQL_URL = 'mysql+pymysql://root:mysql@12138@47.96.231.167:3306/douyin?charset=UTF8MB4'
    db = create_engine(MYSQL_URL, pool_recycle=2400, pool_size=20, max_overflow=10)
    data = pd.read_sql_query('select user_id,`desc` from posts', db)

    return data

def cut_word(df):
    jieba.enable_paddle()
    ignore_flag = ['m', 'w', 'xc', 'r', 'q', 'p', 'c', 'u', 'v', 'd', 'TIME']
    ignore_words = stpwrdlst
    def chinese_word_cut(text):
        text1 = re.sub(r'[^\w\s]', ' ', text).strip()

        words = pseg.cut(text1, use_paddle=True)
        arr = []
        for word, flag in words:
            temp = word.strip()
            if (flag not in ignore_flag) and (temp not in ignore_words):
                arr.append(temp)
        return arr

    def handle_agg(desc):
        arr = []
        for item in desc:
            arr += chinese_word_cut(item)
        return arr

    result = df.groupby('user_id').agg({'user_id': 'min', 'desc': handle_agg})
    return result
def cut_word2(df):
    # jieba.enable_paddle()
    # ignore_flag = ['m', 'w', 'xc', 'r', 'q', 'p', 'c', 'u', 'v', 'd', 'TIME','x', 'uj', 'k', 't']
    need_flag = ['n','nr', 'ns', 'nw','vn', 'j', 'eng', 'nt', 's', 'an', 'nz','nrt', 'nrfg', 'ORG','PER','LOC']

    ignore_words = stpwrdlst

    def chinese_word_cut(text):
        text1 = re.sub(r'[^\w\s]', ' ', text).strip()

        words = pseg.cut(text1)
        arr = []
        for word, flag in words:
            temp = word.strip()
            if (flag in need_flag) and (temp not in ignore_words):
                arr.append(temp)
        return arr

        # words = jieba.cut(text)
        # arr = []
        # for word in words:
        #     temp = word.strip()
        #     if temp not in ignore_words:
        #         arr.append(temp)
        # return arr

    def handle_agg(desc):
        arr = []
        for item in desc:
            first = chinese_word_cut(item)
            second = [item for item in first if (item != '') and (len(item)>1)]
            arr += second
        return arr

    result = df.groupby('user_id').agg({'user_id': 'min', 'desc': handle_agg})
    return result
def gen_train_corpus(df):
    def handleRow(row):
        tokens = row.desc
        if len(tokens) > 0:

            return gensim.models.doc2vec.TaggedDocument(tokens, [row.user_id])
        return None

    temp = df.apply(handleRow, axis='columns')
    temp1 = temp[temp.notnull()]
    train_corpus = list(temp1)
    return train_corpus

def gen_model():
    # if os.path.isfile(file):
    #     print('删除旧文件', file)
    #     os.remove(file)
    print('从数据库中加载数据...')
    data = get_data_from_db()
    print('进行分词处理..')
    result = cut_word2(data)
    print('生成训练数据...')
    train_corpus = gen_train_corpus(result)
    print('生成模型...')
    model = gensim.models.doc2vec.Doc2Vec(vector_size=100, min_count=2, epochs=10)
    model.build_vocab(train_corpus)
    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)
    save_model(model)
    return model


def get_user(uid,db):
    user = db.execute('select * from users where user_id={}'.format(uid)).first()
    if user:
        print(user.nickname)
        print(user.signature)
    return user

def get_model():
    if os.path.exists(file):
        model = gensim.models.doc2vec.Doc2Vec.load(file)
    else:
        model = gen_model()
    return model

def gen_MatrixSimilarity():
    # if os.path.isdir(sim_dir):
    #     print('删除原来模型数据...')
    #     os.removedirs(sim_dir)
    if not os.path.exists(sim_dir):
        print('新建文件夹...')
        os.mkdir(sim_dir)
    print('从数据库中加载数据...')
    data = get_data_from_db()
    print('进行分词处理..')
    result = cut_word2(data)
    print('生成语料字典...')
    dictionary = corpora.Dictionary(result.desc)
    dictionary.save(join(sim_dir, '抖音视频.dic'))
    print('生成词袋...')
    corpus = [dictionary.doc2bow(text) for text in result.desc]
    print('生成tfidf模型...')
    tfidf = models.TfidfModel(dictionary=dictionary)
    tfidf.save(join(sim_dir,'抖音视频.tfidf'))
    print('生成lsi模型...')
    corpus_tfidf = tfidf[corpus]
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary)
    lsi.save(join(sim_dir,'抖音视频.lsi'))
    print('生成相似度索引...')
    mSimilar = similarities.MatrixSimilarity(lsi[corpus_tfidf])
    mSimilar.save(join(sim_dir,'抖音视频.mSimilar'))
    print('生成文档编号映射...')
    with open(join(sim_dir, '文档编号映射.txt'), 'a', encoding='utf-8') as f:
        for item in result.index:
            f.write(item)
            f.write('\n')
    print('完成')
    return dictionary, tfidf, lsi, mSimilar, result.index

def get_MatrixSimilarity(doc, topN=10):
    if os.path.isdir(sim_dir):
        print('加载词典...')
        dictionary = corpora.Dictionary.load(join(sim_dir, '抖音视频.dic'))
        print('加载tfidf模型...')
        tfidf = models.TfidfModel.load(join(sim_dir,'抖音视频.tfidf'))
        print('加载LSI模型...')
        lsi = models.LsiModel.load(join(sim_dir,'抖音视频.lsi'))
        print('加载相似度索引...')
        mSimilar = similarities.MatrixSimilarity.load(join(sim_dir,'抖音视频.mSimilar'))
        with open(join(sim_dir, '文档编号映射.txt')) as f:
            f_content = f.read()
            # 将停用词表转换为list
            id_Map = f_content.splitlines()
    else:
        dictionary, tfidf, lsi, mSimilar, id_Map = gen_MatrixSimilarity()

    # 把测试语料转成词袋向量
    vec_bow = dictionary.doc2bow(doc)
    # 求tfidf值
    vec_tfidf = tfidf[vec_bow]
    # 转成lsi向量
    vec_lsi = lsi[vec_tfidf]
    # 求解相似性文档
    sims = mSimilar[vec_lsi]
    print('排序后的结果：')
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    topN_sims = sims[:topN]
    result = [(id_Map[item[0]], item[1]) for item in topN_sims]
    print('相似查询结果', result)
    return result

def get_d2v(doc, topN=10):
    train_corpus = gen_train_corpus(doc)
    print('加载模型...')
    model = get_model()
    print('进行相似对比...')
    inferred_vector = model.infer_vector(train_corpus[0].words)
    sims = model.docvecs.most_similar([inferred_vector], topn=topN)
    # print('更新模型...')
    # update_model(model, train_corpus[:1])
    return sims

def get_similar(user_posts, topn=10, rate=1):
    data = DataFrame(user_posts)
    print('进行分词处理..')
    result = cut_word2(data)
    print('生成测试数据...')
    print(result.user_id)
    print(list(result.desc))
    sims_d2v=get_d2v(result, topn)
    print('d2v模型下的： ', sims_d2v)
    # sims_matrix = get_MatrixSimilarity(result.desc[0], topn)
    # print('MatrixSimilarity下的', sims_matrix)
    # res = compute_sims(sims_d2v, sims_matrix, rate)
    return sims_d2v[:topn]

def compute_sims(sims_d2v, sims_matrix, rate=0.5):
    def scale(data, range_values=(0,1)):
        first = data[1:-1] #去掉最大值和最小值，不参与放缩
        second = dict(first)
        min_num = min(second.values())
        max_num = max(second.values())
        res=[]
        for xx in first:
            temp = ((xx[1] - min_num) / (1.0*(max_num - min_num))) * (range_values[1] - range_values[0]) + range_values[0]
            res.append((xx[0], temp))
        res.insert(0,(data[0][0], 1))
        res.append((data[-1][0], 0))
        return res
    print('before', sims_d2v)
    scale_d2v = scale(sims_d2v)
    print('after', scale_d2v)
    print('before', sims_matrix)
    scale_matrix = scale(sims_matrix)
    print('after', scale_matrix)

    dict1 = dict(scale_d2v)
    dict2 = dict(scale_matrix)

    temp = dict()
    for key in dict1.keys() | dict2.keys():
        val1 = dict1.get(key,0)
        val2 = dict2.get(key,0)
        val = val1*rate+val2*(1-rate)

        temp[key] = min(val, 0.999)

    res = list(temp.items())

    res.sort(key=lambda item: -item[1])
    print('最终计算结果',res)
    return res

def get_similar_yield(user_posts, topn=10):
    data = DataFrame(user_posts)
    yield '进行分词处理..'
    result = cut_word2(data)
    yield '生成测试数据...'
    train_corpus = gen_train_corpus(result)
    yield '加载模型...'
    model = get_model()
    yield '进行相似对比...'
    inferred_vector = model.infer_vector(train_corpus[0].words)
    sims = model.docvecs.most_similar([inferred_vector], topn=topn)
    # update_model(model, train_corpus[:1])
    yield sims

def update_model(model, train_corpus):
    # tte = model.corpus_count  # total_examples参数更新
    # for item in train_corpus:
    #     tag = item.tags[0]
    #     try:
    #         temp = model[tag]
    #     except KeyError as e:
    #         tte+=1
    #         print('update_model键异常', e)
    #     except Exception as e:
    #         print('其他异常')
    print('新增数据', )
    model.build_vocab(train_corpus, update=True)
    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.epochs)  # 完成增量训练
    print('增量更新',model.corpus_count)
    save_model(model)

def save_model(model):
    model.save(file)

if __name__ == '__main__':
    # get_MatrixSimilarity(['游戏', '主播', '直播', '英雄', '王者'])
    gen_model()
    gen_MatrixSimilarity()










