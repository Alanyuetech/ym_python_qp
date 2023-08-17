# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 16:08:30 2022

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

num = '290014'
fund_id = pd.read_excel('名单.xlsx',engine='openpyxl',dtype={'id':'str'})[['id']]

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

def get_aad(num):
    
    url = 'http://fundf10.eastmoney.com/zcpz_'+num+'.html'
    r = requests.get(url,headers=headers)
    r.encoding='utf-8'
    data=r.text
    html=r.content
    
    data = requests.get(url,headers=headers).text
    
    data=data.replace(" ",'')
    data=data.replace('\n','').replace('\r','')
    

    p_standard_deviation='净资产（亿元）</th></tr></thead><tbody><tr><td>(.*?)</td><tdclass="tor">(.*?)</td><tdclass="tor">(.*?)</td><tdclass="tor">(.*?)</td><tdclass="tor">(.*?)</td>'
    
    
    data_SD=re.findall(p_standard_deviation, data)
    
    data_SD=[x for x in data_SD[0]]
    
    data_info=pd.DataFrame()
    data_info.loc[0,'基金代码']=num
    data_info.loc[0,'报告期']=data_SD[0]
    data_info.loc[0,'股票占净比']=data_SD[1]
    data_info.loc[0,'债券占净比']=data_SD[2]
    data_info.loc[0,'现金占净比']=data_SD[3]
    data_info.loc[0,'净资产（亿元）']=data_SD[4]

    return data_info

fund_aad = pd.DataFrame()
fund_aad_erro = pd.DataFrame()
fund_aad_erro_1 = pd.DataFrame()


for index,row in fund_aad_erro[:].iterrows():
    try:
        fund_aad_b = get_aad(row['id'])
        fund_aad = fund_aad.append(fund_aad_b)
        print(index,row['id'])

    except:
        fund_aad_erro_1.loc[index,'id'] = row['id']
        print(index,row['id'],'错误')
        
        
        
fund_aad.to_excel('股票占净比.xlsx')















































