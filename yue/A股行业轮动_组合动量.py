# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 14:05:08 2023

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



stock_pools = ['沪深300','上证50','中证500']
start_date_list = ['20180101','20220101']
start_date = '20180101'
dln = [20,40,60]
weights = [0.4,0.3,0.3]


index_stock_info_df = ak.index_stock_info()
def con_stock(display_name):
    "通过指数名称，获取指数成分股"
    index_code = index_stock_info_df[index_stock_info_df['display_name']=='{}'.format(display_name)]['index_code'].values[0]
    index_stock_cons_df = ak.index_stock_cons(symbol="{}".format(index_code))
    index_stock_cons_df['品种代码'] = index_stock_cons_df['品种代码'].drop_duplicates()
    index_stock_cons_df = index_stock_cons_df.dropna(axis=0,how='any')
    return index_stock_cons_df
    



def stock_data(stock_id,start_date,end_date="22220101",biaoshi='收盘'):
    "A股股票数据"
    stock_data_b = ak.stock_zh_a_hist(symbol=stock_id, period="daily", 
                                   start_date="{}".format(start_date),end_date=end_date,
                                   adjust="hfq")[['日期','{}'.format(biaoshi)]].rename(columns={'{}'.format(biaoshi):stock_id})  
    return stock_data_b
    

def stock_pool_data(stock_pool_name,start_date):
    "获取股票池数据"
    pool_con_stock = con_stock(stock_pool_name)  #股票池名称，拿到成分股
    pool_stock_data = pd.DataFrame()
    for index,row in pool_con_stock.iterrows():
        stock_data_b = stock_data(row['品种代码'],start_date)
        if len(pool_stock_data)==0:
            pool_stock_data = stock_data_b.copy().sort_values(['日期'],ascending=[1]).reset_index(drop=True)
        else:
            pool_stock_data = pd.merge(pool_stock_data,stock_data_b,on='日期',how='outer').sort_values(['日期'],ascending=[1]).reset_index(drop=True)
    
    return pool_stock_data
    

def hold_stocks(stock_pool_data_b,posi_num):
    

    stock_data_bb = stock_pool_data_b[:posi_num]
    sat_dln =  pd.DataFrame(stock_data_bb.tail(1).iloc[0,1:].reset_index().loc[:,'index']).copy()
    for dln_n in dln:
        sat_dln_b = pd.DataFrame(stock_data_bb.tail(1).iloc[0,1:]/stock_data_bb.head(1).iloc[0,1:]-1).reset_index().rename(columns={0:'{}'.format(dln_n)})   #对应动量计算
        sat_dln = pd.merge(sat_dln,sat_dln_b,how='outer',on='index')
      
    sat_dln_weight = sat_dln.copy()
    for col_num in range(1,len(sat_dln.columns)):
        sat_dln_weight.iloc[:,col_num] = sat_dln_weight.iloc[:,col_num]*weights[col_num-1]
        
    sat_dln_weight['Col_sum'] = sat_dln_weight.iloc[:,1:].copy().apply(lambda x: x.sum(), axis=1)
    holdstocks = sat_dln_weight.sort_values(['Col_sum'],ascending=0).head(holding_num).reset_index(drop=True).rename(columns={'index':'id'}) #统计出接下来持有的股票代码
    
    return holdstocks     

    

def holding_return(stock_pool_data_b,):   #选取股票后，计算该组股票未来holding_days的总涨跌幅
    stock_pool_data_b
    
    

    
    
def strategy_final(stock_pool_name,start_date,dln,weights,holding_days,holding_num):
    stock_pool_data_b = stock_pool_data(stock_pool_name,start_date)  
    
    posi_num=0     #标定每一次筛选股票后的位置
    for position_num in range(len(dln)):
        if position_num==0:  
            posi_num+=max(dln)    #统计数据的位置
            holdstocks = hold_stocks(stock_pool_data_b,posi_num)
            
            
        else:
            posi_num+=holding_days
        
        
        
        
        
    for dln_n in dln:
        print(dln_n)
        stock_data_bb = stock_pool_data_b
    
    
    return stock_pool_data_b
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    



