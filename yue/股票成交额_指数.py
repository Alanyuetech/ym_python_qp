# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 15:41:12 2021

@author: Administrator
"""

"当日成交额前20名，与大盘指数的相关性测试"
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


"返回所有美股代码"
usstock_id = pd.DataFrame()
usstock_id = pd.DataFrame(ak.stock_us_spot_em()['代码'])

"拿到美股数据"
usstock_data = pd.DataFrame()
id_count = 0
for id in usstock_id['代码']:
    stock_us_hist_df = ak.stock_us_hist(symbol=id,start_date="20180101", end_date=date_work)
    stock_us_hist_df['代码'] = id
    usstock_data = usstock_data.append(stock_us_hist_df)
    print('{}'.format(id))
    id_count+=1
    if id_count>=10:
        break

usstock_data = usstock_data.sort_values(by=['日期','代码'],ascending=(0,0))


##########################################################################
"报错 改变代理模式"
"返回所有A股代码"
cnstock_id = pd.DataFrame()
cnstock_id = pd.DataFrame(ak.stock_zh_a_spot_em()['代码'])
"拿到A股数据"
cnstock_data = pd.DataFrame()
data_id_erro = pd.DataFrame()
id_count = 0


for id in cnstock_id.loc[0:,'代码']:
    try:
        stock_cn_hist_df = ak.stock_zh_a_hist(symbol=id,start_date="20180101", end_date=date_work)
        stock_cn_hist_df['代码'] = id
        cnstock_data = cnstock_data.append(stock_cn_hist_df)
        print(id_count,'{}'.format(id))
        id_count+=1
    # if id_count>=10:
    #     break
    except:       
        data_id_erro = data_id_erro.append(pd.DataFrame([[id_count,id]]))
        print(id_count,'{}  错误'.format(id))
        id_count+=1
        continue 


# "同上"
# for index,row in cnstock_id.iterrows():
#     stock_cn_hist_df = ak.stock_zh_a_hist(symbol=row['代码'],start_date="20180101", end_date="20210813")
#     stock_cn_hist_df['代码'] = row['代码']
#     cnstock_data = cnstock_data.append(stock_cn_hist_df)
#     print(index,'{}'.format(row['代码']))

"数据处理——获得每日成交额前20 "   
cnstock_data = cnstock_data.sort_values(by=['日期','成交额'],ascending=(0,0))
cnstock_data_d = cnstock_data.groupby(by='日期').head(20).reset_index(drop=True)

"计算每日成交额前20个股票中 涨跌幅>0的个数  即每日涨跌幅正数个数"
cnstock_data_dg0 = pd.DataFrame(cnstock_data_d[cnstock_data_d['涨跌幅']>0].groupby(by='日期').size()).sort_values(by=['日期'],ascending=0).reset_index().rename(columns={0:'正数个数'})

"每日成交额前20的涨跌幅和换手率进行平均"
cnstock_data_d = cnstock_data_d.groupby(by='日期').agg({'涨跌幅':'mean','换手率':'mean'}).sort_values(by=['日期'],ascending=0).reset_index()


"国内指数"

sh_index = ak.stock_zh_index_daily_em(symbol="sh000001").sort_values(by='date',ascending=0).reset_index(drop=True)
sz_index = ak.stock_zh_index_daily_em(symbol="sz399001").sort_values(by='date',ascending=0).reset_index(drop=True)
cyb_index = ak.stock_zh_index_daily_em(symbol="sz399006").sort_values(by='date',ascending=0).reset_index(drop=True)

"国内指数每日涨幅"
sh_index['sh_change'] = sh_index['close']/sh_index['close'].shift(-1) -1
sz_index['sz_change'] = sz_index['close']/sz_index['close'].shift(-1) -1
cyb_index['cyb_change'] = cyb_index['close']/cyb_index['close'].shift(-1) -1

"只取日期和每日涨幅，与成交额统计数据 日期列明保持一致"
sh_index = sh_index[['date','sh_change']].rename(columns={'date':'日期'})
sz_index = sz_index[['date','sz_change']].rename(columns={'date':'日期'})
cyb_index = cyb_index[['date','cyb_change']].rename(columns={'date':'日期'})

index_final = pd.merge(left=sh_index,right=sz_index,on='日期')
index_final = pd.merge(left=index_final,right=cyb_index,on='日期')

"merge 国内指数每日涨幅"
cnstock_data_d = pd.merge(left=cnstock_data_d,right=index_final,on='日期')

"北向资金净买额"
hgt_data = ak.stock_em_hsgt_hist(symbol="沪股通").sort_values(by='日期',ascending=0).reset_index(drop=True)[['日期','当日成交净买额']].rename(columns={'当日成交净买额':'沪股通'})
sgt_data = ak.stock_em_hsgt_hist(symbol="深股通").sort_values(by='日期',ascending=0).reset_index(drop=True)[['日期','当日成交净买额']].rename(columns={'当日成交净买额':'深股通'})
bx_data = pd.merge(left=hgt_data,right=sgt_data,on='日期')
bx_data['北向_当日成交净买额(亿)'] = (bx_data['沪股通'] + bx_data['深股通'])/100
"日期格式统一"
bx_data['日期'] = bx_data['日期'].astype(str)

"merge 北向资金"
cnstock_data_d = pd.merge(left=cnstock_data_d,right=bx_data,on='日期')

"merge  正数个数"
cnstock_data_d = pd.merge(cnstock_data_d,cnstock_data_dg0,on='日期')

"输出xlsx"
cnstock_data_d.to_excel('日股票成交额前20_涨跌幅&换手率平均{}.xlsx'.format(date_work))  

"输出报错的股票代码"
data_id_erro = data_id_erro.reset_index(drop=True)
data_id_erro.to_excel('报错股票代码{}.xlsx'.format(date_work))  


























