# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 10:44:01 2021

@author: Administrator
"""



"实时A股成交额"


import akshare as ak
import pandas as pd
import time 
import numpy as np
import datetime


"读取各个指数成分股文件"
cfg_000001 = pd.read_excel('cfg_000001.xlsx',engine='openpyxl',dtype={'代码':'str'})
cfg_399001 = pd.read_excel('cfg_399001.xlsx',engine='openpyxl',dtype={'代码':'str'})
cfg_399006 = pd.read_excel('cfg_399006.xlsx',engine='openpyxl',dtype={'代码':'str'})
cfg_000300 = pd.read_excel('cfg_000300.xlsx',engine='openpyxl',dtype={'代码':'str'})
cfg_399905 = pd.read_excel('cfg_399905.xlsx',engine='openpyxl',dtype={'代码':'str'})
cfg_000016 = pd.read_excel('cfg_000016.xlsx',engine='openpyxl',dtype={'代码':'str'})

"基金代码前面补0"
for i in ['cfg_000001','cfg_399001','cfg_399006','cfg_000300','cfg_399905','cfg_000016']:
    locals()['{}'.format(i)]['代码'] = locals()['{}'.format(i)]['代码'].map(lambda x:'00000'+x if len(x)==1 else
                                      ('0000'+x if len(x)==2 else 
                                       ('000'+x if len(x)==3 else
                                        ('00'+x if len(x)==4 else
                                         ('0'+x if len(x)==5 else x)))))




def sleep_time(hour,minu,sec):
    return hour*3600+minu*60+sec

def turnover():
    "A股所有股票数据"
    a_stock = ak.stock_zh_a_spot_em()
    
    
    "A股所有股票成交额"
    a_stock_turnover = a_stock['成交额'].sum()/100000000
    
    "上证指数实时成交额"
    a_stock_sh = pd.merge(left=cfg_000001,right=a_stock,on='代码')
    a_stock_sh_turnover = a_stock_sh['成交额'].sum()/100000000
    
    
    
    a_stock_sh_turnover = a_stock_sh[a_stock_sh['代码'].str.slice(0,1)=='6']['成交额'].sum()/100000000
    
    "创业板指实时成交额"
    a_stock_cyb = pd.merge(left=cfg_399006,right=a_stock,on='代码')
    a_stock_cyb_turnover = a_stock_cyb['成交额'].sum()/100000000
    
    
    "深证指数实时成交额"
    a_stock_sz = pd.merge(left=cfg_399001,right=a_stock,on='代码')
    a_stock_sz_turnover = a_stock_sz['成交额'].sum()/100000000
    
    
    
    a_stock_sz_turnover = a_stock_sz[a_stock_sz['代码'].str.slice(0,1)=='0']['成交额'].sum()/100000000

    "沪深300指数实时成交额"
    a_stock_hs300 = pd.merge(left=cfg_000300,right=a_stock,on='代码')
    a_stock_hs300_turnover = a_stock_hs300['成交额'].sum()/100000000

    "中证500指数实时成交额"
    a_stock_zz500 = pd.merge(left=cfg_399905,right=a_stock,on='代码')
    a_stock_zz500_turnover = a_stock_zz500['成交额'].sum()/100000000

    "上证50指数实时成交额"
    a_stock_szh50 = pd.merge(left=cfg_000016,right=a_stock,on='代码')
    a_stock_szh50_turnover = a_stock_szh50['成交额'].sum()/100000000


    print("A股所有股票成交额:{}亿    \n上证指数实时成交额:{}亿   \n深证指数实时成交额:{}亿   \n创业板指实时成交额:{}亿  \n沪深300指数实时成交额:{}亿  \n上证50指数实时成交额:{}亿  \n中证500指数实时成交额:{}亿"
          .format(a_stock_turnover,a_stock_sh_turnover,a_stock_sz_turnover,a_stock_cyb_turnover,a_stock_hs300_turnover,a_stock_zz500_turnover,a_stock_szh50_turnover))
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    
    
    
    



"新浪数据源慢一些"
def turnover_sina():
    "A股所有股票数据"
    a_stock = ak.stock_zh_index_spot()
    a_stock_index = a_stock[(a_stock['名称']=='上证指数')|(a_stock['名称']=='深证成指')|(a_stock['名称']=='沪深300')|(a_stock['名称']=='中证500')|(a_stock['名称']=='上证50')]
    print(a_stock_index)



second = sleep_time(0,0,7)
while True:
    time.sleep(second)
    turnover()
