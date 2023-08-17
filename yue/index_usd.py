# -*- coding: utf-8 -*-
"""
Created on Wed Aug  4 13:09:10 2021

@author: Administrator
"""

import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
"确定当前时间"
timeStamp=time.time()
now_time = time.strftime('%Y%m%d',time.localtime(timeStamp))

start_date = str('20050101')


"伦敦布伦特原油"
crude_oil = ak.futures_global_commodity_hist(sector="能源", symbol="伦敦布伦特原油", 
                                             start_date=start_date,  end_date="{}".format(now_time))
"美元指数"
usd = ak.index_investing_global(country="美国", index_name="美元指数", period="每日",
                                start_date=start_date, end_date="{}".format(now_time))

"合并 美元指数 伦敦布伦特原油"
data = pd.merge(left=usd,right=crude_oil,how='inner',on='日期')
"整理格式"
data['月份'] = data['日期'].apply(lambda x:x.strftime('%Y%m%d')[:6])
data = data[['月份','收盘_x','收盘_y']].rename(columns={'收盘_x':'美元指数','收盘_y':'伦敦布伦特原油'})
mean_data = data.groupby('月份').agg("mean")
corr_data = data.groupby('月份').agg("corr")
corr_data = corr_data[['美元指数']].rename(columns={'美元指数':'相关系数'})
corr_data = corr_data.reset_index()
corr_data = corr_data[['月份','相关系数']]
corr_data = corr_data.drop(corr_data[corr_data['相关系数']==1].index).reset_index()[['月份','相关系数']]
# corr_data.to_excel('美元指数&布伦特原油_相关系数.xlsx',index=False)
corr_data = corr_data.set_index(["月份"])
"画图"
# corr_data.plot(kind='bar')


"美股三大指数数据——时间跨度为2000年至今"  "美股数据需要代理开全局"

# spx_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
#                                       period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))

# dow_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
#                                       period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))

naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))
naq_index['前一天收盘价'] = naq_index['收盘'].shift(-1)
naq_index['涨跌幅'] = naq_index['收盘']/naq_index['前一天收盘价'] - 1
naq_index = naq_index[['涨跌幅']].reset_index()
naq_index['月份'] = naq_index['日期'].apply(lambda x:x.strftime('%Y%m%d')[:6])
naq_index = naq_index[['月份','涨跌幅']]
naq_index = naq_index.groupby('月份').agg("sum")
naq_index_corr_data= pd.merge(left=corr_data,right=naq_index,how='inner',on='月份')
naq_index_corr_data['下月涨跌幅'] = naq_index_corr_data['涨跌幅'].shift(-1)
naq_index_corr_data = naq_index_corr_data.reset_index()
corr_naq_corr_data = naq_index_corr_data[['相关系数','下月涨跌幅']].corr()
"美元原油相关性超过0.3的进行研究"
naq_index_corr_data_pt = naq_index_corr_data[abs(naq_index_corr_data['相关系数'])>0.3]
corr_naq_corr_data_pt = naq_index_corr_data_pt[['相关系数','下月涨跌幅']].corr()






