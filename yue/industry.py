# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 15:10:21 2022

@author: Administrator
"""

"industry"


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


industry_index =  ak.stock_board_industry_name_em()




def industry_take(industry_name):
    ans = ak.stock_board_industry_cons_em(symbol="{}".format(industry_name))
    ans['industry'] = industry_name
    industry_b = ans[['代码','名称','industry']].copy().rename(columns={'代码':'code','名称':'name'})
    return industry_b




industry = pd.DataFrame()
for index,row in industry_index.iterrows():
    industry_b = industry_take(row['板块名称'])
    industry = industry.append(industry_b)
    print(index,row['板块名称'])
    
    
    
industry.to_excel("industry岳{}.xlsx".format(date_work))
   

