# -*- coding: utf-8 -*-
"""
Created on Thu Sep 29 13:16:19 2022

@author: Administrator
"""

def stock_max_latest_yue():
    
    import pandas as pd
    import akshare as ak
    import numpy as np
    import datetime
    import requests
    import re
    import time
    
    delta = delta_one_year = datetime.timedelta(days=180)
    sz = pd.read_csv('全部A股.csv',dtype={'代码': 'str'})
    cyb = pd.read_csv('创业板.csv',dtype={'代码': 'str'})
    kcb = pd.read_csv('科创板.csv',dtype={'代码': 'str'})
    
    def order_for_id(data,num):
        for m in range(len(data)):
            data.iloc[m,num]=str(data.iloc[m,num])
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]       
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]
        return data
    
    
    sz = order_for_id(sz, 1)
    cyb = order_for_id(cyb, 1)
    kcb = order_for_id(kcb, 1)
    
    sz_list = [x for x in sz['代码']]
    cyb_list = [x for x in cyb['代码']]
    kcb_list = [x for x in kcb['代码']]
    
 
   
    
    def getLastWeekDay(day=datetime.datetime.now()):
        now=day
        if now.isoweekday()==1:
          dayStep=3
        else:
          dayStep=1
        lastWorkDay = now - datetime.timedelta(days=dayStep)
        
        
        return lastWorkDay
    
    date_work=getLastWeekDay().strftime('%Y%m%d')
    
    def max_latest_all(stockid,start_date,end_date):

        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stockid, period="daily", start_date=start_date, end_date=end_date, adjust="")
        stock_info= ak.stock_individual_info_em(symbol=stockid)
        ans = pd.DataFrame(stock_zh_a_hist_df.iloc[stock_zh_a_hist_df['收盘'].idxmax()]).T.rename(columns={'收盘':'max_close'})[['日期','max_close']]
        ans['latest'] =  stock_zh_a_hist_df.tail(1)['收盘'].iloc[0]
        ans['market_value'] = stock_info.loc[stock_info['item']=='总市值','value'].iloc[0]
        ans['id'] = stockid
        ans['name'] = stock_info.loc[stock_info['item']=='股票简称','value'].iloc[0]

        return ans
    
    def max_latest_hk(stockid,start_date,end_date):

        stock_hk_hist_df = ak.stock_hk_hist(symbol=stockid, period="daily", start_date=start_date, end_date=end_date, adjust="")

        ans = pd.DataFrame(stock_hk_hist_df.iloc[stock_hk_hist_df['收盘'].idxmax()]).T.rename(columns={'收盘':'max_close'})[['日期','max_close']]
        ans['latest'] =  stock_hk_hist_df.tail(1)['收盘'].iloc[0]
        # ans['market_value'] =
        ans['id'] = stockid


        return ans
    
    
    
    
    
    max_latest = pd.DataFrame()
    hk_max_latest = pd.DataFrame()
    start_date = "20220101"
    
    stock_id = sz[['代码','名称']].append(cyb[['代码','名称']])
    stock_id = stock_id.append(kcb[['代码','名称']])
    stock_id = stock_id.drop_duplicates()
    
    
    for index,row in stock_id[:].iterrows():
        try:
            stockdata_b = max_latest_all(row['代码'],start_date,date_work)
            max_latest = max_latest.append(stockdata_b)
            print(index,row['代码'],row['名称'])
        except:
            print(index,row['代码'],row['名称'],'错误')

    
    max_latest.to_excel('max_latest{}.xlsx'.format(date_work),index=False)
    
    
    
    # hk_stock_id = ak.stock_hk_spot_em()[['代码','名称']] 
    # for index,row in hk_stock_id[:].iterrows():
    #     try:
    #         hk_stockdata_b = max_latest_hk(row['代码'],start_date,date_work)
    #         hk_max_latest = hk_max_latest.append(hk_stockdata_b)
    #         print(index,row['代码'],row['名称'])
    #     except:
    #         print(index,row['代码'],row['名称'],'错误')
    # hk_max_latest.to_excel('hk_max_latest{}.xlsx'.format(date_work),index=False)



if __name__ == '__main__':
    stock_max_latest_yue()
    pass













