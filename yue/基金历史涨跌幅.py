# -*- coding: utf-8 -*-
"""
Created on Wed Dec 15 13:09:07 2021

@author: Administrator
"""

"基金历史涨跌幅"



"国内基金数据  AVE 当日"
import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
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

"基金列表"
# fund_id = pd.read_excel('两周累计爬取_筛选{}.xlsx'.format(date_work),engine='openpyxl',dtype={'id':'str'})[['id']]

fund_id = pd.read_excel('fund_id0111.xlsx',engine='openpyxl',dtype={'id':'str'})[['id']]
"基金代码前面补0"
fund_id['id'] = fund_id['id'].map(lambda x:'00000'+x if len(x)==1 else
                                  ('0000'+x if len(x)==2 else 
                                   ('000'+x if len(x)==3 else
                                    ('00'+x if len(x)==4 else
                                     ('0'+x if len(x)==5 else x)))))





fund_data_hz = pd.DataFrame()


# "中途中断,填入下一个准备跑的数据  最后merge的时候 fund_id需要更新成原始版本-- 运行上方fund_id=零时AVE_测试0813"
# fund_id = fund_id.loc[156:,:]

"拿出每个基金的历史 累计净值走势"
for index,row  in fund_id[:].iterrows():
    # "单个基金历史 单位净值走势"
    # tt = '519995'  #样例
    # fund_data = ak.fund_em_open_fund_info(fund=tt, indicator="单位净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    fund_data = ak.fund_open_fund_info_em(fund=row['id'], indicator="单位净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    "防止float和双精度格式冲突"
    fund_data['单位净值'] = fund_data['单位净值'].astype(float)
    "净值日期 转变为 int "
    fund_data['净值日期'] = fund_data['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
    fund_data['涨跌幅'] = fund_data['单位净值']/ fund_data['单位净值'].shift(-1)-1
    "拿数据从  20220601  开始"
    fund_data = fund_data[(fund_data['净值日期']>=20221201)&(fund_data['净值日期']<=20230228)].sort_values(by='净值日期',ascending=False).reset_index(drop=True)
    fund_data = fund_data[['净值日期','涨跌幅']].rename(columns={'涨跌幅':'{}'.format('{}').format(row['id'])})
    if index==0:
        fund_data_hz=fund_data
    else:   
        fund_data_hz = pd.merge(fund_data_hz,fund_data,on='净值日期',how='outer')
    print(index,row['id'])
     
fund_data_hz = fund_data_hz[(fund_data_hz['净值日期']>=20230101)&(fund_data_hz['净值日期']<=20230228)]    
    
    
    
    
    
"空值填充为0"  
fund_data_hz = fund_data_hz.fillna(0)  
  
fund_data_hz = fund_data_hz.sort_values(['净值日期'],ascending=[1]).reset_index(drop=True)

fund_data_hz.to_excel('基金历史数据日{}.xlsx'.format(now_day))


##########################  周——单独成表 #########################

"从开始日期开始，每5个数据求和"
fund_data_hz_w = fund_data_hz.copy(deep=True)
fund_data_hz_w = fund_data_hz_w.sort_values(['净值日期'],ascending=[1]).reset_index(drop=True)
fund_data_hz_w['周组'] = fund_data_hz_w.index

fund_data_hz_w['周组'] = fund_data_hz_w['周组'].apply(lambda x:x//5)
fz = fund_data_hz_w[['净值日期','周组']].groupby('周组').tail(1).rename(columns={'净值日期':'周标签'})
fund_data_hz_w = pd.merge(fund_data_hz_w,fz,on='周组',how='left')

fund_data_hz_w['净值日期'] = fund_data_hz_w['净值日期'].astype('str')
fund_data_hz_w = fund_data_hz_w.groupby(['周组','周标签']).agg('sum')
# fund_data_hz_w.to_excel('基金历史数据周{}.xlsx'.format(now_day))

##################################################################

 
"存放在一张表当中"
fund_data_hz_w = fund_data_hz_w.reset_index()
fund_data_hz_w = fund_data_hz_w.drop(fund_data_hz_w.columns[[0]],axis=1)
fund_data_hz_w = fund_data_hz_w.rename(columns={'周标签':'净值日期'})
fund_data_hz_w['净值日期'] = fund_data_hz_w['净值日期'].apply(lambda x:str(x)+'周')
fund_data_hz['净值日期'] = fund_data_hz['净值日期'].astype('str')

fund_data_hz = pd.concat([fund_data_hz,fund_data_hz_w])
fund_data_hz = fund_data_hz.sort_values(['净值日期'],ascending=[1]).reset_index(drop=True)

fund_data_hz['净值日期'] = fund_data_hz['净值日期'].apply(lambda x:'五日求和' if ('周' in x) else x)


fund_data_hz.to_excel('基金历史数据{}.xlsx'.format(now_day))

































