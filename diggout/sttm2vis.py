'''
短文本主题建模，参考链接https://www.yanxishe.com/TextTranslation/2077
模型的实现工具包来源: https://github.com/rwalk/gsdmm
模型使用pyLDAvis进行交互展示
'''

# import sys
# import os
#
# cur_file_path = os.path.dirname(__file__)
# sys.path.append(cur_file_path)
from .gsdmm import MovieGroupProcess
from collections import defaultdict
import numpy as np

# 模型生成
def gen_mgp(K=10):
    mgp = MovieGroupProcess(K=K, alpha=0.1, beta=0.1, n_iters=30)
    return mgp

# 模型使用pyLDAvis可视化的数据准备
def prepare_data(origin_mgp, docs, vocab):
    mgp = clean_mgp(origin_mgp)
    temp_frequence_dict = defaultdict(int)
    zero = []
    for k, v in enumerate(mgp.cluster_word_distribution):
        if len(v) == 0:
            zero.append(k)
    print('为0的簇', zero)
    doc_topic_dists = []
    doc_length = []
    for doc in docs:
        doc_topic_dists.append([v for i, v in enumerate(mgp.score(doc)) if i not in zero])

        doc_length.append(len(doc))
        for k in doc:
            temp_frequence_dict[k] += 1

    temp_frequence = []
    for item in vocab:
        temp_frequence.append(temp_frequence_dict[item])

    topic_term_dists = []
    for idx, topic in enumerate(mgp.cluster_word_distribution):
        if idx not in zero:
            topic_term_dists_dict = defaultdict(int)
            word_count = mgp.cluster_word_count[idx]
            for k, v in topic.items():
                topic_term_dists_dict[k] = v / word_count
            topic_term_dists_item = []
            for k in vocab:
                topic_term_dists_item.append(topic_term_dists_dict[k])
            topic_term_dists.append(topic_term_dists_item)
    data = {
        'vocab': list(vocab),  # 词汇集合
        'doc_lengths': doc_length,  # 每个文档包含的单词数量
        'term_frequency': temp_frequence,  # 单词频率(顺序符合单词列表)
        'doc_topic_dists': doc_topic_dists,  # 每个文档的主题占比
        'topic_term_dists': topic_term_dists,  # 每个主题内部的单词占比(顺序符合单词列表)

    }
    return data

#清除空的集群
def clean_mgp(mgp):
    cluster_word_distribution = [item for item in mgp.cluster_word_distribution if len(item)>0]
    cluster_doc_count = [item for item in mgp.cluster_doc_count if item>0]
    cluster_word_count = [item for item in mgp.cluster_word_count if item>0]
    params = {
        'K': len(cluster_word_distribution),
        'alpha': mgp.alpha,
        'beta': mgp.beta,
        'D': mgp.number_docs,
        'vocab_size': mgp.vocab_size,
        'cluster_word_count': cluster_word_count,
        'cluster_doc_count': cluster_doc_count,
        'cluster_word_distribution': cluster_word_distribution
    }
    return mgp.from_data(**params)
def showResult(mgp):
    doc_count = np.array(mgp.cluster_doc_count)
    print('Number of documents per topic :', doc_count)
    print('*' * 20)
    # Topics sorted by the number of document they are allocated to
    top_index = doc_count.argsort()[-10:][::-1]
    print('Most important clusters (by number of docs inside):', top_index)
    print('*' * 20)


    def top_words(cluster, top_index, topN=5):
        for idx in top_index:
            print('cluster ', idx, ' : ')
            arr = sorted(cluster[idx].items(), key=lambda item: -item[1])
            print(arr[:topN])
            print('*' * 20)


    # Show the top 5 words in term frequency for each cluster
    top_words(mgp.cluster_word_distribution, top_index)