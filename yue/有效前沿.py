# -*- coding: utf-8 -*-
"""
Created on Thu Feb 10 14:49:02 2022

@author: Administrator
"""

"有效前沿、 通过遍历确定占比 "

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


"输入需要测试的不同资产数据"

stock_list = pd.DataFrame()
stock_list['stock_id'] = ['AAPL','MSFT','GOOGL','AMZN','TSLA','FB']
p_n = len(stock_list)
"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_list = pd.merge(stock_list,us_stock[['代码','stock_id']],how='left',on='stock_id')

"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20150101", end_date=now_day, adjust="")
    stock_data_b['代码']=row['代码']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])

data_merge = pd.DataFrame()
data_merge['日期'] = stock_data['日期'].drop_duplicates().sort_values().reset_index(drop=True)

for index,row in stock_list.iterrows():
    locals()['data_{}'.format(row['stock_id'])] =  stock_data[stock_data['代码']==row['代码']]
    locals()['data_{}'.format(row['stock_id'])]['{}涨跌幅'.format(row['stock_id'])] = locals()['data_{}'.format(row['stock_id'])]['涨跌幅']
    data_merge = pd.merge(data_merge,locals()['data_{}'.format(row['stock_id'])][['日期','{}涨跌幅'.format(row['stock_id'])]],how='left',on='日期')

data_merge = data_merge.dropna()

"循环遍历不同的资产配比，计算最大的  E(P)/σ"

def ep_σ(w1,w2,w3,w4,w5,w6,data_merge):    # wn 的个数需要具体情况具体设定  stock_list中有多少资产类别，就用多少个比重参数
    "根据输入的配比，形成新的df，计算该配比下的 E(P) 和 σ"
    ans_b = pd.DataFrame()
    ans_data = data_merge.copy()
    for i in range(1,data_merge.shape[1]):
        ans_data.iloc[:,i] = data_merge.iloc[:,i]*locals()['w{}'.format(i)]/100
    
    ans_data['E(p)'] = ans_data.iloc[:,1:data_merge.shape[1]].sum(axis=1) 
    ans_b.loc[0,'E(p)'] = ans_data['E(p)'].mean()
    ans_b.loc[0,'σ'] = ans_data['E(p)'].std(ddof = 0)     #设置为总体标准差

    return ans_b


"设定配比参数df"
"   设置遍历粒度"
w_df = pd.DataFrame()
w_df['w1'] = range(10,101,4)
w_df['key'] = 'key'
w_df_b = w_df.copy()
for i in range(2,p_n+1):  #设定配比参数的个数
    w_df = pd.merge(w_df,w_df_b,on='key')
w_df = w_df.drop(['key'], 1)


w_df_columns = list()
for i in range(1,p_n+1):
    w_df_columns.append('w{}'.format(i))

w_df.columns = w_df_columns
w_df['w'] = w_df.iloc[:,0:w_df.shape[1]].sum(axis=1) 
w_df = w_df[w_df['w']==100].reset_index(drop=True)
w_df = w_df.iloc[:,0:w_df.shape[1]-1]


"循环配比"
ans = pd.DataFrame()
for index,row in w_df.iterrows():
    ans_b = ep_σ(row['w1'],row['w2'],row['w3'],row['w4'],row['w5'],row['w6'],data_merge)
    ans_b['w'] = '{}_{}_{}_{}_{}_{}'.format(row['w1'],row['w2'],row['w3'],row['w4'],row['w5'],row['w6'])
    ans = pd.concat([ans,ans_b])
    
    
    
ans = ans.reset_index(drop=True)
ans['E(P)/σ'] = ans['E(p)']/ans['σ']
   
"获取有效前沿"
min_σ = ans['σ'].min()
gmvp_ep = ans[ans['σ'] == min_σ].reset_index(drop=True).loc[0,'E(p)']
ans = ans[ans['E(p)']>=gmvp_ep].reset_index(drop=True)

"画散点图"
x = ans['σ']
y = ans['E(p)']

plt.scatter(x, y)
plt.show()
    

    
    
    
    
    
    
    
    
    
    





