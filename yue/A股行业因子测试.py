# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 15:42:37 2022

@author: Administrator
"""

"A股行业因子测试"


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



def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:str(x).zfill(6))
    return fund_id


def stock_data(stockid,statr_date,end_date,period="daily"):    #股票数据  
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stockid, period=period, start_date=statr_date, end_date=end_date, adjust="hfq")
    if len(stock_zh_a_hist_df)!=0:
        stock_zh_a_hist_df['代码'] = stockid
        stock_zh_a_hist_df['月'] = stock_zh_a_hist_df['日期'].str.slice(5,7).astype('str').str.replace('-','')
        stock_zh_a_hist_df['季度'] = stock_zh_a_hist_df['月'].apply(lambda x:'1季度' if (x[-2:]>='01')&(x[-2:]<='03') 
                                              else ('2季度' if (x[-2:]>='04')&(x[-2:]<='06') 
                                                    else ('3季度' if (x[-2:]>='07')&(x[-2:]<='09') else '4季度') ) )
        stock_zh_a_hist_df['年'] =stock_zh_a_hist_df['日期'].str.slice(0,4)
        stock_zh_a_hist_df = stock_zh_a_hist_df[['代码','日期','收盘','月','季度','年']]
    else:
        pass
    return stock_zh_a_hist_df


def interval_increase(stockdata,interval='季度'):
    if len(stockdata)!=0:
        ans_data_head = stockdata.groupby(['年','{}'.format(interval)]).head(1).reset_index(drop=True).rename(columns={'收盘':'{}初收盘'.format(interval)})
        ans_data_tail = stockdata.groupby(['年','{}'.format(interval)]).tail(1).reset_index(drop=True).rename(columns={'收盘':'{}末收盘'.format(interval)})
        ans_data_q = pd.merge(ans_data_head[['代码','年','{}'.format(interval),'{}初收盘'.format(interval)]],ans_data_tail[['代码','年','{}'.format(interval),'{}末收盘'.format(interval)]]
                              ,how='inner',on=['代码','年','{}'.format(interval)])  
        ans_data_q['{}涨幅 %'.format(interval)] = (ans_data_q['{}末收盘'.format(interval)]/ans_data_q['{}初收盘'.format(interval)] - 1)*100
    else:
        ans_data_q = pd.DataFrame()
    return ans_data_q




stock_id = pd.read_csv('全部A股.csv')
# stock_id = pd.read_excel('工作簿1.xlsx',engine='openpyxl')     #测试备用

stock_id = bu_zero(stock_id,'代码')
stock_id = stock_id[['代码','名称','所属行业']].copy()


stock_data_all = pd.DataFrame()
interval_chg = pd.DataFrame()
statr_date = '20120101'
interval_b = '月'    #季度/月

for index,row in stock_id[:].iterrows():
    time.sleep(1)
    stock_data_b = stock_data(row['代码'],statr_date,now_day)
    stock_data_all = stock_data_all.append(stock_data_b)
    interval_chg_b = interval_increase(stock_data_b,interval_b)
    interval_chg = interval_chg.append(interval_chg_b)
    print(index,row['代码'])
    
interval_chg = pd.merge(interval_chg,stock_id,how='left',on='代码')    

interval_chg_gb = interval_chg.groupby(['{}'.format(list(interval_chg)[2]),'所属行业']).agg({'{}涨幅 %'.format(list(interval_chg)[2]):'mean'}).reset_index()
interval_chg_gb_firstn = interval_chg_gb.sort_values(['{}'.format(list(interval_chg)[2]),'{}涨幅 %'.format(list(interval_chg)[2])],ascending=[1,0]).groupby(by='{}'.format(list(interval_chg)[2])).head(10)  

interval_chg_gb.to_excel('A股行业月度涨幅汇总all.xlsx')  
interval_chg_gb_firstn.to_excel('A股行业月度涨幅汇总.xlsx')  
    
    
    
    
    
    



