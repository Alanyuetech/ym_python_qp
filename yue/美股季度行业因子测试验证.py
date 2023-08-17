# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 14:14:13 2021

@author: Administrator
"""

"季度换股测试验证"


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
date_work=getLastWeekDay().strftime('%Y%m%d')
now_day = datetime.datetime.now().strftime('%Y%m%d')


def final_py(stock_50b_list,wz):
    
    "所有美股"
    us_stock =  ak.stock_us_spot_em()
    us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
    stock_50b_list = pd.merge(stock_50b_list,us_stock[['代码','stock_id']],how='left',on='stock_id')
    
    
    stock_50b_list.drop(stock_50b_list[pd.isna(stock_50b_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
    stock_50b_list = stock_50b_list.reset_index(drop=True)
    
    # "模糊查询"
    # aa = us_stock.loc[us_stock['名称'].str.contains('小米')]
    # aa = us_stock.loc[us_stock['代码'].str.contains('BF_')]
    
    "近 N 年股票数据"   "时间较快，不用留档"
    stock_data = pd.DataFrame()
    end_date = '20221231'        # 设定日期,季度末日期  
    
    # stock_50b_list= stock_50b_list.loc[481:,:]
    
    for index,row in stock_50b_list.iterrows():
        stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20130101", end_date=end_date, adjust="hfq")   
        stock_data_b['代码']=row['代码']
        stock_data = stock_data.append(stock_data_b)
        print(index,row['代码'])
    
    
    ans_data = pd.merge(stock_data[['日期','收盘','代码']],stock_50b_list[['名称','所属行业','代码']],how='left',on='代码')
    
    
    "按季度分割数据，每个季度计算不同行业的涨跌幅"
    ans_data['月日'] = ans_data['日期'].apply(lambda x:x[5:])
    ans_data['年'] = ans_data['日期'].apply(lambda x:x[:4])
    ans_data['季度'] = ans_data['日期'].apply(lambda x:'1季度' if (x[5:7]>='01')&(x[5:7]<='03') 
                                          else ('2季度' if (x[5:7]>='04')&(x[5:7]<='06') 
                                                else ('3季度' if (x[5:7]>='07')&(x[5:7]<='09') else '4季度') ) )
    
    ans_data_head = ans_data.groupby(['代码','年','季度']).head(1).reset_index(drop=True).rename(columns={'收盘':'季度初收盘'})
    ans_data_tail = ans_data.groupby(['代码','年','季度']).tail(1).reset_index(drop=True).rename(columns={'收盘':'季度末收盘'})
    ans_data_q = pd.merge(ans_data_head[['代码','年','季度','名称','所属行业','季度初收盘']],ans_data_tail[['代码','年','季度','季度末收盘']]
                          ,how='inner',on=['代码','年','季度'])
    ans_data_q['季度涨幅 %'] = (ans_data_q['季度末收盘']/ans_data_q['季度初收盘'] - 1)*100
    
    ans_data_q_q_i = ans_data_q.groupby(['季度','所属行业']).agg('mean').reset_index()
    ans_data_q_q_i5 = ans_data_q_q_i.sort_values(['季度','季度涨幅 %'],ascending=[1,0]).groupby(['季度']).head(5)[['季度','所属行业','季度涨幅 %']]
    
    # "去掉油气中流，特种化学品"
    # ans_data_q_q_i5_drop = ans_data_q_q_i.drop(ans_data_q_q_i[(ans_data_q_q_i['所属行业'].astype('str')=='油气中流')|
    #                                                           (ans_data_q_q_i['所属行业'].astype('str')=='特种化学品')|
    #                                                           (ans_data_q_q_i['所属行业'].astype('str')=='太阳能')].index).sort_values(['季度','季度涨幅 %'],ascending=[1,0]).groupby(['季度']).head(5)[['季度','所属行业','季度涨幅 %']]
    
    
    
    
    ans_data_q_q_i5.to_excel('美股季度行业分析{}--{}.xlsx'.format(wz,now_day))
    
    # ans_data_q_q_i5_drop.to_excel('美股季度行业分析200亿--{}.xlsx'.format(now_day))   
        
    
    

for i in range(0,2):
    if i==0:
        "读取股票代码列表"
        stock_list = pd.read_excel('美股所有股票数据.xlsx',engine='openpyxl')    #  美股200亿以上筛选
        stock_list = stock_list.rename(columns={'代码':'stock_id'})
        stock_50b_list = stock_list[stock_list['总市值-亿']>=200]    #此处修改 >200亿   >500亿
        final_doc = final_py(stock_50b_list,'所有美股200亿')
    else:
        "读取股票代码列表"
        stock_list = pd.read_excel('美股200亿以上筛选.xlsx',engine='openpyxl')   #  美股200亿以上筛选
        stock_list = stock_list.rename(columns={'代码':'stock_id'})
        stock_50b_list = stock_list.copy()
        final_doc = final_py(stock_50b_list,'股票池200亿') 
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    