# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 11:27:54 2022

@author: Administrator
"""


"美股动量因子研究  跑一次82个小时左右"


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
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20110101", end_date="22220101", adjust="hfq")
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
f1=60



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


def test_group(stockid,stock_data,start_date,end_date,d1,d2,d3,d4,d5,f1):
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
    f1 : int
        未来n个交易日涨跌幅
    Returns：stockid数据,d1~d5、f1涨跌幅
    '''
    df_b = stock_data[stock_data['代码']==stockid][['代码','日期','收盘']].reset_index(drop=True)
    # start_data_index = df_b[df_b['日期']>=start_date].head(1).index.tolist()[0]  
    ans = pd.DataFrame(df_b[['代码','日期']])
    for i in [d1,d2,d3,d4,d5,f1]:     #循环 前n个交易日 和 未来n个交易日
        ans_b = n_chg(df_b,start_date,end_date,i)
        ans = pd.merge(ans,ans_b,'left','日期')    
    return  ans

chg_df = pd.DataFrame()
for index,row in stock_list.iterrows():
    chg_df_b = test_group(row['代码'],stock_data,start_date,end_date,d1,d2,d3,d4,d5,f1)
    chg_df = chg_df.append(chg_df_b)
    print(index,row['代码'])





"分析模块"
######################################################################################################################################
"去除数据中的含nan行     如果分析d1~d5中的组数变少，如只分析d1~d3，建议只去除d1~d3中的含nan行"
chg_df_nonan = chg_df.dropna(axis=0,how='any').reset_index(drop=True)

'''
筛选组合，筛选出该列前百分之n的数据   
'''
# percent_n=[50,60,70,70,70]
def verify_group(chg_df_nonan,percent_n):
    '''
    得到每个组合所有日期的聚合数据
    
    chg_df_nonan : DataFrame
        数据.
    percent_n : list
        筛选组合.
    Returns f1涨跌幅的平均值
    '''   
    #按每一天分组，每一天进行筛选,可以得到每一天符合参数的股票
    chg_df_nonan_1 = chg_df_nonan.groupby(['日期']).apply(lambda x:x[
                                  (x['{}涨跌幅'.format(d1)]>= np.percentile(x['{}涨跌幅'.format(d1)], percent_n[0]))&
                                  (x['{}涨跌幅'.format(d2)]>= np.percentile(x['{}涨跌幅'.format(d2)], percent_n[1]))&
                                  (x['{}涨跌幅'.format(d3)]>= np.percentile(x['{}涨跌幅'.format(d3)], percent_n[2]))&
                                  (x['{}涨跌幅'.format(d4)]>= np.percentile(x['{}涨跌幅'.format(d4)], percent_n[3]))&
                                  (x['{}涨跌幅'.format(d5)]>= np.percentile(x['{}涨跌幅'.format(d5)], percent_n[4]))]).reset_index(drop=True)
    
    # #全部数据下的筛选，没有价值
    # chg_df_nonan_1 = chg_df_nonan[(chg_df_nonan['{}涨跌幅'.format(d1)]>= np.percentile(chg_df_nonan['{}涨跌幅'.format(d1)], percent_n[0]))&
    #                               (chg_df_nonan['{}涨跌幅'.format(d2)]>= np.percentile(chg_df_nonan['{}涨跌幅'.format(d2)], percent_n[1]))&
    #                               (chg_df_nonan['{}涨跌幅'.format(d3)]>= np.percentile(chg_df_nonan['{}涨跌幅'.format(d3)], percent_n[2]))&
    #                               (chg_df_nonan['{}涨跌幅'.format(d4)]>= np.percentile(chg_df_nonan['{}涨跌幅'.format(d4)], percent_n[3]))&
    #                               (chg_df_nonan['{}涨跌幅'.format(d5)]>= np.percentile(chg_df_nonan['{}涨跌幅'.format(d5)], percent_n[4]))]
    
    
    verity_b = chg_df_nonan_1.groupby('日期').agg({'代码':'count','{}涨跌幅'.format(f1):'mean'}).reset_index()
    verity_b = verity_b.rename(columns={'代码':'筛选股票数量','{}涨跌幅'.format(f1):'{}涨跌幅平均'.format(f1)})
    verity_b['筛选组合'] = '{}_{}_{}_{}_{}'.format(percent_n[0],percent_n[1],percent_n[2],percent_n[3],percent_n[4])
    verity_b = verity_b.groupby('筛选组合').agg('mean').reset_index().drop('日期', axis=1).rename(columns={'筛选股票数量':'筛选股票数量平均','{}涨跌幅平均'.format(f1):'{}涨跌幅按日期聚合后平均'.format(f1)})

    return verity_b
    




def percent_def(interval,width_s,width_e,group_n):
    '''
    此项为了生成用来循环的百分位数组合，如：
    80,80,70,70,70
    50,60,70,70,70  (54333)等
    
    interval : int
        间隔：10 百分比间隔
    width_s : int
        宽度开始位置:1，即当前采用10，可调整
    width_e : int
        度结束位置:10，即当前采用90，可调整                    开始、结束位置为10%~90%
    group_n : int
        组数：5  最后生成列数，需要循环多少组就生产多少列

    Returns
    -------
    percent_df : dataframe
        最后生成的表格
    '''
    

    percent_bb = pd.DataFrame()   
    for i in range(width_s,width_e):
        percent_bb.loc[i,'num'] = i*interval     
    percent_bb['key'] = 0         
    percent_df = percent_bb.copy()
    
    for i in range(1,group_n):
        percent_df = pd.merge(percent_df,percent_bb,on='key',how='outer')                  
    percent_df = percent_df.drop(['key'],axis=1)
    percent_df.columns = ['num{}'.format(i) for i in range(1,group_n+1)]

    return percent_df

       
percent_df = percent_def(10,1,10,5)   #生成参数列表
percent_df=percent_df.values.tolist()    #dataframe 一行转list



verity_df = pd.DataFrame()    #每个组合所有日期的筛选数据
i = 0

"如果需要暂停，重新跑，下方代码可以选取percent_df的后面一段"
# percent_df = percent_df[25363:]


for percent_n in percent_df:
    verity_df_b = verify_group(chg_df_nonan,percent_n)
    verity_df = verity_df.append(verity_df_b)
    
    i+=1
    print(i,percent_n)


verity_df.to_excel('美股动量研究数据_每个组合{}.xlsx'.format(now_day))   




# "如果verify_group方法中不进行聚合，则允许下方的聚合，次情况是用来测试短时间段的，verity_df输出每个参数每日的明细，verity_df_agg输出每个参数的平均值"
# verity_df_agg = verity_df.groupby('筛选组合').agg('mean').reset_index().drop('日期', axis=1).rename(columns={'筛选股票数量':'筛选股票数量平均','{}涨跌幅平均'.format(f1):'{}涨跌幅按日期聚合后平均'.format(f1)})
# verity_df_agg.to_excel('动量研究数据_每个组合{}.xlsx'.format(now_day))   


















