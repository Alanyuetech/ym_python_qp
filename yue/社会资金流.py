# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 14:36:54 2023

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


"社融数据"
macro_china_shrzgm_df = ak.macro_china_shrzgm().sort_values('月份',ascending=0).reset_index(drop=True)
sr = macro_china_shrzgm_df[['月份','社会融资规模增量']].rename(columns={'社会融资规模增量':'社融'})
sr['年'] = sr['月份'].str.slice(0,4)
sr['月'] = sr['月份'].str.slice(4,6)
sr['时间'] = sr['月份']
sr = sr[['时间','年','月','社融']]

"m2数据"
m2 = pd.read_excel('m2数据.xlsx',engine='openpyxl',dtype={'code':'str'})   
m2['年'] = m2['日期'].dt.strftime('%Y')
m2['月'] = m2['日期'].dt.strftime('%m')
m2['时间'] = m2['日期'].dt.strftime('%Y%m')
m2 = m2[['时间','年','月','今值']].rename(columns={'今值':'m2'})

data = pd.merge(sr,m2,on=['时间','年','月'])
data['社融同比'] = np.nan
data['m2同比'] = np.nan
data['社融同比环比'] = np.nan
data['m2同比环比'] = np.nan


for index,row in data[:58].iterrows():
    data.loc[index,'社融同比'] = row['社融']/data[data['时间']==str(int(row['时间'])-100)].iloc[0,3]-1
    data.loc[index,'m2同比'] = row['m2']/data[data['时间']==str(int(row['时间'])-100)].iloc[0,4]-1
    
    
    

    






















































