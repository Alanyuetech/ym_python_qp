# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 15:28:27 2021

@author: Administrator
"""

"股指期货和对应指数  分时数据"


import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime

now_day = datetime.datetime.now().strftime('%Y%m%d')
from datetime import *
def getLastWeekDay(day=datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - timedelta(days=dayStep)
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y%m%d')


"股指  分时数据  新浪   "
hs300_index = ak.stock_zh_a_minute(symbol='sh000300', period='5').rename(columns={'day':'time','close':'index_close'}).sort_values(by=['time'],ascending=0).reset_index(drop=True)
zz500_index = ak.stock_zh_a_minute(symbol='sz399905', period='5').rename(columns={'day':'time','close':'index_close'}).sort_values(by=['time'],ascending=0).reset_index(drop=True)
sz50_index = ak.stock_zh_a_minute(symbol='sh000016', period='5').rename(columns={'day':'time','close':'index_close'}).sort_values(by=['time'],ascending=0).reset_index(drop=True)


"股指期货分时数据"
hs300_future = ak.futures_zh_minute_sina(symbol="IF2110", period="5").rename(columns={'datetime':'time','close':'future_close'})
zz500_future = ak.futures_zh_minute_sina(symbol="IC2110", period="5").rename(columns={'datetime':'time','close':'future_close'})
sz50_future = ak.futures_zh_minute_sina(symbol="IH2110", period="5").rename(columns={'datetime':'time','close':'future_close'})


"指数  股指期货  数据聚合"
hs300 = pd.merge(hs300_index[['time','index_close']],hs300_future[['time','future_close']],on='time')
zz500 = pd.merge(zz500_index[['time','index_close']],zz500_future[['time','future_close']],on='time')
sz50 = pd.merge(sz50_index[['time','index_close']],sz50_future[['time','future_close']],on='time')

hs300['index_close'] = hs300['index_close'].astype(float)
zz500['index_close'] = zz500['index_close'].astype(float)
sz50['index_close'] = sz50['index_close'].astype(float)


"设置分类聚合标签"
"日期标签"
hs300['day'] = hs300['time'].apply(lambda x:x[:11])
zz500['day'] = zz500['time'].apply(lambda x:x[:11])
sz50['day'] = sz50['time'].apply(lambda x:x[:11])
"上下午标签"
hs300['ampm'] = hs300['time'].apply(lambda x:'pm' if x[11:]>='13:00:00' else 'am')
zz500['ampm'] = zz500['time'].apply(lambda x:'pm' if x[11:]>='13:00:00' else 'am')
sz50['ampm'] = sz50['time'].apply(lambda x:'pm' if x[11:]>='13:00:00' else 'am')
"小时标签"
hs300['hour'] = hs300['time'].apply(lambda x:x[11:13])
zz500['hour'] = zz500['time'].apply(lambda x:x[11:13])
sz50['hour'] = sz50['time'].apply(lambda x:x[11:13])


"求  diff = 指数 - 股指期货"

hs300['diff'] = hs300['index_close'] - hs300['future_close']
zz500['diff'] = zz500['index_close'] - zz500['future_close']
sz50['diff'] = sz50['index_close'] - sz50['future_close']


"求期货增长幅度"
hs300['diff_f'] = hs300['future_close'] - hs300['future_close'].shift(-1)
zz500['diff_f'] = zz500['future_close'] - zz500['future_close'].shift(-1) 
sz50['diff_f'] = sz50['future_close'] - sz50['future_close'].shift(-1) 



############################################################################################################################

"按日期聚合"
hs300_avg = hs300.groupby(by='day').agg('mean').reset_index()
zz500_avg = zz500.groupby(by='day').agg('mean').reset_index()
sz50_avg = sz50.groupby(by='day').agg('mean').reset_index()


############################################################################################################################

"按  日期+上下午  聚合"
hs300_ampm_avg = hs300.groupby(by=['day','ampm']).agg('mean').reset_index()
zz500_ampm_avg = zz500.groupby(by=['day','ampm']).agg('mean').reset_index()
sz50_ampm_avg = sz50.groupby(by=['day','ampm']).agg('mean').reset_index()

"am的diff平均 - pm的diff平均"
hs300_ampm_avg['am-pm'] = hs300_ampm_avg['diff'] - hs300_ampm_avg['diff'].shift(-1)
zz500_ampm_avg['am-pm'] = zz500_ampm_avg['diff'] - zz500_ampm_avg['diff'].shift(-1)
sz50_ampm_avg['am-pm'] = sz50_ampm_avg['diff'] - sz50_ampm_avg['diff'].shift(-1)
"由于上方是通过shift来算的，故只保留am行的"
hs300_ampm_avg['am-pm'] = hs300_ampm_avg.apply(lambda x: np.nan if x['ampm']=='pm' else x['am-pm'] ,axis=1)
zz500_ampm_avg['am-pm'] = zz500_ampm_avg.apply(lambda x: np.nan if x['ampm']=='pm' else x['am-pm'] ,axis=1)
sz50_ampm_avg['am-pm'] = sz50_ampm_avg.apply(lambda x: np.nan if x['ampm']=='pm' else x['am-pm'] ,axis=1)

hs300_ampm_avg = hs300_ampm_avg.drop(hs300_ampm_avg[hs300_ampm_avg['ampm']=='pm'].index)[['day','am-pm']]
zz500_ampm_avg = zz500_ampm_avg.drop(zz500_ampm_avg[zz500_ampm_avg['ampm']=='pm'].index)[['day','am-pm']]
sz50_ampm_avg = sz50_ampm_avg.drop(sz50_ampm_avg[sz50_ampm_avg['ampm']=='pm'].index)[['day','am-pm']]

############################################################################################################################

"按 日期+小时 聚合"
hs300_h_avg = hs300.groupby(by=['day','hour']).agg('mean').reset_index()
zz500_h_avg = zz500.groupby(by=['day','hour']).agg('mean').reset_index()
sz50_h_avg = sz50.groupby(by=['day','hour']).agg('mean').reset_index()

"当前小时的diff平均  -  前一个小时的diff平均"
hs300_h_avg['h-lh'] = hs300_h_avg['diff'] - hs300_h_avg['diff'].shift(1)
zz500_h_avg['h-lh'] = zz500_h_avg['diff'] - zz500_h_avg['diff'].shift(1)
sz50_h_avg['h-lh'] = sz50_h_avg['diff'] - sz50_h_avg['diff'].shift(1)
























