# -*- coding: utf-8 -*-
"""
Created on Sun May 28 19:26:34 2017

@author: zanzh41414222
"""

import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

def scrapy_twitter():
    consumer_key = ""
    consumer_secret = ''
    access_token = ''
    access_secret = ''
    auth = OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token,access_secret)

        #获取流
    class MyListener(StreamListener): 
        def get_FileSize(filePath):
            
            fsize = os.path.getsize(filePath)
            fsize = fsize/float(1024*1024)
            return round(fsize,2)
        
        def on_data(self, data):
            try:
                with open('twitter.json', 'a') as f:
                    f.write(data)
                    return True
            except BaseException as e:
                print("Error on_data: %s" % str(e))
            return True       
        def on_error(self, status):
            print(status)
            return True

    try:
        api = tweepy.API(auth) #检验网络
    except:
        print('please use vpn')
    for status in tweepy.Cursor(api.home_timeline).items(2):
        print(status.text)

    twitter_stream=Stream(auth, MyListener())
    twitter_stream.filter(track=['trump'])
scrapy_twitter()
