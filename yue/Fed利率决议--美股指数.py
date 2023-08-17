# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 14:15:07 2021

@author: Administrator
"""

"Fed利率决议--美股指数"


import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
import xlsxwriter
import openpyxl
from openpyxl.styles import PatternFill,Font,Alignment
now_day = datetime.datetime.now().strftime('%Y%m%d')





"参数设置"
start_date = '19810101'
country = '美国'
index_name = '纳斯达克综合指数'      #纳斯达克综合指数  标普500指数     道琼斯指数
period = '每日'





"美联储利率--某些数据有问题，直接在金十数据上复制到本地"   
# us_interest_rate = pd.DataFrame(ak.macro_bank_usa_interest_rate()).reset_index().sort_values(['index'],ascending=0).reset_index(drop=True)
us_interest_rate = pd.read_excel('Fed-rate.xlsx',engine='openpyxl')
us_interest_rate['index'] = us_interest_rate['index'].apply(lambda x:str(x)[:10])
us_interest_rate['index'] = us_interest_rate['index'].astype('str').str.replace('-','')
us_interest_rate = us_interest_rate.rename(columns={'index':'日期'})



"美股三大指数数据——时间跨度为2007年至今"  "美股数据需要代理开全局"

"获取指数数据，并调整日期"
def index_data(country,index_name,period,start_date,end_date):
    time_diff = (int(end_date)-int(start_date))//10000   #是否超过15年，因为每次数据只能爬5000条。
    if time_diff>15:
        
        end_date_b = str(int(start_date)//10000 + 10)+'1231'
        start_date_b = start_date
        index_data = pd.DataFrame()   
        while start_date_b <end_date :
        
            index_data_b = ak.index_investing_global(country=country, index_name=index_name, 
                                          period=period, start_date=start_date_b, end_date=end_date_b)
            
            index_data = pd.concat([index_data,index_data_b])
            
            start_date_b = str(int(end_date_b)//10000 + 1)+'0101'
            end_date_b = str(int(start_date_b)//10000 + 10)+'1231'         
            
    else:
        index_data = ak.index_investing_global(country=country, index_name=index_name, 
                                      period=period, start_date=start_date, end_date=end_date)     
    
    index_data['日期'] = index_data['日期'].astype('str').str.replace('-','') 
    return index_data

 


idx_data = index_data(country,index_name,period,start_date,now_day).sort_values('日期',ascending=0).reset_index(drop=True)
idx_data = idx_data[['日期','收盘']].rename(columns={'收盘':'idx_data'}).sort_values(['日期'],ascending=0)

"spx500  直接运行"
idx_data = pd.read_excel('SPX500_data.xlsx',engine='openpyxl',dtype={'日期':'str'})



# ans = pd.merge(idx_data,us_interest_rate,on='日期',how='left')
# ans['利率'] = ans['usa_interest_rate']
# ans['利率'] = ans['利率'].fillna(method='bfill')



# idx_data_1 = idx_data[(idx_data['日期']>='19821215')&(idx_data['日期']<='19840810')].reset_index(drop=True)
# idx_data_2 = idx_data[(idx_data['日期']>='19860822')&(idx_data['日期']<='19870925')].reset_index(drop=True)
# idx_data_3 = idx_data[(idx_data['日期']>='19880212')&(idx_data['日期']<='19890518')].reset_index(drop=True)
# idx_data_4 = idx_data[(idx_data['日期']>='19920905')&(idx_data['日期']<='19950202')].reset_index(drop=True)
# idx_data_5 = idx_data[(idx_data['日期']>='19981118')&(idx_data['日期']<='20000517')].reset_index(drop=True)
# idx_data_6 = idx_data[(idx_data['日期']>='20030626')&(idx_data['日期']<='20060630')].reset_index(drop=True)
# idx_data_7 = idx_data[(idx_data['日期']>='20151217')&(idx_data['日期']<='20181220')].reset_index(drop=True)


"加息周期内"
idx_data_1 = idx_data[(idx_data['日期']>='19821215')&(idx_data['日期']<='19840920')].reset_index(drop=True)
idx_data_2 = idx_data[(idx_data['日期']>='19860822')&(idx_data['日期']<='19871104')].reset_index(drop=True)
idx_data_3 = idx_data[(idx_data['日期']>='19880212')&(idx_data['日期']<='19890606')].reset_index(drop=True)
idx_data_4 = idx_data[(idx_data['日期']>='19920905')&(idx_data['日期']<='19950706')].reset_index(drop=True)
idx_data_5 = idx_data[(idx_data['日期']>='19981118')&(idx_data['日期']<='20010103')].reset_index(drop=True)
idx_data_6 = idx_data[(idx_data['日期']>='20030626')&(idx_data['日期']<='20070918')].reset_index(drop=True)
idx_data_7 = idx_data[(idx_data['日期']>='20151217')&(idx_data['日期']<='20190130')].reset_index(drop=True)



"加息周期开始后n个交易日"
n = 250
idx_data_1 = idx_data[(idx_data['日期']>='19821215')].tail(n).reset_index(drop=True)
idx_data_2 = idx_data[(idx_data['日期']>='19860822')].tail(n).reset_index(drop=True)
idx_data_3 = idx_data[(idx_data['日期']>='19880212')].tail(n).reset_index(drop=True)
idx_data_4 = idx_data[(idx_data['日期']>='19920905')].tail(n).reset_index(drop=True)
idx_data_5 = idx_data[(idx_data['日期']>='19981118')].tail(n).reset_index(drop=True)
idx_data_6 = idx_data[(idx_data['日期']>='20030626')].tail(n).reset_index(drop=True)
idx_data_7 = idx_data[(idx_data['日期']>='20151217')].tail(n).reset_index(drop=True)
"加息周期开始前n个交易日"
n = 250
idx_data_1 = idx_data[(idx_data['日期']<'19821215')].head(n).reset_index(drop=True)
idx_data_2 = idx_data[(idx_data['日期']<'19860822')].head(n).reset_index(drop=True)
idx_data_3 = idx_data[(idx_data['日期']<'19880212')].head(n).reset_index(drop=True)
idx_data_4 = idx_data[(idx_data['日期']<'19920905')].head(n).reset_index(drop=True)
idx_data_5 = idx_data[(idx_data['日期']<'19981118')].head(n).reset_index(drop=True)
idx_data_6 = idx_data[(idx_data['日期']<'20030626')].head(n).reset_index(drop=True)
idx_data_7 = idx_data[(idx_data['日期']<'20151217')].head(n).reset_index(drop=True)




"各个加息周期下的涨幅平均"
idx_data_avg_num = pd.DataFrame()
for i in range(1,8):
    idx_data_avg_num.loc[i-1,'开始时间'] = locals()['idx_data_{}'.format(i)].tail(1).reset_index(drop=True).loc[0,'日期']
    idx_data_avg_num.loc[i-1,'结束时间'] = locals()['idx_data_{}'.format(i)].head(1).reset_index(drop=True).loc[0,'日期']
    idx_data_avg_num.loc[i-1,'整体涨幅'] = (locals()['idx_data_{}'.format(i)].head(1).reset_index(drop=True).loc[0,'idx_data']/locals()['idx_data_{}'.format(i)].tail(1).reset_index(drop=True).loc[0,'idx_data'] - 1 )
    idx_data_avg_num.loc[i-1,'平均涨幅'] = (locals()['idx_data_{}'.format(i)].head(1).reset_index(drop=True).loc[0,'idx_data']/locals()['idx_data_{}'.format(i)].tail(1).reset_index(drop=True).loc[0,'idx_data'] - 1 )/locals()['idx_data_{}'.format(i)]['日期'].count()
    idx_data_avg_num.loc[i-1,'交易日数量'] = locals()['idx_data_{}'.format(i)]['日期'].count()

idx_data_avg_num.to_excel('{}Fedrate--{}{}.xlsx'.format(n,index_name,now_day))

"整体区间内的涨幅平均         整体涨幅不需要跑最后的   /count()"
idx_data_avg =( idx_data.head(1).reset_index(drop=True).loc[0,'idx_data']/idx_data.tail(1).reset_index(drop=True).loc[0,'idx_data'] - 1)/idx_data['日期'].count()



