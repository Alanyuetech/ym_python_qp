# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 13:09:02 2023

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



bond_investing_global_df  = pd.read_csv('中国十年期国债收益率历史数据.csv')
bond_investing_global_df['日期'] = bond_investing_global_df['日期'].str.replace('年','-').str.replace('月','-').str.replace('日','')
bond_investing_global_df['年'] = bond_investing_global_df['日期'].str.split('-',expand = True)[0]
bond_investing_global_df['月'] = bond_investing_global_df['日期'].str.split('-',expand = True)[1].map(lambda x:str(x).zfill(2))
bond_investing_global_df['日'] = bond_investing_global_df['日期'].str.split('-',expand = True)[2].map(lambda x:str(x).zfill(2))
bond_investing_global_df['日期'] = bond_investing_global_df['年']+'-'+bond_investing_global_df['月']+'-'+bond_investing_global_df['日']
bond_investing_global_df = bond_investing_global_df.rename(columns={'收盘':'10Y国债收盘'})





def plt_module(trading_list_plt,symbol_i,start_date):
    
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


def single_stock_operation(single_stock_id,start_date,s_period,l_period,holding_days):
    
    stock_us_data_b = ak.stock_zh_a_hist(symbol=single_stock_id, period="daily", 
                                       start_date="{}".format(start_date),end_date="22220101",
                                       adjust="hfq")
                                                                                            #可循环项
    stock_us_data_turnover_madiff = stock_us_data_b[['日期','换手率']].copy()
    stock_us_data_turnover_madiff.iloc[:,1:] = np.nan  
    
    
    for i in range(l_period-1,len(stock_us_data_b)):  
            
        if stock_us_data_b.loc[i-s_period+1:i,'换手率'].mean()>stock_us_data_b.loc[i-l_period+1:i,'换手率'].mean():   #短周期比长周期活跃
            stock_us_data_turnover_madiff.loc[i,'换手率'] = 1
        elif stock_us_data_b.loc[i-s_period+1:i,'换手率'].mean()<stock_us_data_b.loc[i-l_period+1:i,'换手率'].mean():  #长周期比短周期活跃
            stock_us_data_turnover_madiff.loc[i,'换手率'] = -1
        else:
            stock_us_data_turnover_madiff.loc[i,'换手率'] = 0

                                                                  
    trading_list = pd.DataFrame(columns=('品种','买多/卖空','建仓时间','退出时间','操作收益率'))    
    t_index = 0
    
    for i in range(l_period,len(stock_us_data_turnover_madiff)-holding_days):  #行   留下一定的行

        if (stock_us_data_turnover_madiff.loc[i,'换手率']+stock_us_data_turnover_madiff.loc[i-1,'换手率']==0)&(stock_us_data_turnover_madiff.loc[i-s_period:i-1,'换手率'].sum()==-1*s_period):            
            trading_list.loc[t_index,'品种'] = single_stock_id
            trading_list.loc[t_index,'买多/卖空'] = '买多'
            trading_list.loc[t_index,'建仓时间'] = stock_us_data_turnover_madiff.iloc[i+1,0]
            trading_list.loc[t_index,'退出时间'] = stock_us_data_turnover_madiff.iloc[i+1+holding_days-1,0]
            trading_list.loc[t_index,'操作收益率'] = stock_us_data_b.loc[i+1+holding_days-1,'收盘'] / stock_us_data_b.loc[i+1,'开盘'] - 1
            print('买多{} 建仓时间:{}  退出时间:{}  操作收益:{}'.format(single_stock_id,trading_list.loc[t_index,'建仓时间'],trading_list.loc[t_index,'退出时间'],trading_list.loc[t_index,'操作收益率']))
            t_index+=1
        # elif (stock_us_data_turnover_madiff.loc[i,'换手率']+stock_us_data_turnover_madiff.loc[i-1,'换手率']==0)&(stock_us_data_turnover_madiff.loc[i-s_period:i-1,'换手率'].sum()==1*s_period):
        #     trading_list.loc[t_index,'品种'] = single_stock_id
        #     trading_list.loc[t_index,'买多/卖空'] = '卖空'
        #     trading_list.loc[t_index,'建仓时间'] = stock_us_data_turnover_madiff.iloc[i+1,0]
        #     trading_list.loc[t_index,'退出时间'] = stock_us_data_turnover_madiff.iloc[i+1+holding_days-1,0]
        #     trading_list.loc[t_index,'操作收益率'] = 1 - stock_us_data_b.loc[i+1+holding_days-1,'收盘']  / stock_us_data_b.loc[i+1,'开盘']         
        #     print("卖空  建仓时间:{}  退出时间:{}  操作收益:{}".format(trading_list.loc[t_index,'建仓时间'],trading_list.loc[t_index,'退出时间'],trading_list.loc[t_index,'操作收益率']))
        #     t_index+=1
        else:
            pass 


    return trading_list




def short_strategy(symbol_i='自定义名单',start_date='20220101',parameters=[5,10,5],head_tail_num=100):
    s_period,l_period,holding_days = parameters[0],parameters[1],parameters[2]
    
    if symbol_i!='自定义名单':
        "不同板块/行业成分股"
        stock_plate =  ak.stock_board_concept_name_em()[['板块代码','板块名称']] 
        stock_us_famous_spot = ak.stock_board_concept_cons_em(symbol="{}".format(symbol_i))[['代码','名称']]

    else:
        "股票名单"  
        if head_tail_num>0:
            stock_us_famous_spot = pd.read_excel('A股短期策略股票池.xlsx',engine='openpyxl')[:1493].head(head_tail_num)[['代码','名称']].reset_index(drop=True)
            stock_us_famous_spot = bu_zero(stock_us_famous_spot,'代码')
        else :
            stock_us_famous_spot = pd.read_excel('A股短期策略股票池.xlsx',engine='openpyxl')[:1493].tail(-head_tail_num)[['代码','名称']].reset_index(drop=True)
            stock_us_famous_spot = bu_zero(stock_us_famous_spot,'代码')            
    
    
                    
    "每个股票循环"
    trading_list = pd.DataFrame()   
    for index,row in stock_us_famous_spot[:].iterrows():
        trading_list_b = single_stock_operation(row['代码'],start_date,s_period,l_period,holding_days)                            
        trading_list = trading_list.append(trading_list_b)
        trading_list = trading_list.reset_index(drop=True)
                
    trading_list['操作收益率'] = trading_list['操作收益率'].astype('float')
    trading_list_groupby_date = trading_list.groupby(by='退出时间').agg({'操作收益率':'mean'}).reset_index()    #这里可以修改  建仓时间/退出时间
    trading_list_groupby_date = pd.merge(trading_list_groupby_date,bond_investing_global_df[['日期','10Y国债收盘']],how='left',left_on='退出时间',right_on='日期')   #这里可以修改  建仓时间/退出时间
    trading_list_groupby_date = trading_list_groupby_date[['退出时间','操作收益率','10Y国债收盘']]

    
      
    
###################################################################################################################################################################    
    "净值计算--日频复利"
    # trading_list_change = (1+trading_list_groupby_date['操作收益率']).prod()-1
    # stock_us_data_date = ak.stock_us_hist(symbol='105.AAPL', period="daily",start_date="{}".format(start_date),end_date="22220101",adjust="hfq")[['日期']]
    # trading_list_plt = pd.merge(stock_us_data_date,trading_list_groupby_date,left_on='日期',right_on='退出时间',how='left')
    # trading_list_plt['计算过程'] = trading_list_plt['操作收益率']+1
    # trading_list_plt['计算过程'] = trading_list_plt['计算过程'].fillna(1)
    
    
    
    # trading_list_plt['净值'] = 1
    # for index,row in trading_list_plt[1:].iterrows():
    #     trading_list_plt.loc[index,'净值'] =  trading_list_plt.loc[index-1,'净值'] * trading_list_plt.loc[index,'计算过程']
    
 
###################################################################################################################################################################      
    
    "净值计算--日频收益率求和--收益不参与"
    # trading_list_change = trading_list_groupby_date['操作收益率'].sum()
    # stock_us_data_date = ak.stock_us_hist(symbol='105.AAPL', period="daily",start_date="{}".format(start_date),end_date="22220101",adjust="hfq")[['日期']]
    # trading_list_plt = pd.merge(stock_us_data_date,trading_list_groupby_date,left_on='日期',right_on='退出时间',how='left')
    
    # trading_list_plt['计算过程'] = trading_list_plt['操作收益率']+0
    # trading_list_plt['计算过程'] = trading_list_plt['计算过程'].fillna(0)
    # trading_list_plt['净值'] = 1   
    
    # for index,row in trading_list_plt[1:].iterrows():
    #     trading_list_plt.loc[index,'净值'] =  trading_list_plt.loc[index-1,'净值'] + trading_list_plt.loc[index,'计算过程']/holding_days
    
###################################################################################################################################################################      
  
    "净值计算--日频收益率复利--拆分为 1/holding_days 个小账户，每个账户内复利，即全部的钱跨holding_days滚动全额投资，"
    trading_list_groupby_date['标序'] = trading_list_groupby_date.index%holding_days + 1
    stock_us_data_date = ak.stock_zh_a_hist(symbol='600519', period="daily",start_date="{}".format(start_date),end_date="22220101",adjust="hfq")[['日期']]
    trading_list_plt = pd.merge(stock_us_data_date,trading_list_groupby_date,left_on='日期',right_on='退出时间',how='left')
    trading_list_plt['净值'] = 1
    for bx in range(1,trading_list_groupby_date['标序'].max()+1):  
        bx_networth = trading_list_groupby_date[trading_list_groupby_date['标序']==bx].copy().reset_index(drop=True)
        bx_networth['计算过程'] = bx_networth['操作收益率']+1
        bx_networth['{}'.format(bx)] =  1  
        
        for index,row in bx_networth[:].iterrows():
            bx_networth.loc[index,'{}'.format(bx)] =  bx_networth.loc[:index,'计算过程'].prod()
        
        trading_list_plt = pd.merge(trading_list_plt,bx_networth[['退出时间','{}'.format(bx)]],how='left',on='退出时间')
        trading_list_plt['{}'.format(bx)] = trading_list_plt['{}'.format(bx)].fillna(method='ffill') 
        trading_list_plt['{}'.format(bx)] = trading_list_plt['{}'.format(bx)].fillna(1)
    
    trading_list_plt['净值'] = trading_list_plt.iloc[:,6:].mean(axis=1)
    

   


###################################################################################################################################################################      
     

    
    trading_list_plt['当前回撤'] = np.nan    
    for index,row in trading_list_plt[1:].iterrows():
        trading_list_plt.loc[index,'当前回撤'] = 1 - trading_list_plt.loc[index,'净值']/trading_list_plt.loc[:index,'净值'].max()
        
        
    "画图"
    plt_module(trading_list_plt,symbol_i,start_date)
    
    #############################################
    diff_days = (datetime.datetime.strptime(trading_list_groupby_date.iloc[-1,0],"%Y-%m-%d")-datetime.datetime.strptime(trading_list_groupby_date.iloc[0,0],"%Y-%m-%d")).days
    
    "perform analysis"
    trading_list_perform_ana_bb = pd.DataFrame()
    trading_list_perform_ana_bb.loc[0,'股票类别'] = symbol_i
    trading_list_perform_ana_bb.loc[0,'数据开始时间'] = start_date
    trading_list_perform_ana_bb.loc[0,'策略收益统计时间'] = trading_list_groupby_date.iloc[0,0]
    trading_list_perform_ana_bb.loc[0,'当前净值'] = trading_list_plt.loc[trading_list_plt.index.max(),'净值']
    trading_list_perform_ana_bb.loc[0,'历史净值最大值'] = trading_list_plt['净值'].max()
    trading_list_perform_ana_bb.loc[0,'历史净值最小值'] = trading_list_plt['净值'].min()
    trading_list_perform_ana_bb.loc[0,'波动率'] = trading_list_plt[trading_list_plt['日期']>=trading_list_groupby_date.iloc[0,0]]['净值'].std()
    trading_list_perform_ana_bb.loc[0,'夏普'] = ((math.pow(trading_list_plt.loc[trading_list_plt.index.max(),'净值'],360/diff_days)-1)-(trading_list_groupby_date['10Y国债收盘'].mean())/100)/trading_list_perform_ana_bb.loc[0,'波动率']
    trading_list_perform_ana_bb.loc[0,'最大回撤'] = trading_list_plt['当前回撤'].max()
    trading_list_perform_ana_bb.loc[0,'操作胜率'] = len(trading_list_groupby_date[trading_list_groupby_date['操作收益率']>0])/len(trading_list_groupby_date)
    trading_list_perform_ana_bb.loc[0,'parameters'] = '{},{},{}'.format(s_period,l_period,holding_days)
    trading_list_perform_ana_bb.loc[0,'head_tail_num'] = '{}'.format(head_tail_num)
    
    return trading_list_perform_ana_bb,trading_list




symbol_list = ['自定义名单']

start_date_list = ['20180101','20220101']

trading_list_perform_ana = pd.DataFrame(columns=('股票类别','数据开始时间','策略收益统计时间','当前净值','历史净值最大值','历史净值最小值','波动率','夏普','最大回撤'))



for symbol_i in symbol_list:
    if symbol_i=='自定义名单':
        for head_tail_num in [400,450,500,550,600]:  #[30,50,100,150,200,-30,-50,-100,-150,-200]
            for start_date in start_date_list:
                # for parameters in [[3,5,3],[3,5,5],[3,5,10],[3,10,3],[3,10,5],[3,10,10],[5,10,3],[5,10,5],[5,10,10]]:
                for parameters in [[10,20,60],[10,40,60],[10,60,60],[20,40,60],[20,60,60],[40,60,60]]:
                    
                    
                    trading_list_perform_ana_b,trading_list = short_strategy(symbol_i,start_date,parameters,head_tail_num)   #循环股票名单
                    # trading_list_perform_ana_b,trading_list = short_strategy('自定义名单',start_date,parameters,head_tail_num)   #自定义股票名单
                    trading_list_perform_ana = trading_list_perform_ana.append(trading_list_perform_ana_b)
                    trading_list_perform_ana = trading_list_perform_ana.reset_index(drop=True)
                    
                    trading_list_dategroupby=trading_list.groupby('退出时间').agg('count')
    else:                           
        for start_date in start_date_list:
            # for parameters in [[3,5,3],[3,5,5],[3,5,10],[3,10,3],[3,10,5],[3,10,10],[5,10,3],[5,10,5],[5,10,10]]:
            for parameters in [[10,20,60],[10,40,60],[10,60,60],[20,40,60],[20,60,60],[40,60,60]]:
                
                
                trading_list_perform_ana_b,trading_list = short_strategy(symbol_i,start_date,parameters,head_tail_num)   #循环股票名单
                # trading_list_perform_ana_b,trading_list = short_strategy('自定义名单',start_date,parameters,head_tail_num)   #自定义股票名单
                trading_list_perform_ana = trading_list_perform_ana.append(trading_list_perform_ana_b)
                trading_list_perform_ana = trading_list_perform_ana.reset_index(drop=True)
                
                trading_list_dategroupby=trading_list.groupby('退出时间').agg('count')




######################################################################################################################
"real"

 

def single_stock_real_operation(single_stock_id,start_date,s_period,l_period):
    
    stock_us_data_b = ak.stock_zh_a_hist(symbol=single_stock_id, period="daily", 
                                       start_date="{}".format(start_date),end_date="22220101",
                                       adjust="hfq")
                                                                                            #可循环项
    stock_us_data_turnover_madiff = stock_us_data_b[['日期','换手率']].copy()
    stock_us_data_turnover_madiff.iloc[:,1:] = np.nan  
    
    
    for i in range(l_period-1,len(stock_us_data_b)):  
            
        if stock_us_data_b.loc[i-s_period+1:i,'换手率'].mean()>stock_us_data_b.loc[i-l_period+1:i,'换手率'].mean():   #短周期比长周期活跃
            stock_us_data_turnover_madiff.loc[i,'换手率'] = 1
        elif stock_us_data_b.loc[i-s_period+1:i,'换手率'].mean()<stock_us_data_b.loc[i-l_period+1:i,'换手率'].mean():  #长周期比短周期活跃
            stock_us_data_turnover_madiff.loc[i,'换手率'] = -1
        else:
            stock_us_data_turnover_madiff.loc[i,'换手率'] = 0

                                                                  
    trading_list = pd.DataFrame(columns=('品种','买多/卖空'))    
   
    "只判断最新的一天"
    i_loc = stock_us_data_turnover_madiff.index.max()
    if (stock_us_data_turnover_madiff.loc[i_loc,'换手率']+stock_us_data_turnover_madiff.loc[i_loc-1,'换手率']==0)&(stock_us_data_turnover_madiff.loc[i_loc-s_period:i_loc-1,'换手率'].sum()==-1*s_period):            
        trading_list.loc[0,'品种'] = single_stock_id
        trading_list.loc[0,'买多/卖空'] = '买多'
        
        print('买多  品种:{}  '.format(single_stock_id))

    # elif (stock_us_data_turnover_madiff.loc[i_loc,'换手率']+stock_us_data_turnover_madiff.loc[i_loc-1,'换手率']==0)&(stock_us_data_turnover_madiff.loc[i_loc-s_period:i_loc-1,'换手率'].sum()==1*s_period):
    #     trading_list.loc[0,'品种'] = single_stock_id
    #     trading_list.loc[0,'买多/卖空'] = '卖空'
           
    #     print('卖空  品种:{}  '.format(single_stock_id))

    else:

        print('无操作  品种:{}  '.format(single_stock_id)) 


    return trading_list





def short_real_strategy(symbol_i='自定义名单',parameters=[5,10]):    
    s_period,l_period = parameters[0],parameters[1]
    
    if symbol_i!='自定义名单':
        "不同板块/行业成分股"
        stock_plate =  ak.stock_board_concept_name_em()[['板块代码','板块名称']] 
        stock_us_famous_spot = ak.stock_board_concept_cons_em(symbol="{}".format(symbol_i))[['代码','名称']]

    else:
        "股票名单"  
        stock_us_famous_spot = pd.read_excel('A股短期策略股票池.xlsx',engine='openpyxl')[:100][['代码','名称']]
        stock_us_famous_spot = bu_zero(stock_us_famous_spot,'代码')
    
    "修改开始日期，拿过去13个月的数据  使用 D250 也可以cover"
    start_date = (datetime.datetime.now() - relativedelta(months=+13)).strftime('%Y%m%d')
                
    "每个股票循环"
    trading_list = pd.DataFrame()   
    for index,row in stock_us_famous_spot[:].iterrows():
        trading_list_b = single_stock_real_operation(row['代码'],start_date,s_period,l_period)                            
        trading_list = trading_list.append(trading_list_b)
        trading_list = trading_list.reset_index(drop=True)
    trading_list = trading_list.reset_index(drop=True)           
    return trading_list
    



for parameters in [[5,10]]:
    # trading_list_perform_ana_b,trading_list = short_strategy(symbol_i,start_date,parameters)   #循环股票名单
    trading_list = short_real_strategy('自定义名单',parameters)   #自定义股票名单
    
    
