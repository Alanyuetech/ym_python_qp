# -*- coding: utf-8 -*-
"""
Created on Wed Dec  1 09:52:55 2021

@author: Administrator
"""

"获取美股实时周涨幅--平时用作验证，周六用作填表"

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

def get_last_wxday(input_date,n):
    "获取输入日期的上周几"
    inp_date = datetime.datetime.strptime(input_date, '%Y%m%d')
    week_n = inp_date.weekday()+1
    date_ans = inp_date - datetime.timedelta(days=week_n + 7 - n )
    date_ans = date_ans.strftime('%Y%m%d')
    return date_ans

def get_wxday(input_date,n):
    "获取输入日期的本周几"
    inp_date = datetime.datetime.strptime(input_date, '%Y%m%d')
    week_n = inp_date.weekday()+1
    date_ans = inp_date - datetime.timedelta(days=week_n - n )
    date_ans = date_ans.strftime('%Y%m%d')
    return date_ans



last_friday = get_last_wxday(now_day,5)      #  要写上一周最后一个交易日的日子，周五没有交易就定位到周四
monday = get_wxday(now_day,1)



"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列



"获取5个板块的股票代码"
for i in range(0,7):
    locals()['id_group_'+str(i+1)] = pd.read_excel('美股5个策略的股票代码.xlsx',engine='openpyxl',sheet_name=i)
    locals()['id_group_'+str(i+1)] = pd.merge(locals()['id_group_'+str(i+1)],us_stock[['代码','stock_id']],how='left',on='stock_id')


"获取某段时间内的每日涨幅"   
def stock_data(id_group_n,start_date,end_date):
    stock_data = pd.DataFrame()
    for index,row in id_group_n.iterrows():
        stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date=start_date, end_date=end_date)
        stock_data_b['代码']=row['代码']
        stock_data = stock_data.append(stock_data_b)
    return stock_data


"周涨幅   和    每日涨幅   一次跑一个"

########################    周涨幅     ###################################################################

"获取截至今天的周涨幅"
def week_change(id_group_n,stock_data_n):
    "当日收盘价/上周五收盘价 - 1 "
    if len(id_group_n)==0:
        return id_group_n
    ans = pd.merge(id_group_n,stock_data_n[['代码','日期','收盘']],how='left',on='代码')
    id_group_n['周涨幅'] = ((ans.groupby('代码').tail(1).reset_index(drop=True)['收盘'])/(ans.groupby('代码').head(1).reset_index(drop=True)['收盘']) -1)
    id_group_n['周涨幅'] = id_group_n['周涨幅'].apply(lambda x: '%.2f%%' % (x*100))
   
    return id_group_n
    

"获取截至今天的周涨幅"
for i in range(1,8):
    locals()['stock_data_'+str(i)] = stock_data(locals()['id_group_'+str(i)],last_friday,now_day)   
    locals()['id_group_w_'+str(i)] = week_change(locals()['id_group_'+str(i)],locals()['stock_data_'+str(i)])
    
    print('sheet'+str(i)+'   结束')
    

"将周涨幅结果放到五个sheet里"
writer = pd.ExcelWriter('美股策略周涨幅.xlsx')
for i in range(1,8):
    locals()['id_group_w_'+str(i)].to_excel(writer,sheet_name='sheet{}'.format(i), index=False) 
writer.save()
writer.close()


########################    区间内每日涨幅     ###########################################################
# id_group_n=id_group_1
# stock_data_n=stock_data_1

"每日涨幅调整"
def day_change(id_group_n,stock_data_n):
    "调整格式：行为股票代码，列为日期"
    ans = pd.merge(id_group_n,stock_data_n[['日期','涨跌幅','代码']],how='left',on='代码')
    ans['涨跌幅'] = ans['涨跌幅'].apply(lambda x: '%.2f%%' % (x))
    ans = ans.groupby(['日期','代码'], as_index=False).sum()
    ans = pd.pivot(ans, index="代码", columns="日期",values='涨跌幅').reset_index()
    ans = pd.merge(id_group_n,ans,how='left',on='代码')
    zzf = ans.pop('周涨幅')
    ans['周涨幅'] = zzf
    return ans
     
     
"某段时间内的每日涨幅"

for i in range(1,8):
    locals()['stock_data_'+str(i)] = stock_data(locals()['id_group_'+str(i)],monday,now_day)   
    locals()['id_group_d_'+str(i)] = day_change(locals()['id_group_'+str(i)],locals()['stock_data_'+str(i)])
    
    print('sheet'+str(i)+'   结束')


"将日涨幅结果放到五个sheet里"
writer = pd.ExcelWriter('美股策略每日涨幅.xlsx')
for i in range(1,8):
    locals()['id_group_d_'+str(i)].to_excel(writer,sheet_name='sheet{}'.format(i), index=False) 
writer.save()
writer.close()  
    
    
    
    
    
