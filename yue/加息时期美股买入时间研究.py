# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 13:59:55 2022

@author: Administrator
"""

'''
加息后美股复苏时间
'''

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




"FED利率决议"
us_interest_rate = pd.read_excel('美联储利率决议报告.xlsx',engine='openpyxl')
us_interest_rate['日期'] = us_interest_rate['日期'].astype('str').str.slice(0,10)



"美股指数-----全局模式"


"获取指数数据，并调整日期"
def index_data(country,index_name,period,start_date,end_date):
    time_diff = (int(end_date)-int(start_date))//10000   #是否超过15年，因为每次数据只能爬5000条。
    if time_diff>15:
        
        end_date_b = str(int(start_date)//10000 + 10)+'1231'
        start_date_b = start_date
        index_data = pd.DataFrame()   
        while start_date_b <end_date :
        
            index_data_b = ak.index_investing_global(country=country, index_name=index_name, 
                                          period=period, start_date=start_date_b, end_date=end_date_b)
            
            index_data = pd.concat([index_data,index_data_b])
            
            start_date_b = str(int(end_date_b)//10000 + 1)+'0101'
            end_date_b = str(int(start_date_b)//10000 + 10)+'1231'         
            
    else:
        index_data = ak.index_investing_global(country=country, index_name=index_name, 
                                      period=period, start_date=start_date, end_date=end_date)     
    
    index_data['日期'] = index_data['日期'].astype('str')
    return index_data

naq_index = index_data("美国","纳斯达克综合指数","每日","19820101",now_day).sort_values('日期'
                                                                            ,ascending=0).reset_index(drop=True).rename(columns={'收盘':'纳指'})[['日期','纳指']]
sp500_index = index_data("美国","标普500指数","每日","19820101",now_day).sort_values('日期'
                                                                             ,ascending=0).reset_index(drop=True).rename(columns={'收盘':'标普'})[['日期','标普']]
dj_index = index_data("美国","道琼斯指数","每日","19820101",now_day).sort_values('日期'
                                                                        ,ascending=0).reset_index(drop=True).rename(columns={'收盘':'道琼斯'})[['日期','道琼斯']]



"合并数据  处理数据"
dfs = [sp500_index,naq_index,dj_index,us_interest_rate]
merge_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='outer'),dfs)
merge_data = merge_data.sort_values('日期',ascending=0).reset_index(drop=True)

merge_data['今值'] = merge_data['今值'].shift(1)
merge_data['预测值'] = merge_data['预测值'].shift(1)
merge_data['前值'] = merge_data['前值'].shift(1)
"替换- 为nan"
merge_data = merge_data.replace('-',np.nan)
merge_data = merge_data.fillna(method='bfill')

merge_data = merge_data.sort_values('日期',ascending=1)

merge_data.to_excel('加息后买入美股时间{}.xlsx'.format(date_work))



"确定加息周期"
writer = pd.ExcelWriter('cycle_{}.xlsx'.format(date_work))

'由于美联储与国内有时差，所以加息开始日期为公布加息开始日期的前一天（时差一天），加息结束日期为下一次降息日期的前两天（时差一天+不含降息的一天）'
start_day = ['1983-03-31','1987-01-05','1988-03-30','1994-02-04','1999-06-30','2004-06-30','2015-12-16','2022-03-16']
end_day = ['1984-09-19','1987-11-03','1989-06-05','1995-07-05','2001-01-02','2007-09-17','2019-07-30','2022-06-21']

cycle_df = pd.DataFrame()
cycle_df_b = pd.DataFrame()

for i in range(8):
    locals()['cycle_{}'.format(i)] = merge_data[(merge_data['日期']>=start_day[i])&(merge_data['日期']<=end_day[i])].reset_index(drop=True)
    loc_0 = locals()['cycle_{}'.format(i)].loc[0,:]
    locals()['cycle_{}'.format(i)]['标普chg'] = 100*(locals()['cycle_{}'.format(i)]['标普']/loc_0['标普'] - 1)
    locals()['cycle_{}'.format(i)]['纳指chg'] = 100*(locals()['cycle_{}'.format(i)]['纳指']/loc_0['纳指'] - 1)
    locals()['cycle_{}'.format(i)]['道琼斯chg'] = 100*(locals()['cycle_{}'.format(i)]['道琼斯']/loc_0['道琼斯'] - 1)    
    
    cycle_df_b.loc[0,'周期标识'] = '{}  ~~  {}'.format(start_day[i],end_day[i])
    cycle_df_b.loc[0,'周期跨度'] = len(locals()['cycle_{}'.format(i)] )
    cycle_df_b.loc[0,'标普最小值所在位置'] = locals()['cycle_{}'.format(i)]['标普'].idxmin()+1
    cycle_df_b.loc[0,'纳指最小值所在位置'] = locals()['cycle_{}'.format(i)]['纳指'].idxmin()+1
    cycle_df_b.loc[0,'道琼斯最小值所在位置'] = locals()['cycle_{}'.format(i)]['道琼斯'].idxmin()+1
    cycle_df_b.loc[0,'标普最小值所在利率'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['标普'].idxmin(),'今值']
    cycle_df_b.loc[0,'纳指最小值所在利率'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['纳指'].idxmin(),'今值']
    cycle_df_b.loc[0,'道琼斯最小值所在利率'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['道琼斯'].idxmin(),'今值']
    cycle_df_b.loc[0,'标普最小值_利率变动'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['标普'].idxmin()
                                                                  ,'今值'] - locals()['cycle_{}'.format(i)].loc[0,'今值']
    cycle_df_b.loc[0,'纳指最小值_利率变动'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['纳指'].idxmin()
                                                                  ,'今值'] - locals()['cycle_{}'.format(i)].loc[0,'今值']
    cycle_df_b.loc[0,'道琼斯最小值_利率变动'] = locals()['cycle_{}'.format(i)].loc[locals()['cycle_{}'.format(i)]['道琼斯'].idxmin()
                                                                  ,'今值'] - locals()['cycle_{}'.format(i)].loc[0,'今值']  
    
    cycle_df_b.loc[0,'标普最小值跌幅'] = locals()['cycle_{}'.format(i)]['标普chg'].min()
    cycle_df_b.loc[0,'纳指最小值跌幅'] = locals()['cycle_{}'.format(i)]['纳指chg'].min()
    cycle_df_b.loc[0,'道琼斯最小值跌幅'] = locals()['cycle_{}'.format(i)]['道琼斯chg'].min()    
    
    
    cycle_df = cycle_df.append(cycle_df_b)
    
    
    # locals()['cycle_{}'.format(i)].to_excel('cycle_{}_{}.xlsx'.format(i,date_work))
    locals()['cycle_{}'.format(i)].to_excel(writer,sheet_name='sheet{}'.format(i), index=False) 
    
cycle_df.to_excel('cycle_df_{}.xlsx'.format(date_work))
        
    
writer.save()
writer.close()

















