# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 13:28:07 2023

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
import math
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




now = datetime.datetime.now()
delta_180=datetime.timedelta(days=180)
after_180=(now-delta_180).strftime('%Y%m%d')

def industries_percent_position(data,bs='收盘'):
    data = data.sort_values('日期',ascending=0).reset_index(drop=True)
    max_data = data.iloc[[data['收盘'].idxmax()]].reset_index(drop=True).rename(columns={'收盘':'最大值','日期':'最大值出现日期'})
    min_data = data.iloc[[data['收盘'].idxmin()]].reset_index(drop=True).rename(columns={'收盘':'最小值','日期':'最小值出现日期'})
    now_data = data.iloc[[0]]
    indus_posi = pd.merge(now_data,max_data,on='板块名称')
    indus_posi = pd.merge(indus_posi,min_data,on='板块名称')
    indus_posi['(max-now)/(max-min)'] = (indus_posi['最大值']-indus_posi['收盘'])/(indus_posi['最大值']-indus_posi['最小值'])
    indus_posi['now/max'] = indus_posi['收盘']/indus_posi['最大值']   
    
    
    
    "最大值以来数据"
    data_b = data[data['日期']>=max_data.loc[0,'最大值出现日期']]
    max_data_b = data_b.iloc[[data_b['收盘'].idxmax()]].reset_index(drop=True).rename(columns={'收盘':'最大值以来最大值','日期':'最大值以来最大值出现日期'})
    min_data_b = data_b.iloc[[data_b['收盘'].idxmin()]].reset_index(drop=True).rename(columns={'收盘':'最大值以来最小值','日期':'前低日期'})

    indus_posi = pd.merge(indus_posi,max_data_b,on='板块名称')
    indus_posi = pd.merge(indus_posi,min_data_b,on='板块名称')
    indus_posi['(max-now)/(max-min) 最大值以来'] = (indus_posi['最大值以来最大值']-indus_posi['收盘'])/(indus_posi['最大值以来最大值']-indus_posi['最大值以来最小值'])
    indus_posi['now/max  最大值以来'] = indus_posi['收盘']/indus_posi['最大值以来最大值']   
    indus_posi['(now-min)/min  最大值以来'] = (indus_posi['收盘']-indus_posi['最大值以来最小值'])/indus_posi['最大值以来最小值']  
    indus_posi = indus_posi[['板块名称','日期','(max-now)/(max-min)','(now-min)/min  最大值以来','收盘',
                             '最大值出现日期','最小值出现日期',
                             '前低日期']]    
    
    
    return indus_posi




industries = ak.stock_board_industry_name_em()
industries_mv = ak.stock_board_industry_name_em()[['板块名称','总市值']]
industries_mv['总市值-亿'] = industries_mv['总市值']/100000000
industries_mv = industries_mv[['板块名称','总市值-亿']]



indus_posi_data = pd.DataFrame()
for index,row in industries[:].iterrows():
    industry_data_b = ak.stock_board_industry_hist_em(symbol="{}".format(row['板块名称']), 
                                                      start_date=after_180,end_date=date_work, period="日k", adjust="hfq")[['日期','收盘']]
    
    
    
    industry_data_b['板块名称'] = row['板块名称']
    
    indus_posi_b = industries_percent_position(industry_data_b)
    
    indus_posi_data = indus_posi_data.append(indus_posi_b)
    print(index,row['板块名称'])

indus_posi_data = pd.merge(indus_posi_data,industries_mv,on='板块名称')


indus_posi_data.to_excel('行业所处时间段位置百分比_{}.xlsx'.format(now.strftime('%Y%m%d')))





















