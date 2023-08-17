# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 10:06:46 2022

@author: Administrator
"""


import akshare as ak
import pandas as pd
import time 
import matplotlib as mpl
from matplotlib import pyplot as plt 
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
import xlsxwriter
import openpyxl
from openpyxl.styles import PatternFill,Font,Alignment
import statsmodels.api as sm
import yfinance as yf
from functools import reduce

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




now = datetime.datetime.now()
last_3m = (now+relativedelta(months=-3)).strftime('%Y%m%d')
last_6m = (now+relativedelta(months=-6)).strftime('%Y%m%d')
last_1y = (now+relativedelta(years=-1)).strftime('%Y%m%d')
last_2y = (now+relativedelta(years=-2)).strftime('%Y%m%d')


fund_id = pd.read_excel('行业复盘名单.xlsx',engine='openpyxl',dtype={'id':'str'})[['id']]
"基金代码前面补0"
fund_id['id'] = fund_id['id'].map(lambda x:'00000'+x if len(x)==1 else
                                  ('0000'+x if len(x)==2 else 
                                   ('000'+x if len(x)==3 else
                                    ('00'+x if len(x)==4 else
                                     ('0'+x if len(x)==5 else x)))))

fund_data_hz = pd.DataFrame()

def max_drawback(stock_data):
    
    "可能存在 应该使用loc[index,row]的问题，不行就直接用for循环"
    "找当前日期前的最大值，算出截至当日的最大回撤，算出整个区间段内的最大回撤"
    stock_data['前最大值'] = stock_data.apply(lambda x:stock_data[stock_data['净值日期']<x['净值日期']]['累计净值'].max(),axis=1)
    stock_data['截至当日最大回撤'] = 100*(1 - stock_data['累计净值']/stock_data['前最大值'])
    max_db = round(stock_data['截至当日最大回撤'].max(),2)
       
    # "for 循环   备用"
    # for index,row in stock_data.iterrows():
    #     stock_data.loc[index,'前最大值'] = stock_data[stock_data['净值日期']<row['净值日期']]['累计净值'].max()
    # for index,row in stock_data.iterrows():                 
    #     stock_data.loc[index,'截至当日最大回撤'] = 100*(1 - row['累计净值']/row['前最大值'])
    # max_db = round(stock_data['截至当日最大回撤'].max(),2)
    
    
    return max_db



def industry__analyse(fundid,bs):
    '''
    bs:单位净值走势 or 累计净值走势
    '''
    fund_data_b = pd.DataFrame()
    fund_data = ak.fund_open_fund_info_em(fund=fundid, indicator=bs).sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    fund_data['净值日期'] = fund_data['净值日期'].astype('str').str.replace('-','')
    fund_data_b.loc[0,'id'] = fundid
    fund_data_b.loc[0,'近3月高点'] = fund_data[fund_data['净值日期']>=last_3m]['累计净值'].max()  
    fund_data_b.loc[0,'近半年高点'] = fund_data[fund_data['净值日期']>=last_6m]['累计净值'].max()   
    fund_data_b.loc[0,'近1年高点'] = fund_data[fund_data['净值日期']>=last_1y]['累计净值'].max()   
    fund_data_b.loc[0,'近2年高点'] = fund_data[fund_data['净值日期']>=last_2y]['累计净值'].max()   
    fund_data_b.loc[0,'半年最大回撤'] = max_drawback(fund_data[fund_data['净值日期']>=last_6m]) 
    fund_data_b.loc[0,'一年最大回撤'] = max_drawback(fund_data[fund_data['净值日期']>=last_1y])  
    fund_data_b.loc[0,'当前'] = fund_data.loc[0,'累计净值']

    return fund_data_b


for index,row  in fund_id[:].iterrows():
    fund_data_b = industry__analyse(row['id'],'累计净值走势')
    fund_data_hz = fund_data_hz.append(fund_data_b)
    print(index,row['id'])
    
    
fund_data_hz.to_excel('行业复盘{}.xlsx'.format(now_day))
  

































