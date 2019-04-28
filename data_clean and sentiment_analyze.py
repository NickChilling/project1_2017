# -*- coding: utf-8 -*-
"""
Created on Fri Jun 9 09:42:20 2017

@author: zanzh
"""

from textblob import TextBlob as tb
from matplotlib import pyplot as plt 
import pandas as pd
import re 
import numpy as np
import json

#清理reddit中数据
def data_cleanr():
  
    #读取json文件
    reddit=[] 
    for line in open('reddit.json','r'):  
        reddit.append(json.loads(line))
    data = pd.DataFrame(reddit)

    #逐条读取comments
    comment=[]
    for ro in data.comments:
        for paren in ro:
            comment.append(paren)

    #将comment 中的list 转化为str
    comment = pd.DataFrame(comment)
    comment.post_date = [str(date[0:1]) for date in comment.post_date]
    comment.score = [str(sore[0:1]) for sore in comment.score] 
    comment.text = [str(date[0:1]) for date in comment.text]

    
    #去除多余的列
    comment = comment.drop(['user','parent','commentID'],axis=1)   

    #清理时间序列
    time = [str(tim[12:20]) for tim in comment.post_date]
    comment.post_date = time
    
    #确认时间数据类型
    #for date in comment.post_date:  
    #    print(type(date))

    #去除所有TEXT中空值
    comment[comment.score=='[]'] = np.nan   
    comment = comment.dropna()
    
    #删除TEXT中发送图片和网址的评论
    comment[comment.text.str.contains('a href')==True ] =np.nan
    comment = comment.dropna()

    #删除TEXT中带标题字段
    comment[comment.text.str.contains('<blockquote>')==True ] =np.nan
    comment = comment.dropna()

    #清理text文本
    tex_behind = [te.split('</')[0] for te in comment.text]
    tex_front = [te.split('>')[2] for te in tex_behind]
    comment.text = tex_front
 
    #定义表情
    emotion_full = re.compile(r'.*<[a-zA-Z0-9]*')
    emotion = re.compile(r'<[a-zA-Z0-9]*')
    
    #将表情字段删除
    emo = []
    for line in comment['text']:
        if emotion_full.match(line):
            emo.append(re.sub(emotion,'',str(line)))
        else:
            emo.append(line)
    comment.text = emo
    #提取SCORE中数值，并转换为int
    mark_with = [mar.split(' ')[0] for mar in comment.score]
    mark =[ int(m1.split("'")[1]) for m1 in mark_with]
    comment.score = mark

    #确认score数据类型 
    #for i in comment.score:
    #print(type(i))
    #将清理好的数据储存
    comment.to_csv('reddit_cleaned.csv')

#对twitter中数据进行清理
def data_cleant():
    twitter = []
    count=0
    for line in open('twitter.json','r'):
        if count%2 ==0:
            twitter.append(json.loads(line))
        count += 1
    twitter = pd.DataFrame(twitter)
    twitter = twitter[['created_at','text']]
    

    #定义需清理的字段
    #网址
    http = re.compile(r'https://.*')
    #@对象 字符串
    quote = re.compile(r'@.*:')
    #标点
    punc =re.compile(r'[@#]+')
    
    #清理字段
    twitter.text = [re.sub(http,'',str(line)) for line in twitter.text]
    twitter.text = [line.strip('RT ') for line in twitter.text]
    twitter.text = [re.sub(quote,'',str(line)) for line in twitter.text]
    twitter.text = [re.sub(punc,'',str(line)) for line in twitter.text]
    #清理空值
    twitter[twitter.text==''] = np.nan
    twitter = twitter.dropna()


    #将清理好的数据储存
    twitter.to_csv('twitter_cleaned.csv')  

#情感分析
def sentiment_analyze():
    rdt_sa = pd.read_csv('reddit_cleaned.csv',encoding = 'gbk')
    twi_sa = pd.read_csv('twitter_cleaned.csv',encoding = 'gbk' )
    
    #计算情感极性
    rdt_sa['sentiment'] = [tb(str(line)).sentiment.polarity for line in rdt_sa.text]
    twi_sa['sentiment'] = [tb(str(line)).sentiment.polarity for line in twi_sa.text]
    #计算主\客观程度
    rdt_sa['subjectivity'] = [tb(str(line)).sentiment.subjectivity for line in rdt_sa.text]
    twi_sa['subjectivity'] = [tb(str(line)).sentiment.subjectivity for line in twi_sa.text]
    
    #对reddi中 评论socore +1  以表示这种情感的频率
    rdt_sa['score'] = [ i+1 for i in rdt_sa.score]
    
    
    # 将 情感极性和主客观程度都为 0 的数据删除   这部分数据存在问题
    rdt_sa[(rdt_sa.subjectivity == 0 ) & (rdt_sa.sentiment == 0)] = np.nan   
    rdt_sa = rdt_sa.dropna()
    
    twi_sa[(twi_sa.subjectivity == 0 ) & (twi_sa.sentiment == 0)] = np.nan   
    twi_sa = twi_sa.dropna()
    
    
    
    #将unnamed 栏重新按序列赋值,并将其设为索引
    rdt_sa['Unnamed: 0'] =np.arange(len(rdt_sa))
    rdt_sa = rdt_sa.set_index('Unnamed: 0')
    twi_sa['Unnamed: 0'] =np.arange(len(twi_sa))
    twi_sa = twi_sa.set_index('Unnamed: 0')
    
    
    print('reddit数据',rdt_sa.head(5),'\n','twitter数据',twi_sa.head(5),'\n')
    rect_senti = []
    rect_sub = []
    twi_senti = []
    twi_sub = []
    count1 = 0
    count2 = 0

        #在reddit 中因为有vote 存在，所以将vote的score 将sentiment的频率加权
    for senti in rdt_sa.sentiment:
        if rdt_sa.score[count1]>0:
            x1 = np.arange(rdt_sa.score[count1])
            for i in x1:
                rect_senti.append(senti)
                
        #如果vote 的score是负数，则将其score+1（前面已经处理）  以其score加权频率 并返回其情感的负数
        if rdt_sa.score[count1]<0:
            x2 = np.arange(rdt_sa.score[count1]*(-1))
            for l in x2:
                rect_senti.append(senti*(-1))
    
    
        #subjectivity 也是同理
    for subj in rdt_sa.subjectivity:
        if rdt_sa.score[count2]>0:
            x3 = np.arange(rdt_sa.score[count2])
            for i in x3:
                rect_sub.append(subj)
        #如果vote 的score是负数，则将其score+1（前面已经处理）  以其score加权频率 并返回其情感的负数
        if rdt_sa.score[count2]<0:
            x4 =np.arange(rdt_sa.score[count2]*(-1))
            for l in x4:
                rect_sub.append((1-subj))
        count2 += 1
        
    #将twitter中数据也转为list
    for senti in twi_sa.sentiment:
        twi_senti.append(senti)
    for subj in twi_sa.subjectivity:
        twi_sub.append(subj)  
        
    #画分布饼图
    #reddit frequency
    reddi_pos = 0
    reddi_neg = 0
    reddi_neu = 0
    reddi_obj = 0
    reddi_subj = 0
    for i in rect_senti:
        if i > 0:
            reddi_pos += 1
        if i == 0:
            reddi_neu += 1
        if i < 0:
            reddi_neg += 1
    for i in rect_sub:
        if i >= 0.5:
            reddi_subj += 1
        if i < 0.5:
            reddi_obj += 1
    #twitter frequency
    twi_pos = 0
    twi_neg = 0
    twi_neu = 0
    twi_obj = 0
    twi_subj = 0
    for i in twi_senti:
        if i > 0:
            twi_pos += 1
        if i == 0:
            twi_neu += 1
        if i < 0:
            twi_neg += 1
    for i in twi_sub:
        if i >= 0.5:
            twi_subj += 1
        if i < 0.5:
            twi_obj += 1
    '''
    #开始画图sentiment
    plt.figure(1)
    plt.subplot(121)
    labels1 = 'positive','negative','neutral'
    sizes1 = [reddi_pos,reddi_neg,reddi_neu]
    colors1 = ['red','yellowgreen','lightskyblue']
    plt.pie(sizes1,labels=labels1,colors=colors1,autopct='%1.1f%%',shadow=True,startangle=90)
    plt.title('F1-Reddit-1')
    plt.axis('equal')
        #subjectivity
    plt.subplot(122)
    labels2 = 'reddit_objective','reddit_subject'
    sizes2 = [reddi_obj,reddi_subj]
    colors2 = ['green', 'gold']
    plt.pie(sizes2,labels=labels2,colors=colors2,autopct='%1.1f%%',shadow=True,startangle=90)
    plt.title('F1-Reddit-2')
    plt.axis('equal')
    
    #画twitter 图
    #开始画图sentiment
    plt.figure(2)
    plt.subplot(121)
    labels3 = 'positive','negative','neutral'
    sizes3 = [twi_pos,twi_neg,twi_neu]
    plt.pie(sizes3,labels=labels3,colors=colors1,autopct='%1.1f%%',shadow=True,startangle=90)
    plt.title('F2-Twitter-1')
    plt.axis('equal')
    
    #subjectivity
    plt.subplot(122)
    labels4 = 'objective','subject'
    sizes4 = [twi_obj,twi_subj]
    plt.pie(sizes4,labels=labels4,colors=colors2,autopct='%1.1f%%',shadow=True,startangle=90)
    plt.title('F2-Twitter-2')
    plt.axis('equal')     
        
        
    #reddit sentiment 的直方图 
    plt.figure(3)
    plt.subplot(321)
    reddit_p1 = np.array(rect_senti) 
    plt.hist(reddit_p1, bins = np.arange(-1,1,0.1))
    plt.title("F3-Reddit-1") 
        #reddit subjectivity 的直方图
    plt.subplot(325)
    reddit_p2 = np.array(rect_sub) 
    plt.hist(reddit_p2, bins = np.arange(0,1,0.05))
    plt.title("F3-Reddit-2") 
      
    #画twitter sentiment中的直方图
    plt.subplot(322)
    twitter_p1 = np.array(twi_senti) 
    plt.hist(twitter_p1, bins = np.arange(-1,1,0.1))
    plt.title("F3-Twitter-1") 
    
    # twitter subjectivity的直方图
    plt.subplot(326)
    twitter_p2 = np.array(twi_sub) 
    plt.hist(twitter_p2, bins = np.arange(0,1,0.05))
    plt.title("F3-Twitter-2")     
    plt.show()
    '''
    print('reddit平均情感分数为%s' % np.mean(rect_senti),'\n')
    print('reddit平均主观程度为%s' % np.mean(rect_sub),'\n')
    print('twitter平均情感分数为%s' % np.mean(twi_senti),'\n')
    print('twitter平均主观程度为%s' % np.mean(twi_sub),'\n')
data_cleanr()
data_cleant()
sentiment_analyze()