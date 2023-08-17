# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 15:00:56 2022

@author: 666
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




industry_list = ak.stock_board_industry_name_em()

df=pd.DataFrame()
for index,row in industry_list.iterrows():
    df_b = ak.stock_board_industry_hist_em(symbol=row['板块名称'], adjust="").sort_values(['日期'],ascending=0).head(20).reset_index(drop=True)
    df_b['板块名称'] = row['板块名称']
    df = df.append(df_b)
    print(index,row['板块名称'])
    
    

#df.to_excel('东方财富板块数据{}.xlsx'.format(now_day))    