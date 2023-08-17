# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 14:45:30 2020

@author: 86178
"""
import pymysql
import pandas as pd
import tushare as ts
from datetime import *

'''db=pymysql.connect(host='192.168.10.166',port=3306,user='baseroot',password='123456',database='rank_data',charset='utf8')
cur=db.cursor()
sql = 'SELECT * FROM project.stock_data;'
cur.execute(sql)
data_source=cur.fetchall()
data_source=pd.DataFrame(data_source,columns=['industry_id','stock_id','stock_name'])
cur.execute(insert_sql)
sql_ind='SELECT * FROM rank_data.sz;'
data_source_ind=cur.fetchall()
data_source_ind=pd.DataFrame(data_source_ind,columns=['industry_id','industry_name'])
data_final=pd.merge(data_source_ind,data_source,how='left',on='industry_id')



df_sz=ts.get_hist_data('sz',start='2020-01-01',end='2020-12-07')
df_sh=ts.get_hist_data('sh',start='2020-01-01',end='2020-12-07')
df_cyb=ts.get_hist_data('cyb',start='2020-01-01',end='2020-12-07')

df_sz['date']=df_sz.index
df_sh['date']=df_sh.index 
df_cyb['date']=df_cyb.index

data_sh=pd.concat([df_sh['date'],df_sh['close'],df_sh['p_change']],axis=1)
data_sz=pd.concat([df_sz['date'],df_sz['close'],df_sz['p_change']],axis=1)
data_cyb=pd.concat([df_cyb['date'],df_cyb['close'],df_cyb['p_change']],axis=1)

data_sz.reset_index(drop=True,inplace=True)
data_sh.reset_index(drop=True,inplace=True)
data_cyb.reset_index(drop=True,inplace=True)

data_sh.reset_index(drop=True,inplace=True)

data_sh.to_sql('sh_index',con='mysql+pymysql://baseroot:123456@192.168.10.167/market_index?charset=utf8',if_exists='replace',index=False)
data_sz.to_sql('sz_index',con='mysql+pymysql://baseroot:123456@192.168.10.167/market_index?charset=utf8',if_exists='replace',index=False)
data_cyb.to_sql('cyb_index',con='mysql+pymysql://baseroot:123456@192.168.10.167/market_index?charset=utf8',if_exists='replace',index=False)'''

 
def getLastWeekDay(day=datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - timedelta(days=dayStep)
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y-%m-%d')

data_insert_sh=ts.get_hist_data('sh',start=str(date_work),end=str(date_work))
data_insert_sh['date']=data_insert_sh.index
data_insert_sh.drop(['open', 'high',  'low', 'volume', 'price_change',
       'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
data_insert_sh.to_sql('sh_index',con='mysql+pymysql://root:123456@192.168.10.166/market_index?charset=utf8',if_exists='append',index=False)

data_insert_sz=ts.get_hist_data('sz',start=str(date_work),end=str(date_work))
data_insert_sz['date']=data_insert_sz.index
data_insert_sz.drop(['open',  'high',  'low', 'volume', 'price_change',
       'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
data_insert_sz.to_sql('sz_index',con='mysql+pymysql://root:123456@192.168.10.166/market_index?charset=utf8',if_exists='append',index=False)

data_insert_cyb=ts.get_hist_data('cyb',start=str(date_work),end=str(date_work))
data_insert_cyb['date']=data_insert_cyb.index
data_insert_cyb.drop(['open', 'high',  'low', 'volume', 'price_change',
       'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
data_insert_cyb.to_sql('cyb_index',con='mysql+pymysql://root:123456@192.168.10.166/market_index?charset=utf8',if_exists='append',index=False)





