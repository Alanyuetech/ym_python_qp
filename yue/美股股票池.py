# -*- coding: utf-8 -*-
"""
Created on Wed Jan  5 13:09:30 2022

@author: Administrator
"""

"全部美股数据————股票池    行业筛选通过excel筛选"


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




us_stock_all = pd.read_csv('全部美股源数据.csv')

"市值200亿以上"
us_stock = us_stock_all[us_stock_all['总市值']>=20000000000]

"剔除没有行业标识的"
us_stock = us_stock[us_stock['所属行业']!='-']

"通过之前的名单，罗列出匹配的行业"

# industry_list = pd.DataFrame(us_stock_all['所属行业'].drop_duplicates() )
# print(list(industry_list['所属行业']))

# industry_list = pd.DataFrame(us_stock_200_last['所属行业'].drop_duplicates() )

# us_stock = pd.merge(us_stock,industry_list,how='inner',on='所属行业')



us_stock = us_stock[['代码','名称','所属行业','最新价','涨跌幅','总市值','换手率%','市盈率TTM','市盈率(静)','市净率']]

us_stock['总市值-亿'] = us_stock['总市值']/100000000
us_stock = us_stock[['代码','名称','所属行业','最新价','涨跌幅','总市值','总市值-亿','换手率%','市盈率TTM','市盈率(静)','市净率']]

us_stock.to_excel("美股200亿以上筛选{}.xlsx".format(date_work))



























