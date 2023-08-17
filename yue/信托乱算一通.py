# -*- coding: utf-8 -*-
"""
Created on Wed Dec 22 14:15:40 2021

@author: Administrator
"""

"夏普"


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



-0.022050403359911257


"001718"
"001366"
"161834"
"519002"
"519133"
x1 = -0.022050403359911257
x2 = -0.019687084836375553
x3 = -0.015344150995924847
x4 = 0
x5 = -0.014973058584018106


x = (x1+x2+x3+x4+x5)/5

jj = ak.fund_em_etf_fund_info(fund="519133", start_date="20201221", end_date="20211221")
jj = jj.fillna(0)
jj['日增长率'] = jj['日增长率']/100
x = jj['日增长率'].mean() - 1.22* np.std(jj['日增长率'])
sharp =  (jj['日增长率'].mean()-x)/np.std(jj['日增长率'])





ans = pd.read_excel('信托计算.xlsx',engine='openpyxl',dtype={'时间':'str'})

avg1 = ans['盈亏比例'].mean()
std1 = np.std(ans['盈亏比例'])
sharp = (ans['盈亏比例'].mean()-x2)/np.std(ans['盈亏比例'])


sharp = ans['盈亏比例'].mean()/np.std(ans['盈亏比例'])

std = np.std(ans['盈亏比例'], ddof =1)












