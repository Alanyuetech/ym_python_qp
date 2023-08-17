# -*- coding: utf-8 -*-
"""
Created on Mon Nov  8 13:11:16 2021

@author: Administrator
"""

"分析成交额前20指标明细"

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

now_day = datetime.datetime.now().strftime('%Y%m%d')

# ans = pd.read_excel('成交额前20指标明细20211105.xlsx',engine='openpyxl',dtype={'时间':'str'})

ans = pd.read_excel('成交额前20指标明细{}.xlsx'.format(now_day),engine='openpyxl',dtype={'时间':'str'})
a=[]
for i in range(0,len(ans),50):##每隔20行取数据
    a.append(i)

df = ans.iloc[a]


df.to_excel("成交额-股指期货{}.xlsx".format(now_day),index=False)




