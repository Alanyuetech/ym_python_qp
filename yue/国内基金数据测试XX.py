# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 14:57:21 2021

@author: Administrator
"""


"国内基金数据  测试"
import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
now_day = datetime.datetime.now().strftime('%Y%m%d')
"基金列表"
fund_id = pd.read_excel('临时AVE_测试0813.xlsx',dtype={'id':'str'})
"基金代码前面补0"
fund_id['id'] = fund_id['id'].map(lambda x:'00000'+x if len(x)==1 else
                                  ('0000'+x if len(x)==2 else 
                                   ('000'+x if len(x)==3 else
                                    ('00'+x if len(x)==4 else
                                     ('0'+x if len(x)==5 else x)))))


fund_data_hz = pd.DataFrame()
"拿出每个基金的历史 累计净值走势"
for index,row  in fund_id.iterrows():
    # "单个基金历史 累计净值走势"
    # tt = '001643'  #样例
    # fund_data = ak.fund_em_open_fund_info(fund=tt, indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    fund_data = ak.fund_em_open_fund_info(fund=row['id'], indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    "防止float和双精度格式冲突"
    fund_data['累计净值'] = fund_data['累计净值'].astype(float)
    "净值日期 转变为 int "
    fund_data['净值日期'] = fund_data['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
    "计算  日增长率"
    fund_data['前一日累计净值'] = fund_data['累计净值'].shift(-1)
    fund_data['日增长率'] = fund_data['累计净值']/fund_data['前一日累计净值'] - 1
    "拿数据从  20180101  开始"
    fund_data = fund_data[fund_data['净值日期']>=20180101].sort_values(by='净值日期',ascending=False).reset_index(drop=True)
    
    
    "过去60个交易日  日增长率 求和"
    fund_data['p60日增长率和'] = np.nan
    sum_data=list()
    fund_data['日增长率'] = fund_data['日增长率'].astype(float)
    for i in range(len(fund_data)-60):
        fund_data.loc[i,'p60日增长率和'] = sum(fund_data.loc[i:60+i,'日增长率'])
    
    "过去一年p60  日增长率求和  的平均值"
    fund_data['p1yp60日增长率和ave'] = 0
    for index_1,row_i in fund_data.iterrows():
        fund_data.loc[index_1,'p1yp60日增长率和ave'] = fund_data[(fund_data['净值日期']>row_i['净值日期']-10000)&(fund_data['净值日期']<=row_i['净值日期'])]['p60日增长率和'].mean()
    
    "计算未来D30  D90  涨跌幅"    
    fund_data['f30累计净值'] = fund_data['累计净值'].shift(30)
    fund_data['f90累计净值'] = fund_data['累计净值'].shift(90)
    fund_data['D30'] = (fund_data['f30累计净值']-fund_data['累计净值'])/fund_data['累计净值']
    fund_data['D90'] = (fund_data['f90累计净值']-fund_data['累计净值'])/fund_data['累计净值']
    
    "只取如下时间段的数据"
    fund_data = fund_data[(fund_data['净值日期']==20190630)|(fund_data['净值日期']==20190830)|
                          (fund_data['净值日期']==20191030)|(fund_data['净值日期']==20191230)|
                          (fund_data['净值日期']==20200228)|(fund_data['净值日期']==20200430)|
                          (fund_data['净值日期']==20200630)|(fund_data['净值日期']==20200831)|
                          (fund_data['净值日期']==20201030)|(fund_data['净值日期']==20201230)|
                          (fund_data['净值日期']==20210226)|(fund_data['净值日期']==20210430)|
                          (fund_data['净值日期']==20210630)]

    fund_data['id'] = row['id']
    fund_data_hz = fund_data_hz.append(fund_data)
    print(index,row['id'])
    
fund_data_hz.to_excel('国内基金数据测试XX{}.xlsx'.format(now_day))    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    