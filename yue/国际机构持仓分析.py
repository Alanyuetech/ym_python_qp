# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 16:20:01 2022

@author: Administrator
"""


"国际机构持仓分析"

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


ins_holdings = pd.read_excel('国际机构持仓明细_part2022q2.xlsx',engine='openpyxl')   
us_stock = pd.read_excel('美股所有股票数据.xlsx',engine='openpyxl')  
ins_holdings = pd.merge(ins_holdings,us_stock[['代码','所属行业']],how='left',on='代码')
cn_stock = pd.read_excel('中概股名单.xlsx',engine='openpyxl')   
ins_stock = pd.read_excel('国际机构股票汇总_all2022q2.xlsx',engine='openpyxl')  



ins_holdings_ana = ins_holdings.groupby(['所属行业']).agg('sum').reset_index()[['所属行业','持仓市值(亿美元)','持仓市值权重']]
ins_holdings_ana = ins_holdings_ana.sort_values('持仓市值(亿美元)',ascending=0)

ins_holdings_ana.to_excel('国际机构持仓行业分析_part{}.xlsx'.format(date_work))


ins_stocks_ana = ins_holdings.groupby(['股票名称','代码']).agg('sum').reset_index()[['股票名称','代码','持仓市值(亿美元)','持仓市值权重']]
ins_stocks_ana = ins_stocks_ana.sort_values('持仓市值(亿美元)',ascending=0)
ins_stocks_ana = pd.merge(ins_stocks_ana,us_stock[['代码','所属行业']],how='left',on='代码')[['代码','股票名称','所属行业','持仓市值(亿美元)','持仓市值权重']]
ins_stocks_ana = pd.merge(ins_stocks_ana,ins_holdings[['股票名称','行业']].drop_duplicates(),how='left',on='股票名称')
ins_stocks_ana['所属行业'] = ins_stocks_ana.apply(lambda x:x['行业'] if pd.isna(x['所属行业']) else x['所属行业'],axis=1)
ins_stocks_ana = ins_stocks_ana[['代码','股票名称','所属行业','持仓市值(亿美元)','持仓市值权重']]


ins_stocks_ana.to_excel('国际机构持仓股票分析_part{}.xlsx'.format(date_work))



ins_holdings_cn = pd.merge(ins_holdings,cn_stock[['代码','是否中概股']],how='inner',on='代码')
ins_holdings_cn_ins = ins_holdings_cn.groupby(['机构名称']).agg('sum').reset_index()[['机构名称','持仓市值(亿美元)','持仓市值权重']].sort_values('持仓市值(亿美元)',ascending=0)
ins_holdings_cn_ind = ins_holdings_cn.groupby(['所属行业']).agg('sum').reset_index()[['所属行业','持仓市值(亿美元)','持仓市值权重']].sort_values('持仓市值(亿美元)',ascending=0)
ins_holdings_cn_sto = ins_holdings_cn.groupby(['股票名称']).agg('sum').reset_index()[['股票名称','持仓市值(亿美元)','持仓市值权重']].sort_values('持仓市值(亿美元)',ascending=0)

ins_holdings_cn_ins.to_excel('国际机构持仓中概股机构分析_part{}.xlsx'.format(date_work))
ins_holdings_cn_ind.to_excel('国际机构持仓中概股行业分析_part{}.xlsx'.format(date_work))
ins_holdings_cn_sto.to_excel('国际机构持仓中概股股票分析_part{}.xlsx'.format(date_work))



ins_stock = pd.merge(ins_stock,us_stock[['代码','所属行业']],how='left',on='代码')
ins_stock['所属行业'] = ins_stock.apply(lambda x:x['行业'] if pd.isna(x['所属行业']) else x['所属行业'],axis=1)

ins_stock['机构持仓比例'] = ins_stock['机构持仓比例'].replace('--',np.nan).astype('float')
ins_stock_ana1 = ins_stock.groupby('所属行业').agg('sum').reset_index()[['所属行业','持仓市值(亿美元)']]
ins_stock_ana2 = ins_stock.groupby('所属行业').agg('mean').reset_index()[['所属行业','机构持仓比例']]
ins_stock_ana = pd.merge(ins_stock_ana1,ins_stock_ana2,on='所属行业').rename(columns={'持仓市值(亿美元)':'持仓市值(亿美元)汇总','机构持仓比例':'机构持仓比例平均'})
ins_stock_ana = ins_stock_ana.sort_values('持仓市值(亿美元)汇总',ascending=0).reset_index(drop=True)
ins_stock_ana.to_excel('国际机构持仓股票行业分析_all{}.xlsx'.format(date_work))




"两个季度对比——持仓明细"

ins_holdings_q = pd.read_excel('国际机构持仓明细_part2022q1.xlsx',engine='openpyxl') 
ins_holdings_q = pd.merge(ins_holdings_q,us_stock[['代码','所属行业']],how='left',on='代码')
ins_holdings_q_ana = ins_holdings_q.groupby(['所属行业']).agg('sum').reset_index()[['所属行业','持仓市值(亿美元)','持仓市值权重']]
ins_holdings_q_ana = ins_holdings_q_ana.sort_values('持仓市值(亿美元)',ascending=0).rename(columns={'持仓市值(亿美元)':'前持仓市值(亿美元)','持仓市值权重':'前持仓市值权重'})


ins_holdings_ana_chg = pd.merge(ins_holdings_ana,ins_holdings_q_ana,on='所属行业')
ins_holdings_ana_chg['持仓市值(亿美元)_chg%'] = 100*(ins_holdings_ana_chg['持仓市值(亿美元)']/ins_holdings_ana_chg['前持仓市值(亿美元)'] - 1)
ins_holdings_ana_chg['持仓市值权重_chg%'] = 100*(ins_holdings_ana_chg['持仓市值权重']/ins_holdings_ana_chg['前持仓市值权重'] - 1)
ins_holdings_ana_chg = ins_holdings_ana_chg.sort_values('持仓市值(亿美元)',ascending=0)

ins_holdings_ana_chg.to_excel('国际机构持仓行业对比_part{}.xlsx'.format(date_work))




"两个季度对比——股票"


ins_stocks_q_ana = ins_holdings_q.groupby(['股票名称','代码']).agg('sum').reset_index()[['股票名称','代码','持仓市值(亿美元)','持仓市值权重']]
ins_stocks_q_ana = ins_stocks_q_ana.sort_values('持仓市值(亿美元)',ascending=0)
ins_stocks_q_ana = pd.merge(ins_stocks_q_ana,us_stock[['代码','所属行业']],how='left',on='代码')[['代码','股票名称','所属行业','持仓市值(亿美元)','持仓市值权重']]
ins_stocks_q_ana = pd.merge(ins_stocks_q_ana,ins_holdings[['股票名称','行业']].drop_duplicates(),how='left',on='股票名称')
ins_stocks_q_ana['所属行业'] = ins_stocks_q_ana.apply(lambda x:x['行业'] if pd.isna(x['所属行业']) else x['所属行业'],axis=1)
ins_stocks_q_ana = ins_stocks_q_ana[['代码','股票名称','所属行业','持仓市值(亿美元)','持仓市值权重']].rename(columns={'持仓市值(亿美元)':'前持仓市值(亿美元)','持仓市值权重':'前持仓市值权重'})




ins_stocks_ana_chg = pd.merge(ins_stocks_ana,ins_stocks_q_ana[['代码','前持仓市值(亿美元)','前持仓市值权重']],on='代码')
ins_stocks_ana_chg['持仓市值(亿美元)_chg%'] = 100*(ins_stocks_ana_chg['持仓市值(亿美元)']/ins_stocks_ana_chg['前持仓市值(亿美元)'] - 1)
ins_stocks_ana_chg['持仓市值权重_chg%'] = 100*(ins_stocks_ana_chg['持仓市值权重']/ins_stocks_ana_chg['前持仓市值权重'] - 1)
ins_stocks_ana_chg = ins_stocks_ana_chg.sort_values('持仓市值(亿美元)',ascending=0)

ins_stocks_ana_chg.to_excel('国际机构持仓股票对比_part{}.xlsx'.format(date_work))


"两个季度对比——中概股"

ins_holdings_q_cn = pd.merge(ins_holdings_q,cn_stock[['代码','是否中概股']],how='inner',on='代码')

ins_holdings_q_cn_ins = ins_holdings_q_cn.groupby(['机构名称']).agg('sum').reset_index()[['机构名称','持仓市值(亿美元)','持仓市值权重']].sort_values('持仓市值(亿美元)',ascending=0).rename(columns={'持仓市值(亿美元)':'前持仓市值(亿美元)','持仓市值权重':'前持仓市值权重'})
ins_holdings_q_cn_ind = ins_holdings_q_cn.groupby(['所属行业']).agg('sum').reset_index()[['所属行业','持仓市值(亿美元)','持仓市值权重']].sort_values('持仓市值(亿美元)',ascending=0).rename(columns={'持仓市值(亿美元)':'前持仓市值(亿美元)','持仓市值权重':'前持仓市值权重'})
ins_holdings_q_cn_sto = ins_holdings_q_cn.groupby(['股票名称']).agg('sum').reset_index()[['股票名称','持仓市值(亿美元)','持仓市值权重']].sort_values('持仓市值(亿美元)',ascending=0).rename(columns={'持仓市值(亿美元)':'前持仓市值(亿美元)','持仓市值权重':'前持仓市值权重'})


ins_holdings_q_cn_ins_chg = pd.merge(ins_holdings_cn_ins,ins_holdings_q_cn_ins,how='inner',on='机构名称')
ins_holdings_q_cn_ind_chg = pd.merge(ins_holdings_cn_ind,ins_holdings_q_cn_ind,how='inner',on='所属行业')
ins_holdings_q_cn_sto_chg = pd.merge(ins_holdings_cn_sto,ins_holdings_q_cn_sto,how='inner',on='股票名称')


ins_holdings_q_cn_ins_chg['持仓市值(亿美元)_chg%'] = 100*(ins_holdings_q_cn_ins_chg['持仓市值(亿美元)']/ins_holdings_q_cn_ins_chg['前持仓市值(亿美元)'] - 1)
ins_holdings_q_cn_ind_chg['持仓市值(亿美元)_chg%'] = 100*(ins_holdings_q_cn_ind_chg['持仓市值(亿美元)']/ins_holdings_q_cn_ind_chg['前持仓市值(亿美元)'] - 1)
ins_holdings_q_cn_sto_chg['持仓市值(亿美元)_chg%'] = 100*(ins_holdings_q_cn_sto_chg['持仓市值(亿美元)']/ins_holdings_q_cn_sto_chg['前持仓市值(亿美元)'] - 1)

ins_holdings_q_cn_ins_chg['持仓市值权重_chg%'] = 100*(ins_holdings_q_cn_ins_chg['持仓市值权重']/ins_holdings_q_cn_ins_chg['前持仓市值权重'] - 1)
ins_holdings_q_cn_ind_chg['持仓市值权重_chg%'] = 100*(ins_holdings_q_cn_ind_chg['持仓市值权重']/ins_holdings_q_cn_ind_chg['前持仓市值权重'] - 1)
ins_holdings_q_cn_sto_chg['持仓市值权重_chg%'] = 100*(ins_holdings_q_cn_sto_chg['持仓市值权重']/ins_holdings_q_cn_sto_chg['前持仓市值权重'] - 1)

ins_holdings_q_cn_ins_chg.to_excel('国际机构持仓中概股机构对比_part{}.xlsx'.format(date_work))
ins_holdings_q_cn_ind_chg.to_excel('国际机构持仓中概股行业对比_part{}.xlsx'.format(date_work))
ins_holdings_q_cn_sto_chg.to_excel('国际机构持仓中概股股票对比_part{}.xlsx'.format(date_work))
















