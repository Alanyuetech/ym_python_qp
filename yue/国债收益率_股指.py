# -*- coding: utf-8 -*-
"""
Created on Tue Jul 19 15:29:25 2022

@author: Administrator
"""

"国债收益率_股指"


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




bond_zh_us_rate_df = ak.bond_zh_us_rate()
bond_zh_us_rate_df['日期'] = bond_zh_us_rate_df['日期'].astype('str')
us_rate_df = bond_zh_us_rate_df[['日期','美国国债收益率2年','美国国债收益率10年','美国国债收益率10年-2年']].copy().rename(
    columns={'美国国债收益率2年':'US2Y','美国国债收益率10年':'US10Y','美国国债收益率10年-2年':'US10Y-2Y'})
us_rate_df['US10Y-2Y'] = us_rate_df['US10Y'] - us_rate_df['US2Y']


"美股指数-----全局模式"
naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="20101231", end_date="22222222")

sp500_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="20101231", end_date="22222222")

dj_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
                                      period="每日", start_date="20101231", end_date="22222222")


naq_index['日期'] = naq_index['日期'].astype('str')
sp500_index['日期'] = sp500_index['日期'].astype('str')
dj_index['日期'] = dj_index['日期'].astype('str')

naq_index['纳指'] = 100*(naq_index['收盘']/naq_index['收盘'].shift(1) - 1)
sp500_index['标普'] = 100*(sp500_index['收盘']/sp500_index['收盘'].shift(1) - 1)
dj_index['道琼斯'] = 100*(dj_index['收盘']/dj_index['收盘'].shift(1) - 1)


naq_index = naq_index[['日期','纳指']]
sp500_index = sp500_index[['日期','标普']]
dj_index = dj_index[['日期','道琼斯']]


"数据聚合"


merge_data_b =  [us_rate_df,naq_index,sp500_index,dj_index]
merge_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),merge_data_b)
merge_data = merge_data[merge_data['日期']>='2010-12-31']
merge_data.iloc[:,4:] = merge_data.iloc[:,4:].fillna(method='bfill')

"国债收益率与下一日美股指数————研究"
merge_data.iloc[:,4:] = merge_data.iloc[:,4:].shift(-1)


"使用国债涨跌幅代替原始数据"
merge_data['US2Y'] = 100*(merge_data['US2Y']/merge_data['US2Y'].fillna(method='ffill').shift(1) - 1)
merge_data['US10Y'] = 100*(merge_data['US10Y']/merge_data['US10Y'].fillna(method='ffill').shift(1) - 1)
merge_data['US10Y-2Y'] = 100*(merge_data['US10Y-2Y']/merge_data['US10Y-2Y'].fillna(method='ffill').shift(1) - 1)

merge_data = merge_data.dropna(axis=0,how='any').reset_index(drop=True)



# def treasury_usind_d(merge_data,bs,nummin,nummax):
#     datas = merge_data[(merge_data['{}'.format(bs)]>=nummin)&(merge_data['{}'.format(bs)]<=nummax)]
#     data = pd.DataFrame(datas.agg('mean')).T
#     data['{}筛选下限'.format(bs)] = nummin
#     data['{}筛选上限'.format(bs)] = nummax
#     data['区间宽度'] = nummax-nummin
#     data['上下限数量'] = len(datas)
#     data['上下限数量出现概率'] = len(datas)/len(merge_data)
  
#     return data


"单边统计"
def treasury_usind_d(merge_data,num,bs,gz):
    if bs=='大于等于':
        datas = merge_data[(merge_data['{}'.format(gz)]>=num)]
    elif bs=='小于等于':
        datas = merge_data[(merge_data['{}'.format(gz)]<=num)]
               
    data = pd.DataFrame(datas.agg('mean')).T
    data['{}筛选标识'.format(gz)] = "{}{}".format(bs,num)
    data['数量'] = len(datas)
    data['出现概率'] = len(datas)/len(merge_data)
    
    if bs=='大于等于':
        data['纳指胜率'] = len(datas[datas['纳指']>0])/len(datas)
        data['标普胜率'] = len(datas[datas['标普']>0])/len(datas)
        data['道琼斯胜率'] = len(datas[datas['道琼斯']>0])/len(datas)
    elif bs=='小于等于':
        data['纳指胜率'] = len(datas[datas['纳指']>0])/len(datas)
        data['标普胜率'] = len(datas[datas['标普']>0])/len(datas)
        data['道琼斯胜率'] = len(datas[datas['道琼斯']>0])/len(datas)
        
 
    return data


"9和95依赖于  merge_vix_usind   中 VIX  的上下限"

for gz in ['US2Y','US10Y','US10Y-2Y']:
    locals()['data_treasury_usind_{}'.format(gz)] = pd.DataFrame()
    for num in range(-30,45,5):                 
        data_b = treasury_usind_d(merge_data,num,'大于等于',gz)
        locals()['data_treasury_usind_{}'.format(gz)] = locals()['data_treasury_usind_{}'.format(gz)].append(data_b)

    for num in range(-25,50,5):         
        data_b = treasury_usind_d(merge_data,num,'小于等于',gz)
        locals()['data_treasury_usind_{}'.format(gz)] = locals()['data_treasury_usind_{}'.format(gz)].append(data_b)

    locals()['data_treasury_usind_{}'.format(gz)].to_excel('{}涨跌幅--美股指数{}.xlsx'.format(gz,date_work))
    



def test_treasury_usind(days,max_limit,min_limit):
    
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

    return vix_usind_test_sum




tail_days = 250
vix_usind_test_sum = pd.DataFrame()
for nummin in range(-30,65,5):
    for nummax in range(nummin+5,70,5):
        vix_usind_test_sum_b = test_vix_usind(tail_days,nummax,nummin)
        vix_usind_test_sum = vix_usind_test_sum.append(vix_usind_test_sum_b)


  
vix_usind_test_sum.to_excel('VIX涨跌幅--美股_{}test_{}.xlsx'.format(tail_days,date_work))




























