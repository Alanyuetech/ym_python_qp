# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 15:43:34 2022

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
now_day = datetime.datetime.now().strftime('%Y%m%d')
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

option_holding = pd.read_excel('2022Q3_13Foption.xlsx',engine='openpyxl')  
option_holding['reported_mv'] = option_holding['reported_mv'].astype('str').str.replace('$','').str.replace('b','').astype('float')
option_holding['%shares_change'] = 100*(option_holding['shares_reported']/option_holding['previous_shares'] - 1) 
option_holding.loc[np.isinf(option_holding['%shares_change']),'%shares_change'] = np.nan


us_stock = pd.read_excel('allusstock.xlsx',engine='openpyxl')[['代码','名称']] 
option_holding = pd.merge(option_holding,us_stock,left_on='stock',right_on='代码',how='left')



option_holding_groupby_type = option_holding.groupby('type').agg({'%portfolio':'mean',
                                                                  '%shares_change':'mean',
                                                                  'reported_mv': 'sum'}).reset_index()


option_holding_groupby_type_stock = option_holding.groupby(['type','stock']).agg({'名称':'max','%portfolio':'mean',
                                                                  '%shares_change':'mean',
                                                                  'reported_mv': 'sum'}).reset_index().sort_values(['stock','reported_mv'],ascending=[1,0])







