# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 14:30:16 2023

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

stock_fund = pd.read_excel('股票型基金.xlsx',engine='openpyxl',dtype={'代码':'str'})  
mix_fund = pd.read_excel('混合型基金.xlsx',engine='openpyxl',dtype={'代码':'str'})  
stock_fund = bu_zero(stock_fund,'代码')
mix_fund = bu_zero(mix_fund,'代码')



start_date_list=['20230131']
end_date_list = ['20230228']



def max_down(fund_id_data,start_date,end_date):
    maxdown_b = pd.DataFrame()
    fund_data = fund_id_data[(fund_id_data['净值日期']>=start_date)&(fund_id_data['净值日期']<=end_date)].copy().sort_values('净值日期',ascending=0).reset_index(drop=True)
    for index,row in fund_data.iterrows():
        # fund_data.loc[index,'前最大值'] = fund_data.loc[index+1:,'累计净值'].max()
        fund_data.loc[index,'回撤'] = 1-fund_data.loc[index,'累计净值']/fund_data.loc[index+1:,'累计净值'].max()

    maxdown_b.loc[0,'开始日期'] = fund_data.tail(1).reset_index(drop=True).loc[0,'净值日期']
    maxdown_b.loc[0,'结束时间'] = fund_data.loc[0,'净值日期']
    maxdown_b.loc[0,'最大回撤'] = fund_data['回撤'].max()
    
    
    return maxdown_b






for bs in ['股票型','混合型']:
    if bs == '股票型':
        fund_code=stock_fund.copy()
    elif bs == '混合型':
        fund_code=mix_fund.copy()
    else:
        pass
    
    for end_date in end_date_list:
        for start_date in start_date_list:
            maxdown = pd.DataFrame()
            n=0
            for index,row in fund_code[:].iterrows():
                try:
                    fund_id_data = ak.fund_open_fund_info_em(fund=row['代码'], indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
                    fund_id_data['净值日期'] = fund_id_data['净值日期'].astype('str').str.replace('-','').astype('str')
     
                    maxdown_b=max_down(fund_id_data,start_date,end_date) 
                    maxdown_b['代码']=row['代码']
                    maxdown_b['名称']=row['名称']
                    maxdown = maxdown.append(maxdown_b)   
                   
                    print(index,start_date,end_date,row['代码'],row['名称'])  
                except:
                    n+=1
                    print(index,'报错',row['代码'],row['名称'])
                
            maxdown.to_excel('{}_最大回撤_{}.xlsx'.format(bs,start_date))

#可优化：把两个开始时间放到一起






