# -*- coding: utf-8 -*-
"""
Created on Mon Aug 16 14:12:01 2021

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
fund_id = pd.read_excel('岳岳数据.xlsx',dtype={'id':'str'})
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
    # tt = '090018'  #样例
    # fund_data = ak.fund_em_open_fund_info(fund=tt, indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    fund_data = ak.fund_em_open_fund_info(fund=row['id'], indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    "防止float和双精度格式冲突"
    fund_data['累计净值'] = fund_data['累计净值'].astype(float)
    "净值日期 转变为 int "
    fund_data['净值日期'] = fund_data['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
    "按月分组取每月的第一个交易日数据"
    fund_data['月份'] = fund_data['净值日期'].map(lambda x:str(x)[:6])
    fund_data_m = fund_data.groupby(by='月份').tail(1).reset_index(drop=True)
    "过去1~12个月的涨跌幅"
    for i in range(1,13):
        fund_data_m['p{}m'.format(i)] = fund_data_m['累计净值']/fund_data_m['累计净值'].shift(int('-{}'.format(i))) -1
    "未来1~12个月的涨跌幅"
    for i in range(1,13):
        fund_data_m['f{}m'.format(i)] = fund_data_m['累计净值'].shift(int('{}'.format(i)))/fund_data_m['累计净值'] -1
    
    fund_data_m_final = fund_data_m[(fund_data_m['净值日期']>=20190101)&(fund_data_m['净值日期']<20200901)].reset_index(drop=True)
    

    fund_data_m_final['id'] = row['id']
    fund_data_hz = fund_data_hz.append(fund_data_m_final)
    print(index,row['id'])
    
fund_data_hz.to_excel('国内基金数据测试DU{}.xlsx'.format(now_day))    