# -*- coding: utf-8 -*-
"""
Created on Tue Dec  6 13:23:28 2022

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


bond_investing_global_df  = pd.read_csv('美国十年期国债收益率历史数据.csv')
bond_investing_global_df['日期'] = bond_investing_global_df['日期'].str.replace('年','-').str.replace('月','-').str.replace('日','')
bond_investing_global_df['年'] = bond_investing_global_df['日期'].str.split('-',expand = True)[0]
bond_investing_global_df['月'] = bond_investing_global_df['日期'].str.split('-',expand = True)[1].map(lambda x:str(x).zfill(2))
bond_investing_global_df['日'] = bond_investing_global_df['日期'].str.split('-',expand = True)[2].map(lambda x:str(x).zfill(2))
bond_investing_global_df['日期'] = bond_investing_global_df['年']+'-'+bond_investing_global_df['月']+'-'+bond_investing_global_df['日']
bond_investing_global_df = bond_investing_global_df.rename(columns={'收盘':'10Y国债收盘'})



symbol_list = ['科技类', '金融类', '医药食品类', '媒体类', '汽车能源类', '制造零售类']

start_date_list = ['20180101','20220101']

trading_list_perform_ana = pd.DataFrame(columns=('股票类别','数据开始时间','策略开始时间','当前净值','历史净值最大值','历史净值最小值','波动率','夏普','最大回撤'))

trading_list_perform_ana_index = 0
for symbol_i in symbol_list:
    for start_date in start_date_list:
        for parameters in [[3,5,3],[3,5,5],[3,5,10],[3,10,3],[3,10,5],[3,10,10],[5,10,3],[5,10,5],[5,10,10]]:
            
            s_period,l_period,holding_days = parameters[0],parameters[1],parameters[2]
            
            # print(s_period,l_period,holding_days)        
            # print(symbol_i,start_date)
    
            "知名美股策略"
            # stock_us_famous_spot = ak.stock_us_famous_spot_em(symbol='科技类')   #可循环项
            stock_us_famous_spot = ak.stock_us_famous_spot_em(symbol='{}'.format(symbol_i))
            stock_us_famous_spot = stock_us_famous_spot.dropna(axis=0,how='any')
            stock_us_famous_spot['stock_id'] = stock_us_famous_spot['代码'].str.rsplit('.',expand = True)[1]
            
            stock_us_list = ak.stock_us_spot_em() 
            
            
            "获得知名美股的历史数据"
            
            
            stock_us_data_turnover = pd.DataFrame()
            stock_us_data_closeprice = pd.DataFrame()
            stock_us_data_openprice = pd.DataFrame()
            
            
            
            for index,row in stock_us_famous_spot.iterrows():
                stock_us_data_b = ak.stock_us_hist(symbol=row['代码'], period="daily", 
                                                   start_date="{}".format(start_date),end_date="22220101",
                                                   adjust="hfq").rename(columns={'换手率':'换手率{}'.format(row['代码']),
                                                                                 '收盘':'收盘{}'.format(row['代码']),'开盘':'开盘{}'.format(row['代码'])})
                                                                                                        #可循环项
                if index==0:
                    stock_us_data_turnover = stock_us_data_b[['日期','换手率{}'.format(row['代码'])]].copy()
                    stock_us_data_closeprice = stock_us_data_b[['日期','收盘{}'.format(row['代码'])]].copy()
                    stock_us_data_openprice = stock_us_data_b[['日期','开盘{}'.format(row['代码'])]].copy()
            
                else:
                    stock_us_data_turnover = pd.merge(stock_us_data_turnover,stock_us_data_b[['日期','换手率{}'.format(row['代码'])]],on='日期')
                    stock_us_data_closeprice = pd.merge(stock_us_data_closeprice,stock_us_data_b[['日期','收盘{}'.format(row['代码'])]],on='日期')
                    stock_us_data_openprice = pd.merge(stock_us_data_openprice,stock_us_data_b[['日期','开盘{}'.format(row['代码'])]],on='日期')
                           
                print(index,row['stock_id'])
            
            
            
            stock_us_data_turnover_madiff = stock_us_data_turnover.copy()
            stock_us_data_turnover_madiff.iloc[:,1:] = np.nan
            
            # s_period = 3   #短期MA   #可循环项
            # l_period = 5   #长期MA   #可循环项
            
            for j in range(1,stock_us_data_turnover.shape[1]):   #列
                for i in range(l_period,len(stock_us_data_turnover)+1):  #行

                        
                    if stock_us_data_turnover.iloc[i-s_period:i,j].mean()>stock_us_data_turnover.iloc[i-l_period:i,j].mean():   #短周期比长周期活跃
                        stock_us_data_turnover_madiff.iloc[i-1,j] = 1
                    elif stock_us_data_turnover.iloc[i-s_period:i,j].mean()<stock_us_data_turnover.iloc[i-l_period:i,j].mean():  #长周期比短周期活跃
                        stock_us_data_turnover_madiff.iloc[i-1,j] = -1
                    else:
                        stock_us_data_turnover_madiff.iloc[i-1,j] = 0
                    
                    
            # holding_days = 5    #持有时间    #可循环项
            trading_list = pd.DataFrame(columns=('品种','买多/卖空','建仓时间','退出时间','操作收益率'))
            columns_list = pd.DataFrame(list(stock_us_data_turnover_madiff.copy()))
            columns_list[0] = columns_list[0].str.replace('换手率','')
            
            t_index = 0
            
            #长短周期活跃度变化（相邻两天和为0），且变化前的趋势具备一定的延续性（madiff没有变动）
            
            for j in range(1,stock_us_data_turnover_madiff.shape[1]):   #列
                for i in range(l_period+1,len(stock_us_data_turnover_madiff)-holding_days):  #行   留下一定的行

                    if (stock_us_data_turnover_madiff.iloc[i,j]+stock_us_data_turnover_madiff.iloc[i-1,j]==0)&(stock_us_data_turnover_madiff.iloc[i-s_period:i,j].sum()==-1*s_period):            
                        trading_list.loc[t_index,'品种'] = columns_list.loc[j,0]
                        trading_list.loc[t_index,'买多/卖空'] = '买多'
                        trading_list.loc[t_index,'建仓时间'] = stock_us_data_turnover_madiff.iloc[i+1,0]
                        trading_list.loc[t_index,'退出时间'] = stock_us_data_turnover_madiff.iloc[i+1+holding_days-1,0]
                        trading_list.loc[t_index,'操作收益率'] = stock_us_data_closeprice.iloc[i+1+holding_days-1,j] / stock_us_data_openprice.iloc[i+1,j] - 1
                        print('买多  建仓时间：{}  退出时间：{}  操作收益：{}'.format(trading_list.loc[t_index,'建仓时间'],trading_list.loc[t_index,'退出时间'],trading_list.loc[t_index,'操作收益率']))
                        t_index+=1
                    elif (stock_us_data_turnover_madiff.iloc[i,j]+stock_us_data_turnover_madiff.iloc[i-1,j]==0)&(stock_us_data_turnover_madiff.iloc[i-s_period:i,j].sum()==1*s_period):
                        trading_list.loc[t_index,'品种'] = columns_list.loc[j,0]
                        trading_list.loc[t_index,'买多/卖空'] = '卖空'
                        trading_list.loc[t_index,'建仓时间'] = stock_us_data_turnover_madiff.iloc[i+1,0]
                        trading_list.loc[t_index,'退出时间'] = stock_us_data_turnover_madiff.iloc[i+1+holding_days-1,0]
                        trading_list.loc[t_index,'操作收益率'] = 1 - stock_us_data_closeprice.iloc[i+1+holding_days-1,j] / stock_us_data_openprice.iloc[i+1,j]             
                        print("卖空  建仓时间:{}  退出时间:{}  操作收益:{}".format(trading_list.loc[t_index,'建仓时间'],trading_list.loc[t_index,'退出时间'],trading_list.loc[t_index,'操作收益率']))
                        t_index+=1
                    else:
                        pass
            
            trading_list['操作收益率'] = trading_list['操作收益率'].astype('float')
            trading_list_groupby_date = trading_list.groupby(by='建仓时间').agg({'操作收益率':'mean'}).reset_index()
            trading_list_groupby_date = pd.merge(trading_list_groupby_date,bond_investing_global_df[['日期','10Y国债收盘']],how='left',left_on='建仓时间',right_on='日期')
            trading_list_groupby_date = trading_list_groupby_date[['建仓时间','操作收益率','10Y国债收盘']]
            trading_list_change = (1+trading_list_groupby_date['操作收益率']).prod()-1
            
            
            "净值计算"
            
            trading_list_plt = pd.merge(stock_us_data_closeprice[['日期']],trading_list_groupby_date,left_on='日期',right_on='建仓时间',how='left')
            trading_list_plt['计算过程'] = trading_list_plt['操作收益率']+1
            trading_list_plt['计算过程'] = trading_list_plt['计算过程'].fillna(1)
            
            
            
            trading_list_plt['净值'] = 1
            for index,row in trading_list_plt[1:].iterrows():
                trading_list_plt.loc[index,'净值'] =  trading_list_plt.loc[index-1,'净值'] * trading_list_plt.loc[index,'计算过程']
            
            trading_list_plt['当前回撤'] = np.nan    
            for index,row in trading_list_plt[1:].iterrows():
                trading_list_plt.loc[index,'当前回撤'] = 1 - trading_list_plt.loc[index,'净值']/trading_list_plt.loc[:index,'净值'].max()
                
                
            "画图"
            #############################################
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 添加这条可以让图形显示中文
            x_axis_data = trading_list_plt['日期']
            y_axis_data = trading_list_plt['净值']
            # plot中参数的含义分别是横轴值，纵轴值，线的形状，颜色，透明度,线的宽度和标签
            plt.plot(x_axis_data, y_axis_data, color='#4169E1', alpha=0.8, linewidth=1, label='{}{}策略净值'.format(symbol_i,start_date))  #可循环项，label中加 format
            # 显示标签，如果不加这句，即使在plot中加了label='一些数字'的参数，最终还是不会显示标签
            plt.legend(loc="upper right")
            plt.xlabel('日期')
            plt.ylabel('净值')
            plt.show()
            
            #############################################
            diff_days = (datetime.datetime.strptime(trading_list_groupby_date.iloc[-1,0],"%Y-%m-%d")-datetime.datetime.strptime(trading_list_groupby_date.iloc[0,0],"%Y-%m-%d")).days
            
            "perform analysis"
            
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'股票类别'] = symbol_i
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'数据开始时间'] = start_date
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'策略开始时间'] = trading_list_groupby_date.iloc[0,0]
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'当前净值'] = trading_list_plt.iloc[-1,-2]
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'历史净值最大值'] = trading_list_plt['净值'].max()
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'历史净值最小值'] = trading_list_plt['净值'].min()
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'波动率'] = trading_list_plt[trading_list_plt['日期']>=trading_list_groupby_date.iloc[0,0]]['净值'].std()
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'夏普'] = ((math.pow(trading_list_plt.iloc[-1,-2],360/diff_days)-1)-(trading_list_groupby_date['10Y国债收盘'].mean())/100)/trading_list_perform_ana.loc[trading_list_perform_ana_index,'波动率']
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'最大回撤'] = trading_list_plt['当前回撤'].max()
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'操作胜率'] = len(trading_list_groupby_date[trading_list_groupby_date['操作收益率']>0])/len(trading_list_groupby_date)
            trading_list_perform_ana.loc[trading_list_perform_ana_index,'parameters'] = '{},{},{}'.format(s_period,l_period,holding_days)
            
            trading_list_perform_ana_index += 1
    










