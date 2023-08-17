# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 10:38:47 2023

@author: Administrator
"""



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
from functools import reduce
import statsmodels.api as sm
from itertools import *
import math
time_start = time.time()

def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay
date_work=getLastWeekDay().strftime('%Y%m%d')

def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:str(x).zfill(6))
    return fund_id

###################################################################################################################################

big_index = pd.DataFrame([
    ['沪深300','sh000300'],
    ['中证500','sh000905'],
    ['中证800','sh000906']               
    ],columns=('大盘指数名称','大盘指数代码'))

sml_index = pd.DataFrame([
    ['创业板指','sz399006'],
    ['中证1000','sh000852'],
    ['国证2000','sz399303']              
    ],columns=('小盘指数名称','小盘指数代码'))


def jiandaocha(b_index,s_index):
    
    
    b_index_data = ak.stock_zh_index_daily_em(symbol="{}".format(b_index)).sort_values('date',ascending=0).reset_index(drop=True)[['date','close']].rename(columns={'close':'b_index_data'})
    b_index_data['date'] = b_index_data['date'].str.replace('-','')
    b_index_data['b_chg'] = b_index_data['b_index_data']/b_index_data['b_index_data'].shift(-1) - 1
    
    s_index_data = ak.stock_zh_index_daily_em(symbol="{}".format(s_index)).sort_values('date',ascending=0).reset_index(drop=True)[['date','close']].rename(columns={'close':'s_index_data'})
    s_index_data['date'] = s_index_data['date'].str.replace('-','')
    s_index_data['s_chg'] = s_index_data['s_index_data']/s_index_data['s_index_data'].shift(-1) - 1
    
    data = pd.merge(b_index_data[['date','b_chg']].copy(),s_index_data[['date','s_chg']].copy(),how='outer',on='date')
    data['gap'] = data['b_chg']-data['s_chg']
    data['gap_all_acc'] = data.apply(lambda x:data[data['date']<=x['date']]['gap'].sum(),axis=1) 
    
    return data[['date','gap','gap_all_acc']]   #如果gap_acc在这里，就是从历史数据来计算累计




writer = pd.ExcelWriter('A股剪刀差.xlsx')

for index1,row1 in big_index[:].iterrows():
    for index2,row2 in sml_index[:].iterrows():

        jiandaocha_data = jiandaocha('{}'.format(row1['大盘指数代码']),'{}'.format(row2['小盘指数代码']))
        jiandaocha_data = jiandaocha_data[jiandaocha_data['date']>='20130101']

        jiandaocha_data['gap_acc'] = jiandaocha_data.apply(
            lambda x:jiandaocha_data[jiandaocha_data['date']<=x['date']]['gap'].sum(),axis=1)  #如果gap_acc在这里，就是从需要的日期开始计算累计

        jiandaocha_data.drop(jiandaocha_data[jiandaocha_data['gap'].isna()].index).sort_values('date',ascending=1).to_excel(writer,sheet_name='{}_{}'.format(row1['大盘指数名称'],row2['小盘指数名称']), index=False) 
        print(row1['大盘指数名称'],row2['小盘指数名称'])
        
writer.save()  #save之后再write会导致整体重新写入


###################################################################################################################################
'''
所有指数净值化 、设定起始日期--依据收盘价计算每日涨跌幅--由涨跌幅计算出每日净值
'''
stock_index = pd.DataFrame([
    ['上证指数','sh000001'],
    ['沪深300','sh000300'],
    ['中证500','sh000905'],
    ['中证800','sh000906'],
    ['创业板指','sz399006'],
    ['中证1000','sh000852'],
    ['国证2000','sz399303']               
    ],columns=('指数名称','指数代码'))

def plt_stc(stc_index_data):
    stc_index_data
    plt.plot(stc_index_data['date'], stc_index_data['net_value'], 'k')     # plot(横坐标，纵坐标， 颜色)
    plt.plot(stc_index_data['date'], stc_index_data['filtering'], 'b')
    plt.xlabel('Time')
    plt.ylabel('Value')
    # plt.grid()网格线设置
    plt.grid(True)
    plt.show() 
    return


def calculate_nv(start_time,stc_index,lb_index='full'):
    stc_index_data = ak.stock_zh_index_daily_em(symbol="{}".format(stc_index)).sort_values('date',ascending=0).reset_index(drop=True)[['date','close']].rename(columns={'close':'stc_index_data'})
    stc_index_data['date'] = stc_index_data['date'].str.replace('-','')
    stc_index_data['b_chg'] = stc_index_data['stc_index_data']/stc_index_data['stc_index_data'].shift(-1) - 1
    stc_index_data['net_value'] = np.nan
    stc_index_data.loc[stc_index_data['date']==start_time,'net_value'] = 1
    stc_index_data = stc_index_data[stc_index_data['date']>=start_time]
    for i in reversed(list(stc_index_data[:-1].index)):
        stc_index_data.loc[i,'net_value'] = stc_index_data.loc[i+1,'net_value'] * (1 + stc_index_data.loc[i,'b_chg'])
    
    "基于Numpy.convolve实现滑动平均滤波"  
    
    stc_index_data['filtering'] = np.convolve(stc_index_data['net_value'], np.ones(int(100)) / float(100), '{}'.format(lb_index))   # full  same   valid
    plt_stc(stc_index_data)

    
    return stc_index_data


dfs = []
for index,row in stock_index.iterrows():
    locals()['{}'.format(row['指数代码'])] = calculate_nv('20140331',row['指数代码'],'full')[['date','net_value','filtering']].rename(columns={'net_value':'{}'.format(row['指数名称']),'filtering':'{}滤波'.format(row['指数名称'])})
    dfs.append(locals()['{}'.format(row['指数代码'])])
    

merge_data = reduce(lambda x,y:pd.merge(x,y,on='date',how='left'),dfs)
merge_data.sort_values('date',ascending=1).to_excel('A股指数convolve滤波走势.xlsx')    



























