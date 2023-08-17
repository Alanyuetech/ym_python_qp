# -*- coding: utf-8 -*-
"""
Created on Tue Jun 29 09:20:55 2021

@author: 86178
"""
'''录入每日基金涨幅原始数据'''
import pandas as pd
import numpy as np 
import requests
import re
from selenium import webdriver
import time
import datetime
import pymysql

delta=datetime.timedelta(days=270)
delta_56=datetime.timedelta(days=56)

now = datetime.datetime.now()

now_use=now.strftime('%Y%m%d')
delta_1=datetime.timedelta(days=1)
yesterday=now-delta_1
yesterday=yesterday.strftime('%Y%m%d')

def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    
    
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y%m%d')

after_use = (now-delta).strftime('%Y%m%d')
after_56=(now-delta_56).strftime('%Y%m%d')

url='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_56+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
url_270='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_use+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'


def essential_infor(url):
    option = webdriver.ChromeOptions()    
    option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    browser=webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe',chrome_options=option)        # 全屏
    browser.get(url)
    time.sleep(8)
    element = browser.find_element_by_css_selector('#allfund')
    browser.execute_script("arguments[0].click();",element)
    time.sleep(8)
    data=browser.page_source
    browser.quit()
    p_buy = '<td><a .*? class="buy(.*?)"'
    buy = re.findall(p_buy, data)
    p_id_num='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
    id_num=re.findall(p_id_num,data,re.S)
    p_info='<td class=.*?>(.*?)</td>'
    info=re.findall(p_info,data,re.S)
    
    p_days='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>.*?</a></td><td><a href=.*? title=.*?>.*?/a></td><td>(.*?)</td>'
    days=re.findall(p_days,data,re.S)
    p_buy = '<td><a .*? class="buy(.*?)"'
    buy = re.findall(p_buy, data)
    p_id_num='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
    id_num=re.findall(p_id_num,data,re.S)
    
    p_name='<tbody>.*?<td><a href=.*?>.*?</a></td><td><a href=".*?" title="(.*?)">.*?</a></td>'
    name=re.findall(p_name,data,re.S)
    
    bijiao=[[],[],[],[],[],[],[],[],[],[],[],[],[]]
    for i in range(len(info)):
        bijiao[i%13].append(info[i])
    
    data_final = pd.DataFrame(columns=['单位净值','累计净值','日增长率','近1周','近1月','近3月','近6月','近1年'	,'近2年'	,'近3年'	,'今年来','成立来','自定义'])
    for i in range(len(bijiao)):
        data_final.iloc[:,i]=bijiao[i]
        
    data_final['id']=id_num
    data_final['days']=days
    data_final['buy']=buy
    return data_final

def read_items(address):
    items=pd.read_csv(address,converters = {u'id':str})
    return items

data_today=essential_infor(url)
data_D270=essential_infor(url_270)

con = pymysql.connect(host='192.168.10.167',user='root',password='123456',database='all_info_data')
cursor = con.cursor()
missing=list()
already = list()

data_today_insert = data_today.copy()

def insert_info(data_today):
    i=1
    for id_num in range(len(data_today)):
        try:
            sql = 'INSERT INTO`all_info_data`.`{}` (days,ACC_price,Net_price,p_change) values ({},{},{},{});'.format(data_today.iloc[id_num,13],now_use,data_today.iloc[id_num,1],data_today.iloc[id_num,0],data_today.iloc[id_num,0])
            cursor.execute(sql)
            con.commit()
            already.append(data_today.iloc[id_num,13])
            print(data_today.iloc[id_num,13])
        except:
            missing.append(data_today.iloc[id_num,13])
        print(i)
        i+=1
        
    con.close()
insert_info(data_today_insert)