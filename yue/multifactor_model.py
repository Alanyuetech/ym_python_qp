# -*- coding: utf-8 -*-
"""
Created on Thu May  5 15:07:02 2022

@author: 666
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
import statsmodels.api as sm
import yfinance as yf

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




#################################################################################################################################

"数据准备"

"开全局模式"
# aa = ak.stock_us_fundamental(symbol="info")



"股票名单"
stock_list = pd.read_excel('美股200亿以上筛选.xlsx',engine='openpyxl')
stock_list = stock_list.rename(columns={'代码':'stock_id'})

"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_list = pd.merge(stock_list,us_stock[['代码','stock_id']],how='left',on='stock_id')


stock_list.drop(stock_list[pd.isna(stock_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
stock_list = stock_list.reset_index(drop=True)

# stock_list = stock_list.loc[:9,:]
"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20110101", end_date="22220101", adjust="")  #这里使用不复权的数据
    stock_data_b['代码']=row['代码']
    stock_data_b['stock_id'] = row['stock_id']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])

stock_data['日期'] =  stock_data['日期'].apply(lambda x:int(x[0:4]+x[5:7]+x[8:]))
print('股票数据完成')


#################################################################################################################################
'''
以3因子作为模板，作为多因子模型搭建的基础框架以及思路引导（包括但不限于：）
fama-french三因子模型
1:选取每个季度的200亿以上股票的数据~~~大约300~400只股票进行参数回归
2：因子公式：E[Ri] - Rf = beta*(E[Rm]-Rf) + smb*E[RSMB] + hml*E[RHML]
    对beta 、beta_smb 、beta_hml 三个参数进行回归
    E[Ri]：单个股票 or 股票组合的收益率
    E[RSMB]：规模因子收益率
    E[RHML]：价值因子收益率
    SMB: B组 市值前50%     S组 市值后50%
    HML：H组 账面市值比大于70%分位数    L组 账面市值比大于30%分位数 小于70%分位数     M组 账面市值比小于30%分位数  
    SMB = (SH+SM+SL)/3 - (BH+BM+BL)/3
    HML = (SH+BH)/2 - (SL+BL)/2
    
3:账面市值比=1/PB=bvps/price    市值=收盘价*成交量/换手率

'''

#################################################################################################################################
"市值"
stock_data['市值_亿'] = (100*stock_data['收盘']*stock_data['成交量']/stock_data['换手率'])/100000000

#################################################################################################################################

"账面市值比"    #全局模式

pb_data = pd.DataFrame()




# stock_list = pb_erro.copy()   #记得重新跑stock_list
pb_erro = pd.DataFrame()


for index,row in stock_list.iterrows():     #如果 pb_erro  有内容，将stock_list变成 pb_erro 重新更新一下。
    try:
        pb_data_b = ak.stock_us_fundamental(stock='{}'.format(row['stock_id']), symbol="PB")
        pb_data_b = pb_data_b[pb_data_b['date']>='2011-01-01']
        pb_data_b['代码']=row['代码']
        pb_data_b['stock_id'] = row['stock_id']
        pb_data = pb_data.append(pb_data_b)
        print(index,row['stock_id'])
    except:
        pb_erro = pb_erro.append(stock_list.loc[index,:])
        print(index,row['stock_id'],'错误')  





pb_data['date'] =  pb_data['date'].apply(lambda x:int(x[0:4]+x[5:7]+x[8:]))  
pb_data  = pb_data.rename(columns={'date':'日期'})                
print('PB数据完成')


final_data = pd.merge(stock_data[['日期','代码','stock_id','收盘','涨跌幅','市值_亿']],pb_data[['日期','代码','stock_id','book_value_per_share']],how='left',on=['日期','代码','stock_id'])
final_data['bvps'] = final_data.groupby('stock_id')['book_value_per_share'].fillna(method='ffill') 

final_data['bvps'] = final_data['bvps'].astype('str')
final_data = final_data[final_data['bvps']!='nan']

final_data['bvps'] = final_data['bvps'].astype('str').str.replace('$','').astype('str').str.replace(',','').astype('float')
final_data['账面市值比'] = final_data['bvps']/final_data['收盘']

#################################################################################################################################

"市值分组"

"去掉市值为无穷大的"
final_data = final_data[final_data['市值_亿']!=float("inf")]


mv_label = final_data[['日期','市值_亿']].groupby(['日期']).quantile(.50).reset_index().rename(columns={'市值_亿':'市值分组标签'})
final_data=pd.merge(final_data,mv_label,how='left',on='日期')
final_data['市值分组'] = final_data.apply(lambda x:"S" if x['市值_亿']<=x['市值分组标签'] else "B",axis=1)




#################################################################################################################################

"BM分组"

bm_label_7 = final_data[['日期','账面市值比']].groupby(['日期']).quantile(.70).reset_index().rename(columns={'账面市值比':'BM分组标签7'})
bm_label_3 = final_data[['日期','账面市值比']].groupby(['日期']).quantile(.30).reset_index().rename(columns={'账面市值比':'BM分组标签3'})
final_data=pd.merge(final_data,bm_label_7,how='left',on='日期')
final_data=pd.merge(final_data,bm_label_3,how='left',on='日期')
final_data['BM分组'] = final_data.apply(lambda x:"H" if x['账面市值比']>x['BM分组标签7'] else ("L" if x['账面市值比']<x['BM分组标签3'] else "M"),axis=1)


#################################################################################################################################
"构建SMB   HML因子"
smb_hml = final_data.groupby(['日期','市值分组','BM分组']).agg({'涨跌幅':'mean'}).reset_index()
smb_data = smb_hml.groupby(['日期','市值分组']).agg({'涨跌幅':'mean'}).reset_index()
hml_data = smb_hml.groupby(['日期','BM分组']).agg({'涨跌幅':'mean'}).reset_index()

smb_s = smb_data[smb_data['市值分组']=='S'].rename(columns={'涨跌幅':'SMB_S'})
smb_b = smb_data[smb_data['市值分组']=='B'].rename(columns={'涨跌幅':'SMB_B'})

hml_h = hml_data[hml_data['BM分组']=='H'].rename(columns={'涨跌幅':'HML_H'})
hml_l = hml_data[hml_data['BM分组']=='L'].rename(columns={'涨跌幅':'HML_L'})

if len(smb_s)!=len(smb_b):
    print('smb_s 和 smb_b 日期数不同')
else:
    smb = pd.merge(smb_s,smb_b,how='inner',on='日期')
    smb['smb'] = smb['SMB_S'] - smb['SMB_B']

if len(hml_h)!=len(hml_l):
    print('hml_h 和 hml_l 日期数不同')
else:
    hml = pd.merge(hml_h,hml_l,how='inner',on='日期')
    hml['hml'] = hml['HML_H'] - hml['HML_L']
    
#################################################################################################################################   
"Rf模块"
bond_us_rate = ak.bond_zh_us_rate()[['日期','美国国债收益率10年']].rename(columns={'美国国债收益率10年':'rf_rate'})  
bond_us_rate = bond_us_rate.fillna(method='ffill')
bond_us_rate['日期'] = bond_us_rate['日期'].astype('str').str.replace('-','').astype('int')
#################################################################################################################################  
"Rm模块"
naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="20110101", end_date="22220101")

naq_index['naq涨跌幅'] = 100* (naq_index['收盘']/naq_index['收盘'].shift(1) - 1)
naq_index['日期'] = naq_index['日期'].astype('str').str.replace('-','').astype('int')


#################################################################################################################################
'''RMW模块、CMA模块 数据准备
        yfinance中拿到 balance sheet 和 earning 的数据
'''

import yfinance as yf

def balance_sheet_earning_data(stock_id):
    # stock_id = 'AAPL'   #用于测试
    ans = pd.DataFrame()  #建立df
    stock = yf.Ticker('{}'.format(stock_id))
    stock_balance_sheet = stock.balance_sheet  
    stock_earnings = stock.earnings.reset_index()
    stock_earnings['Year'] = stock_earnings['Year'].astype('str')
    
    ans = stock_balance_sheet.T[['Total Stockholder Equity','Total Assets']].reset_index().rename(columns={'':'Year'})
    ans['Year'] = ans['Year'].apply(lambda x:x.strftime('%Y%m%d')[:4])
    ans = pd.merge(ans,stock_earnings[['Year','Earnings']],on='Year',how='left')
    ans['stock_id'] = stock_id
    
    return ans

stock_financial_reports = pd.DataFrame()  #建立df
stock_financial_reports_b = pd.DataFrame()  #建立备用df  


financial_erro = pd.DataFrame()  #建立出错df  
for index,row in stock_list.iterrows():   #如果 financial_erro有内容，将stock_list变成financial_erro重新更新一下。
    try:
        stock_financial_reports_b = balance_sheet_earning_data(row['stock_id']).sort_values(['Year'],ascending=[0])  #确保时间是倒序
        stock_financial_reports = stock_financial_reports.append(stock_financial_reports_b)
        print(index,row['stock_id'])
    except:
        financial_erro = financial_erro.append(stock_list.loc[index,:])  #重新跑的时候要改成 financial_erro_1 = financial_erro_1.append(stock_list.loc[index,:])
        print(index,row['stock_id'],'错误')  



#################################################################################################################################
"RMW分组"
roe = stock_financial_reports[['Year','stock_id','Total Stockholder Equity','Earnings']]
roe['roe'] = roe['Total Stockholder Equity']/roe['Earnings']

roe_label_7 = roe[['Year','roe']].groupby(['Year']).quantile(.70).reset_index().rename(columns={'roe':'roe分组标签7'})
roe_label_3 = roe[['Year','roe']].groupby(['Year']).quantile(.30).reset_index().rename(columns={'roe':'roe分组标签3'})
roe=pd.merge(roe,roe_label_7,how='left',on='Year')
roe=pd.merge(roe,roe_label_3,how='left',on='Year')
roe['roe分组'] = roe.apply(lambda x:"H" if x['roe']>x['roe分组标签7'] else ("L" if x['roe']<x['roe分组标签3'] else "M"),axis=1)




#################################################################################################################################
"CMA分组"
assets_change = stock_financial_reports[['Year','stock_id','Total Assets']]
assets_change['last_TotalAssets'] = assets_change.groupby(['stock_id'])['Total Assets'].shift(-1)
assets_change['assets_chg'] = assets_change['Total Assets']/assets_change['last_TotalAssets']-1

assets_chg = assets_change[['Year','stock_id','assets_chg']]


assets_chg_label_7 = assets_chg[['Year','assets_chg']].groupby(['Year']).quantile(.70).reset_index().rename(columns={'assets_chg':'assets_chg分组标签7'})
assets_chg_label_3 = assets_chg[['Year','assets_chg']].groupby(['Year']).quantile(.30).reset_index().rename(columns={'assets_chg':'assets_chg分组标签3'})
assets_chg=pd.merge(assets_chg,assets_chg_label_7,how='left',on='Year')
assets_chg=pd.merge(assets_chg,assets_chg_label_3,how='left',on='Year')
assets_chg['assets_chg分组'] = assets_chg.apply(lambda x:"H" if x['assets_chg']>x['assets_chg分组标签7'] else ("L" if x['assets_chg']<x['assets_chg分组标签3'] else "M"),axis=1)
assets_chg = assets_chg.dropna(axis=0,how='any')   #第一年数据无法计算出，所以第一年没有资产增长率

#################################################################################################################################

"构建RMW因子  CMA因子"
rmw_cma_data = pd.merge(roe[['Year','stock_id','roe分组']],assets_chg[['Year','stock_id','assets_chg分组']]
                        ,on=['Year','stock_id'])  #最近一年如果没有资产增长率，就会缺失时间
final_data['Year'] = final_data['日期'].astype('str').str.slice(0,4)
final_data = pd.merge(final_data,rmw_cma_data,on=['Year','stock_id'])

rmw_cma = final_data.groupby(['日期','roe分组','assets_chg分组']).agg({'涨跌幅':'mean'}).reset_index()
rmw_data = rmw_cma.groupby(['日期','roe分组']).agg({'涨跌幅':'mean'}).reset_index()
cma_data = rmw_cma.groupby(['日期','assets_chg分组']).agg({'涨跌幅':'mean'}).reset_index()

rmw_h = rmw_data[rmw_data['roe分组']=='H'].rename(columns={'涨跌幅':'RMW_H'})
rmw_l = rmw_data[rmw_data['roe分组']=='L'].rename(columns={'涨跌幅':'RMW_L'})

cma_h = cma_data[cma_data['assets_chg分组']=='H'].rename(columns={'涨跌幅':'CMA_H'})
cma_l = cma_data[cma_data['assets_chg分组']=='L'].rename(columns={'涨跌幅':'CMA_L'})



if len(rmw_h)!=len(rmw_l):
    print('rmw_h 和 rmw_l 日期数不同')
else:
    rmw = pd.merge(rmw_h,rmw_l,how='inner',on='日期')
    rmw['rmw'] = rmw['RMW_H'] - rmw['RMW_L']

if len(cma_h)!=len(cma_l):
    print('cma_h 和 cma_l 日期数不同')
else:
    cma = pd.merge(cma_h,cma_l,how='inner',on='日期')
    cma['cma'] = cma['CMA_L'] - cma['CMA_H']

#################################################################################################################################
"merge 数据"  "三因子"
merge_data = final_data[['日期','代码','stock_id','涨跌幅']]
merge_data = pd.merge(merge_data,smb[['日期','smb']],on='日期',how='left')
merge_data = pd.merge(merge_data,hml[['日期','hml']],on='日期',how='left')
merge_data = pd.merge(merge_data,bond_us_rate,on='日期',how='left')
merge_data = merge_data.fillna(method='ffill')   #用前一天的数据填充:Rf
merge_data = pd.merge(merge_data,naq_index[['日期','naq涨跌幅']],on='日期',how='left')  
# merge_data.loc[merge_data[merge_data['naq涨跌幅'].isnull()].index,'naq涨跌幅'] = -1.2   #最近日期的股指数据没有就补充
merge_data['ERi-Rf'] = merge_data['涨跌幅'] - merge_data['rf_rate']
merge_data['ERm-Rf'] = merge_data['naq涨跌幅'] - merge_data['rf_rate']


######
"五因子，加入"
merge_data = pd.merge(merge_data,rmw[['日期','rmw']],on='日期',how='left')
merge_data = pd.merge(merge_data,cma[['日期','cma']],on='日期',how='left')
merge_data = merge_data.dropna(axis=0,how='any')   #第一年数据无法计算出，所以第一年没有资产增长率



# merge_data = merge_data.loc[:100,:]
# merge_data = merge_data[merge_data['日期']>=20150101]
#################################################################################################################################
"三因子参数回归"

datas = merge_data[['ERi-Rf','ERm-Rf','smb','hml']]
y = datas.iloc[:, 0] # 因变量为第 1 列数据
x = datas.iloc[:, 1:4] # 自变量为第 2 列到第 4 列数据
# x = sm.add_constant(x) # 若模型中有截距，必须有这一步
model = sm.OLS(y, x).fit() # 构建最小二乘模型并拟合
print(model.summary()) # 输出回归结果


######


"五因子参数回归"

datas = merge_data[['ERi-Rf','ERm-Rf','smb','hml','rmw','cma']]
y = datas.iloc[:, 0] # 因变量为第 1 列数据
x = datas.iloc[:, 1:6] # 自变量为第 2 列到第 4 列数据
# x = sm.add_constant(x) # 若模型中有截距，必须有这一步
model = sm.OLS(y, x).fit() # 构建最小二乘模型并拟合
print(model.summary()) # 输出回归结果



























