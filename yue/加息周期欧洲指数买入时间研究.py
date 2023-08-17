# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 14:32:21 2022

@author: Administrator
"""

"加息周期欧洲指数买入时间研究"

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



"ECB利率决议"
eu_interest_rate = pd.read_excel('欧央行利率决议报告.xlsx',engine='openpyxl')
eu_interest_rate['日期'] = eu_interest_rate['日期'].astype('str').str.slice(0,10)
eu_interest_rate = eu_interest_rate[['日期','今值','前值']].copy().replace('-',np.nan)

"欧洲斯托克50---STOXX50  WSJ下载 https://www.wsj.com/market-data/quotes/index/XX/SX5E/historical-prices"
stoxx_data = pd.read_excel('stoxx_historicaldata.xlsx',engine='openpyxl')

'处理日期格式'
stoxx_data['日期'] = stoxx_data['Date'].apply(lambda x: (('20'+x[6:8]+'-'+x[0:2]+'-'+x[3:5]) if int(x[6:8])<50 else ('19'+x[6:8]+'-'+x[0:2]+'-'+x[3:5]) ) 
                                            if type(x)==str 
                                            else (('20'+str(x)[8:10]+'-'+str(x)[2:4]+'-'+str(x)[5:7]) if int(str(x)[8:10])<50  else ('19'+str(x)[8:10]+'-'+str(x)[2:4]+'-'+str(x)[5:7])))



stoxx_data = stoxx_data[['日期','Close']].copy().rename(columns={'Close':'stoxx50'})

'合并数据'
stoxx_eurate = pd.merge(stoxx_data,eu_interest_rate,how='outer',on='日期').sort_values('日期',ascending=0).reset_index(drop=True)
stoxx_eurate = stoxx_eurate.fillna(method='bfill')
merge_data = stoxx_eurate.copy().sort_values('日期',ascending=1).reset_index(drop=True)

'加息周期'
'欧洲时差没有导致数据时间有错位，加息开始时间为实际加息时间，加息结束时间为加息后第一次降息时间的前一天'
start_day = ['1999-12-01','2006-01-01','2011-04-07']
end_day = ['2001-05-31','2008-10-07','2011-11-02']


merge_data.to_excel('加息后买入斯托克50时间{}.xlsx'.format(date_work))

"确定加息周期"
writer = pd.ExcelWriter('cycle_eur_{}.xlsx'.format(date_work))


cycle_df = pd.DataFrame()
cycle_df_b = pd.DataFrame()


for i in range(3):
    locals()['cycle_{}'.format(i)] = merge_data[(merge_data['日期']>=start_day[i])&(merge_data['日期']<=end_day[i])].reset_index(drop=True)
    loc_0 = locals()['cycle_{}'.format(i)].loc[0,:]
    locals()['cycle_{}'.format(i)]['stoxx50chg'] = 100*(locals()['cycle_{}'.format(i)]['stoxx50']/loc_0['stoxx50'] - 1)  
    
    cycle_df_b.loc[0,'周期标识'] = '{}  ~~  {}'.format(start_day[i],end_day[i])
    cycle_df_b.loc[0,'周期跨度'] = len(locals()['cycle_{}'.format(i)] )
    cycle_df_b.loc[0,'stoxx50最小值所在位置'] = locals()['cycle_{}'.format(i)]['stoxx50'].idxmin()+1
    cycle_df_b.loc[0,'stoxx50最小值所在利率'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['stoxx50'].idxmin(),'今值']
    cycle_df_b.loc[0,'stoxx50最小值_利率变动'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['stoxx50'].idxmin()
                                                                  ,'今值'] - locals()['cycle_{}'.format(i)].loc[0,'今值']  
    cycle_df_b.loc[0,'stoxx50最小值跌幅'] = locals()['cycle_{}'.format(i)]['stoxx50chg'].min()
    cycle_df_b.loc[0,'stoxx50最大值所在位置'] = locals()['cycle_{}'.format(i)]['stoxx50'].idxmax()+1
    cycle_df_b.loc[0,'stoxx50最大值所在利率'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['stoxx50'].idxmax(),'今值']    
    cycle_df_b.loc[0,'stoxx50最大值_利率变动'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['stoxx50'].idxmax()
                                                                  ,'今值'] - locals()['cycle_{}'.format(i)].loc[0,'今值']      
    
    
    cycle_df = cycle_df.append(cycle_df_b)
    
    
    # locals()['cycle_{}'.format(i)].to_excel('cycle_{}_{}.xlsx'.format(i,date_work))
    locals()['cycle_{}'.format(i)].to_excel(writer,sheet_name='sheet{}'.format(i), index=False) 
    
    
    
    
cycle_df.to_excel('cycle_eur_df_{}.xlsx'.format(date_work))
        
    
writer.save()
writer.close()




























