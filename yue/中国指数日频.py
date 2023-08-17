# -*- coding: utf-8 -*-
"""
Created on Mon May 30 12:13:17 2022

@author: 666
"""



import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime

now_day = datetime.datetime.now().strftime('%Y%m%d')
from datetime import *
def getLastWeekDay(day=datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - timedelta(days=dayStep)
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y%m%d')


"股指  分时数据  "

sz_index = ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20220101", end_date="22220101").rename(columns={'收盘':'上证'})[['日期','上证']]
shz_index = ak.index_zh_a_hist(symbol="399001", period="daily", start_date="20220101", end_date="22220101").rename(columns={'收盘':'深证'})[['日期','深证']]
hs300_index = ak.index_zh_a_hist(symbol="000300", period="daily", start_date="20220101", end_date="22220101").rename(columns={'收盘':'沪深300'})[['日期','沪深300']]
cyb_index = ak.index_zh_a_hist(symbol="399006", period="daily", start_date="20220101", end_date="22220101").rename(columns={'收盘':'创业板'})[['日期','创业板']]

index = pd.merge(sz_index,shz_index,on='日期')
index = pd.merge(index,hs300_index,on='日期')
index = pd.merge(index,cyb_index,on='日期')

index.to_excel('中国指数日频{}.xlsx'.format(date_work),index=False)