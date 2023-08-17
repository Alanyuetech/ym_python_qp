# -*- coding: utf-8 -*-
"""
Created on Fri Jul 22 14:57:45 2022

@author: Administrator
"""

"A股股票时间段涨跌幅"

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




"股票列表"
stock_id = pd.read_excel('A股股票id.xlsx',engine='openpyxl',dtype={'id':'str'})[['id']]
stock_id = bu_zero(stock_id,'id')


stock_data = pd.DataFrame()
for index,row in stock_id.iterrows():
    stock_data_b = ak.stock_zh_a_hist(symbol="{}".format(row['id']), period="daily", start_date="20220331", end_date='20220721', adjust="hfq")
    stock_data.loc[index,'id'] = row['id']
    stock_data.loc[index,'区间涨跌幅%'] = 100*(stock_data_b.tail(1)['收盘'].iloc[0] / stock_data_b.head(1)['收盘'].iloc[0] - 1)
    stock_data.loc[index,'区间'] = '20220331--20220721'
    print(index,row['id'])
    
stock_data.to_excel('A股股票时间段涨跌幅{}.xlsx'.format(now_day))   