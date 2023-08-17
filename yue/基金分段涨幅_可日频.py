# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 15:38:41 2022

@author: Administrator
"""



import pandas as pd
import numpy as np
import requests
import re
from selenium import webdriver
import time
import datetime
import pymysql
import akshare as ak
def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay
date_work=getLastWeekDay().strftime('%Y%m%d')

delta_56=datetime.timedelta(days=60)

now = datetime.datetime.now()
now_use=now.strftime('%Y%m%d')

after_56=(now-delta_56).strftime('%Y%m%d')


url='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_56+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'



'''每日基金的基本信息'''
def essential_infor(url):
    # option = webdriver.ChromeOptions()
    # option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    # browser=webdriver.Chrome(chrome_options=option)        # 全屏
    
    option = webdriver.ChromeOptions()    
    option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    browser=webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe',chrome_options=option)        # 全屏

    browser.get(url)
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
    
    data_final = pd.DataFrame(columns=['单位净值','累计净值','D1','D7','D30','D90','D180','D360','D720','近3年','今年来','成立来','D60'])
    for i in range(len(bijiao)):
        data_final.iloc[:,i]=bijiao[i]
        
    data_final['id']=id_num
    data_final['days']=days
    data_final['buy']=buy
    return data_final



data_today=essential_infor(url)

data_today.to_excel('基金D60_{}.xlsx'.format(date_work))


