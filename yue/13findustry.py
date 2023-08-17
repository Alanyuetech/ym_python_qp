# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 15:05:23 2022

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



data = pd.read_excel('2022Q313F行业分析.xlsx',engine='openpyxl')[['公司','行业','市值--亿','组合中所占百分比']]
data_groupby_percent = data.groupby('行业').agg({'市值--亿':'sum','组合中所占百分比':'mean'}).reset_index().rename(columns={'市值--亿':'市值--亿(总和)','组合中所占百分比':'组合中所占百分比(平均)'})







