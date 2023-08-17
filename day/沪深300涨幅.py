# -*- coding: utf-8 -*-
"""
Created on Thu Jun 24 14:16:36 2021

@author: 86178
"""


from dateutil.relativedelta import relativedelta
import yfinance as yf
import tushare as ts
import datetime
import pandas as pd






def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    
    
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y%m%d')

now = datetime.datetime.now()
D90 = (now - relativedelta(months=3)).strftime('%Y-%m-%d')
D180 = (now - relativedelta(months=6)).strftime('%Y-%m-%d')
D270 = (now - relativedelta(months=9)).strftime('%Y-%m-%d')
D360 = (now - relativedelta(months=12)).strftime('%Y-%m-%d')
D720 = (now - relativedelta(months=24)).strftime('%Y-%m-%d')
 
hs300 = ts.get_k_data('hs300')

info_D90 = hs300[hs300['date']>D90]
close_list = [x for x in info_D90['close']]
res_D90 = ((close_list[-1] - close_list[0])/close_list[0])*100

info_D180 = hs300[hs300['date']>D180]
close_list = [x for x in info_D180['close']]
res_D180 = ((close_list[-1] - close_list[0])/close_list[0])*100

info_D270 = hs300[hs300['date']>D270]
close_list = [x for x in info_D270['close']]
res_D270 = ((close_list[-1] - close_list[0])/close_list[0])*100

info_D360 = hs300[hs300['date']>D360]
close_list = [x for x in info_D360['close']]
res_D360 = ((close_list[-1] - close_list[0])/close_list[0])*100

info_D720 = hs300[hs300['date']>D720]
close_list = [x for x in info_D720['close']]
res_D720 = ((close_list[-1] - close_list[0])/close_list[0])*100

result = pd.DataFrame([str(res_D90)+'%',str(res_D180)+'%',str(res_D270)+'%',str(res_D360)+'%',str(res_D720)+'%'],index=['D90','D180','D270','D360','D720'],columns=['HS300'])
result.to_excel('HS300涨幅{}.xlsx'.format(date_work))
