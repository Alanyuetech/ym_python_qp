# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 13:35:26 2022

@author: Administrator
"""

"中美联动研究"
'''
北向资金和国内指数对于美股指数有一定的指导意义，但是自相关程度太高，
不论是用模型预测还是使用统计方式预测都会出现预测值和真实值之间方差过大的问题

解决方法：类似的指标/策略只用一个，只使用北向资金来对美股指数进行策略的研究。'''

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





"中国指数"

sz_index = ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20180101", end_date="22220101").rename(columns={'收盘':'上证'})[['日期','上证']]
shz_index = ak.index_zh_a_hist(symbol="399001", period="daily", start_date="20180101", end_date="22220101").rename(columns={'收盘':'深证'})[['日期','深证']]
hs300_index = ak.index_zh_a_hist(symbol="000300", period="daily", start_date="20180101", end_date="22220101").rename(columns={'收盘':'沪深300'})[['日期','沪深300']]
cyb_index = ak.index_zh_a_hist(symbol="399006", period="daily", start_date="20180101", end_date="22220101").rename(columns={'收盘':'创业板'})[['日期','创业板']]



"北向资金净流入"
north_fund_net = ak.stock_hsgt_north_net_flow_in_em(symbol="北上").rename(columns={'date':'日期','value':'北向'})
north_fund_net['北向'] = north_fund_net['北向']/10000






###########################################################################################################################################    


'''因变量：美国上市的中国概念ETF
    自变量：中国的大盘指数，北向资金
'''


"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock = us_stock.loc[us_stock['名称'].str.contains('中国')][['序号','名称','代码']]     #中国代码标样
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
us_stock.drop(us_stock[pd.isna(us_stock['代码'])].index, inplace=True)   #删除没有没有代码的股票
us_stock = us_stock.reset_index(drop=True)


"合并所有ETF数据"
us_stock_data = pd.DataFrame()
num=1
for index,row in us_stock.iterrows():
    if num ==1:
        us_stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20200101", end_date="22220101", adjust="").rename(columns={'收盘':'{}'.format(row['stock_id'])})[['日期','{}'.format(row['stock_id'])]]
        us_stock_data = us_stock_data_b.copy()
        print(index,row['代码'])
        num = 2
    else:
        us_stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20200101", end_date="22220101", adjust="").rename(columns={'收盘':'{}'.format(row['stock_id'])})[['日期','{}'.format(row['stock_id'])]]
        us_stock_data = pd.merge(us_stock_data,us_stock_data_b,how='outer',on='日期')
        print(index,row['代码'])
    
 

# stock_data_b = ak.stock_us_hist(symbol='{}'.format('107.CQQQ'), start_date="20200101", end_date="22220101", adjust="").rename(columns={'收盘':'CQQQ'})[['日期','CQQQ']]

 

def linear_regression_us(dv,indv_1,indv_2,indv_3,indv_4,indv_5,n,a,b):
    "线性回归--数据合并"
    
    "dfs合并需要回归的数据，首列因变量，后续为自变量"
    dfs = [dv,indv_1,indv_2,indv_3,indv_4,indv_5]
    merge_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),dfs)
    merge_data = merge_data.sort_values('日期')
    merge_data = merge_data.dropna(axis=0,how='any') 

    "回归"

    datas = merge_data.copy()
    y = datas.iloc[:, n] # 因变量为第 2 列数据
    x = datas.iloc[:, a:b] # 自变量为第 3 列到第 n 列数据
    # x = sm.add_constant(x) # 若模型中有截距，必须有这一步
    model = sm.OLS(y, x).fit() # 构建最小二乘模型并拟合
    print(model.summary()) # 输出回归结果   
    
for i in range(21,22):           #   stock_data.shape[1]
    print('因变量为：{}'.format(us_stock[us_stock['stock_id']==us_stock_data.iloc[:,i].name].reset_index(drop=True).loc[0,'名称']))
    dv =  us_stock_data.iloc[:,[0,i]]   
    linear_regression_us(dv,sz_index,shz_index,hs300_index,cyb_index,north_fund_net,1,2,7)
    print("")
    
    
    
###########################################################################################################################################

'''因变量：中国大盘指数
    自变量：美国三大指数，北向资金
'''

"美股指数-----全局模式"
naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="20180101", end_date="22220101").rename(columns={'收盘':'纳指'})[['日期','纳指']]

sp500_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="20180101", end_date="22220101").rename(columns={'收盘':'标普'})[['日期','标普']]

dj_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
                                      period="每日", start_date="20180101", end_date="22220101").rename(columns={'收盘':'道琼斯'})[['日期','道琼斯']]

naq_index['日期'] = naq_index['日期'].astype('str')
sp500_index['日期'] = sp500_index['日期'].astype('str')
dj_index['日期'] = dj_index['日期'].astype('str')


"合并所有中国指数数据"
stock_data_b =  [sz_index,shz_index,hs300_index,cyb_index]
stock_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),stock_data_b)


def linear_regression_cn(dv,indv_1,indv_2,indv_3,indv_4,n,a,b):
    "线性回归--数据合并"
    
    "dfs合并需要回归的数据，首列因变量，后续为自变量"
    dfs = [dv,indv_1,indv_2,indv_3,indv_4]
    merge_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),dfs)
    merge_data = merge_data.sort_values('日期')
    merge_data = merge_data.fillna(method='ffill')   #用前一日的数据填充
    merge_data.iloc[:,2:] = merge_data.iloc[:,2:].shift(1)   #第3列后用前一天的数据
    merge_data = merge_data.dropna(axis=0,how='any') 

    "回归"

    datas = merge_data.copy()
    y = datas.iloc[:, n] # 因变量为第 2 列数据
    x = datas.iloc[:, a:b] # 自变量为第 3 列到第 n 列数据,如果需要限定几列，才有必要使用b
    # x = sm.add_constant(x) # 若模型中有截距，必须有这一步
    model = sm.OLS(y, x).fit() # 构建最小二乘模型并拟合
    print(model.summary()) # 输出回归结果


    
for i in range(1,5):           #   stock_data.shape[1]
    # print('因变量为：{}'.format(us_stock[us_stock['stock_id']==stock_data.iloc[:,i].name].reset_index(drop=True).loc[0,'名称']))
    print('因变量为：{}'.format(list(stock_data.iloc[:,[0,i]])[1]))
    dv =  stock_data.iloc[:,[0,i]]
    linear_regression_cn(dv,naq_index,sp500_index,dj_index,north_fund_net,1,2,4)
    print("")
    


###########################################################################################################################################

'''因变量：中国大盘指数
    自变量：美国三大指数，北向资金
'''

"美股指数-----全局模式"
naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="20180101", end_date="22220101").rename(columns={'收盘':'纳指'})[['日期','纳指']]

sp500_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="20180101", end_date="22220101").rename(columns={'收盘':'标普'})[['日期','标普']]

dj_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
                                      period="每日", start_date="20180101", end_date="22220101").rename(columns={'收盘':'道琼斯'})[['日期','道琼斯']]

naq_index['日期'] = naq_index['日期'].astype('str')
sp500_index['日期'] = sp500_index['日期'].astype('str')
dj_index['日期'] = dj_index['日期'].astype('str')


"合并所有中国指数数据"
stock_data_b =  [sz_index,shz_index,hs300_index,cyb_index]
stock_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),stock_data_b)


def linear_regression_cn(dv,indv_1,indv_2,indv_3,indv_4,n,a,b):
    "线性回归--数据合并"
    
    "dfs合并需要回归的数据，首列因变量，后续为自变量"
    dfs = [dv,indv_1,indv_2,indv_3,indv_4]
    merge_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),dfs)
    merge_data = merge_data.sort_values('日期')
    merge_data = merge_data.fillna(method='ffill')   #用前一日的数据填充
    merge_data.iloc[:,2:] = merge_data.iloc[:,2:].shift(1)   #第3列后用前一天的数据
    merge_data = merge_data.dropna(axis=0,how='any') 

    "回归"

    datas = merge_data.copy()
    y = datas.iloc[:, n] # 因变量为第 2 列数据
    x = datas.iloc[:, a:b] # 自变量为第 3 列到第 n 列数据,如果需要限定几列，才有必要使用b
    # x = sm.add_constant(x) # 若模型中有截距，必须有这一步
    model = sm.OLS(y, x).fit() # 构建最小二乘模型并拟合
    print(model.summary()) # 输出回归结果


    
for i in range(1,5):           #   stock_data.shape[1]
    # print('因变量为：{}'.format(us_stock[us_stock['stock_id']==stock_data.iloc[:,i].name].reset_index(drop=True).loc[0,'名称']))
    print('因变量为：{}'.format(list(stock_data.iloc[:,[0,i]])[1]))
    dv =  stock_data.iloc[:,[0,i]]
    linear_regression_cn(dv,naq_index,sp500_index,dj_index,north_fund_net,1,2,4)
    print("")
    

#########################################################################

"通用版本回归"



def linear_regression(dv,indv,n,a,b):
    "线性回归--数据合并"
    "dv为单列输入，indv为多列输入，n:因变量位置，1（第二列）  ，a,b:自变量位置 2:xx （第三列到xx列）     "
    "dfs合并需要回归的数据，首列因变量，后续为自变量"
    dfs = [dv,indv]
    merge_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),dfs)
    merge_data = merge_data.sort_values('日期')
    # merge_data = merge_data.fillna(method='ffill')   #用前一日的数据填充
    # merge_data.iloc[:,2:] = merge_data.iloc[:,2:].shift(1)   #第3列后用前一天的数据
    merge_data = merge_data.dropna(axis=0,how='any') 

    "回归"

    datas = merge_data.copy()
    y = datas.iloc[:, 1] # 因变量为第 2 列数据
    x = datas.iloc[:, 2:] # 自变量为第 3 列到第 n 列数据,如果需要限定几列，才有必要使用b
    # x = sm.add_constant(x) # 若模型中有截距，必须有这一步
    model = sm.OLS(y, x).fit() # 构建最小二乘模型并拟合
    print(model.summary()) # 输出回归结果


indv = [sz_index,shz_index,hs300_index,cyb_index]    #自变量 
indv = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),indv)
for i in range(1,5):           #   stock_data.shape[1]
    # print('因变量为：{}'.format(us_stock[us_stock['stock_id']==stock_data.iloc[:,i].name].reset_index(drop=True).loc[0,'名称']))
    print('因变量为：{}'.format(list(stock_data.iloc[:,[0,i]])[1]))
    dv =  stock_data.iloc[:,[0,i]]
    linear_regression(dv,indv,1,2,5)
    print("")


###########################################################################################################################################

"数据准备"
dfs = [north_fund_net,sz_index,shz_index,hs300_index,cyb_index]
merge_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),dfs)
merge_data = merge_data.sort_values('日期')
merge_data = merge_data.dropna(axis=0,how='any') 
"回归"
datas = merge_data[['CQQQ','上证','深证','沪深300','创业板','北向']]
y = datas.iloc[:, 0] # 因变量为第 1 列数据
x = datas.iloc[:, 1:6] # 自变量为第 2 列到第 4 列数据
# x = sm.add_constant(x) # 若模型中有截距，必须有这一步
model = sm.OLS(y, x).fit() # 构建最小二乘模型并拟合
print(model.summary()) # 输出回归结果
"预测"
merge_data['CQQQ_exp'] = -0.0486 * merge_data['上证'] + 0.0036 * merge_data['深证'] + 0.0435 * merge_data['沪深300'] - 0.0075 * merge_data['创业板']
merge_data['CQQQ_chg'] = 100*(merge_data['CQQQ']/merge_data['CQQQ'].shift(1) -1)
merge_data['CQQQ_expchg'] = 100*(merge_data['CQQQ_exp']/merge_data['CQQQ_exp'].shift(1) -1)
merge_data['expchg-chg'] = merge_data['CQQQ_expchg'] - merge_data['CQQQ_chg']

avg_expchg_chg = merge_data['expchg-chg'].mean()





























