# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 14:21:51 2022

@author: 666
"""



"美股动量因子选股"


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


"""
获取股票代码  此项部分可分为两类获取途径：
    1:全部股票进行排序
    2:股票名单进行排序
"""

"全部股票"
######################################################################################################################################



######################################################################################################################################

"股票名单"
stock_list = pd.read_excel('美股200亿以上筛选.xlsx',engine='openpyxl')
stock_list = stock_list.rename(columns={'代码':'stock_id'})

"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_list = pd.merge(stock_list,us_stock[['代码','stock_id']],how='left',on='stock_id')


stock_list.drop(stock_list[pd.isna(stock_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
stock_list = stock_list.reset_index(drop=True)


"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20110101", end_date="22220101", adjust="hfq")    #选股时候的时间设置不用非常长，够用即可
    stock_data_b['代码']=row['代码']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])

stock_data['日期'] =  stock_data['日期'].apply(lambda x:int(x[0:4]+x[5:7]+x[8:]))


"""
动量因子测试：
    1: D5 D10 D20 D60 D120 D240 ————测试组
    2:未来一个季度  D60 ————验证组
"""

# stockid = '105.AAPL'
start_date = 20201131    #  暂时没用
end_date = 20211131      #  暂时没用
d1=-5
d2=-20
d3=-60
d4=-120
d5=-250



def n_chg(df_b,start_date,end_date,dfn):
    '''
    dfn : int
        过去n个交易日/未来n个交易日
    Returns：dfn下的涨跌幅，前n个交易日   或者   未来n个交易日
    '''
    df_b['{}收盘'.format(dfn)] = df_b['收盘'].shift(-dfn)
    df_b['{}涨跌幅'.format(dfn)] = df_b['收盘']/df_b['{}收盘'.format(dfn)] - 1 if dfn<0 else df_b['{}收盘'.format(dfn)]/df_b['收盘'] - 1
    ans_b = df_b[['日期','{}涨跌幅'.format(dfn)]]
    return ans_b



def test_group(stockid,stock_data,start_date,end_date,d1,d2,d3,d4,d5):
    '''
    stockid : str
        股票代码，如：105.ADI
    stock_data : DataFrame
        数据
    start_date : int
        开始日期
    end_date : int
        结束日期   两个日期卡中间的测试时间
    d1~d5: int
        过去n个交易日涨跌幅
    Returns：stockid数据,d1~d5、f1涨跌幅
    '''
    df_b = stock_data[stock_data['代码']==stockid][['代码','日期','收盘']].reset_index(drop=True)
    # start_data_index = df_b[df_b['日期']>=start_date].head(1).index.tolist()[0]  
    ans = pd.DataFrame(df_b[['代码','日期']])
    for i in [d1,d2,d3,d4,d5]:     #循环 前n个交易日 
        ans_b = n_chg(df_b,start_date,end_date,i)
        ans = pd.merge(ans,ans_b,'left','日期')    
    return  ans


chg_df = pd.DataFrame()
for index,row in stock_list.iterrows():
    chg_df_b = test_group(row['代码'],stock_data,start_date,end_date,d1,d2,d3,d4,d5)
    chg_df = chg_df.append(chg_df_b)
    print(index,row['代码'])


"分析模块"
######################################################################################################################################
"去除数据中的含nan行     如果分析d1~d5中的组数变少，如只分析d1~d3，建议只去除d1~d3中的含nan行"
chg_df_nonan = chg_df.dropna(axis=0,how='any').reset_index(drop=True)


"由美股动量因子研究所得的参数"
percent_n=[10,50,80,90,90]

"筛选组合，筛选出该列前百分之n的数据"

choice_df = chg_df_nonan.groupby(['日期']).apply(lambda x:x[
                              (x['{}涨跌幅'.format(d1)]>= np.percentile(x['{}涨跌幅'.format(d1)], percent_n[0]))&
                              (x['{}涨跌幅'.format(d2)]>= np.percentile(x['{}涨跌幅'.format(d2)], percent_n[1]))&
                              (x['{}涨跌幅'.format(d3)]>= np.percentile(x['{}涨跌幅'.format(d3)], percent_n[2]))&
                              (x['{}涨跌幅'.format(d4)]>= np.percentile(x['{}涨跌幅'.format(d4)], percent_n[3]))&
                              (x['{}涨跌幅'.format(d5)]>= np.percentile(x['{}涨跌幅'.format(d5)], percent_n[4]))]).reset_index(drop=True)



"特定日期后选股，每日选出的股票进行整理"
n_date = 20221001   #截取该日期之后的数据，季度初日期


choice_df_n = choice_df[choice_df['日期']>=n_date].sort_values('日期',ascending=0).reset_index(drop=True)
count_n = pd.DataFrame(choice_df_n['代码'].value_counts()).reset_index().rename(columns={'代码':'出现次数','index':'代码'})
choice_df_n = pd.merge(choice_df_n,count_n,on='代码',how='left')
choice_df_n = choice_df_n.sort_values(['日期','出现次数'],ascending=[0,0])

choice_df_n.to_excel('美股动量因子选股{}.xlsx'.format(now_day))  
































































