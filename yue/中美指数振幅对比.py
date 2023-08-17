# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 10:26:13 2022

@author: Administrator
"""

"中美指数振幅对比"


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

sz_index = ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20161230", end_date="22220101").rename(columns={'振幅':'上证'})[['日期','上证']]
hs300_index = ak.index_zh_a_hist(symbol="000300", period="daily", start_date="20161230", end_date="22220101").rename(columns={'振幅':'沪深300'})[['日期','沪深300']]
cyb_index = ak.index_zh_a_hist(symbol="399006", period="daily", start_date="20161230", end_date="22220101").rename(columns={'振幅':'创业板'})[['日期','创业板']]





"美股指数"
naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="20161229", end_date="22220101")

sp500_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="20161229", end_date="22220101")

dj_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
                                      period="每日", start_date="20161229", end_date="22220101")



naq_index['日期'] = naq_index['日期'].astype('str')
sp500_index['日期'] = sp500_index['日期'].astype('str')
dj_index['日期'] = dj_index['日期'].astype('str')


naq_index['纳指'] = 100*((naq_index['高'] - naq_index['低'])/naq_index['收盘'].shift(1))
sp500_index['标普'] = 100*((sp500_index['高'] - sp500_index['低'])/sp500_index['收盘'].shift(1))
dj_index['道琼斯'] = 100*((dj_index['高'] - dj_index['低'])/dj_index['收盘'].shift(1))


naq_index = naq_index[['日期','纳指']]
sp500_index = sp500_index[['日期','标普']]
dj_index = dj_index[['日期','道琼斯']]


"分段对比"

sz_dj = pd.merge(sz_index,dj_index,on='日期',how='left')
sz_dj['道琼斯'] = sz_dj['道琼斯'].shift(1)

hs300_sp500 = pd.merge(hs300_index,sp500_index,on='日期',how='left')
hs300_sp500['标普'] = hs300_sp500['标普'].shift(1)

cyb_naq = pd.merge(cyb_index,naq_index,on='日期',how='left')
cyb_naq['纳指'] = cyb_naq['纳指'].shift(1)


sz_dj = sz_dj.dropna(axis=0,how='any')
hs300_sp500 = hs300_sp500.dropna(axis=0,how='any')
cyb_naq = cyb_naq.dropna(axis=0,how='any')

"统计"




def swing_st(datas,char_us,char_cn,nummin,nummax,std_num):
    data = datas[(datas['{}'.format(char_us)]>=nummin)&(datas['{}'.format(char_us)]<nummax)]
    
    
    data_st = pd.DataFrame()
    data_st.loc[0,'{}_振幅范围(设定)'.format(char_us)] = '[{},{})'.format(nummin,nummax)
    
    data_st.loc[0,'{}_振幅范围'.format(char_cn)] = '[{},{}]'.format(data['{}'.format(char_cn)].min(),data['{}'.format(char_cn)].max())
    
    
    if len(data)==0:
        data_st.loc[0,'{}_振幅数据量'.format(char_cn)] = len(data)
        data_st.loc[0,'{}_振幅平均'.format(char_cn)] = data['{}'.format(char_cn)].mean()
        data_st.loc[0,'{}_振幅中位数'.format(char_cn)] = data['{}'.format(char_cn)].median() 
        data_st.loc[0,'{}_振幅±{}σ范围'.format(char_cn,std_num)] = '[{},{}]'.format(round(data['{}'.format(char_cn)].mean()-std_num*data['{}'.format(char_cn)].std(),3)
                                                                       ,round(data['{}'.format(char_cn)].mean()+std_num*data['{}'.format(char_cn)].std(),3))
        data_st.loc[0,'{}_振幅±{}σ有效范围'.format(char_cn,std_num)] = '[{},{}]'.format(max(round(data['{}'.format(char_cn)].mean()-std_num*data['{}'.format(char_cn)].std(),3),data['{}'.format(char_cn)].min())
                                                                       ,min(round(data['{}'.format(char_cn)].mean()+std_num*data['{}'.format(char_cn)].std(),3),data['{}'.format(char_cn)].max()))
        
        data_st.loc[0,'{}_振幅±{}σ有效范围数据出现概率'.format(char_cn,std_num)] = np.nan
    else:
    
        data_st.loc[0,'{}_振幅数据量'.format(char_cn)] = len(data)
        data_st.loc[0,'{}_振幅平均'.format(char_cn)] = data['{}'.format(char_cn)].mean()
        data_st.loc[0,'{}_振幅中位数'.format(char_cn)] = data['{}'.format(char_cn)].median() 
        data_st.loc[0,'{}_振幅±{}σ范围'.format(char_cn,std_num)] = '[{},{}]'.format(round(data['{}'.format(char_cn)].mean()-std_num*data['{}'.format(char_cn)].std(),3)
                                                                       ,round(data['{}'.format(char_cn)].mean()+std_num*data['{}'.format(char_cn)].std(),3))

        data_st.loc[0,'{}_振幅±{}σ有效范围'.format(char_cn,std_num)] = '[{},{}]'.format(max(round(data['{}'.format(char_cn)].mean()-std_num*data['{}'.format(char_cn)].std(),3),data['{}'.format(char_cn)].min())
                                                                       ,min(round(data['{}'.format(char_cn)].mean()+std_num*data['{}'.format(char_cn)].std(),3),data['{}'.format(char_cn)].max()))
        data_st.loc[0,'{}_振幅±{}σ有效范围数据出现概率'.format(char_cn,std_num)] = len(data[(data['{}'.format(char_cn)]>=round(data['{}'.format(char_cn)].mean()-std_num*data['{}'.format(char_cn)].std(),3))
                                                                 &(data['{}'.format(char_cn)]<=round(data['{}'.format(char_cn)].mean()+std_num*data['{}'.format(char_cn)].std(),3))])/len(data)

    return data_st




sz_dj_st = pd.DataFrame()
hs300_sp500_st = pd.DataFrame()
cyb_naq_st = pd.DataFrame()

for i in range(0,32):
    print(round(i*0.3,1),round((i+1)*0.3,1))
    sz_dj_stb = swing_st(sz_dj,'道琼斯','上证',round(i*0.3,1),round((i+1)*0.3,1),1)
    hs300_sp500_stb = swing_st(hs300_sp500,'标普','沪深300',round(i*0.3,1),round((i+1)*0.3,1),1)
    cyb_naq_stb = swing_st(cyb_naq,'纳指','创业板',round(i*0.3,1),round((i+1)*0.3,1),1)
    
    sz_dj_st = sz_dj_st.append(sz_dj_stb)
    hs300_sp500_st = hs300_sp500_st.append(hs300_sp500_stb)
    cyb_naq_st = cyb_naq_st.append(cyb_naq_stb)


sz_dj_st.to_excel('振幅_上证道琼斯{}.xlsx'.format(date_work))
hs300_sp500_st.to_excel('振幅_沪深标普{}.xlsx'.format(date_work))
cyb_naq_st.to_excel('振幅_创业板纳指{}.xlsx'.format(date_work))



































