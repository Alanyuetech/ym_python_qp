# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 10:45:18 2023

@author: Administrator
"""

"国内宏观数据分析择时"


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

def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay
date_work=getLastWeekDay().strftime('%Y%m%d')


####################################################
def time_bs_creative(df,ori_time='date',bs=['年','月','日','年季','年月','月日'],timing='15'):
    "将输入的df中的日期字段 如 20230101 添加一些时间标识，年，月，日，季度"
    df_columns = list(df.columns)    
    df['年'] = df['{}'.format(ori_time)].str.slice(0,4)
    df['月'] = df['{}'.format(ori_time)].str.slice(4,6)
    df['日'] = df['{}'.format(ori_time)].str.slice(6,8)
    df['年月'] = df['{}'.format(ori_time)].str.slice(0,6)
    df['月日'] = df['{}'.format(ori_time)].str.slice(4,8)    
    df['年季'] = df.apply(lambda x:'{}Q1'.format(x['年']) if (x['月日']>='01{}'.format(timing))&(x['月日']<'04{}'.format(timing)) 
                        else('{}Q2'.format(x['年']) if (x['月日']>='04{}'.format(timing))&(x['月日']<'07{}'.format(timing)) 
                             else('{}Q3'.format(x['年']) if (x['月日']>='07{}'.format(timing))&(x['月日']<'10{}'.format(timing))
                                  else ('{}Q4'.format(str(int(x['年'])-1)) if x['月日']<'01{}'.format(timing) 
                                        else '{}Q4'.format(x['年']) ) ) ),axis=1)   
    return df[df_columns+bs]
####################################################
def period_chg(df,timing='15',time_bs='年季'):
    "timing 每个月的 timing日 作为计算的起始周期"
    df_ym = df[['{}'.format(time_bs)]].drop_duplicates().reset_index(drop=True)
    df_columns = list(df.columns)  

    for index,row in df_ym[:].iterrows():
        try:         
            df_ym.loc[index,'time_final'] = df[df['{}'.format(time_bs)]==row['{}'.format(time_bs)]].head(1).reset_index(drop=True).loc[0,'{}'.format(df_columns[1])]
        except:
            pass
    df_ym['chg'] = df_ym['time_final'].shift(1)/df_ym['time_final']-1
    df_ym['chg_old'] = df_ym['chg'].shift(-1)
    # df_ym['chg_old_1'] = df_ym['time_final']/df_ym['time_final'].shift(-1)-1
    df_ym['chg_qual'] = df_ym['chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    df_ym['chg_old_qual'] = df_ym['chg_old'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    return df_ym



################################################################################################################################################################################################################
################################################################################################################################################################################################################
################################################################################################################################################################################################################

def total_function(index_bs,fjd_n):

    
    "    数据获取    "
    
    
    
    
    ####################################################
    "官方制造业PMI   月底 或 月初 公布"  #金10下载
    pmi= pd.read_excel('制造业PMI.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    pmi['date'] = pmi['date'].map(lambda x:(datetime.datetime.strptime('19000101','%Y%m%d')+datetime.timedelta(days=x-2)).strftime('%Y%m%d'))
    pmi = pmi[pmi['date']>='20110901']
    ####################################################
    "财新制造业PMI   月底 或 月初 公布"  # buy   后金10下载
    cx_pmi= pd.read_excel('财新PMI.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    cx_pmi['date'] = cx_pmi['date'].str.replace('-','')
    ####################################################
    "PPI 当月同比   前半月 公布"  #金10下载
    "PPI 预期误差   前半月 公布"    #金10下载
    ppi_tb = pd.read_excel('PPI金十.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    ppi_tb['date'] = ppi_tb['日期'].map(lambda x:(datetime.datetime.strptime('19000101','%Y%m%d')+datetime.timedelta(days=x-2)).strftime('%Y%m%d'))
    ppi_tb = ppi_tb[['date','今值(%)','预测值(%)','前值(%)']]
    ppi_tb = ppi_tb[ppi_tb['date']>='20110901']
    ####################################################
    "CFETS人民币汇率指数    周五公布，有月底数据"    #官网下载  最多一年的数据
    cfets_index= pd.read_excel('CFETS人民币汇率指数.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    cfets_index['date'] = cfets_index['date'].str.replace('-','')
    ####################################################
    "美元 人民币  中间价    日频"    #buy
    usdcny = pd.read_excel('美元中间价.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    usdcny['date'] = usdcny['date'].str.replace('-','')
    usdcny = usdcny[usdcny['date']>='20110901']
    ####################################################
    "中债企业债到期收益率(AA):1个月    日频"     #buy 后官网下载
    "中债国开债到期收益率:10年    日频"      #buy 后官网下载
    cnbond = pd.read_excel('中债.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    cnbond['date'] = cnbond['date'].map(lambda x:x.strftime('%Y%m%d'))
    cnbond = cnbond[cnbond['date']>='20110901']
    ####################################################
    wind_data = pd.read_excel('881001.WI-行情走势.xlsx',engine='openpyxl',dtype={'code':'str'})[['交易日期','收盘价','涨跌幅(%)']].rename(
        columns={'收盘价':'wind_alla','交易日期':'date','涨跌幅(%)':'wind_alla_rate'}) 
    wind_data['date'] = wind_data['date'].str.replace('-','')
    "wind全A前一个月收益率    日频"   #wind官网下载
    wind_alla = wind_data[['date','wind_alla']][wind_data['date']>='20120101'].copy()
    ####################################################
    "wind全A 120日滚动波动率    日频"   #wind全A计算所得  使用涨跌幅计算波动率
    wind_alla_bdl = wind_data[['date','wind_alla_rate','wind_alla']].copy()
    for index,row in wind_alla_bdl[wind_alla_bdl['date']>='20120101'].iterrows():
        wind_alla_bdl.loc[index,'D120_rate_std'] = wind_alla_bdl[index:index+120]['wind_alla_rate'].std(ddof=0)
        wind_alla_bdl.loc[index,'D120_std'] = wind_alla_bdl[index:index+120]['wind_alla'].std(ddof=0)
    
    # wind_alla_bdl = wind_alla_bdl[['date','D120_rate_std']][wind_alla_bdl['date']>='20120101'].copy()    #二选一  每日涨跌幅的波动率
    wind_alla_bdl = wind_alla_bdl[['date','D120_std']][wind_alla_bdl['date']>='20120101'].copy()         #二选一  每日收盘价的波动率
    ####################################################
    "A股指数数据"
    hs300 = ak.stock_zh_index_daily_em(symbol="{}".format(index_bs)).sort_values('date',ascending=0).reset_index(drop=True)[['date','close']]   #作为模块时    
    # hs300 = ak.stock_zh_index_daily_em(symbol="sz399006").sort_values('date',ascending=0).reset_index(drop=True)[['date','close']]   #直接运行时
    hs300['date'] = hs300['date'].str.replace('-','')
    hs300 = hs300[hs300['date']>='20110901']
    
    ################################################################################################################################################################################################################
    ################################################################################################################################################################################################################
    ################################################################################################################################################################################################################
    
    
    "    数据处理   季度 "
    
    
    
    
    ####################################################
    "指数"
    hs300 = time_bs_creative(hs300,bs=['年季','日'])   #增加年，月，日，季度时间标识
    hs300_ym = period_chg(hs300)[['年季','chg_qual']].rename(columns={'chg_qual':'hs300_chg_qual'})
    ####################################################
    "美元中间价"
    usdcny = time_bs_creative(usdcny,bs=['年季','日'])   #增加年，月，日，季度时间标识
    usdcny_ym = period_chg(usdcny)[['年季','chg_old_qual']].rename(columns={'chg_old_qual':'usdcny_chg_qual'})
    ####################################################
    "ppi当月同比"
    ppi_tb = time_bs_creative(ppi_tb,bs=['年季','日'])   #增加年，月，日，季度时间标识
    ppi_tb['预期误差'] = ppi_tb['今值(%)']-ppi_tb['预测值(%)']
    ppi_tb_ym = ppi_tb[['年季','今值(%)','预期误差']].copy()
    ppi_tb_ym['ppi_tb_chg'] = ppi_tb_ym['今值(%)']-ppi_tb_ym['今值(%)'].shift(-1)
    ppi_tb_ym['ppi_error_chg'] = ppi_tb_ym['预期误差']-ppi_tb_ym['预期误差'].shift(-1)
    
    ppi_tb_ym['ppi_tb_qual'] = ppi_tb_ym['ppi_tb_chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    ppi_tb_ym['ppi_error_qual'] = ppi_tb_ym['ppi_error_chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    ppi_tb_ym = ppi_tb_ym[['年季','ppi_tb_qual','ppi_error_qual']].copy()
    ####################################################
    "wind全A前一个月收益率" 
    wind_alla = time_bs_creative(wind_alla,bs=['年季','日'])   #增加年，月，日，季度时间标识
    wind_alla_ym = period_chg(wind_alla)[['年季','chg_old_qual']].rename(columns={'chg_old_qual':'wind_alla_chg_qual'})
    ####################################################
    "wind全A 120日滚动波动率" 
    wind_alla_bdl = time_bs_creative(wind_alla_bdl,bs=['年季','日'])   #增加年，月，日，季度时间标识
    wind_alla_bdl_ym = period_chg(wind_alla_bdl)[['年季','chg_old_qual']].rename(columns={'chg_old_qual':'wind_alla_bdl_chg_qual'})
    ####################################################
    "官方制造业PMI"
    pmi = time_bs_creative(pmi,bs=['年季','日'])   #增加年，月，日，季度时间标识
    pmi_ym = period_chg(pmi)[['年季','chg_old_qual']].rename(columns={'chg_old_qual':'pmi_chg_qual'})
   
    ####################################################
    "财新PMI"
    cx_pmi = time_bs_creative(cx_pmi,bs=['年季','日']) 
    cx_pmi_ym = period_chg(cx_pmi)[['年季','chg_old_qual']].rename(columns={'chg_old_qual':'cx_pmi_chg_qual'})
    
    ####################################################
    "CFETS人民币汇率指数"
    cfets_index = time_bs_creative(cfets_index,bs=['年季','日'])   #增加年，月，日，季度时间标识
    cfets_index_ym = period_chg(cfets_index)[['年季','chg_old_qual']].rename(columns={'chg_old_qual':'cfets_chg_qual'})
    ####################################################
    "中债企业债到期收益率(AA):1个月" 
    "中债国开债到期收益率:10年" 
    cnbond = time_bs_creative(cnbond,bs=['年季','日']) 
    cbcb_ym = period_chg(cnbond[['date','cbcb','年季','日']].copy())[['年季','chg_old_qual']].rename(columns={'chg_old_qual':'cbcb_chg_qual'})
    csid_ym = period_chg(cnbond[['date','csid','年季','日']].copy())[['年季','chg_old_qual']].rename(columns={'chg_old_qual':'csid_chg_qual'})
    
    ################################################################################################################################################################################################################
    ################################################################################################################################################################################################################
    ################################################################################################################################################################################################################
    
    
    "    数据整合    "
    
    dfs = [hs300_ym,pmi_ym,cx_pmi_ym,ppi_tb_ym,cfets_index_ym,usdcny_ym,cbcb_ym,csid_ym,wind_alla_ym,wind_alla_bdl_ym]   # 这里未来是可以输入参数来循环的
    data_all = reduce(lambda x,y:pd.merge(x,y,on='年季',how='left'),dfs)
    
    sfactor_direction = pd.DataFrame([
        ['sfactor1',1],    
        ['sfactor2',1], 
        ['sfactor3',-1], 
        ['sfactor4',-1], 
        ['sfactor5',1], 
        ['sfactor6',-1], 
        ['sfactor7',-1], 
        ['sfactor8',1], 
        ['sfactor9',1], 
        ['sfactor10',-1]
        ],columns=['sfactor','direction'])
    
    
    
    data_all_adjust = data_all.copy()
    for i in range(2,data_all_adjust.shape[1]):  #第一列年月，第二列指数涨跌幅
        data_all_adjust.iloc[:,i] = data_all_adjust.iloc[:,i]*sfactor_direction.iloc[i-2,1]
    
    data_all_adjust['Row_sum'] = data_all_adjust.iloc[:,1:].apply(lambda x: x.sum(), axis=1)
    
    fjd = fjd_n
    data_all_adjust['Row_sum_qual'] = data_all_adjust['Row_sum'].map(lambda x:1 if x>fjd else(-1 if x<fjd else -1))
    
    data_all_adjust['真-预'] = data_all_adjust['hs300_chg_qual']-data_all_adjust['Row_sum_qual']
    
    "1： 去掉23年2月   1："
    data_stat_b = data_all_adjust[1:84].copy()
    data_stat=pd.DataFrame()
    data_stat.loc[0,'无争议正确率%'] = len(data_stat_b[data_stat_b['真-预']==0])/len(data_stat_b)
    data_stat.loc[0,'可控损失正确率%'] = len(data_stat_b[data_stat_b['真-预']>=0])/len(data_stat_b)


    return  data_stat

index_bs_df = pd.DataFrame([
    ['上证指数','sh000001'],
    ['深证成指','sz399001'],
    ['创业板指','sz399006'],
    ['沪深300','sh000300']              
    ],columns=('预测指数名称','预测指数代码'))

data_stat = pd.DataFrame()
for fjd_i in range(-3,7):
    for index,row in index_bs_df.iterrows():
        data_stat_bb = total_function(row['预测指数代码'],fjd_i)
        data_stat_bb['预测指数名称'] = row['预测指数名称']
        data_stat_bb['预测指数代码'] = row['预测指数代码']  
        data_stat = data_stat.append(data_stat_bb)
################################################################################################################################################################################################################
################################################################################################################################################################################################################
################################################################################################################################################################################################################

