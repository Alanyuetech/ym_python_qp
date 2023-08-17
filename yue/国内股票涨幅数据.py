# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 13:10:39 2022

@author: Administrator
"""


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
from functools import reduce
import statsmodels.api as sm
from itertools import *
time_start = time.time()

def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay
date_work=getLastWeekDay().strftime('%Y%m%d')

def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:str(x).zfill(6))
    return fund_id

stock_id = pd.read_excel('8-1至今涨幅.xlsx',engine='openpyxl',dtype={'code':'str'})  
stock_id = bu_zero(stock_id,'代码')

stock_data = pd.DataFrame()
for index,row in stock_id.iterrows():
    stock_data_b =  ak.stock_zh_a_hist(symbol=row['代码'], period="daily", start_date="20220801", end_date='22222222',
                                        adjust="")
    stock_data_b = stock_data_b[['日期','涨跌幅']].rename(columns={'涨跌幅':'{}'.format(row['代码'])})
    
    if index==0:
        stock_data = stock_data_b.copy()
    else:
        stock_data = pd.merge(stock_data,stock_data_b,on='日期',how='outer')
    print(index,row['代码'])


#最后一列加个合计
stock_data.loc['Row_sum'] = stock_data.apply(lambda x: x.sum())


    
stock_data.to_excel('股票涨幅{}.xlsx'.format(date_work))