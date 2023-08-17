# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 16:11:51 2021

@author: Administrator
"""

"财报信号季度数据分析"




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


data = pd.read_excel('财报信号季度数据.xlsx',engine='openpyxl')

q_data = data.groupby(['年份','季度'],as_index=False).agg('mean').sort_values(['年份','季度'],ascending=[1,1])

"前一个季度表现不好，后一个季度表现如何？"

q_data = q_data[q_data['年份']>=2015].reset_index(drop=True)
q_data['下季度涨跌幅'] = q_data['涨跌幅'].shift(-1)

q_data['下季-本季'] = q_data['下季度涨跌幅']-q_data['涨跌幅']
q_data_ltz = q_data[ q_data['涨跌幅'] <0 ]                                       # 涨跌幅小于零  筛选
q_data_ltz_mean =  q_data_ltz.mean()

q_data_ltz_mean.to_excel('财报信号失效平均值{}.xlsx'.format(now_day))
q_data_ltz.to_excel('财报信号失效--小于0{}.xlsx'.format(now_day))
q_data.to_excel('财报信号季度数据{}.xlsx'.format(now_day))




















