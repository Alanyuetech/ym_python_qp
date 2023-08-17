# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 15:47:22 2022

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



d7 = (datetime.datetime.now()-datetime.timedelta(days=7)).strftime('%Y-%m-%d')
d30 = (datetime.datetime.now()-datetime.timedelta(days=30)).strftime('%Y-%m-%d')
d60 = (datetime.datetime.now()-datetime.timedelta(days=60)).strftime('%Y-%m-%d')
d90 = (datetime.datetime.now()-datetime.timedelta(days=90)).strftime('%Y-%m-%d')
d120 = (datetime.datetime.now()-datetime.timedelta(days=120)).strftime('%Y-%m-%d')
d180 = (datetime.datetime.now()-datetime.timedelta(days=180)).strftime('%Y-%m-%d')
d270 = (datetime.datetime.now()-datetime.timedelta(days=270)).strftime('%Y-%m-%d')
d360 = (datetime.datetime.now()-datetime.timedelta(days=360)).strftime('%Y-%m-%d')
d540 = (datetime.datetime.now()-datetime.timedelta(days=540)).strftime('%Y-%m-%d')
d720 = (datetime.datetime.now()-datetime.timedelta(days=720)).strftime('%Y-%m-%d')




"中国指数"

sz_index = ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20161230", end_date="22220101").rename(columns={'涨跌幅':'上证'})[['日期','上证']]
shz_index = ak.index_zh_a_hist(symbol="399001", period="daily", start_date="20170101", end_date="22220101").rename(columns={'涨跌幅':'深证'})[['日期','深证']]
hs300_index = ak.index_zh_a_hist(symbol="000300", period="daily", start_date="20161230", end_date="22220101").rename(columns={'涨跌幅':'沪深300'})[['日期','沪深300']]
cyb_index = ak.index_zh_a_hist(symbol="399006", period="daily", start_date="20161230", end_date="22220101").rename(columns={'涨跌幅':'创业板'})[['日期','创业板']]



data_b =  [sz_index,shz_index,hs300_index,cyb_index]
data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),data_b).sort_values('日期',ascending=0).reset_index(drop=True)

def index_interval(index_data,start_date,bs):
    index_data_b = index_data[index_data['日期']>=start_date]
    ans_b = pd.DataFrame(index_data_b.iloc[:,1:].sum()).rename(columns={0:'{}'.format(bs)}).reset_index()
    return ans_b
    

ans = pd.DataFrame(['上证','深证','沪深300','创业板'],columns=['index'])
interval_index = ['d7','d30','d60','d90','d120','d180','d270','d360','d540','d720']

for i in interval_index:
    
    ans_b = index_interval(data,locals()['{}'.format(i)],i)
    ans = pd.merge(ans,ans_b,on='index')
    print(locals()['{}'.format(i)])


ans.to_excel('国内大盘指数{}.xlsx'.format(date_work))