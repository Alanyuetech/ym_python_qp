# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 16:37:05 2022

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


us_stock =  ak.stock_us_spot_em()
stock_data_b = ak.stock_us_hist(symbol='105.QQQ', start_date="20110101", end_date="22220101", adjust="")  #这里使用不复权的数据

aa = ak.get_us_stock_name()
print(aa)