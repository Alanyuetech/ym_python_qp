# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 10:58:01 2022

@author: Administrator
"""

"美股活跃度因子  选股"

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


"设置计算基准时间点 ———— int 格式"
# end_date = int(now_day)   # 当前日期
end_date = 20221231        # 设定日期,季度末日期       


"读取股票代码列表"
stock_list = pd.read_excel('美股200亿以上筛选.xlsx',engine='openpyxl')
stock_list = stock_list.rename(columns={'代码':'stock_id'})
stock_50b_list = stock_list[stock_list['总市值-亿']>=200]    #此处修改 >200亿   >500亿


"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_50b_list = pd.merge(stock_50b_list,us_stock[['代码','stock_id']],how='left',on='stock_id')


stock_50b_list.drop(stock_50b_list[pd.isna(stock_50b_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
stock_50b_list = stock_50b_list.reset_index(drop=True)




# stock_50b_list= stock_50b_list.loc[61:,:]

"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_50b_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date=str(20130101), end_date=str(end_date), adjust="hfq")
    stock_data_b['代码']=row['代码']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])


ans_data = pd.merge(stock_data[['日期','收盘','成交量','换手率','代码']],stock_50b_list[['名称','所属行业','代码']],how='left',on='代码')
# ans_data['流通市值c'] = ans_data['收盘'] *(100*ans_data['成交量']/ans_data['换手率'])     #100 换手率从百分比变为小数



"换手率   过去m年的序列   过去p个月的平均   处于前 n% 的位置"

def factor_calculation(ans_data,stock_id,m,p,n):     # ans_data全部股票所有时间段数据，stock_id股票代码，过去m年序列，过去p个月平均，前n%位置

    ans = ans_data[ans_data['代码']==stock_id].copy()
    ans['日期'] = ans['日期'].astype('str').str.replace('-','').astype('int')
    ans = ans[ans['日期']>int((datetime.datetime.strptime(str(end_date),'%Y%m%d')-relativedelta(years=+m)).strftime('%Y%m%d'))]   #拿到过去m年特定股票的数据
    
    factor_c_b = pd.DataFrame()
    factor_c_b.loc[0,'代码'] = ans.iloc[0,4]
    factor_c_b.loc[0,'名称'] = ans.iloc[0,5]
    factor_c_b.loc[0,'所属行业'] = ans.iloc[0,6]
    factor_c_b.loc[0,'过去{}月平均'.format(p)] = ans[ans['日期']>=int((datetime.datetime.strptime(str(end_date),'%Y%m%d')-relativedelta(months=+p)).strftime('%Y%m%d'))]['换手率'].mean()                            
    a=100-n
    factor_c_b.loc[0,'过去{}年前{}%分位'.format(m,n)] = np.percentile(ans['换手率'], a)       
    factor_c_b.loc[0,'超出{}%百分比'.format(n)] = factor_c_b.loc[0,'过去{}月平均'.format(p)]/factor_c_b.loc[0,'过去{}年前{}%分位'.format(m,n)] -1 if factor_c_b.loc[0,'过去{}年前{}%分位'.format(m,n)]!=0 else np.nan
    return factor_c_b

factor_c_all = pd.DataFrame()
m = 1
p = 1
n = 25
for index,row in stock_50b_list.iterrows():
    factor_c_b = factor_calculation(ans_data,row['代码'],m,p,n)   
    factor_c_all = pd.concat([factor_c_all,factor_c_b])
    print(index,row['代码'],row['名称'])
factor_c_all = factor_c_all.reset_index(drop=True)    
"筛选 过去p月平均 >= 过去m年前n%分位"
factor_c = factor_c_all[factor_c_all['过去{}月平均'.format(p)]>=factor_c_all['过去{}年前{}%分位'.format(m,n)]]

factor_c.to_excel("美股活跃度因子选股{}.xlsx".format(date_work))
print('完成')


















