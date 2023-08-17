# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 14:54:53 2021

@author: Administrator
"""



"国内基金数据  AVE 当日"
import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime

from yue.ave import fund_data

now_day = datetime.datetime.now().strftime('%Y%m%d')
def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay
date_work=getLastWeekDay().strftime('%Y%m%d')

def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:str(x).zfill(6))
    return fund_id

########

"基金列表"
# fund_id = pd.read_excel('两周累计爬取_筛选20221019.xlsx',engine='openpyxl',dtype={'id':'str'})
fund_id = pd.read_excel('两周累计爬取_筛选{}.xlsx'.format(date_work),engine='openpyxl',dtype={'id':'str'})[['id']]
fund_id = bu_zero(fund_id,'id')






# "拿出每个基金的历史 累计净值走势  不用跑了"
# for index,row  in fund_id.iterrows():
#     # "单个基金历史 累计净值走势"
#     # tt = '001643'  #样例
#     # fund_data = ak.fund_open_fund_info_em(fund=tt, indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
#     fund_data = ak.fund_open_fund_info_em(fund=row['id'], indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
#     "防止float和双精度格式冲突"
#     fund_data['累计净值'] = fund_data['累计净值'].astype(float)
#     "净值日期 转变为 int "
#     fund_data['净值日期'] = fund_data['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
#     "计算  日增长率"
#     fund_data['前一日累计净值'] = fund_data['累计净值'].shift(-1)
#     fund_data['日增长率'] = fund_data['累计净值']/fund_data['前一日累计净值'] - 1
#     "拿数据从  20180101  开始"
#     fund_data = fund_data[fund_data['净值日期']>=20180101].sort_values(by='净值日期',ascending=False).reset_index(drop=True)
    
    
#     "过去60个交易日  日增长率 求和"
#     fund_data['p60日增长率和'] = np.nan
#     sum_data=list()
#     fund_data['日增长率'] = fund_data['日增长率'].astype(float)
#     for i in range(len(fund_data)-60):
#         fund_data.loc[i,'p60日增长率和'] = sum(fund_data.loc[i:60+i,'日增长率'])
    
      
#     "过去120个交易日  日增长率 求和"
#     fund_data['p120日增长率和'] = np.nan
#     for i in range(len(fund_data)-120):
#         fund_data.loc[i,'p120日增长率和'] = sum(fund_data.loc[i:120+i,'日增长率'])
    
    
      
#     "过去180个交易日  日增长率 求和"
#     fund_data['p180日增长率和'] = np.nan
#     for i in range(len(fund_data)-180):
#         fund_data.loc[i,'p180日增长率和'] = sum(fund_data.loc[i:180+i,'日增长率'])
    
    
      
#     "过去240个交易日  日增长率 求和"
#     fund_data['p240日增长率和'] = np.nan
#     for i in range(len(fund_data)-240):
#         fund_data.loc[i,'p240日增长率和'] = sum(fund_data.loc[i:240+i,'日增长率'])
    
    
    
    
#     "过去一年p60  日增长率求和  的平均值"
#     fund_data['p1yp60日增长率和ave'] = 0
#     fund_data['p1yp120日增长率和ave'] = 0
#     fund_data['p1yp180日增长率和ave'] = 0
#     fund_data['p1yp240日增长率和ave'] = 0
#     for index_1,row_i in fund_data.iterrows():
#         fund_data.loc[index_1,'p1yp60日增长率和ave'] = fund_data[(fund_data['净值日期']>row_i['净值日期']-10000)&(fund_data['净值日期']<=row_i['净值日期'])]['p60日增长率和'].mean()
#         fund_data.loc[index_1,'p1yp120日增长率和ave'] = fund_data[(fund_data['净值日期']>row_i['净值日期']-10000)&(fund_data['净值日期']<=row_i['净值日期'])]['p120日增长率和'].mean()
#         fund_data.loc[index_1,'p1yp180日增长率和ave'] = fund_data[(fund_data['净值日期']>row_i['净值日期']-10000)&(fund_data['净值日期']<=row_i['净值日期'])]['p180日增长率和'].mean()
#         fund_data.loc[index_1,'p1yp240日增长率和ave'] = fund_data[(fund_data['净值日期']>row_i['净值日期']-10000)&(fund_data['净值日期']<=row_i['净值日期'])]['p240日增长率和'].mean()
#     # "计算未来D30  D90  涨跌幅"    
#     # fund_data['f30累计净值'] = fund_data['累计净值'].shift(30)
#     # fund_data['f90累计净值'] = fund_data['累计净值'].shift(90)
#     # fund_data['D30'] = (fund_data['f30累计净值']-fund_data['累计净值'])/fund_data['累计净值']
#     # fund_data['D90'] = (fund_data['f90累计净值']-fund_data['累计净值'])/fund_data['累计净值']
    
#     # "只取如下时间段的数据"
#     # fund_data = fund_data[(fund_data['净值日期']==20190630)|(fund_data['净值日期']==20190830)|
#     #                       (fund_data['净值日期']==20191030)|(fund_data['净值日期']==20191230)|
#     #                       (fund_data['净值日期']==20200228)|(fund_data['净值日期']==20200430)|
#     #                       (fund_data['净值日期']==20200630)|(fund_data['净值日期']==20200831)|
#     #                       (fund_data['净值日期']==20201030)|(fund_data['净值日期']==20201230)|
#     #                       (fund_data['净值日期']==20210226)|(fund_data['净值日期']==20210430)|
#     #                       (fund_data['净值日期']==20210630)]
    
#     fund_data = fund_data.head(1)[['净值日期','p1yp60日增长率和ave','p1yp120日增长率和ave','p1yp180日增长率和ave','p1yp240日增长率和ave']]
#     fund_data['id'] = row['id']
#     fund_data_hz = fund_data_hz.append(fund_data)
#     print(index,row['id'])
  
    
  
    
  
    
# "拿出每个基金的历史 累计净值走势   修改时间：20220302  "  
# def fund_data(fundid):
#     # "单个基金历史 累计净值走势"
#     # tt = '001643'  #样例
#     # fund_data = ak.fund_open_fund_info_em(fund=tt, indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
#     fund_data_b = ak.fund_open_fund_info_em(fund=fundid, indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
#     "防止float和双精度格式冲突"
#     fund_data_b['累计净值'] = fund_data_b['累计净值'].astype(float)
#     "净值日期 转变为 int "
#     fund_data_b['净值日期'] = fund_data_b['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
#     "计算  日增长率"
#     fund_data_b['前一日累计净值'] = fund_data_b['累计净值'].shift(-1)
#     fund_data_b['日增长率'] = fund_data_b['累计净值']/fund_data_b['前一日累计净值'] - 1
#     "拿数据从  20180101  开始"
#     fund_data_b = fund_data_b[fund_data_b['净值日期']>=20180101].sort_values(by='净值日期',ascending=False).reset_index(drop=True)
    
    
#     "过去60个交易日  日增长率 求和"
#     fund_data_b['p60日增长率和'] = np.nan
#     sum_data=list()
#     fund_data_b['日增长率'] = fund_data_b['日增长率'].astype(float)
#     for i in range(len(fund_data_b)-60):
#         fund_data_b.loc[i,'p60日增长率和'] = sum(fund_data_b.loc[i:60+i,'日增长率'])
    
      
#     "过去120个交易日  日增长率 求和"
#     fund_data_b['p120日增长率和'] = np.nan
#     for i in range(len(fund_data_b)-120):
#         fund_data_b.loc[i,'p120日增长率和'] = sum(fund_data_b.loc[i:120+i,'日增长率'])
    
    
      
#     "过去180个交易日  日增长率 求和"
#     fund_data_b['p180日增长率和'] = np.nan
#     for i in range(len(fund_data_b)-180):
#         fund_data_b.loc[i,'p180日增长率和'] = sum(fund_data_b.loc[i:180+i,'日增长率'])
    
    
      
#     "过去240个交易日  日增长率 求和"
#     fund_data_b['p240日增长率和'] = np.nan
#     for i in range(len(fund_data_b)-240):
#         fund_data_b.loc[i,'p240日增长率和'] = sum(fund_data_b.loc[i:240+i,'日增长率'])
    
    
    
    
#     "过去一年p60  日增长率求和  的平均值"
#     fund_data_b['p1yp60日增长率和ave'] = 0
#     fund_data_b['p1yp120日增长率和ave'] = 0
#     fund_data_b['p1yp180日增长率和ave'] = 0
#     fund_data_b['p1yp240日增长率和ave'] = 0
#     for index_1,row_i in fund_data_b.iterrows():
#         fund_data_b.loc[index_1,'p1yp60日增长率和ave'] = fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p60日增长率和'].mean()
#         fund_data_b.loc[index_1,'p1yp120日增长率和ave'] = fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p120日增长率和'].mean()
#         fund_data_b.loc[index_1,'p1yp180日增长率和ave'] = fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p180日增长率和'].mean()
#         fund_data_b.loc[index_1,'p1yp240日增长率和ave'] = fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p240日增长率和'].mean()
#     # "计算未来D30  D90  涨跌幅"    
#     # fund_data_b['f30累计净值'] = fund_data_b['累计净值'].shift(30)
#     # fund_data_b['f90累计净值'] = fund_data_b['累计净值'].shift(90)
#     # fund_data_b['D30'] = (fund_data_b['f30累计净值']-fund_data_b['累计净值'])/fund_data_b['累计净值']
#     # fund_data_b['D90'] = (fund_data_b['f90累计净值']-fund_data_b['累计净值'])/fund_data_b['累计净值']
    
#     # "只取如下时间段的数据"
#     # fund_data_b = fund_data_b[(fund_data_b['净值日期']==20190630)|(fund_data_b['净值日期']==20190830)|
#     #                       (fund_data_b['净值日期']==20191030)|(fund_data_b['净值日期']==20191230)|
#     #                       (fund_data_b['净值日期']==20200228)|(fund_data_b['净值日期']==20200430)|
#     #                       (fund_data_b['净值日期']==20200630)|(fund_data_b['净值日期']==20200831)|
#     #                       (fund_data_b['净值日期']==20201030)|(fund_data_b['净值日期']==20201230)|
#     #                       (fund_data_b['净值日期']==20210226)|(fund_data_b['净值日期']==20210430)|
#     #                       (fund_data_b['净值日期']==20210630)]
    
#     fund_data_b = fund_data_b.head(1)[['净值日期','p1yp60日增长率和ave','p1yp120日增长率和ave','p1yp180日增长率和ave','p1yp240日增长率和ave']]
#     fund_data_b['id'] = fundid     
#     return fund_data_b
    



fund_data_hz = pd.DataFrame()


"中途中断,填入下一个准备跑的数据  最后merge的时候 fund_id需要更新成原始版本"
# fund_id = fund_id.loc[3102:,:]



for index,row  in fund_id[:].iterrows():
    fund_data_bb = fund_data(row['id'])
    fund_data_hz = fund_data_hz.append(fund_data_bb)
    print(index,row['id'])
    

    
"去重"
# fund_data_hz_b = fund_data_hz.drop_duplicates() 
# fund_data_hz = fund_data_hz_b



fund_data_hz = fund_data_hz.reset_index(drop=True)
fund_data_hz = pd.merge(left=fund_data_hz,right=fund_id,on='id')

########
fund_data_hz.to_excel('国内基金数据AVE_XX{}.xlsx'.format(date_work))   
print('完成') 