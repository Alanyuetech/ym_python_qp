# -*- coding: utf-8 -*-
"""
Created on Mon Nov 22 11:43:51 2021

@author: Administrator
"""


"美股回撤测试验证"

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


"读取股票代码列表"
stock_list = pd.read_excel('美股200亿以上筛选.xlsx',engine='openpyxl')
stock_list = stock_list.rename(columns={'代码':'stock_id'})
stock_50b_list = stock_list[stock_list['总市值-亿']>=200]      #此处修改 >200亿   >500亿


"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_50b_list = pd.merge(stock_50b_list,us_stock[['代码','stock_id']],how='left',on='stock_id')


stock_50b_list.drop(stock_50b_list[pd.isna(stock_50b_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
stock_50b_list = stock_50b_list.reset_index(drop=True)

# "模糊查询"
# aa = us_stock.loc[us_stock['名称'].str.contains('小米')]
# aa = us_stock.loc[us_stock['代码'].str.contains('BF_')]


"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_50b_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20110101", end_date="22220101", adjust="hfq")
    stock_data_b['代码']=row['代码']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])


###################################################################################################################################
# "找到新股，新股选股时使用"
# new_stock_50b_list = stock_data.groupby(by='代码').head(1)   #拿到第一个交易日
# new_stock_50b_list = new_stock_50b_list[new_stock_50b_list['日期']>='2021-01-01']
# new_stock_list = pd.merge(new_stock_50b_list['代码'],stock_50b_list[['stock_id','代码','名称','所属行业']],on='代码',how='left')
# new_stock_list.to_excel('新股列表观察{}.xlsx'.format(now_day))
###################################################################################################################################

"过去 n 个交易日 回撤幅度 达到 x% ，测试 m 个交易日后 的涨幅  or  测试上涨 y% 需要多少个交易日"

def us_stock_test(stock_id,stock_data,n,x,m,y):    
    x = x/100
    y = y/100 
    "此函数的方式为：设置回撤幅度，找到过去交易日内满足此回撤幅度的日期"
    "由于算法问题，可能会出现一段时间内最大回撤为30%，但设定为20%，则会出现连续交易日都满足回撤为20%的情况，增加达到回撤条件的次数"
    
    stock_test = stock_data[stock_data['代码']==stock_id][['日期','收盘','涨跌幅','代码']]
    stock_test['回撤前'] = stock_test['收盘']/(1-x)
    stock_test = stock_test.sort_values(['日期'],ascending=0).reset_index(drop=True)
    stock_test['回撤前日期']=''  
    stock_test['回撤前收盘']=np.nan
    for index,row in stock_test.iterrows():
        stock_test_b = stock_test.loc[index:index+n-1]   #近 n 个交易日
        ans_b = stock_test_b.loc[index+1:index+n-1][stock_test_b['收盘']>=row['回撤前']].head(1).reset_index(drop=True)
        if len(ans_b)>0:
            stock_test.loc[index,'回撤前日期'] = ans_b.loc[0,'日期']
            stock_test.loc[index,'回撤前收盘'] = ans_b.loc[0,'收盘']
    stock_test['未来涨跌幅'] = stock_test['收盘'].shift(m)/stock_test['收盘'] -1
    stock_test = stock_test[stock_test['回撤前日期']!='']    
    ans = pd.DataFrame(columns=(['代码','达到回撤条件次数','回撤后上涨次数','回撤后上涨概率','未来涨跌幅平均值']))
    ans.loc[0,'代码'] = stock_id
    ans.loc[0,'达到回撤条件次数'] = len(stock_test)
    ans.loc[0,'回撤后上涨次数'] = len(stock_test[stock_test['未来涨跌幅']>=0])
    ans.loc[0,'回撤后上涨概率'] = len(stock_test[stock_test['未来涨跌幅']>=0])/len(stock_test) if len(stock_test)!=0 else np.nan
    ans.loc[0,'未来涨跌幅平均值'] = stock_test['未来涨跌幅'].mean()
    
    return ans

def us_df(stock_50b_list,n,x,m,y):
    df = pd.DataFrame(columns=(['代码','达到回撤条件次数','回撤后上涨次数','回撤后上涨概率','未来涨跌幅平均值']))
    for index,row in stock_50b_list.iterrows():
        df_b = us_stock_test(row['代码'],stock_data,n,x,m,y)
        df = df.append(df_b)
        print(index,row['代码'])
    df = df.reset_index(drop=True)   
    df_mean = df[['达到回撤条件次数','回撤后上涨次数','回撤后上涨概率','未来涨跌幅平均值']].mean()    #平均值
    
    return (df,df_mean)


############################################
"一组数据单独测试时"
n = 60         #过去交易日
x = 25          #回撤幅度
m = 120         #未来交易日数
y = 20     #未来上涨幅度
usdf = us_df(stock_50b_list, n, x, m, y)
df = usdf[0]
df_mean = usdf[1]

##################################################################################################

"循环  n,x,m  找到最佳的期限和回撤幅度组合"
df_mean = pd.DataFrame(columns=(['达到回撤条件次数','回撤后上涨次数','回撤后上涨概率','未来涨跌幅平均值','参数']))

# '下方时间不太合理，按照交易日算，一个月应该是20而不是30 修改日期：20220411'
# for n in range(30,240,30):
#     for x in range(10,50,5):
#         for m in range(30,240,30):
#             usdf = us_df(stock_50b_list, n, x, m, y)
#             locals()['df_{}_{}_{}'.format(n,x,m)] = usdf[0]
#             locals()['df_mean_{}_{}_{}'.format(n,x,m)] = usdf[1]
#             locals()['df_mean_{}_{}_{}'.format(n,x,m)] = pd.DataFrame(locals()['df_mean_{}_{}_{}'.format(n,x,m)]).T 
#             locals()['df_mean_{}_{}_{}'.format(n,x,m)]['参数'] = '{}_{}_{}'.format(n,x,m)
#             df_mean = df_mean.append(locals()['df_mean_{}_{}_{}'.format(n,x,m)])
#             print(n,x,m)

'研究时间锁定为[20,60,120,250]'
for n in [20,60,120,250]:
    for x in range(10,55,5):
        for m in [20,60,120,250]:
            usdf = us_df(stock_50b_list, n, x, m, y)
            locals()['df_{}_{}_{}'.format(n,x,m)] = usdf[0]
            locals()['df_mean_{}_{}_{}'.format(n,x,m)] = usdf[1]
            locals()['df_mean_{}_{}_{}'.format(n,x,m)] = pd.DataFrame(locals()['df_mean_{}_{}_{}'.format(n,x,m)]).T 
            locals()['df_mean_{}_{}_{}'.format(n,x,m)]['参数'] = '{}_{}_{}'.format(n,x,m)
            df_mean = df_mean.append(locals()['df_mean_{}_{}_{}'.format(n,x,m)])
            print(n,x,m)

            
            
df_mean = df_mean.reset_index(drop=True)
   
df_mean.to_excel("美股回撤测试验证{}.xlsx".format(date_work))  
            
##################################################################################################


"测试新股回撤：将时间拉回到股票刚发行后的头一年时间"
stock_data = stock_data.groupby('代码').head(250)


"循环  n,x,m  找到最佳的期限和回撤幅度组合"
new_df_mean = pd.DataFrame(columns=(['达到回撤条件次数','回撤后上涨次数','回撤后上涨概率','未来涨跌幅平均值','参数']))
# '下方时间不太合理，按照交易日算，一个月应该是20而不是30 修改日期：20220411'
# for n in range(20,140,20):
#     for x in range(10,55,5):
#         for m in range(20,80,20):
#             usdf = us_df(stock_50b_list, n, x, m, y)
#             locals()['new_df_{}_{}_{}'.format(n,x,m)] = usdf[0]
#             locals()['new_df_mean_{}_{}_{}'.format(n,x,m)] = usdf[1]
#             locals()['new_df_mean_{}_{}_{}'.format(n,x,m)] = pd.DataFrame(locals()['new_df_mean_{}_{}_{}'.format(n,x,m)]).T 
#             locals()['new_df_mean_{}_{}_{}'.format(n,x,m)]['参数'] = '{}_{}_{}'.format(n,x,m)
#             new_df_mean = new_df_mean.append(locals()['new_df_mean_{}_{}_{}'.format(n,x,m)])
#             print(n,x,m)
     
'研究时间锁定为[20,60,120,250]'
for n in [20,60,120]:
    for x in range(10,55,5):
        for m in [20,60,120]:
            usdf = us_df(stock_50b_list, n, x, m, y)
            locals()['new_df_{}_{}_{}'.format(n,x,m)] = usdf[0]
            locals()['new_df_mean_{}_{}_{}'.format(n,x,m)] = usdf[1]
            locals()['new_df_mean_{}_{}_{}'.format(n,x,m)] = pd.DataFrame(locals()['new_df_mean_{}_{}_{}'.format(n,x,m)]).T 
            locals()['new_df_mean_{}_{}_{}'.format(n,x,m)]['参数'] = '{}_{}_{}'.format(n,x,m)
            new_df_mean = new_df_mean.append(locals()['new_df_mean_{}_{}_{}'.format(n,x,m)])
            print(n,x,m)      
            
new_df_mean = new_df_mean.reset_index(drop=True)
new_df_mean.to_excel("新股回撤测试验证{}.xlsx".format(date_work))  




##################################################################################################
# "单个股票穿透观察"
# n = 60         #过去交易日
# x = 25          #回撤幅度
# m = 120         #未来交易日数
# y = 20     #未来上涨幅度

# stock_id = '106.ORCL'
# stock_test = stock_data[stock_data['代码']==stock_id][['日期','收盘','涨跌幅','代码']]
# stock_test['回撤前'] = stock_test['收盘']/(1-x)
# stock_test = stock_test.sort_values(['日期'],ascending=0).reset_index(drop=True)
# stock_test['回撤前日期']=''
# stock_test['回撤前收盘']=np.nan
# for index,row in stock_test.iterrows():
#     stock_test_b = stock_test.loc[index:index+n-1]   #近 n 个交易日 (时间倒叙，所以是最近n个交易日)
#     ans_b = stock_test_b.loc[index+1:index+n-1][stock_test_b['收盘']>=row['回撤前']].head(1).reset_index(drop=True)
#     if len(ans_b)>0:
#         stock_test.loc[index,'回撤前日期'] = ans_b.loc[0,'日期']
#         stock_test.loc[index,'回撤前收盘'] = ans_b.loc[0,'收盘']
# stock_test['未来涨跌幅'] = stock_test['收盘'].shift(m)/stock_test['收盘'] -1
# stock_test = stock_test[stock_test['回撤前日期']!='']    
# ans = pd.DataFrame(columns=(['代码','达到回撤条件次数','回撤后上涨次数','回撤后上涨概率','未来涨跌幅平均值']))
# ans.loc[0,'代码'] = stock_id
# ans.loc[0,'达到回撤条件次数'] = len(stock_test)
# ans.loc[0,'回撤后上涨次数'] = len(stock_test[stock_test['未来涨跌幅']>=0])
# ans.loc[0,'回撤后上涨概率'] = len(stock_test[stock_test['未来涨跌幅']>=0])/len(stock_test) if len(stock_test)!=0 else np.nan
# ans.loc[0,'未来涨跌幅平均值'] = stock_test['未来涨跌幅'].mean()

##################################################################################################

"新股"   #需要的是所有200亿以上的股票池

# "通过下方代码选新股范围，复制到富途牛牛后手动删除不符合要求的股票，最后形成  新股列表观察.xlsx"
# new_stock_50b_list = stock_data.groupby(by='代码').head(1)   #拿到第一个交易日
# new_stock_50b_list = new_stock_50b_list[new_stock_50b_list['日期']>='2021-01-01']
# new_stock_50b_list['代码'] = new_stock_50b_list['代码'].str.split('.',expand=True)[1]  #分列
# new_stock_50b_list.to_excel('新股列表观察{}.xlsx'.format(now_day))



# new_stock_list =  pd.read_excel('新股列表观察.xlsx',engine='openpyxl',dtype={'时间':'str'})
# new_stock_list = pd.merge(new_stock_list,stock_50b_list[['stock_id','代码']],on='stock_id',how='left')

# "分析新股"
# new_stock_data = pd.merge(new_stock_list[['代码']],stock_data[['日期','收盘','涨跌幅','代码']],how='left',on='代码')
# n = 120    # 区间:发行后120个交易日
# def new_stock_analysis(stock_id,new_stock_data,n):
    
#     new_stock_test = new_stock_data[new_stock_data['代码']==stock_id][['日期','收盘','涨跌幅','代码']].reset_index(drop=True)
#     ans = pd.DataFrame(columns=(['代码','发行日','区间内最大收盘价日期','最大收盘价后最小收盘价日期','现价日期','上涨时间','回撤时间',
#                                  '发行日收盘','最大收盘价','最大收盘价后最小收盘价','回撤幅度','现价','回撤后上涨幅度']))
#     ans.loc[0,'代码'] = stock_id
#     ans.loc[0,'发行日'] = new_stock_test.loc[0,'日期']
#     ans.loc[0,'发行日收盘'] = new_stock_test.loc[0,'收盘']
#     ans.loc[0,'现价日期'] = new_stock_test.tail(1).reset_index(drop=True).loc[0,'日期']
#     ans.loc[0,'现价'] = new_stock_test.tail(1).reset_index(drop=True).loc[0,'收盘']  
    
    
#     if len(new_stock_test) >= n:
#         new_stock_test = new_stock_test.loc[0:n-1]    #取前n个交易日
        
#         max_num = new_stock_test['收盘'].idxmax()
#         ans_max = new_stock_test.loc[max_num]  #最大收盘价的当日信息
#         ans.loc[0,'区间内最大收盘价日期'] = ans_max['日期']
#         ans.loc[0,'最大收盘价'] = ans_max['收盘']
#         new_stock_test = new_stock_test.loc[max_num:n-1]    #取最大收盘价至第n个交易日——最大收盘价后
#         min_num = new_stock_test['收盘'].idxmin()
#         ans_min = new_stock_test.loc[min_num]  #最大收盘价后最小收盘价的当日信息
#         ans.loc[0,'最大收盘价后最小收盘价日期'] = ans_min['日期']
#         ans.loc[0,'最大收盘价后最小收盘价'] = ans_min['收盘']
#         ans.loc[0,'回撤幅度'] = 1 - ans.loc[0,'最大收盘价后最小收盘价']/ans.loc[0,'最大收盘价'] 
#         ans.loc[0,'回撤后上涨幅度'] = ans.loc[0,'现价']/ans.loc[0,'最大收盘价后最小收盘价'] - 1
#         ans.loc[0,'上涨时间'] = max_num
#         ans.loc[0,'回撤时间'] = min_num-max_num
#     else:
#         max_down_side=0
#         for index,row in new_stock_test.iterrows():
#             ans_b = new_stock_test.loc[0:index]   #取某一天之前的所有数据
#             down_side = 1-ans_b.tail(1).reset_index(drop=True).loc[0,'收盘']/ans_b['收盘'].max()
#             max_down_side = max(max_down_side,down_side)
#             if max_down_side==down_side:
#                 ans.loc[0,'区间内最大收盘价日期'] = ans_b.loc[ans_b['收盘'].idxmax(),'日期']
#                 ans.loc[0,'最大收盘价'] = ans_b.loc[ans_b['收盘'].idxmax(),'收盘']
#                 ans.loc[0,'最大收盘价后最小收盘价日期'] = ans_b.tail(1).reset_index(drop=True).loc[0,'日期']
#                 ans.loc[0,'最大收盘价后最小收盘价'] = ans_b.tail(1).reset_index(drop=True).loc[0,'收盘']
#                 ans.loc[0,'回撤幅度'] = down_side
#                 ans.loc[0,'回撤后上涨幅度'] = ans.loc[0,'现价']/ans.loc[0,'最大收盘价后最小收盘价'] - 1
#                 ans.loc[0,'上涨时间'] = ans_b['收盘'].idxmax()
#                 ans.loc[0,'回撤时间'] = ans_b.tail(1).reset_index().loc[0,'index']-ans_b['收盘'].idxmax()
#     return ans


# new_df = pd.DataFrame(columns=(['代码','发行日','区间内最大收盘价日期','最大收盘价后最小收盘价日期','现价日期','上涨时间','回撤时间',
#                                  '发行日收盘','最大收盘价','最大收盘价后最小收盘价','回撤幅度','现价','回撤后上涨幅度']))
# for index,row in new_stock_list.iterrows():
#     print(index,row['代码'])
#     new_df_b = new_stock_analysis(row['代码'],new_stock_data,n)
#     new_df = new_df.append(new_df_b)
# new_df = new_df.reset_index(drop=True)    


# new_df_mean = new_df[['上涨时间','回撤时间','回撤幅度','回撤后上涨幅度']].mean()    #平均值


# new_df_mean.to_excel("新股回撤测试验证{}.xlsx".format(date_work))  
       
##################################################################################################
"单个股票穿透观察"
# stock_id = '105.LCID'

# new_stock_test = new_stock_data[new_stock_data['代码']==stock_id][['日期','收盘','涨跌幅','代码']].reset_index(drop=True)
# ans = pd.DataFrame(columns=(['代码','发行日','区间内最大收盘价日期','最大收盘价后最小收盘价日期','现价日期',
#                              '发行日收盘','最大收盘价','最大收盘价后最小收盘价','回撤幅度','现价','回撤后上涨幅度']))
# ans.loc[0,'代码'] = stock_id
# ans.loc[0,'发行日'] = new_stock_test.loc[0,'日期']
# ans.loc[0,'发行日收盘'] = new_stock_test.loc[0,'收盘']
# ans.loc[0,'现价日期'] = new_stock_test.tail(1).reset_index(drop=True).loc[0,'日期']
# ans.loc[0,'现价'] = new_stock_test.tail(1).reset_index(drop=True).loc[0,'收盘']  


# if len(new_stock_test) >= n:
#     new_stock_test = new_stock_test.loc[0:n-1]    #取前n个交易日
    
#     max_num = new_stock_test['收盘'].idxmax()
#     ans_max = new_stock_test.loc[max_num]  #最大收盘价的当日信息
#     ans.loc[0,'区间内最大收盘价日期'] = ans_max['日期']
#     ans.loc[0,'最大收盘价'] = ans_max['收盘']
#     new_stock_test = new_stock_test.loc[max_num:n-1]    #取最大收盘价至第n个交易日——最大收盘价后
#     min_num = new_stock_test['收盘'].idxmin()
#     ans_min = new_stock_test.loc[min_num]  #最大收盘价后最小收盘价的当日信息
#     ans.loc[0,'最大收盘价后最小收盘价日期'] = ans_min['日期']
#     ans.loc[0,'最大收盘价后最小收盘价'] = ans_min['收盘']
#     ans.loc[0,'回撤幅度'] = 1 - ans.loc[0,'最大收盘价后最小收盘价']/ans.loc[0,'最大收盘价'] 
#     ans.loc[0,'回撤后上涨幅度'] = ans.loc[0,'现价']/ans.loc[0,'最大收盘价后最小收盘价'] - 1
    
# else:
#     max_down_side=0
#     for index,row in new_stock_test.iterrows():
#         ans_b = new_stock_test.loc[0:index]   #取某一天之前的所有数据
#         down_side = 1-ans_b.tail(1).reset_index(drop=True).loc[0,'收盘']/ans_b['收盘'].max()
#         max_down_side = max(max_down_side,down_side)
#         if max_down_side==down_side:
#             ans.loc[0,'区间内最大收盘价日期'] = ans_b.loc[ans_b['收盘'].idxmax(),'日期']
#             ans.loc[0,'最大收盘价'] = ans_b.loc[ans_b['收盘'].idxmax(),'收盘']
#             ans.loc[0,'最大收盘价后最小收盘价日期'] = ans_b.tail(1).reset_index(drop=True).loc[0,'日期']
#             ans.loc[0,'最大收盘价后最小收盘价'] = ans_b.tail(1).reset_index(drop=True).loc[0,'收盘']
#             ans.loc[0,'回撤幅度'] = down_side
#             ans.loc[0,'回撤后上涨幅度'] = ans.loc[0,'现价']/ans.loc[0,'最大收盘价后最小收盘价'] - 1

##################################################################################################



















