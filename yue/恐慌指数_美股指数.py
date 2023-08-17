# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 16:21:11 2022

@author: Administrator
"""

import akshare as ak
import pandas as pd
import time 
import matplotlib as mpl
from matplotlib import pyplot as plt 
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
import xlsxwriter
import openpyxl
from openpyxl.styles import PatternFill,Font,Alignment
import statsmodels.api as sm
import yfinance as yf
from functools import reduce

def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay
date_work=getLastWeekDay().strftime('%Y%m%d')
now_day = datetime.datetime.now().strftime('%Y%m%d')



# vix_index = ak.index_investing_global(country="美国", index_name="VIX恐慌指数", period="每日", start_date="20110101", end_date="22222222").rename(columns={'收盘':'VIX'})
# vix_index['日期'] = vix_index['日期'].astype('str')
# vix_index = vix_index[['日期','VIX']]





vix_index = ak.index_investing_global(country="美国", index_name="VIX恐慌指数", period="每日", start_date="20101231", end_date="22222222")
vix_index['日期'] = vix_index['日期'].astype('str')
vix_index['VIX'] = 100*(vix_index['收盘']/vix_index['收盘'].shift(1) - 1)
vix_index = vix_index[['日期','VIX']]






"美股指数-----全局模式"
naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="20110101", end_date="22222222")

sp500_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="20110101", end_date="22222222")

dj_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
                                      period="每日", start_date="20110101", end_date="22222222")


naq_index['日期'] = naq_index['日期'].astype('str')
sp500_index['日期'] = sp500_index['日期'].astype('str')
dj_index['日期'] = dj_index['日期'].astype('str')


"每日涨跌幅=当日收盘价/前日收盘价 - 1"
# naq_index['纳指'] = 100*(naq_index['收盘']/naq_index['收盘'].shift(1) - 1)
# sp500_index['标普'] = 100*(sp500_index['收盘']/sp500_index['收盘'].shift(1) - 1)
# dj_index['道琼斯'] = 100*(dj_index['收盘']/dj_index['收盘'].shift(1) - 1)



"每日涨跌幅=当日收盘价/当日开盘价 - 1"
naq_index['纳指'] = 100*(naq_index['收盘']/naq_index['开盘'] - 1)
sp500_index['标普'] = 100*(sp500_index['收盘']/sp500_index['开盘'] - 1)
dj_index['道琼斯'] = 100*(dj_index['收盘']/dj_index['开盘'] - 1)




naq_index = naq_index[['日期','纳指']]
sp500_index = sp500_index[['日期','标普']]
dj_index = dj_index[['日期','道琼斯']]

"数据聚合"

merge_vix_usind_b =  [vix_index,naq_index,sp500_index,dj_index]
merge_vix_usind = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),merge_vix_usind_b)
merge_vix_usind = merge_vix_usind.dropna(axis=0,how='any')
"VIX与下一日美股指数————研究"
merge_vix_usind.iloc[:,2:] = merge_vix_usind.iloc[:,2:].shift(-1)
merge_vix_usind = merge_vix_usind.dropna(axis=0,how='any').reset_index(drop=True)


def vix_usind_d(merge_vix_usind,nummin,nummax):
    datas = merge_vix_usind[(merge_vix_usind['VIX']>=nummin)&(merge_vix_usind['VIX']<=nummax)]
    data = pd.DataFrame(datas.agg('mean')).T
    data['VIX筛选下限'] = nummin
    data['VIX筛选上限'] = nummax
    data['区间宽度'] = nummax-nummin
    data['上下限数量'] = len(datas)
    data['上下限数量出现概率'] = len(datas)/len(merge_vix_usind)
  
    return data

"9和95依赖于  merge_vix_usind   中 VIX  的上下限"
data_vix_usind = pd.DataFrame()
for nummin in range(-30,65,5):
    for nummax in range(nummin+5,70,5):
        data_b = vix_usind_d(merge_vix_usind,nummin,nummax)
        data_vix_usind = data_vix_usind.append(data_b)

data_vix_usind.to_excel('VIX涨跌幅--美股指数{}.xlsx'.format(date_work))



"将下方输出为df"
odds_df = pd.DataFrame(columns=(['指数']))
for i in range(3):
    odds_df.loc[i,'指数'] = data_vix_usind.columns[i+1]
    odds_df.loc[i,'胜率(>15)'] = len(merge_vix_usind[(merge_vix_usind['VIX']>=15)&
                                             (merge_vix_usind['{}'.format(data_vix_usind.columns[i+1])]>=0)])/len(merge_vix_usind[merge_vix_usind['VIX']>=15])
    
    
    
    
    
    odds_df.loc[i,'胜率(<-13)'] = len(merge_vix_usind[(merge_vix_usind['VIX']<=-13)&
                                             (merge_vix_usind['{}'.format(data_vix_usind.columns[i+1])]<0)])/len(merge_vix_usind[merge_vix_usind['VIX']<=-13])

    
    
odds_df.to_excel('VIX涨跌幅--美股胜率{}.xlsx'.format(date_work))




def test_vix_usind(days,max_limit,min_limit):
    
    "策略测试----最近days个工作日"
    vix_usind_test = merge_vix_usind.tail(days).copy()
    vix_usind_test['纳指test'] = 0
    vix_usind_test['标普test'] = 0
    vix_usind_test['道琼斯test'] = 0
    
    for index,row in vix_usind_test.iterrows():
    
        if row['VIX']>=max_limit:
            vix_usind_test.loc[index,'纳指test'] = row['纳指']
            vix_usind_test.loc[index,'标普test'] = row['标普']
            vix_usind_test.loc[index,'道琼斯test'] = row['道琼斯']
        elif row['VIX']<min_limit:
            vix_usind_test.loc[index,'纳指test'] = -row['纳指']
            vix_usind_test.loc[index,'标普test'] = -row['标普']
            vix_usind_test.loc[index,'道琼斯test'] = -row['道琼斯']
        else:
            pass
    
    
    vix_usind_test_sum = pd.DataFrame(vix_usind_test.iloc[:,1:].sum()).T
    
    vix_usind_test_sum['纳指alpha'] = vix_usind_test_sum['纳指test']-vix_usind_test_sum['纳指']
    vix_usind_test_sum['标普alpha'] = vix_usind_test_sum['标普test']-vix_usind_test_sum['标普']
    vix_usind_test_sum['道琼斯alpha'] = vix_usind_test_sum['道琼斯test']-vix_usind_test_sum['道琼斯']
    
    
    vix_usind_test_sum['days'] = days
    vix_usind_test_sum['max_limit'] = max_limit
    vix_usind_test_sum['min_limit'] = min_limit
    
    vix_usind_test_sum['操作频率'] = len(vix_usind_test[(vix_usind_test['VIX']>=max_limit)|(vix_usind_test['VIX']<min_limit)])/days


    return vix_usind_test_sum



tail_days_list = [5,10,20,60,120,250,600]
for tail_days in tail_days_list:
    
    # tail_days = 250   单独测试的时候允许以下内容
    vix_usind_test_sum = pd.DataFrame()
    for nummin in range(-30,65,5):
        for nummax in range(nummin+5,70,5):
            vix_usind_test_sum_b = test_vix_usind(tail_days,nummax,nummin)
            vix_usind_test_sum = vix_usind_test_sum.append(vix_usind_test_sum_b)
    
    
      
    vix_usind_test_sum.to_excel('VIX涨跌幅--美股_{}test_{}.xlsx'.format(tail_days,date_work))













