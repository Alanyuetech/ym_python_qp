# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 16:29:15 2022

@author: Administrator
"""
"国内股票收盘价"

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




"基金代码前面补0"
def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:'00000'+x if len(x)==1 else
                                      ('0000'+x if len(x)==2 else 
                                       ('000'+x if len(x)==3 else
                                        ('00'+x if len(x)==4 else
                                         ('0'+x if len(x)==5 else x)))))
    return fund_id




def stock_price(stock_id,start_date,end_date,adjust=""):
    
    df = ak.stock_zh_a_hist(symbol=stock_id, period="daily", start_date=start_date, end_date=end_date, adjust=adjust)
    df = df.rename(columns={'收盘':'{}'.format(stock_id)})
    return df


stock_id = pd.read_excel('A股名单_季度持仓.xlsx',engine='openpyxl',dtype={'id':'str'})



# stock_id = bu_zero(stock_id,'id')


stock_price_data = pd.DataFrame()
stock_price_data_erro = pd.DataFrame()
num = 0
for index,row in stock_id[:].iterrows():
    try:
        if len(row['id'])==6:
            if num ==0 :
                df = stock_price(row['id'],'20220901',date_work,'qfq')[['日期','{}'.format(row['id'])]]
                stock_price_data = df.copy()
            else:
                df = stock_price(row['id'],'20220901',date_work,'qfq')[['日期','{}'.format(row['id'])]]
                stock_price_data = pd.merge(stock_price_data,df,how='left',on='日期')
            num += 1
            print(index,row['id'])
        else:
            df = ak.stock_hk_hist(symbol=row['id'], period="daily", start_date="20220901", end_date="22220101", adjust="qfq")
            df = df.rename(columns={'收盘':'{}'.format(row['id'])})
            df = df[['日期','{}'.format(row['id'])]].copy()
            stock_price_data = pd.merge(stock_price_data,df,how='left',on='日期')
            num += 1
            print(index,row['id'])            
        
    except:   #港股

        stock_price_data_erro.loc[index,'id'] = row['id']
    
stock_price_data = stock_price_data.T
    
stock_price_data.to_excel('国内股票收盘价{}补充.xlsx'.format(date_work))   
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
