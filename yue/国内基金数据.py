# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 13:21:35 2021

@author: Administrator
"""

"国内基金数据"
import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime

"基金列表"
fund_id = pd.read_excel('临时AVE_测试0813.xlsx',dtype={'id':'str'})
"基金代码前面补0"
fund_id['id'] = fund_id['id'].map(lambda x:'00000'+x if len(x)==1 else
                                  ('0000'+x if len(x)==2 else 
                                   ('000'+x if len(x)==3 else
                                    ('00'+x if len(x)==4 else
                                     ('0'+x if len(x)==5 else x)))))


fund_data_hz = pd.DataFrame()
"拿出每个基金的历史 单位净值走势"
for index,row  in fund_id.iterrows():
    "单个基金历史 单位净值走势"
    # tt = '540008'  #样例
    # fund_data = ak.fund_em_open_fund_info(fund=tt, indicator="单位净值走势").reset_index(drop=True)
    fund_data = ak.fund_em_open_fund_info(fund=row['id'], indicator="单位净值走势")
    "净值日期 转变为 int "
    fund_data['净值日期'] = fund_data['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
    "拿数据从  20180101  开始"
    fund_data = fund_data[fund_data['净值日期']>=20180101].reset_index(drop=True)
    fund_data['id'] = row['id']
    fund_data_hz = fund_data_hz.append(fund_data)
    print(index,row['id'])

fund_data_hz = fund_data_hz.reset_index(drop=True)
fund1 = fund_data_hz.loc[0:500000,:]
fund2 = fund_data_hz.loc[500000:1000000,:]
fund3 = fund_data_hz.loc[1000000:1500000,:]
fund4 = fund_data_hz.loc[1500000:len(fund_data_hz)+1,:]



























