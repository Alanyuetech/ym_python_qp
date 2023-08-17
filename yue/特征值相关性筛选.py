# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 15:25:42 2022

@author: Administrator
"""

"多因子筛选————弱相关性"
"输入n个因子数据"
"获取所有因子的相关系数矩阵"
"设定相关系数阈值"
""







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






























