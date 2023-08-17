# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 14:53:12 2022

@author: Administrator
"""

"Fedwatch--target rate & stock index "


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




###################################################################################################

"fedwatch data"   "此数据需要从fedwatch下载保存"
date_list = ['20220316','20220126','20211215','20211103','20210922','20210729']

for i in date_list:
    locals()['fedmeeting_{}'.format(i)] = pd.read_csv('fedmeeting_{}.csv'.format(i))  
    locals()['fedmeeting_{}'.format(i)]['Date'] = locals()['fedmeeting_{}'.format(i)]['Date'].apply(lambda x:int(x[6:]+x[0:2]+x[3:5]))   #修改时间
    if i=='20210922':
        break

"整理数据————按照最近发布利率的时间整合数据    "
t0 = '20210728'
j=1
for i in date_list:
    locals()['t{}'.format(j)] = i
    j+=1
    
    
date_list_df = pd.DataFrame(date_list) 

df = pd.DataFrame() 
for index,row in date_list_df.iterrows():
 
    df_b = locals()['fedmeeting_{}'.format(row[0])][locals()['fedmeeting_{}'.format(row[0])]['Date']
                                                  >int(date_list_df.loc[index+1,0])].sort_values(by='Date',ascending=0)
    df = df.append(df_b).reset_index(drop=True)
    
    if index==4:
        break  


df['50偏移25'] = df['(50-75)']-df['(25-50)']
"50bp 向 25bp 偏移"
df_50to25 = df[['Date','50偏移25']]

###################################################################################################
"获取美股指数数据"
"     参数设置"
start_date = str(df_50to25.tail(1).reset_index(drop=True).loc[0,'Date'])      #时间减一个月，确保指数涨跌幅数据和利率概率的时间保持一致
start_date = (datetime.datetime.strptime(start_date,'%Y%m%d')+relativedelta(months=-1)).strftime('%Y%m%d')
country = '美国'
# index_name = '纳斯达克综合指数'      #纳斯达克综合指数  标普500指数     道琼斯指数
period = '每日'

def index_chg(country,index_name,period,start_date,end_date):   
    idx_data =  ak.index_investing_global(country=country, index_name=index_name, period=period, start_date=start_date, end_date=end_date)
    idx_data = idx_data[['日期','收盘']].rename(columns={'收盘':'idx_data'}).sort_values(['日期'],ascending=0).reset_index(drop=True)
    idx_data['idx_data_shift-1'] =  idx_data['idx_data'].shift(-1)
    idx_data['{}'.format(index_name)] = idx_data['idx_data']/idx_data['idx_data_shift-1'] - 1
    
    idx_data['日期'] = idx_data['日期'].apply(lambda x:int(str(x)[0:4]+str(x)[5:7]+str(x)[8:]))
    idx_data = idx_data[idx_data['日期']>=df_50to25.tail(1).reset_index(drop=True).loc[0,'Date']]
    idx_data = idx_data[['日期','{}'.format(index_name)]]  
    return idx_data

###################################################################################################
for index_name in ['纳斯达克综合指数','标普500指数','道琼斯指数']:
    index_df = index_chg(country,index_name,period,start_date,now_day)   
    df_50to25 = pd.merge(df_50to25,index_df,left_on='Date',right_on='日期',how='inner')
    df_50to25 = df_50to25.drop(['日期'], 1) 

df_50to25.to_excel('Fed概率50偏移25_美股指数{}.xlsx'.format(now_day))




























