# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 14:25:38 2023

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
def time_bs_creative(df,ori_time='date',bs=['年','月','日','季度','年月']):
    "将输入的df中的日期字段 如 20230101 添加一些时间标识，年，月，日，季度"
    df_columns = list(df.columns)    
    df['年'] = df['{}'.format(ori_time)].str.slice(0,4)
    df['月'] = df['{}'.format(ori_time)].str.slice(4,6)
    df['日'] = df['{}'.format(ori_time)].str.slice(6,8)
    df['年月'] = df['{}'.format(ori_time)].str.slice(0,6)
    df['季度'] = df['月'].map(lambda x:'Q1' if x<='03' else('Q2' if x<='06' else ('Q3' if x<='09' else 'Q4')))   
    return df[df_columns+bs]
####################################################
def period_chg(df,timing='15',time_bs='年月'):
    "timing 每个月的 timing日 作为计算的起始周期"
    df_ym = df[['{}'.format(time_bs)]].drop_duplicates().reset_index(drop=True)
    df_columns = list(df.columns)  

    for index,row in df_ym[:].iterrows():
        try:         
            df_ym.loc[index,'time_final'] = df[df['date']<'{}{}'.format(row['{}'.format(time_bs)],timing)].head(1).reset_index(drop=True).loc[0,'{}'.format(df_columns[1])]
        except:
            pass
    df_ym['chg'] = df_ym['time_final'].shift(1) - df_ym['time_final']
    df_ym['chg_old'] = df_ym['chg'].shift(-1)
    # df_ym['chg_old_1'] = df_ym['time_final'] - df_ym['time_final'].shift(-1)
    df_ym['chg_qual'] = df_ym['chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    df_ym['chg_old_qual'] = df_ym['chg_old'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    df_ym['chg_pct'] = df_ym['chg']/df_ym['time_final']
    return df_ym



################################################################################################################################################################################################################
################################################################################################################################################################################################################
################################################################################################################################################################################################################

def total_function(index_bs,fjd_n,bdl_bs,index_bdl_bs,e_or_b):

    
    "    数据获取    "
    
    
    
    
    ####################################################
    "官方制造业PMI   月底 或 月初 公布"  #金10下载
    pmi= pd.read_excel('制造业PMI.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    pmi['date'] = pmi['date'].map(lambda x:(datetime.datetime.strptime('19000101','%Y%m%d')+datetime.timedelta(days=x-2)).strftime('%Y%m%d'))
    pmi = pmi[pmi['date']>='20110901']
    pmi['预测值'] = pmi['预测值'].astype('float64')
    ####################################################
    "财新制造业PMI   月底 或 月初 公布"  # buy   后金10下载
    cx_pmi= pd.read_excel('财新PMI.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    cx_pmi['date'] = cx_pmi['date'].str.replace('-','')
    ####################################################
    "中国规模以上工业增加值年率   15--20日 公布"  #金10下载
    indtr_va= pd.read_excel('规模以上工业增加值.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    indtr_va['date'] = indtr_va['date'].map(lambda x:(datetime.datetime.strptime('19000101','%Y%m%d')+datetime.timedelta(days=x-2)).strftime('%Y%m%d'))
    indtr_va = indtr_va[indtr_va['date']>='20110901']    
    ####################################################
    "PPI 当月同比   前半月 公布"  #金10下载
    "PPI 预期误差   前半月 公布"    #金10下载
    ppi_tb = pd.read_excel('PPI金十.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    ppi_tb['date'] = ppi_tb['日期'].map(lambda x:(datetime.datetime.strptime('19000101','%Y%m%d')+datetime.timedelta(days=x-2)).strftime('%Y%m%d'))
    ppi_tb = ppi_tb[['date','今值(%)','预测值(%)','前值(%)']]
    ppi_tb = ppi_tb[ppi_tb['date']>='20110901']
    ####################################################
    "CPI 当月同比   前半月 公布"  #金10下载
    "CPI 预期误差   前半月 公布"    #金10下载
    cpi_tb = pd.read_excel('CPI金十.xlsx',engine='openpyxl',dtype={'code':'str'}) 
    cpi_tb['date'] = cpi_tb['日期'].map(lambda x:(datetime.datetime.strptime('19000101','%Y%m%d')+datetime.timedelta(days=x-2)).strftime('%Y%m%d'))
    cpi_tb = cpi_tb[['date','今值(%)','预测值(%)','前值(%)']]
    cpi_tb = cpi_tb[cpi_tb['date']>='20110901']
    ####################################################    
    "CRB指数 日频"    #英为财情下载
    crb_tb = pd.read_excel('CRB指数.xlsx',engine='openpyxl',dtype={'code':'str'})  
    crb_tb['date'] = crb_tb['date'].astype('str').str.replace('-','')
    crb_tb = crb_tb[['date','CRB']]
    crb_tb = crb_tb[crb_tb['date']>='20110901']    
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
    "中债国债到期收益率3，5，10年   日频"     #buy 后官网下载
    cn_nation_bond = pd.read_excel('中债国债到期收益率3-5-10年.xlsx',engine='openpyxl',dtype={'code':'str'})[['date','3年','5年','10年']]  #此处可以将3年转变为1年
    cn_nation_bond['date'] = cn_nation_bond['date'].str.replace('-','')
    cn_nation_bond = cn_nation_bond[cn_nation_bond['date']>='20110901']        
    ####################################################
    wind_data = pd.read_excel('881001.WI-行情走势.xlsx',engine='openpyxl',dtype={'code':'str'})[['交易日期','收盘价','涨跌幅(%)']].rename(
        columns={'收盘价':'wind_alla','交易日期':'date','涨跌幅(%)':'wind_alla_rate'}) 
    wind_data['date'] = wind_data['date'].str.replace('-','')
    "wind全A前一个月收益率    日频"   #wind官网下载
    wind_alla = wind_data[['date','wind_alla']][wind_data['date']>='20110901'].copy()
    ####################################################
    "wind全A 120日滚动波动率    日频"   #wind全A计算所得  使用涨跌幅计算波动率
    wind_alla_bdl = wind_data[['date','wind_alla_rate','wind_alla']].copy()
    for index,row in wind_alla_bdl[wind_alla_bdl['date']>='20110901'].iterrows():
        wind_alla_bdl.loc[index,'D120_rate_std'] = wind_alla_bdl[index:index+120]['wind_alla_rate'].std(ddof=0)
        wind_alla_bdl.loc[index,'D120_std'] = wind_alla_bdl[index:index+120]['wind_alla'].std(ddof=0)
    
    if bdl_bs=='收盘价':
        wind_alla_bdl = wind_alla_bdl[['date','D120_std']][wind_alla_bdl['date']>='20110901'].copy()         #二选一  每日收盘价的波动率
    elif bdl_bs=='涨跌幅':
        wind_alla_bdl = wind_alla_bdl[['date','D120_rate_std']][wind_alla_bdl['date']>='20110901'].copy()    #二选一  每日涨跌幅的波动率
    else:
        pass
    
    
    ####################################################
    "A股指数数据"
    
    # hs300 = ak.stock_zh_index_daily_em(symbol="sz399006").sort_values('date',ascending=0).reset_index(drop=True)[['date','close']]   #直接运行时
    hs300 = ak.stock_zh_index_daily_em(symbol="{}".format(index_bs)).sort_values('date',ascending=0).reset_index(drop=True)[['date','close']]   #作为模块时
    hs300['date'] = hs300['date'].str.replace('-','')
    hs300 = hs300[hs300['date']>='20110901']
    
   
    ####################################################
    "A股指数  120日滚动波动率"
    hs300_bdl = hs300.copy()
    hs300_bdl['hs300_rate'] = hs300_bdl['close']/hs300_bdl['close'].shift(-1) - 1
    for index,row in hs300_bdl[hs300_bdl['date']>='20110901'].iterrows():
        hs300_bdl.loc[index,'hs300_D120_rate_std'] = hs300_bdl[index:index+120]['hs300_rate'].std(ddof=0)
        hs300_bdl.loc[index,'hs300_D120_std'] = hs300_bdl[index:index+120]['close'].std(ddof=0)
    
    
    if index_bdl_bs=='收盘价':
        hs300_bdl = hs300_bdl[['date','hs300_D120_std']][hs300_bdl['date']>='20110901'].copy()         #二选一  每日收盘价的波动率
    elif index_bdl_bs=='涨跌幅':
        hs300_bdl = hs300_bdl[['date','hs300_D120_rate_std']][hs300_bdl['date']>='20110901'].copy()    #二选一  每日涨跌幅的波动率
    else:
        pass
    
    
    ####################################################
    "偏股混合型基金指数----作为权益持仓代表   日频"   #ifind
    equity_index = pd.read_excel('885001.WI.xlsx',engine='openpyxl',dtype={'code':'str'})[['date','收盘价']].rename(
        columns={'收盘价':'equity_index'})  
    equity_index['date'] = equity_index['date'].str.replace('-','')
    equity_index = equity_index[['date','equity_index']][equity_index['date']>='20110901'].copy()  
    

    ####################################################
    "中债-新综合指数-------作为固收持仓代表   日频"   
    fixed_income = ak.bond_new_composite_index_cbond(indicator="财富", period="总值").sort_values('date',ascending=0).reset_index(drop=True).rename(
        columns={'value':'fixed_income'})
    fixed_income['date'] = fixed_income['date'].astype('str').str.replace('-','')
    fixed_income = fixed_income[['date','fixed_income']][fixed_income['date']>='20110901'].copy()      
    
    
    
    
    ################################################################################################################################################################################################################
    ################################################################################################################################################################################################################
    ################################################################################################################################################################################################################
    
    
    
    
    
    "    数据处理   month "
    ####################################################    
    "偏股混合型基金指数----作为权益持仓代表   日频"   #ifind
    equity_index = time_bs_creative(equity_index,bs=['年月','日'])   #增加年，月，日，季度时间标识
    equity_index_ym = period_chg(equity_index)[['年月','chg_qual']].rename(columns={'chg_qual':'equity_index_qual'})

    ####################################################   
    "中债-新综合指数-------作为固收持仓代表   日频"  
    fixed_income = time_bs_creative(fixed_income,bs=['年月','日'])   #增加年，月，日，季度时间标识
    fixed_income_ym = period_chg(fixed_income)[['年月','chg_qual']].rename(columns={'chg_qual':'fixed_income_qual'})
    
    ####################################################
    "指数"
    hs300 = time_bs_creative(hs300,bs=['年月','日'])   #增加年，月，日，季度时间标识
    hs300_ym = period_chg(hs300)[['年月','chg_qual']].rename(columns={'chg_qual':'hs300_chg_qual'})
    hs300_old_ym = period_chg(hs300)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'hs300_old_chg_qual'})
    ####################################################
    "美元中间价"
    usdcny = time_bs_creative(usdcny,bs=['年月','日'])   #增加年，月，日，季度时间标识
    usdcny_ym = period_chg(usdcny)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'usdcny_chg_qual'})
    ####################################################
    "ppi当月同比"
    ppi_tb = time_bs_creative(ppi_tb,bs=['年月','日'])   #增加年，月，日，季度时间标识
    ppi_tb['预期误差'] = ppi_tb['今值(%)']-ppi_tb['预测值(%)']
    ppi_ym1 = period_chg(ppi_tb[['date','今值(%)','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'ppi_tb_qual'})
    ppi_ym2 = period_chg(ppi_tb[['date','预期误差','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'ppi_error_qual'})
    ppi_tb_ym=pd.merge(ppi_ym1,ppi_ym2,on='年月')
    
    # ppi_tb_ym = ppi_tb[['年月','今值(%)','预期误差']].copy()
    # ppi_tb_ym['ppi_tb_chg'] = ppi_tb_ym['今值(%)']-ppi_tb_ym['今值(%)'].shift(-1)
    # ppi_tb_ym['ppi_error_chg'] = ppi_tb_ym['预期误差']-ppi_tb_ym['预期误差'].shift(-1)
    
    # ppi_tb_ym['ppi_tb_qual'] = ppi_tb_ym['ppi_tb_chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    # ppi_tb_ym['ppi_error_qual'] = ppi_tb_ym['ppi_error_chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    # ppi_tb_ym = ppi_tb_ym[['年月','ppi_tb_qual','ppi_error_qual']].copy()
    ####################################################    
    "cpi当月同比"
    cpi_tb = time_bs_creative(cpi_tb,bs=['年月','日'])   #增加年，月，日，季度时间标识
    cpi_tb['预期误差'] = cpi_tb['今值(%)']-cpi_tb['预测值(%)']
    cpi_ym1 = period_chg(cpi_tb[['date','今值(%)','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'cpi_tb_qual'})
    cpi_ym2 = period_chg(cpi_tb[['date','预期误差','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'cpi_error_qual'})
    cpi_tb_ym=pd.merge(cpi_ym1,cpi_ym2,on='年月')
    
    # cpi_tb_ym = cpi_tb[['年月','今值(%)','预期误差']].copy()
    # cpi_tb_ym['cpi_tb_chg'] = cpi_tb_ym['今值(%)']-cpi_tb_ym['今值(%)'].shift(-1)
    # cpi_tb_ym['cpi_error_chg'] = cpi_tb_ym['预期误差']-cpi_tb_ym['预期误差'].shift(-1)
    
    # cpi_tb_ym['cpi_tb_qual'] = cpi_tb_ym['cpi_tb_chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    # cpi_tb_ym['cpi_error_qual'] = cpi_tb_ym['cpi_error_chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    # cpi_tb_ym = cpi_tb_ym[['年月','cpi_tb_qual','cpi_error_qual']].copy()
    ####################################################
    "CRB当月同比"
    crb_tb = time_bs_creative(crb_tb,bs=['年月','日']) 
    crb_tb_ym = period_chg(crb_tb)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'crb_tb_qual'})
    
    ####################################################
    "wind全A前一个月收益率" 
    wind_alla = time_bs_creative(wind_alla,bs=['年月','日'])   #增加年，月，日，季度时间标识
    wind_alla_ym = period_chg(wind_alla)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'wind_alla_chg_qual'})
    ####################################################
    "wind全A 120日滚动波动率" 
    wind_alla_bdl = time_bs_creative(wind_alla_bdl,bs=['年月','日'])   #增加年，月，日，季度时间标识
    wind_alla_bdl_ym = period_chg(wind_alla_bdl)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'wind_alla_bdl_chg_qual'})
    
    ####################################################
    "A股指数  120日滚动波动率" 
    hs300_bdl = time_bs_creative(hs300_bdl,bs=['年月','日'])   #增加年，月，日，季度时间标识
    hs300_bdl_ym = period_chg(hs300_bdl)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'hs300_bdl_chg_qual'})
    ####################################################    
    "官方制造业PMI"
    pmi = time_bs_creative(pmi,bs=['年月','日'])   #增加年，月，日，季度时间标识
    pmi['预期误差'] = pmi['pmi'] - pmi['预测值'] 
    for index,row in pmi.iterrows():
        if row['日']>='15':
            pmi.loc[index,'年月'] = (datetime.datetime.strptime(row['date'],'%Y%m%d')+relativedelta(months=+1)).strftime('%Y%m')
        else:
            pass
    pmi_ym1 = period_chg(pmi[['date','pmi','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'pmi_chg_qual'})
    pmi_ym2 = period_chg(pmi[['date','预期误差','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'pmi_error_qual'})
    pmi_ym=pd.merge(pmi_ym1,pmi_ym2,on='年月')
    # pmi_ym = pmi[['年月','pmi']].copy()
    # pmi_ym['pmi_chg'] = pmi_ym['pmi']-pmi_ym['pmi'].shift(-1)
    # pmi_ym = pmi_ym[pmi_ym['年月']>='201201']
    # pmi_ym['pmi_chg_qual'] = pmi_ym['pmi_chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    # pmi_ym = pmi_ym[['年月','pmi_chg_qual']].copy()
    ####################################################
    "财新PMI"
    cx_pmi = time_bs_creative(cx_pmi,bs=['年月','日'])      
    for index,row in cx_pmi.iterrows():
        if row['日']>='15':
            cx_pmi.loc[index,'年月'] = (datetime.datetime.strptime(row['date'],'%Y%m%d')+relativedelta(months=+1)).strftime('%Y%m')
        else:
            pass
    cx_pmi_ym = period_chg(cx_pmi)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'cx_pmi_chg_qual'})
    
    # cx_pmi_ym = cx_pmi[['年月','cx_pmi']].copy()
    # cx_pmi_ym['cx_pmi_chg'] = cx_pmi_ym['cx_pmi']-cx_pmi_ym['cx_pmi'].shift(-1)
    # cx_pmi_ym = cx_pmi_ym[cx_pmi_ym['年月']>='201201']
    # cx_pmi_ym['cx_pmi_chg_qual'] = cx_pmi_ym['cx_pmi_chg'].map(lambda x:1 if x>0 else(-1 if x<0 else 0))
    # cx_pmi_ym = cx_pmi_ym[['年月','cx_pmi_chg_qual']].copy()
    ####################################################
    "中国规模以上工业增加值年率"   
    indtr_va = time_bs_creative(indtr_va,bs=['年月','日']) 
    indtr_va['预期误差'] = indtr_va['今值(%)']-indtr_va['预测值(%)']  
    
    indtr_ym1 = period_chg(indtr_va[['date','今值(%)','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'indtr_tb_qual'})
    indtr_ym2 = period_chg(indtr_va[['date','预期误差','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'indtr_error_qual'})
    indtr_va_ym=pd.merge(indtr_ym1,indtr_ym2,on='年月')      
    
    
    # for index,row in indtr_va.iterrows():
    #     if row['日']>='15':
    #         indtr_va.loc[index,'年月'] = (datetime.datetime.strptime(row['date'],'%Y%m%d')+relativedelta(months=+1)).strftime('%Y%m')
    #     else:
    #         pass
    # indtr_va_ym = period_chg(indtr_va)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'indtr_va_chg_qual'}) 
    
    ####################################################
    "CFETS人民币汇率指数"
    cfets_index = time_bs_creative(cfets_index,bs=['年月','日'])   #增加年，月，日，季度时间标识
    cfets_index_ym = period_chg(cfets_index)[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'cfets_chg_qual'})
    ####################################################
    "中债企业债到期收益率(AA):1个月" 
    "中债国开债到期收益率:10年" 
    cnbond = time_bs_creative(cnbond,bs=['年月','日']) 
    cbcb_ym = period_chg(cnbond[['date','cbcb','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'cbcb_chg_qual'})
    csid_ym = period_chg(cnbond[['date','csid','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'csid_chg_qual'})
    
    
    ####################################################
    "中债国债到期收益率3，5，10年   日频"
    cn_nation_bond = time_bs_creative(cn_nation_bond,bs=['年月','日']) 
    cn_nation_bond_ym1 = period_chg(cn_nation_bond[['date','3年','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'cnnb_3y_qual'})
    cn_nation_bond_ym2 = period_chg(cn_nation_bond[['date','5年','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'cnnb_5y_qual'})
    cn_nation_bond_ym3 = period_chg(cn_nation_bond[['date','10年','年月','日']].copy())[['年月','chg_old_qual']].rename(columns={'chg_old_qual':'cnnb_10y_qual'})
    cn_nation_bond_ym=pd.merge(cn_nation_bond_ym1,cn_nation_bond_ym2,on='年月')    
    cn_nation_bond_ym=pd.merge(cn_nation_bond_ym,cn_nation_bond_ym3,on='年月')    

    
    
    ################################################################################################################################################################################################################
    ################################################################################################################################################################################################################
    ################################################################################################################################################################################################################
    
    
    "    数据整合    "#    hs300_old_ym     hs300_bdl_ym        wind_alla_ym    wind_alla_bdl_ym
    ################################################################################
    if e_or_b=='equity':
        "权益"
        dfs = [hs300_ym,pmi_ym[['年月','pmi_chg_qual']],cx_pmi_ym,ppi_tb_ym[['年月','ppi_error_qual']],cpi_tb_ym[['年月','cpi_tb_qual']]
                    ,cfets_index_ym,usdcny_ym,cbcb_ym,csid_ym,hs300_old_ym,hs300_bdl_ym]     # 权益部分
          
        data_all = reduce(lambda x,y:pd.merge(x,y,on='年月',how='left'),dfs)
        data_all = data_all.fillna(method='bfill')
    
        
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
            
        data_all_adjust['Row_sum'] = data_all_adjust.iloc[:,2:].apply(lambda x: x.sum(), axis=1)
        
        # 一期动量
        # data_all_adjust['Row_sum'] = data_all_adjust['Row_sum']+data_all_adjust['hs300_chg_qual'].shift(-1)  
        #三期动量
        # data_all_adjust['Row_sum'] = data_all_adjust['Row_sum']+data_all_adjust['hs300_chg_qual'].shift(-1)+data_all_adjust['hs300_chg_qual'].shift(-2)+data_all_adjust['hs300_chg_qual'].shift(-3)
    
        fjd = fjd_n
        data_all_adjust['Row_sum_qual'] = data_all_adjust['Row_sum'].map(lambda x:1 if x>fjd else(-1 if x<fjd else -1))
        
        data_all_adjust['真-预'] = data_all_adjust['hs300_chg_qual']-data_all_adjust['Row_sum_qual']
        
        "1： 去掉23年2月   1："
        data_stat_b = data_all_adjust[(data_all_adjust['年月']<='202301')&(data_all_adjust['年月']>='201601')].copy()
        data_stat=pd.DataFrame()
        data_stat.loc[0,'无争议正确率%'] = len(data_stat_b[data_stat_b['真-预']==0])/len(data_stat_b)
        data_stat.loc[0,'可控损失正确率%'] = len(data_stat_b[data_stat_b['真-预']>=0])/len(data_stat_b)
        data_stat.loc[0,'fjd'] = fjd_n
        data_stat.loc[0,'winda波动率'] = bdl_bs
        data_stat.loc[0,'指数波动率'] = index_bdl_bs    
  
    ################################################################################
    elif e_or_b=='fixedincome':
        "固收"    
        dfs = [fixed_income_ym,pmi_ym,indtr_va_ym[['年月','indtr_error_qual']],crb_tb_ym,cpi_tb_ym[['年月','cpi_tb_qual']]
                   ,cfets_index_ym,usdcny_ym,cn_nation_bond_ym,wind_alla_ym,wind_alla_bdl_ym]     # 债券部分     
        
        data_all = reduce(lambda x,y:pd.merge(x,y,on='年月',how='left'),dfs)
        data_all = data_all.fillna(method='bfill')    
        
        sfactor_direction = pd.DataFrame([
            ['sfactor1',-1],    
            ['sfactor2',-1], 
            ['sfactor3',-1], 
            ['sfactor4',-1], 
            ['sfactor5',-1], 
            ['sfactor6',1], 
            ['sfactor7',-1], 
            ['sfactor8',-1], 
            ['sfactor9',-1], 
            ['sfactor10',-1], 
            ['sfactor11',-1], 
            ['sfactor12',1]
            ],columns=['sfactor','direction'])   
        
        data_all_adjust = data_all.copy()   
        for i in range(2,data_all_adjust.shape[1]):  #第一列年月，第二列指数涨跌幅
            data_all_adjust.iloc[:,i] = data_all_adjust.iloc[:,i]*sfactor_direction.iloc[i-2,1]
            
        data_all_adjust['Row_sum'] = data_all_adjust.iloc[:,2:].apply(lambda x: x.sum(), axis=1)
        
        # 一期动量
        # data_all_adjust['Row_sum'] = data_all_adjust['Row_sum']+data_all_adjust['hs300_chg_qual'].shift(-1)  
        #三期动量
        # data_all_adjust['Row_sum'] = data_all_adjust['Row_sum']+data_all_adjust['hs300_chg_qual'].shift(-1)+data_all_adjust['hs300_chg_qual'].shift(-2)+data_all_adjust['hs300_chg_qual'].shift(-3)
    
        fjd = fjd_n
        data_all_adjust['Row_sum_qual'] = data_all_adjust['Row_sum'].map(lambda x:1 if x>fjd else(-1 if x<fjd else -1))
        
        data_all_adjust['真-预'] = data_all_adjust['fixed_income_qual']-data_all_adjust['Row_sum_qual']
        
        "1： 去掉23年2月   1："
        data_stat_b = data_all_adjust[(data_all_adjust['年月']<='202301')&(data_all_adjust['年月']>='201601')].copy()
        data_stat=pd.DataFrame()
        data_stat.loc[0,'无争议正确率%'] = len(data_stat_b[data_stat_b['真-预']==0])/len(data_stat_b)
        data_stat.loc[0,'可控损失正确率%'] = len(data_stat_b[data_stat_b['真-预']>=0])/len(data_stat_b)
        data_stat.loc[0,'fjd'] = fjd_n
        data_stat.loc[0,'winda波动率'] = bdl_bs
        data_stat.loc[0,'指数波动率'] = index_bdl_bs 
        
        ################################################################################    
    else:
        pass

    
    return data_stat,data_stat_b




index_bs_df = pd.DataFrame([
    ['上证指数','sh000001'],
    ['深证成指','sz399001'],
    ['创业板指','sz399006'],
    ['沪深300','sh000300'],
    ['中证800','sh000906'],
    ['中证1000','sh000852']              
    ],columns=('预测指数名称','预测指数代码'))




# '''权益部分,可单独运行'''

# data_stat = pd.DataFrame()
# for index_bdl_bs in ['收盘价','涨跌幅']:
#     for bdl_bs in ['收盘价']:
#         for fjd_i in range(-3,7):
#             for index,row in index_bs_df.iterrows():
#                 data_stat_bb = total_function(row['预测指数代码'],fjd_i,bdl_bs,index_bdl_bs,'equity')[0]
#                 data_stat_bb['预测指数名称'] = row['预测指数名称']
#                 data_stat_bb['预测指数代码'] = row['预测指数代码']  
#                 data_stat = data_stat.append(data_stat_bb)
   
                
   
# "同时刻"                
# ################################################################################################################################################################################################################
# ################################################################################################################################################################################################################
# ################################################################################################################################################################################################################

# '''债券部分，可单独运行'''

# data_stat = pd.DataFrame()
# for index_bdl_bs in ['收盘价']:         #指数 使用哪个
#     for bdl_bs in ['收盘价','涨跌幅']:   #winda使用哪个
#         for fjd_i in range(-12,12):
#             for index,row in index_bs_df[0:1].iterrows():   #所要预测的是债券，当只是使用winda作为风险情绪的时候，不用循环具体的指数
#                 data_stat_bb = total_function(row['预测指数代码'],fjd_i,bdl_bs,index_bdl_bs,'fixedincome')[0]
#                 data_stat_bb['预测指数名称'] = row['预测指数名称']
#                 data_stat_bb['预测指数代码'] = row['预测指数代码']  
#                 data_stat = data_stat.append(data_stat_bb)



################################################################################################################################################################################################################
################################################################################################################################################################################################################
################################################################################################################################################################################################################

'''equity_fixedincome 部分  ，可单独运行'''

 #指数 使用哪个  index_bdl_bs
  #winda使用哪个   bdl_bs
  
e_weight = 50
delta = 20

adj_final = pd.DataFrame()
adj_y = pd.DataFrame()
for f_fjd in range(-10,11):
    e_adj_stat,e_adj = total_function('sz399006',1,'收盘价','收盘价','equity')
    e_adj = e_adj[['年月','Row_sum_qual']].rename(columns={'Row_sum_qual':'e_Row_sum_qual'}) 
    f_adj_stat,f_adj = total_function('sz399006',f_fjd,'收盘价','收盘价','fixedincome')
    f_adj = f_adj[['年月','Row_sum_qual']].rename(columns={'Row_sum_qual':'f_Row_sum_qual'}) 
    adj = pd.merge(e_adj,f_adj,on='年月')
    
    
    
    "中债-新综合指数-------作为固收持仓代表   日频"   
    f_data = ak.bond_new_composite_index_cbond(indicator="财富", period="总值").sort_values('date',ascending=0).reset_index(drop=True).rename(
        columns={'value':'f_data'})
    f_data['date'] = f_data['date'].astype('str').str.replace('-','')
    f_data = f_data[['date','f_data']][f_data['date']>='20110901'].copy()  
    f_data = time_bs_creative(f_data,bs=['年月','日'])   #增加年，月，日，季度时间标识
    f_data_ym = period_chg(f_data)[['年月','chg_pct']].rename(columns={'chg_pct':'f_chg_pct'}) 
    
    
    "偏股混合型基金指数----作为权益持仓代表   日频"   #ifind
    e_data = pd.read_excel('885001.WI.xlsx',engine='openpyxl',dtype={'code':'str'})[['date','收盘价']].rename(
        columns={'收盘价':'e_data'})  
    e_data['date'] = e_data['date'].str.replace('-','')
    e_data = e_data[['date','e_data']][e_data['date']>='20110901'].copy()  
    e_data = time_bs_creative(e_data,bs=['年月','日'])   #增加年，月，日，季度时间标识
    e_data_ym = period_chg(e_data)[['年月','chg_pct']].rename(columns={'chg_pct':'e_chg_pct'}) 
    
    adj = pd.merge(adj,e_data_ym,on='年月')
    adj = pd.merge(adj,f_data_ym,on='年月')
    
    adj['portfolio'] = 0
    adj['case'] = ''
    for index,row in adj.iterrows():
        if row['e_Row_sum_qual']+row['f_Row_sum_qual']==2:
            adj.loc[index,'portfolio'] = (e_weight/100)*row['e_chg_pct']+((100-e_weight)/100)*row['f_chg_pct']
            adj.loc[index,'case'] = '{}_{}_00'.format(e_weight,(100-e_weight))
        elif row['e_Row_sum_qual']+row['f_Row_sum_qual']==-2:     
            adj.loc[index,'portfolio'] = 0.4*row['e_chg_pct']+0.4*row['f_chg_pct']+0.2*0.0012  #0.0012是货币基金万份收益0.6  *20/10000 =0.0012
            adj.loc[index,'case'] = '40_40_20'
        elif (row['e_Row_sum_qual']==1)&(row['f_Row_sum_qual']==-1):
            adj.loc[index,'portfolio'] = ((e_weight+delta)/100)*row['e_chg_pct']+((100-e_weight-delta)/100)*row['f_chg_pct']
            adj.loc[index,'case'] = '{}_{}_00'.format(e_weight,(100-e_weight))
        elif (row['e_Row_sum_qual']==-1)&(row['f_Row_sum_qual']==1):
            adj.loc[index,'portfolio'] = ((e_weight-delta)/100)*row['e_chg_pct']+((100-e_weight+delta)/100)*row['f_chg_pct']
            adj.loc[index,'case'] = '{}_{}_00'.format((e_weight-delta),(100-e_weight+delta))
        else:
            pass
    
    adj['fixed_60_40'] = 0.6*adj['e_chg_pct']+0.4*adj['f_chg_pct']
    
    
    adj['年'] = adj['年月'].str.slice(0,4) 
    adj_y_b = adj.groupby('年').agg('sum')
    adj_y_b['e_weight_delta'] = '{}_{}'.format(e_weight,delta)
    adj_y_b['f_fjd'] = f_fjd
    adj_y = adj_y.append(adj_y_b)
        
    
    adj_final_b = pd.DataFrame(adj[['portfolio','fixed_60_40','e_chg_pct']].sum()).T
    adj_final_b['e_weight_delta'] = '{}_{}'.format(e_weight,delta)
    adj_final_b['f_fjd'] = f_fjd 
    adj_final_b['year_alpha_num'] = '{} —— {}'.format(len(adj_y_b[adj_y_b['portfolio']>=adj_y_b['fixed_60_40']]),len(adj_y_b))
    #滚动一年的计算
    for index,row in adj.iterrows():
        if adj.loc[index:index+11,'portfolio'].sum()>=adj.loc[index:index+11,'fixed_60_40'].sum():
            adj.loc[index,'last_year_alpha_qual'] = 1
            adj.loc[index,'last_year_alpha'] = adj.loc[index:index+11,'portfolio'].sum() - adj.loc[index:index+11,'fixed_60_40'].sum()
        else:
            adj.loc[index,'last_year_alpha_qual'] = 0
            adj.loc[index,'last_year_alpha'] = adj.loc[index:index+11,'portfolio'].sum() - adj.loc[index:index+11,'fixed_60_40'].sum()
            
        
        if row['年月'] == '201612':
            break
        else:
            pass
    adj_final_b['roll_last_year_alpha_qual'] = "{} —— {}".format(adj['last_year_alpha_qual'].sum(),len(adj[(adj['last_year_alpha_qual']==0)|(adj['last_year_alpha_qual']==1)]))  
    adj_final_b['roll_last_year_alpha_avg'] = adj[(adj['last_year_alpha_qual']==0)|(adj['last_year_alpha_qual']==1)]['last_year_alpha'].mean()
        
        
    adj_final = adj_final.append(adj_final_b)
    
    






























