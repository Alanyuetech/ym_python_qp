# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 14:45:30 2020

@author: 86178
"""


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

def index_import():
    import pymysql
    import tushare as ts
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
    
    
    def getLastWeekDay(day=datetime.datetime.now()):
        now=day
        if now.isoweekday()==1:
          dayStep=3
        else:
          dayStep=1
        lastWorkDay = now - datetime.timedelta(days=dayStep)
        return lastWorkDay
    date_work=getLastWeekDay().strftime('%Y-%m-%d')
    
    
    
    
    
    data_insert_sh=ts.get_hist_data('sh',start=str(date_work),end=str(date_work))
    data_insert_sh['date']=data_insert_sh.index
    data_insert_sh.drop(['open', 'high',  'low', 'volume', 'price_change',
           'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)    
    data_insert_sh.to_sql('sh_index',con='mysql+pymysql://root:123456@192.168.10.219/market_index?charset=utf8',if_exists='append',index=False)
    
    data_insert_sz=ts.get_hist_data('sz',start=str(date_work),end=str(date_work))
    data_insert_sz['date']=data_insert_sz.index
    data_insert_sz.drop(['open',  'high',  'low', 'volume', 'price_change',
           'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
    data_insert_sz.to_sql('sz_index',con='mysql+pymysql://root:123456@192.168.10.219/market_index?charset=utf8',if_exists='append',index=False)
    
    data_insert_cyb=ts.get_hist_data('cyb',start=str(date_work),end=str(date_work))
    data_insert_cyb['date']=data_insert_cyb.index
    data_insert_cyb.drop(['open', 'high',  'low', 'volume', 'price_change',
           'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
    data_insert_cyb.to_sql('cyb_index',con='mysql+pymysql://root:123456@192.168.10.219/market_index?charset=utf8',if_exists='append',index=False)
    
    "落地excel文档"
    sh_index = pd.read_excel('sh_index.xlsx',engine='openpyxl')
    sh_index = sh_index.append(data_insert_sh.reset_index(drop=True)).reset_index(drop=True)
    sh_index.to_excel('sh_index.xlsx',index=False)
    
    sz_index = pd.read_excel('sz_index.xlsx',engine='openpyxl')
    sz_index = sz_index.append(data_insert_sz.reset_index(drop=True)).reset_index(drop=True)
    sz_index.to_excel('sz_index.xlsx',index=False)

    cyb_index = pd.read_excel('cyb_index.xlsx',engine='openpyxl')
    cyb_index = cyb_index.append(data_insert_cyb.reset_index(drop=True)).reset_index(drop=True)
    cyb_index.to_excel('cyb_index.xlsx',index=False)    
    
    
    
    
    

    #  replace 用于替换，可以直接取所有的数据，替换整个表    append 平时一天一天的添加
    # data_insert_sh=ts.get_hist_data('sh',start=str('2018-10-22'),end=str(date_work))
    # data_insert_sh['date']=data_insert_sh.index
    # data_insert_sh.drop(['open', 'high',  'low', 'volume', 'price_change',
    #        'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
    # data_insert_sh.to_sql('sh_index',con='mysql+pymysql://root:123456@192.168.10.166/market_index?charset=utf8',if_exists='replace',index=False)
    
    # data_insert_sz=ts.get_hist_data('sz',start=str('2018-10-22'),end=str(date_work))
    # data_insert_sz['date']=data_insert_sz.index
    # data_insert_sz.drop(['open',  'high',  'low', 'volume', 'price_change',
    #        'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
    # data_insert_sz.to_sql('sz_index',con='mysql+pymysql://root:123456@192.168.10.166/market_index?charset=utf8',if_exists='replace',index=False)
    
    # data_insert_cyb=ts.get_hist_data('cyb',start=str('2018-10-22'),end=str(date_work))
    # data_insert_cyb['date']=data_insert_cyb.index
    # data_insert_cyb.drop(['open', 'high',  'low', 'volume', 'price_change',
    #         'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
    # data_insert_cyb.to_sql('cyb_index',con='mysql+pymysql://root:123456@192.168.10.166/market_index?charset=utf8',if_exists='replace',index=False)



    # data_insert_cyb=ts.get_hist_data('cyb',start=str('2018-10-22'),end=str(date_work))
    # data_insert_cyb['date']=data_insert_cyb.index
    # data_insert_cyb.drop(['open', 'high',  'low', 'volume', 'price_change',
    #         'ma5', 'ma10', 'ma20', 'v_ma5', 'v_ma10', 'v_ma20'],axis=1,inplace=True)
    # data_insert_cyb.to_sql('cyb_index',con='mysql+pymysql://root:123456@192.168.10.166/market_index?charset=utf8',if_exists='replace',index=False)





if __name__ == '__main__':
    index_import()
    pass


