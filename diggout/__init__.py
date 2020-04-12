import pandas as pd
from pandas import DataFrame
import jieba
import jieba.analyse
import sys
import os
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import numpy as np
import urllib.request
from io import BytesIO
from pandas import Series
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pyLDAvis
import pyLDAvis.sklearn
import jieba.posseg as pseg

jieba.enable_paddle()
d = os.path.dirname(__file__)
stopwords_file = os.path.join(d,'cn_stopwords.txt')

jieba.analyse.set_stop_words(stopwords_file)

font_path = os.path.join(d, 'HuaWenYuanTi-Light-2.ttf')

save_img_dir  = os.path.join(d, '..', 'svdca', 'assets', 'img')
save_html_dir  = os.path.join(d, '..', 'svdca', 'assets', 'html')

n_features = 1000
# n_topics = 5
combine_step=50

with open(stopwords_file) as stpwrd_dic:
    stpwrd_content = stpwrd_dic.read()
    # 将停用词表转换为list
    stpwrdlst = stpwrd_content.splitlines()

def genCloudImg(data, imageUrl, uid):
    print('底图', imageUrl)
    segments = []
    for desc in data:
        words = jieba.analyse.extract_tags(desc, topK=20, withWeight=True,
                               allowPOS=('n', 'ns', 'nr', 'nz', 'nt', 'nt', 'nw', 'vn', 'an', 'eng')) #分词
        segments += words
    dfSg = DataFrame(segments, columns=['word', 'hz'])
    dfWord = dfSg.groupby('word')['hz'].sum() #生成词频
    try:
        if not imageUrl:
            imgBuf = os.path.join(d, 'default_mask.jpeg')
        else:
            r = urllib.request.urlopen(imageUrl)
            imgBuf = BytesIO(r.read())
    except Exception as e:
        print('头像加载问题', e)
        imgBuf = os.path.join(d, 'default_mask.jpeg')
    alice_mask = np.array(Image.open(imgBuf)) #用户头像作为底图
    image_colors = ImageColorGenerator(alice_mask)
    wc = WordCloud(mask=alice_mask,background_color="white", max_words=1000,
                   font_path=font_path, random_state=42,)
    wc.generate_from_frequencies(dfWord) #词频传入
    wc.recolor(color_func=image_colors) #修改颜色

    print('准备保存图片', save_img_dir)
    filename = '{}.jpg'.format(uid)
    wc.to_file(os.path.join(save_img_dir, filename)) #保存

    return os.path.join('/assets', 'html', filename)

def genLdaHtml(data, uid):
    first = Series(data).apply(chinese_word_cut) #分词
    second = first[first != '']
    third = [second[i:i + combine_step] for i in range(0, len(second), combine_step)]
    four = [' '.join(item) for item in third] #语料生成
    print(len(second), len(four))
    tf_vectorizer = CountVectorizer(strip_accents='unicode',
                                    max_features=n_features,
                                    stop_words=stpwrdlst,
                                    )
    tf = tf_vectorizer.fit_transform(four) #向量化
    n_topics = max(len(four), 5)

    lda = LatentDirichletAllocation(n_topics, max_iter=50,
                                    learning_method='batch',
                                    random_state=0)
    lda.fit(tf) #模型训练

    ldadata = pyLDAvis.sklearn.prepare(lda, tf, tf_vectorizer, mds='mmds') # mds参数传入不同的多维缩放函数。除了pcoa，其他提供的选项还有tsne和mmds
    filename = '{}.html'.format(uid)
    filepath = os.path.join(save_html_dir, filename)
    pyLDAvis.save_html(ldadata, filepath)
    return os.path.join('/assets', 'html', filename)

ignore_flag=['m', 'w', 'xc', 'r', 'q', 'p', 'c' , 'u', 'v', 'd', 'TIME']
def chinese_word_cut(text):
    # arr = jieba.analyse.extract_tags(text, topK=20, allowPOS=('n', 'ns', 'nr', 'nz', 'nt', 'nt', 'nw', 'vn', 'an', 'eng'))
    words = pseg.cut(text, use_paddle=True)
    arr = []
    for word, flag in words:
        if flag not in ignore_flag:
            arr.append(word)
    return ' '.join(arr)