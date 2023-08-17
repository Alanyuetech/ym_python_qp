# -*- coding: utf-8 -*-
"""
Created on Fri Jan 21 14:32:10 2022

@author: Administrator
"""


"美股回撤选股"

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


"读取股票代码列表"
stock_list = pd.read_excel('美股200亿以上筛选.xlsx',engine='openpyxl')
stock_list = stock_list.rename(columns={'代码':'stock_id'})
stock_50b_list = stock_list[stock_list['总市值-亿']>=200]      #此处修改 >200亿   >500亿


"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_50b_list = pd.merge(stock_50b_list,us_stock[['代码','stock_id']],how='left',on='stock_id')


stock_50b_list.drop(stock_50b_list[pd.isna(stock_50b_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
stock_50b_list = stock_50b_list.reset_index(drop=True)

# "模糊查询"
# aa = us_stock.loc[us_stock['名称'].str.contains('小米')]
# aa = us_stock.loc[us_stock['代码'].str.contains('BF_')]

"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_50b_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20130101", end_date="22220101", adjust="hfq")
    stock_data_b['代码']=row['代码']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])

stock_data = stock_data.sort_values(['代码','日期'],ascending=[1,1]).reset_index(drop=True)

def drawback(stock_data,n,x):
    "stock_data————全体数据"
    "n————过去n个交易日"
    "x————回撤幅度x%"
    "通过算法筛选出参数范围下符合回撤要求的股票"
    df = stock_data.groupby('代码').head(120).reset_index(drop=True)
    
    
    
    
    
    
    
    
    
    
    
    return stock_list





"所有股票回撤   （价值股回撤）"
###################################################################################################################








###################################################################################################################





"新股回撤"
###################################################################################################################


"新股"   #需要的是所有200亿以上的股票池

"通过下方代码选新股范围，复制到富途牛牛后手动删除不符合要求的股票，最后形成  新股列表观察.xlsx"
new_stock_50b_list = stock_data.groupby(by='代码').head(1)   #拿到第一个交易日
new_stock_50b_list = new_stock_50b_list[new_stock_50b_list['日期']>='2021-06-01']
new_stock_50b_list['代码'] = new_stock_50b_list['代码'].str.split('.',expand=True)[1]  #分列
new_stock_50b_list.to_excel('新股列表观察{}.xlsx'.format(now_day))



new_stock_list =  pd.read_excel('新股列表观察.xlsx',engine='openpyxl',dtype={'时间':'str'})
new_stock_list = pd.merge(new_stock_list,stock_50b_list[['stock_id','代码']],on='stock_id',how='left')




###################################################################################################################

"计算历史最高点到当前价格的回撤"


"读取股票代码列表"
stock_list = pd.read_excel('新股回撤_目标股票20220214.xlsx',engine='openpyxl')
stock_list = stock_list.rename(columns={'代码':'stock_id'})
stock_50b_list = stock_list[stock_list['总市值-亿']>=200]      #此处修改 >200亿   >500亿


"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_50b_list = pd.merge(stock_50b_list,us_stock[['代码','stock_id']],how='left',on='stock_id')


stock_50b_list.drop(stock_50b_list[pd.isna(stock_50b_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
stock_50b_list = stock_50b_list.reset_index(drop=True)

"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_50b_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20110101", end_date="22220101", adjust="")
    stock_data_b['代码']=row['代码']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])



def drawback_db(idd,stock_data):
    ans = stock_data[stock_data['代码']==idd]
    ans_max = ans['收盘'].max()
    db = 1 - ans.tail(1).reset_index(drop=True).loc[0,'收盘']/ans_max        
    return db


drawback = pd.DataFrame()
"计算出股票距离最高点的回撤"
for index,row in stock_50b_list.iterrows():
    drawback_b = pd.DataFrame()
    drawback_b.loc[0,'代码'] = row['代码']
    drawback_b.loc[0,'drawback'] = drawback_db(row['代码'],stock_data)
    drawback = drawback.append(drawback_b)

drawback.to_excel("新股回撤_目标股票回撤{}.xlsx".format(date_work))  







###################################################################################################################




