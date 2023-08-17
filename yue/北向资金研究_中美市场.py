# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 11:23:28 2022

@author: Administrator
"""

'''
北向资金研究


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




#####################################################################################################################################

"数据准备-----日频"


"北向资金——当日成交净买额"
hgt = ak.stock_hsgt_hist_em(symbol="沪股通").sort_values(by='日期',ascending=0)[['日期','当日成交净买额']].rename(columns={'当日成交净买额':'沪股通'})
hgt = hgt.rename(columns={'沪股通':'沪股通(亿)'})
hgt['日期'] = hgt['日期'].astype(str)

sgt = ak.stock_hsgt_hist_em(symbol="深股通").sort_values(by='日期',ascending=0)[['日期','当日成交净买额']].rename(columns={'当日成交净买额':'深股通'})
sgt = sgt.rename(columns={'深股通':'深股通(亿)'})
sgt['日期'] = sgt['日期'].astype(str)

north_bound = pd.merge(left=hgt,right=sgt,how='outer',on='日期')
north_bound['当日成交净买额(亿)'] = north_bound['沪股通(亿)'] + north_bound['深股通(亿)']
north_bound = north_bound[['日期','当日成交净买额(亿)']]

"中国指数"

sz_index = ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20170101", end_date="22220101").rename(columns={'涨跌幅':'上证'})[['日期','上证']]
shz_index = ak.index_zh_a_hist(symbol="399001", period="daily", start_date="20170101", end_date="22220101").rename(columns={'涨跌幅':'深证'})[['日期','深证']]
hs300_index = ak.index_zh_a_hist(symbol="000300", period="daily", start_date="20170101", end_date="22220101").rename(columns={'涨跌幅':'沪深300'})[['日期','沪深300']]
cyb_index = ak.index_zh_a_hist(symbol="399006", period="daily", start_date="20170101", end_date="22220101").rename(columns={'涨跌幅':'创业板'})[['日期','创业板']]




"美股指数-----全局模式"
naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="20161230", end_date="22220101")

sp500_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="20161230", end_date="22220101")

dj_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
                                      period="每日", start_date="20161230", end_date="22220101")

# dj_index = ak.stock_us_hist(symbol='107.FNGU', start_date="20161230", end_date="22220101")

naq_index['日期'] = naq_index['日期'].astype('str')
sp500_index['日期'] = sp500_index['日期'].astype('str')
dj_index['日期'] = dj_index['日期'].astype('str')



# naq_index['纳指'] = 100*(naq_index['收盘']/naq_index['收盘'].shift(1) - 1)
# sp500_index['标普'] = 100*(sp500_index['收盘']/sp500_index['收盘'].shift(1) - 1)
# dj_index['道琼斯'] = 100*(dj_index['收盘']/dj_index['收盘'].shift(1) - 1)



"每日涨跌幅=当日收盘价/当日开盘价 - 1"
naq_index['纳指'] = 100*(naq_index['收盘']/naq_index['开盘'] - 1)
sp500_index['标普'] = 100*(sp500_index['收盘']/sp500_index['开盘'] - 1)
dj_index['道琼斯'] = 100*(dj_index['收盘']/dj_index['开盘'] - 1)




naq_index = naq_index[['日期','纳指']]
sp500_index = sp500_index[['日期','标普']]
dj_index = dj_index[['日期','道琼斯']]

########################################################################################################################################################
"北向—————国内指数 日频"
"数据聚合"

merge_north_cnind_b =  [north_bound,sz_index,shz_index,hs300_index,cyb_index]
merge_north_cnind = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),merge_north_cnind_b)
merge_north_cnind = merge_north_cnind.dropna(axis=0,how='any')
"北向资金与前一日国内指数————研究"
merge_north_cnind.iloc[:,2:] = merge_north_cnind.iloc[:,2:].shift(1)
merge_north_cnind = merge_north_cnind.dropna(axis=0,how='any')

def north_cnind_d(merge_north_cnind,nummin,nummax):
    datas = merge_north_cnind[(merge_north_cnind['当日成交净买额(亿)']>=nummin)&(merge_north_cnind['当日成交净买额(亿)']<=nummax)]
    data = pd.DataFrame(datas.agg('mean')).T
    data['北向资金筛选下限'] = nummin
    data['北向资金筛选上限'] = nummax
    data['区间宽度'] = nummax-nummin
    data['上下限数量'] = len(datas)
    data['上下限数量出现概率'] = len(datas)/len(merge_north_cnind)
  
    return data


"220和240依赖于merge_north_cnind中当日成交净买额(亿)的上下限"
data_north_cnind = pd.DataFrame()
for nummin in range(-180,220,20):
    for nummax in range(nummin+20,240,20):
        data_b = north_cnind_d(merge_north_cnind,nummin,nummax)
        data_north_cnind = data_north_cnind.append(data_b)

data_north_cnind.to_excel('北向--国内指数{}.xlsx'.format(date_work))



"将下方输出为df"
odds_df = pd.DataFrame(columns=(['指数','胜率(>20)','胜率(<20)']))
for i in range(4):
    odds_df.loc[i,'指数'] = data_north_cnind.columns[i+1]
    odds_df.loc[i,'胜率(>20)'] = len(merge_north_cnind[(merge_north_cnind['当日成交净买额(亿)']>=20)&
                                             (merge_north_cnind['{}'.format(data_north_cnind.columns[i+1])]>=0)])/len(merge_north_cnind[merge_north_cnind['当日成交净买额(亿)']>=20])
    odds_df.loc[i,'胜率(<20)'] = len(merge_north_cnind[(merge_north_cnind['当日成交净买额(亿)']<20)&
                                             (merge_north_cnind['{}'.format(data_north_cnind.columns[i+1])]<0)])/len(merge_north_cnind[merge_north_cnind['当日成交净买额(亿)']<20])

    
    
odds_df.to_excel('北向--国内胜率{}.xlsx'.format(date_work))


######################################





def north_cnind_d(merge_north_cnind,num,bs):
    if bs=='大于等于':
        datas = merge_north_cnind[merge_north_cnind['当日成交净买额(亿)']>=num]
    elif bs=='小于等于':
        datas = merge_north_cnind[merge_north_cnind['当日成交净买额(亿)']<=num]
               
    data = pd.DataFrame(datas.agg('mean')).T
    data['北向资金筛选标识'] = "{}{}".format(bs,num)
    data['数量'] = len(datas)
    data['出现概率'] = len(datas)/len(merge_north_cnind)
    
    if bs=='大于等于':
        data['上证胜率'] = len(datas[datas['上证']>0])/len(datas)
        data['深证胜率'] = len(datas[datas['深证']>0])/len(datas)
        data['沪深300胜率'] = len(datas[datas['沪深300']>0])/len(datas)
        data['创业板胜率'] = len(datas[datas['创业板']>0])/len(datas)
    elif bs=='小于等于':
        data['上证胜率'] = len(datas[datas['上证']<0])/len(datas)
        data['深证胜率'] = len(datas[datas['深证']<0])/len(datas)
        data['沪深300胜率'] = len(datas[datas['沪深300']<0])/len(datas)
        data['创业板胜率'] = len(datas[datas['创业板']<0])/len(datas)
        
 
    return data



"当月成交净买额   设定>=   or  <=的 范围进行统计"
data_north_cnind = pd.DataFrame()

for num in range(-180,210,10):
    data_b = north_cnind_d(merge_north_cnind,num,'大于等于')
    data_north_cnind = data_north_cnind.append(data_b)
    

for num in range(-170,220,10):
    data_b = north_cnind_d(merge_north_cnind,num,'小于等于')
    data_north_cnind = data_north_cnind.append(data_b)





"策略测试----最近30个工作日"
north_cnind_test = merge_north_cnind.head(600).copy()
north_cnind_test['上证test'] = 0
north_cnind_test['深证test'] = 0
north_cnind_test['沪深300test'] = 0
north_cnind_test['创业板test'] = 0
for index,row in north_cnind_test.iterrows():

    if row['当日成交净买额(亿)']>=20:
        north_cnind_test.loc[index,'上证test'] = row['上证']
        north_cnind_test.loc[index,'深证test'] = row['深证']
        north_cnind_test.loc[index,'沪深300test'] = row['沪深300']
        north_cnind_test.loc[index,'创业板test'] = row['创业板']
    elif row['当日成交净买额(亿)']<20:
        north_cnind_test.loc[index,'上证test'] = -row['上证']
        north_cnind_test.loc[index,'深证test'] = -row['深证']
        north_cnind_test.loc[index,'沪深300test'] =- row['沪深300']
        north_cnind_test.loc[index,'创业板test'] = -row['创业板']
    else:
        pass

north_cnind_test_sum = pd.DataFrame(north_cnind_test.iloc[:,1:].sum()).T


   
########################################################################################################################################################
"北向—————美股指数 日频"
"数据聚合"

merge_north_usind_b =  [north_bound,naq_index,sp500_index,dj_index]
merge_north_usind = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),merge_north_usind_b)
merge_north_usind = merge_north_usind.dropna(axis=0,how='any')


def north_usind_d(merge_north_usind,nummin,nummax):
    datas = merge_north_usind[(merge_north_usind['当日成交净买额(亿)']>=nummin)&(merge_north_usind['当日成交净买额(亿)']<=nummax)]
    data = pd.DataFrame(datas.agg('mean')).T
    data['北向资金筛选下限'] = nummin
    data['北向资金筛选上限'] = nummax
    data['区间宽度'] = nummax-nummin
    data['上下限数量'] = len(datas)
    data['上下限数量出现概率'] = len(datas)/len(merge_north_usind)
  
    return data

"220和240依赖于merge_north_usind中当日成交净买额(亿)的上下限"
data_north_usind = pd.DataFrame()
for nummin in range(-180,220,20):
    for nummax in range(nummin+20,240,20):
        data_b = north_usind_d(merge_north_usind,nummin,nummax)
        data_north_usind = data_north_usind.append(data_b)

data_north_usind.to_excel('北向--美股指数{}.xlsx'.format(date_work))



"将下方输出为df"
odds_df = pd.DataFrame(columns=(['指数','胜率(>20)','胜率(<0)']))
for i in range(3):
    odds_df.loc[i,'指数'] = data_north_usind.columns[i+1]
    odds_df.loc[i,'胜率(>20)'] = len(merge_north_usind[(merge_north_usind['当日成交净买额(亿)']>=20)&
                                             (merge_north_usind['{}'.format(data_north_usind.columns[i+1])]>=0)])/len(merge_north_usind[merge_north_usind['当日成交净买额(亿)']>=20])
    odds_df.loc[i,'胜率(<0)'] = len(merge_north_usind[(merge_north_usind['当日成交净买额(亿)']<-20)&
                                             (merge_north_usind['{}'.format(data_north_usind.columns[i+1])]<0)])/len(merge_north_usind[merge_north_usind['当日成交净买额(亿)']<-20])

    
odds_df.to_excel('北向--美股胜率{}.xlsx'.format(date_work))
     

"策略测试----最近30个工作日"
north_usind_test = merge_north_usind.head(600)
north_usind_test['纳指test'] = 0
north_usind_test['标普test'] = 0
north_usind_test['道琼斯test'] = 0
for index,row in north_usind_test.iterrows():

    if row['当日成交净买额(亿)']>=-20:
        north_usind_test.loc[index,'纳指test'] = row['纳指']
        north_usind_test.loc[index,'标普test'] = row['标普']
        north_usind_test.loc[index,'道琼斯test'] = row['道琼斯']
    elif row['当日成交净买额(亿)']<-40:
        north_usind_test.loc[index,'纳指test'] = -row['纳指']
        north_usind_test.loc[index,'标普test'] = -row['标普']
        north_usind_test.loc[index,'道琼斯test'] = -row['道琼斯']
    else:
        pass

north_usind_test_sum = pd.DataFrame(north_usind_test.iloc[:,1:].sum()).T





"批量测试"

def test_north_usind(days,max_limit,min_limit):
    
    "策略测试----最近days个工作日"
    north_usind_test = merge_north_usind.head(days).copy()
    north_usind_test['纳指test'] = 0
    north_usind_test['标普test'] = 0
    north_usind_test['道琼斯test'] = 0
    
    for index,row in north_usind_test.iterrows():
    
        if row['当日成交净买额(亿)']>=max_limit:
            north_usind_test.loc[index,'纳指test'] = row['纳指']
            north_usind_test.loc[index,'标普test'] = row['标普']
            north_usind_test.loc[index,'道琼斯test'] = row['道琼斯']
        elif row['当日成交净买额(亿)']<min_limit:
            north_usind_test.loc[index,'纳指test'] = -row['纳指']
            north_usind_test.loc[index,'标普test'] = -row['标普']
            north_usind_test.loc[index,'道琼斯test'] = -row['道琼斯']
        else:
            pass
    
    
    north_usind_test_sum = pd.DataFrame(north_usind_test.iloc[:,1:].sum()).T
    
    north_usind_test_sum['纳指alpha'] = north_usind_test_sum['纳指test']-north_usind_test_sum['纳指']
    north_usind_test_sum['标普alpha'] = north_usind_test_sum['标普test']-north_usind_test_sum['标普']
    north_usind_test_sum['道琼斯alpha'] = north_usind_test_sum['道琼斯test']-north_usind_test_sum['道琼斯']
    
    
    north_usind_test_sum['days'] = days
    north_usind_test_sum['max_limit'] = max_limit
    north_usind_test_sum['min_limit'] = min_limit
    
    north_usind_test_sum['操作频率'] = len(north_usind_test[(north_usind_test['当日成交净买额(亿)']>=max_limit)|(north_usind_test['当日成交净买额(亿)']<min_limit)])/days

    return north_usind_test_sum



tail_days_list = [5,10,20,60,120,250,600]
for tail_days in tail_days_list:
    # tail_days = 250
    north_usind_test_sum = pd.DataFrame()
    for nummin in range(-180,220,20):
        for nummax in range(nummin+20,240,20):
            north_usind_test_sum_b = test_north_usind(tail_days,nummax,nummin)
            north_usind_test_sum = north_usind_test_sum.append(north_usind_test_sum_b)
    
    
      
    north_usind_test_sum.to_excel('当日北向--美股_{}test_{}.xlsx'.format(tail_days,date_work))


########################################################################################################################################################


"数据准备-----月频   由于跨度较长，所以使用两边的收盘价计算区间内的涨跌幅，代替每日计算出的日涨幅"

"中国指数"

sz_index = ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20170101", end_date="22220101").rename(columns={'收盘':'上证','开盘':'上证开'})[['日期','上证','上证开']]
shz_index = ak.index_zh_a_hist(symbol="399001", period="daily", start_date="20170101", end_date="22220101").rename(columns={'收盘':'深证','开盘':'深证开'})[['日期','深证','深证开']]
hs300_index = ak.index_zh_a_hist(symbol="000300", period="daily", start_date="20170101", end_date="22220101").rename(columns={'收盘':'沪深300','开盘':'沪深300开'})[['日期','沪深300','沪深300开']]
cyb_index = ak.index_zh_a_hist(symbol="399006", period="daily", start_date="20170101", end_date="22220101").rename(columns={'收盘':'创业板','开盘':'创业板开'})[['日期','创业板','创业板开']]




"美股指数-----全局模式"
naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="20161230", end_date="22220101").rename(columns={'收盘':'纳指','开盘':'纳指开'})[['日期','纳指','纳指开']]

sp500_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="20161230", end_date="22220101").rename(columns={'收盘':'标普','开盘':'标普开'})[['日期','标普','标普开']]

dj_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
                                      period="每日", start_date="20161230", end_date="22220101").rename(columns={'收盘':'道琼斯','开盘':'道琼斯开'})[['日期','道琼斯','道琼斯开']]


naq_index['日期'] = naq_index['日期'].astype('str')
sp500_index['日期'] = sp500_index['日期'].astype('str')
dj_index['日期'] = dj_index['日期'].astype('str')





########################################################################################################################################################


"北向—————国内指数 月频"
"数据聚合"

merge_north_cnind_b =  [north_bound,sz_index,shz_index,hs300_index,cyb_index]
merge_north_cnind = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),merge_north_cnind_b)
merge_north_cnind = merge_north_cnind.dropna(axis=0,how='any')
"当月北向资金总和  下一月国内指数涨幅"
merge_north_cnind_mb = merge_north_cnind.copy()
merge_north_cnind_mb['月份'] = merge_north_cnind_mb['日期'].astype('str').str.slice(0,7)


merge_north_cnind_m = merge_north_cnind_mb.groupby('月份').agg('sum').reset_index().sort_values('月份',ascending=0).reset_index(drop=True)
merge_north_cnind_m = merge_north_cnind_m.rename(columns={'当日成交净买额(亿)':'当月成交净买额(亿)'})


merge_north_cnind_mb_head = merge_north_cnind_mb.groupby('月份').head(1).reset_index(drop=True)
merge_north_cnind_mb_tail = merge_north_cnind_mb.groupby('月份').tail(1).reset_index(drop=True)


merge_north_cnind_m['上证'] = 100*( merge_north_cnind_mb_head['上证'] / merge_north_cnind_mb_tail['上证开']  -1).shift(1)
merge_north_cnind_m['深证'] = 100*(merge_north_cnind_mb_head['深证'] / merge_north_cnind_mb_tail['深证开']  -1).shift(1)
merge_north_cnind_m['沪深300'] = 100*(merge_north_cnind_mb_head['沪深300'] / merge_north_cnind_mb_tail['沪深300开']  -1).shift(1)
merge_north_cnind_m['创业板'] = 100*( merge_north_cnind_mb_head['创业板'] / merge_north_cnind_mb_tail['创业板开']  -1).shift(1)

merge_north_cnind_m = merge_north_cnind_m[['月份','当月成交净买额(亿)','上证','深证','沪深300','创业板']].dropna(axis=0,how='any')


# merge_north_cnind_m.to_excel('merge_north_cnind_m_月{}.xlsx'.format(date_work))


def north_cnind_m(merge_north_cnind_m,num,bs):
    if bs=='大于等于':
        datas = merge_north_cnind_m[merge_north_cnind_m['当月成交净买额(亿)']>=num]
    elif bs=='小于等于':
        datas = merge_north_cnind_m[merge_north_cnind_m['当月成交净买额(亿)']<=num]
               
    data = pd.DataFrame(datas.agg('mean')).T
    data['北向资金筛选标识'] = "{}{}".format(bs,num)
    data['数量'] = len(datas)
    data['出现概率'] = len(datas)/len(merge_north_cnind_m)
    
    if bs=='大于等于':
        data['上证胜率'] = len(datas[datas['上证']>0])/len(datas)
        data['深证胜率'] = len(datas[datas['深证']>0])/len(datas)
        data['沪深300胜率'] = len(datas[datas['沪深300']>0])/len(datas)
        data['创业板胜率'] = len(datas[datas['创业板']>0])/len(datas)
    elif bs=='小于等于':
        data['上证胜率'] = len(datas[datas['上证']<0])/len(datas)
        data['深证胜率'] = len(datas[datas['深证']<0])/len(datas)
        data['沪深300胜率'] = len(datas[datas['沪深300']<0])/len(datas)
        data['创业板胜率'] = len(datas[datas['创业板']<0])/len(datas)
        
 
    return data

"当月成交净买额   设定>=   or  <=的 范围进行统计"
data_north_cnind_m = pd.DataFrame()

for num in range(-700,900,50):
    data_b = north_cnind_m(merge_north_cnind_m,num,'大于等于')
    data_north_cnind_m = data_north_cnind_m.append(data_b)
    

for num in range(-650,900,50):
    data_b = north_cnind_m(merge_north_cnind_m,num,'小于等于')
    data_north_cnind_m = data_north_cnind_m.append(data_b)
  

data_north_cnind_m.to_excel('北向--国内指数_月{}.xlsx'.format(date_work))

##########################################
# "将下方输出为df"
# odds_df = pd.DataFrame(columns=(['指数','胜率(>300)','胜率(<150)']))
# for i in range(4):
#     odds_df.loc[i,'指数'] = data_north_cnind_m.columns[i+1]
#     odds_df.loc[i,'胜率(>300)'] = len(merge_north_cnind_m[(merge_north_cnind_m['当月成交净买额(亿)']>=300)&
#                                               (merge_north_cnind_m['{}'.format(merge_north_cnind_m.columns[i+2])]>=0)])/len(merge_north_cnind_m[merge_north_cnind_m['当月成交净买额(亿)']>=300])
#     odds_df.loc[i,'胜率(<150)'] = len(merge_north_cnind_m[(merge_north_cnind_m['当月成交净买额(亿)']<150)&
#                                               (merge_north_cnind_m['{}'.format(merge_north_cnind_m.columns[i+2])]<0)])/len(merge_north_cnind_m[merge_north_cnind_m['当月成交净买额(亿)']<150])
 

    
# odds_df.to_excel('北向--国内胜率{}.xlsx'.format(date_work))
##########################################


"策略测试----最近12个月"
north_cnind_m_test = merge_north_cnind_m.head(12).copy()
north_cnind_m_test['上证test'] = 0
north_cnind_m_test['深证test'] = 0
north_cnind_m_test['沪深300test'] = 0
north_cnind_m_test['创业板test'] = 0
for index,row in north_cnind_m_test.iterrows():

    if row['当月成交净买额(亿)']>=350:
        north_cnind_m_test.loc[index,'上证test'] = row['上证']
        north_cnind_m_test.loc[index,'深证test'] = row['深证']
        north_cnind_m_test.loc[index,'沪深300test'] = row['沪深300']
        north_cnind_m_test.loc[index,'创业板test'] = row['创业板']
    elif row['当月成交净买额(亿)']<=150:
        north_cnind_m_test.loc[index,'上证test'] = -row['上证']
        north_cnind_m_test.loc[index,'深证test'] = -row['深证']
        north_cnind_m_test.loc[index,'沪深300test'] = -row['沪深300']
        north_cnind_m_test.loc[index,'创业板test'] = -row['创业板']
    else:
        pass

north_cnind_m_test_sum = pd.DataFrame(north_cnind_m_test.iloc[:,1:].sum()).T






########################################################################################################################################################


"北向—————国外指数 月频"
"数据聚合"

merge_north_usind_b =  [north_bound,naq_index,sp500_index,dj_index]
merge_north_usind = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),merge_north_usind_b)
merge_north_usind = merge_north_usind.dropna(axis=0,how='any')
"当月北向资金总和  下一月国内指数涨幅"
merge_north_usind_mb = merge_north_usind.copy()
merge_north_usind_mb['月份'] = merge_north_usind_mb['日期'].astype('str').str.slice(0,7)


merge_north_usind_m = merge_north_usind_mb.groupby('月份').agg('sum').reset_index().sort_values('月份',ascending=0).reset_index(drop=True)
merge_north_usind_m = merge_north_usind_m.rename(columns={'当日成交净买额(亿)':'当月成交净买额(亿)'})


merge_north_usind_mb_head = merge_north_usind_mb.groupby('月份').head(1).reset_index(drop=True)
merge_north_usind_mb_tail = merge_north_usind_mb.groupby('月份').tail(1).reset_index(drop=True)


merge_north_usind_m['纳指'] = 100*( merge_north_usind_mb_head['纳指'] / merge_north_usind_mb_tail['纳指开']  -1).shift(1)
merge_north_usind_m['标普'] = 100*(merge_north_usind_mb_head['标普'] / merge_north_usind_mb_tail['标普开']  -1).shift(1)
merge_north_usind_m['道琼斯'] = 100*(merge_north_usind_mb_head['道琼斯'] / merge_north_usind_mb_tail['道琼斯开']  -1).shift(1)

merge_north_usind_m = merge_north_usind_m[['月份','当月成交净买额(亿)','纳指','标普','道琼斯']].dropna(axis=0,how='any')


# merge_north_usind_m.to_excel('merge_north_usind_m_月{}.xlsx'.format(date_work))


def north_usind_m(merge_north_usind_m,num,bs):
    if bs=='大于等于':
        datas = merge_north_usind_m[merge_north_usind_m['当月成交净买额(亿)']>=num]
    elif bs=='小于等于':
        datas = merge_north_usind_m[merge_north_usind_m['当月成交净买额(亿)']<=num]
               
    data = pd.DataFrame(datas.agg('mean')).T
    data['北向资金筛选标识'] = "{}{}".format(bs,num)
    data['数量'] = len(datas)
    data['出现概率'] = len(datas)/len(merge_north_usind_m)
    
    if bs=='大于等于':
        data['纳指胜率'] = len(datas[datas['纳指']>0])/len(datas)
        data['标普胜率'] = len(datas[datas['标普']>0])/len(datas)
        data['道琼斯胜率'] = len(datas[datas['道琼斯']>0])/len(datas)
    elif bs=='小于等于':
        data['纳指胜率'] = len(datas[datas['纳指']<0])/len(datas)
        data['标普胜率'] = len(datas[datas['标普']<0])/len(datas)
        data['道琼斯胜率'] = len(datas[datas['道琼斯']<0])/len(datas)
        
 
    return data

"当月成交净买额   设定>=   or  <=的 范围进行统计"
data_north_usind_m = pd.DataFrame()

for num in range(-700,900,50):
    data_b = north_usind_m(merge_north_usind_m,num,'大于等于')
    data_north_usind_m = data_north_usind_m.append(data_b)
    

for num in range(-650,950,50):
    data_b = north_usind_m(merge_north_usind_m,num,'小于等于')
    data_north_usind_m = data_north_usind_m.append(data_b)
  

data_north_usind_m.to_excel('北向--国外指数_月{}.xlsx'.format(date_work))

##########################################
# "将下方输出为df"
# odds_df = pd.DataFrame(columns=(['指数','胜率(>300)','胜率(<150)']))
# for i in range(4):
#     odds_df.loc[i,'指数'] = data_north_usind_m.columns[i+1]
#     odds_df.loc[i,'胜率(>300)'] = len(merge_north_usind_m[(merge_north_usind_m['当月成交净买额(亿)']>=300)&
#                                               (merge_north_usind_m['{}'.format(merge_north_usind_m.columns[i+2])]>=0)])/len(merge_north_usind_m[merge_north_usind_m['当月成交净买额(亿)']>=300])
#     odds_df.loc[i,'胜率(<150)'] = len(merge_north_usind_m[(merge_north_usind_m['当月成交净买额(亿)']<150)&
#                                               (merge_north_usind_m['{}'.format(merge_north_usind_m.columns[i+2])]<0)])/len(merge_north_usind_m[merge_north_usind_m['当月成交净买额(亿)']<150])
 

    
# odds_df.to_excel('北向--国内胜率{}.xlsx'.format(date_work))
##########################################


"策略测试----最近12个月"
north_usind_m_test = merge_north_usind_m.head(12).copy()
north_usind_m_test['纳指test'] = 0
north_usind_m_test['标普test'] = 0
north_usind_m_test['道琼斯test'] = 0
for index,row in north_usind_m_test.iterrows():

    if row['当月成交净买额(亿)']>=350:
        north_usind_m_test.loc[index,'纳指test'] = row['纳指']
        north_usind_m_test.loc[index,'标普test'] = row['标普']
        north_usind_m_test.loc[index,'道琼斯test'] = row['道琼斯']
    elif row['当月成交净买额(亿)']<=150:
        north_usind_m_test.loc[index,'纳指test'] = -row['纳指']
        north_usind_m_test.loc[index,'标普test'] = -row['标普']
        north_usind_m_test.loc[index,'道琼斯test'] = -row['道琼斯']
    else:
        pass

north_usind_m_test_sum = pd.DataFrame(north_usind_m_test.iloc[:,1:].sum()).T











































