# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 17:02:49 2022

@author: Administrator
"""



"买入股票的基金和基金公司数量"
import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
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



"基金列表"
# fund_id = pd.read_excel('临时AVE_测试0813.xlsx',engine='openpyxl',dtype={'id':'str'})
data = pd.read_excel('基金持仓股票分析明细-岳20220720.xlsx',engine='openpyxl')

def ppp(bs):
    ans = data[['股票名称','{}'.format(bs)]].copy()
    
    ans = ans.dropna(axis=0,how='any').reset_index(drop=True)
    
    df = ans.drop_duplicates()
    df_data = df.groupby('股票名称').agg('count').reset_index()
    
    df_data.to_excel('买入股票的{}数量{}.xlsx'.format(bs,date_work))

for i in ['基金名称','基金公司']:
    ppp(i)