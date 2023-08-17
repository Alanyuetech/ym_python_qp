# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 18:02:37 2022

@author: 666
"""

"美股基本面因子研究"


import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
import xlsxwriter
import openpyxl
from openpyxl.styles import PatternFill,Font,Alignment

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




"开全局模式"
# aa = ak.stock_us_fundamental(symbol="info")



"股票名单"
stock_list = pd.read_excel('美股200亿以上筛选.xlsx',engine='openpyxl')
stock_list = stock_list.rename(columns={'代码':'stock_id'})

"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_list = pd.merge(stock_list,us_stock[['代码','stock_id']],how='left',on='stock_id')


stock_list.drop(stock_list[pd.isna(stock_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
stock_list = stock_list.reset_index(drop=True)

stock_list = stock_list.loc[:9,:]
"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20110101", end_date="22220101", adjust="")  #这里使用不复权的数据
    stock_data_b['代码']=row['代码']
    stock_data_b['stock_id'] = row['stock_id']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])

stock_data['日期'] =  stock_data['日期'].apply(lambda x:int(x[0:4]+x[5:7]+x[8:]))
print('股票数据完成')
#################################################################################################################################
"下一个模块需要受到打开全局模式"

pe_data = pd.DataFrame()
pe_erro = list()
for index,row in stock_list.iterrows():
    try:
        pe_data_b = ak.stock_us_fundamental(stock='{}'.format(row['stock_id']), symbol="PE")
        pe_data_b = pe_data_b[pe_data_b['date']>='2011-01-01']
        pe_data_b['代码']=row['代码']
        pe_data_b['stock_id'] = row['stock_id']
        pe_data = pe_data.append(pe_data_b)
        print(index,row['stock_id'])
    except:
        pe_erro.append(row['stock_id'])
        print(index,row['stock_id'],'错误')  

pe_data['date'] =  pe_data['date'].apply(lambda x:int(x[0:4]+x[5:7]+x[8:]))  
pe_data  = pe_data.rename(columns={'date':'日期'})                
print('EPS数据完成')



#################################################################################################################################
"通过EPS计算每天的PE值"
stock_data = pd.merge(stock_data[['日期','收盘','代码','stock_id']],pe_data,on=['日期','代码','stock_id'],how='left')
stock_data['ttm_net_eps'] = stock_data.groupby('stock_id')['ttm_net_eps'].fillna(method='ffill')

stock_data['ttm_net_eps'] = stock_data['ttm_net_eps'].astype('str')
stock_data = stock_data[stock_data['ttm_net_eps']!='nan']

stock_data['eps'] = stock_data['ttm_net_eps'].astype('str').str.replace('$','').astype('float')
stock_data['pe'] = stock_data['收盘']/stock_data['eps']












































