# -*- coding: utf-8 -*-
"""
Created on Fri Jul 29 15:06:01 2022

@author: Administrator
"""

"宏观数据分析择时"

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



#########################################################################################################################################################
"数据准备-----宏观数据"
###############"经济状况"###############

"GDP"
gdp = pd.DataFrame(ak.macro_usa_gdp_monthly()).reset_index().rename(columns={'index':'日期'})
gdp['日期'] = gdp['日期'].astype('str').str.slice(0,10)


###############"物价水平"###############

"CPI月率"
cpi_m = pd.DataFrame(ak.macro_usa_cpi_monthly()).reset_index().rename(columns={'index':'日期'})
cpi_m['日期'] = cpi_m['日期'].astype('str').str.slice(0,10)


"核心CPI月率"
cpi_m_core = pd.DataFrame(ak.macro_usa_core_cpi_monthly()).reset_index().rename(columns={'index':'日期'})
cpi_m_core['日期'] = cpi_m_core['日期'].astype('str').str.slice(0,10)


"个人支出月率"
per_spending_m = pd.DataFrame(ak.macro_usa_personal_spending()).reset_index().rename(columns={'index':'日期'})
per_spending_m['日期'] = per_spending_m['日期'].astype('str').str.slice(0,10)


"零售销售月率"
retail_sales_m = pd.DataFrame(ak.macro_usa_retail_sales()).reset_index().rename(columns={'index':'日期'})
retail_sales_m['日期'] = retail_sales_m['日期'].astype('str').str.slice(0,10)


"进口物价指数"
import_price = pd.DataFrame(ak.macro_usa_import_price()).reset_index().rename(columns={'index':'日期'})
import_price['日期'] = import_price['日期'].astype('str').str.slice(0,10)


"出口价格指数"
export_price = pd.DataFrame(ak.macro_usa_export_price()).reset_index().rename(columns={'index':'日期'})
export_price['日期'] = export_price['日期'].astype('str').str.slice(0,10)


"美国核心PCE物价指数年率报告"
core_pce_price = pd.DataFrame(ak.macro_usa_core_pce_price()).reset_index().rename(columns={'index':'日期'})
core_pce_price['日期'] = core_pce_price['日期'].astype('str').str.slice(0,10)


"美国实际个人消费支出季率初值报告"
real_consumer_spending = pd.DataFrame(ak.macro_usa_real_consumer_spending()).reset_index().rename(columns={'index':'日期'})
real_consumer_spending['日期'] = real_consumer_spending['日期'].astype('str').str.slice(0,10)

###############"劳动力市场"###############

"LMCI指数"
lmci = pd.DataFrame(ak.macro_usa_lmci()).reset_index().rename(columns={'index':'日期'})
lmci['日期'] = lmci['日期'].astype('str').str.slice(0,10)


"美国失业率报告"
unemployment_rate = pd.DataFrame(ak.macro_usa_unemployment_rate()).reset_index().rename(columns={'index':'日期'})
unemployment_rate['日期'] = unemployment_rate['日期'].astype('str').str.slice(0,10)


"美国挑战者企业裁员人数报告"
job_cuts = pd.DataFrame(ak.macro_usa_job_cuts()).reset_index().rename(columns={'index':'日期'})
job_cuts['日期'] = job_cuts['日期'].astype('str').str.slice(0,10)


"美国非农就业人数报告"
non_farm = pd.DataFrame(ak.macro_usa_non_farm()).reset_index().rename(columns={'index':'日期'})
non_farm['日期'] = non_farm['日期'].astype('str').str.slice(0,10)


"美国ADP就业人数报告"
adp_employment = pd.DataFrame(ak.macro_usa_adp_employment()).reset_index().rename(columns={'index':'日期'})
adp_employment['日期'] = adp_employment['日期'].astype('str').str.slice(0,10)


"美国初请失业金人数报告"
initial_jobless = pd.DataFrame(ak.macro_usa_initial_jobless()).reset_index().rename(columns={'index':'日期'})
initial_jobless['日期'] = initial_jobless['日期'].astype('str').str.slice(0,10)

###############"贸易状况"###############

"美国贸易帐报告"
trade_balance = pd.DataFrame(ak.macro_usa_trade_balance()).reset_index().rename(columns={'index':'日期'})
trade_balance['日期'] = trade_balance['日期'].astype('str').str.slice(0,10)


"美国经常帐报告"
current_account = pd.DataFrame(ak.macro_usa_current_account()).reset_index().rename(columns={'index':'日期'})
current_account['日期'] = current_account['日期'].astype('str').str.slice(0,10)

###############"产业指标"###############
######"制造业"######

"贝克休斯钻井报告"
rig_count = pd.DataFrame(ak.macro_usa_rig_count()).reset_index().rename(columns={'index':'日期'})
rig_count['日期'] = rig_count['日期'].astype('str').str.slice(0,10)


"美国生产者物价指数(PPI)报告"
ppi = pd.DataFrame(ak.macro_usa_ppi()).reset_index().rename(columns={'index':'日期'})
ppi['日期'] = ppi['日期'].astype('str').str.slice(0,10)


"美国核心生产者物价指数(PPI)报告"
core_ppi = pd.DataFrame(ak.macro_usa_core_ppi()).reset_index().rename(columns={'index':'日期'})
core_ppi['日期'] = core_ppi['日期'].astype('str').str.slice(0,10)


"美国API原油库存报告"
api_crude_stock = pd.DataFrame(ak.macro_usa_api_crude_stock()).reset_index().rename(columns={'index':'日期'})
api_crude_stock['日期'] = api_crude_stock['日期'].astype('str').str.slice(0,10)


"美国Markit制造业PMI初值报告"
pmi = pd.DataFrame(ak.macro_usa_pmi()).reset_index().rename(columns={'index':'日期'})
pmi['日期'] = pmi['日期'].astype('str').str.slice(0,10)


"美国ISM制造业PMI报告"
ism_pmi = pd.DataFrame(ak.macro_usa_ism_pmi()).reset_index().rename(columns={'index':'日期'})
ism_pmi['日期'] = ism_pmi['日期'].astype('str').str.slice(0,10)


######"工业"######


"美国工业产出月率报告"
industrial_production_m = pd.DataFrame(ak.macro_usa_industrial_production()).reset_index().rename(columns={'index':'日期'})
industrial_production_m['日期'] = industrial_production_m['日期'].astype('str').str.slice(0,10)


"美国耐用品订单月率报告"
durable_goods_orders_m = pd.DataFrame(ak.macro_usa_durable_goods_orders()).reset_index().rename(columns={'index':'日期'})
durable_goods_orders_m['日期'] = durable_goods_orders_m['日期'].astype('str').str.slice(0,10)


"美国工厂订单月率报告"
factory_orders_m = pd.DataFrame(ak.macro_usa_factory_orders()).reset_index().rename(columns={'index':'日期'})
factory_orders_m['日期'] = factory_orders_m['日期'].astype('str').str.slice(0,10)

######"服务业"######


"美国Markit服务业PMI初值报告"
services_pmi = pd.DataFrame(ak.macro_usa_services_pmi()).reset_index().rename(columns={'index':'日期'})
services_pmi['日期'] = services_pmi['日期'].astype('str').str.slice(0,10)


"美国商业库存月率报告"
business_inventories_m = pd.DataFrame(ak.macro_usa_business_inventories()).reset_index().rename(columns={'index':'日期'})
business_inventories_m['日期'] = business_inventories_m['日期'].astype('str').str.slice(0,10)


"美国ISM非制造业PMI报告"
ism_non_pmi = pd.DataFrame(ak.macro_usa_ism_non_pmi()).reset_index().rename(columns={'index':'日期'})
ism_non_pmi['日期'] = ism_non_pmi['日期'].astype('str').str.slice(0,10)


######"房地产"######


"美国NAHB房产市场指数报告"
nahb_house_market_index = pd.DataFrame(ak.macro_usa_nahb_house_market_index()).reset_index().rename(columns={'index':'日期'})
nahb_house_market_index['日期'] = nahb_house_market_index['日期'].astype('str').str.slice(0,10)


"美国新屋开工总数年化报告"
house_starts = pd.DataFrame(ak.macro_usa_house_starts()).reset_index().rename(columns={'index':'日期'})
house_starts['日期'] = house_starts['日期'].astype('str').str.slice(0,10)


"美国新屋销售总数年化报告"
new_home_sales = pd.DataFrame(ak.macro_usa_new_home_sales()).reset_index().rename(columns={'index':'日期'})
new_home_sales['日期'] = new_home_sales['日期'].astype('str').str.slice(0,10)


"美国营建许可总数报告"
building_permits = pd.DataFrame(ak.macro_usa_building_permits()).reset_index().rename(columns={'index':'日期'})
building_permits['日期'] = building_permits['日期'].astype('str').str.slice(0,10)


"美国成屋销售总数年化报告"
exist_home_sales = pd.DataFrame(ak.macro_usa_exist_home_sales()).reset_index().rename(columns={'index':'日期'})
exist_home_sales['日期'] = exist_home_sales['日期'].astype('str').str.slice(0,10)


"美国FHFA房价指数月率报告"
house_price_index_m = pd.DataFrame(ak.macro_usa_house_price_index()).reset_index().rename(columns={'index':'日期'})
house_price_index_m['日期'] = house_price_index_m['日期'].astype('str').str.slice(0,10)


"美国S&P/CS20座大城市房价指数年率报告"
spcs20 = pd.DataFrame(ak.macro_usa_spcs20()).reset_index().rename(columns={'index':'日期'})
spcs20['日期'] = spcs20['日期'].astype('str').str.slice(0,10)


"美国成屋签约销售指数月率报告"
pending_home_sales_m = pd.DataFrame(ak.macro_usa_pending_home_sales()).reset_index().rename(columns={'index':'日期'})
pending_home_sales_m['日期'] = pending_home_sales_m['日期'].astype('str').str.slice(0,10)


######"领先指标"######


"未决房屋销售月率"
phs_m = pd.DataFrame(ak.macro_usa_phs()).reset_index().rename(columns={'index':'日期'})
phs_m['日期'] = phs_m['日期'].astype('str').str.slice(0,10)


"美国谘商会消费者信心指数报告"
cb_consumer_confidence = pd.DataFrame(ak.macro_usa_cb_consumer_confidence()).reset_index().rename(columns={'index':'日期'})
cb_consumer_confidence['日期'] = cb_consumer_confidence['日期'].astype('str').str.slice(0,10)


"美国NFIB小型企业信心指数报告"
nfib_small_business = pd.DataFrame(ak.macro_usa_nfib_small_business()).reset_index().rename(columns={'index':'日期'})
nfib_small_business['日期'] = nfib_small_business['日期'].astype('str').str.slice(0,10)


"美国密歇根大学消费者信心指数初值报告"
michigan_consumer_sentiment = pd.DataFrame(ak.macro_usa_michigan_consumer_sentiment()).reset_index().rename(columns={'index':'日期'})
michigan_consumer_sentiment['日期'] = michigan_consumer_sentiment['日期'].astype('str').str.slice(0,10)

######"汇率"######


"美元指数"
usd_index = ak.index_investing_global(area="美国", symbol="美元指数", period="每月",
                                                      start_date="20050101", end_date=date_work)[['日期','收盘']].rename(columns={'收盘':'usd_index'})
usd_index['日期'] = usd_index['日期'].astype('str').str.slice(0,10)



"欧元美元"
eur_usd = ak.currency_hist(symbol="usd-jpy",period="每日", start_date="20050101", end_date="20220808").reset_index()[['日期','收盘']].rename(columns={'收盘':'eur_usd'})
eur_usd['日期'] = eur_usd['日期'].astype('str').str.slice(0,10)

######"利率"######
"美国2年期国债收益率"
t_notes = ak.bond_investing_global(country="美国", index_name="美国2年期国债", period="每月", start_date="20000101", end_date=date_work).reset_index()
t_notes['日期'] = t_notes['日期'].astype('str').str.slice(0,10)


"美国10年期国债收益率"
t_bonds = ak.bond_investing_global(country="美国", index_name="美国10年期国债", period="每月", start_date="20000101", end_date=date_work).reset_index()
t_bonds['日期'] = t_bonds['日期'].astype('str').str.slice(0,10)

######"其他"######


"美国EIA原油库存报告"
eia_crude_rate = pd.DataFrame(ak.macro_usa_eia_crude_rate()).reset_index().rename(columns={'index':'日期'})
eia_crude_rate['日期'] = eia_crude_rate['日期'].astype('str').str.slice(0,10)


"美国原油产量报告"
crude_inner = pd.DataFrame(ak.macro_usa_crude_inner()).reset_index().rename(columns={'index':'日期'})
crude_inner['日期'] = crude_inner['日期'].astype('str').str.slice(0,10)

######"风险情绪"######
"恐慌指数"
vix_index = ak.index_investing_global(area="美国", symbol="VIX恐慌指数", period="每月", start_date="20000101", end_date=date_work)
vix_index['日期'] = vix_index['日期'].astype('str')




#########################################################################################################################################################
'''
大类因子          小类因子            影响方向

经济状况            GDP                   1
经济状况         制造业PMI                1
通货膨胀       核心PCE物价指数            -1 
通货膨胀      生产者物价指数(PPI)         -1
汇率             美元指数                 1
汇率             欧元美元                 -1
利率          两年期国债收益率            -1
利率          十年期国债收益率            1
风险情绪         美股指数                 1
风险情绪          VIX指数                 -1

'''


"构建择时指标库"
timing_indivators = pd.DataFrame([['经济状况','GDP',1],
                                  ['经济状况','制造业PMI',1],
                                  ['通货膨胀','核心PCE物价指数',-1],
                                  ['通货膨胀','生产者物价指数(PPI)',-1],
                                  ['汇率','美元指数',1],
                                  ['汇率','欧元美元',-1],
                                  ['利率','两年期国债收益率',-1],
                                  ['利率','十年期国债收益率',1],
                                  ['风险情绪','美股指数',1],
                                  ['风险情绪','VIX指数',-1]
                                
                                  ],columns=('大类因子','小类因子','影响方向'))


"GDP"
gdp = pd.DataFrame(ak.macro_usa_gdp_monthly()).reset_index().rename(columns={'index':'日期'})
gdp['日期'] = gdp['日期'].astype('str').str.slice(0,10)

gdp['gdp月变'] = gdp['gdp'] - gdp['gdp'].shift(1)
gdp['gdp月变方向'] = gdp['gdp月变'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
gdp['月份'] = gdp['日期'].map(lambda x:str(x[:4])+str(x[5:7]))
gdp = gdp.dropna(axis=0,how='any')
gdp = gdp[['月份','gdp月变方向']].copy()

# gdp.to_excel('gdp月变方向{}.xlsx'.format(date_work))




"美国Markit制造业PMI初值报告"
pmi = pd.DataFrame(ak.macro_usa_pmi()).reset_index().rename(columns={'index':'日期'})
pmi['日期'] = pmi['日期'].astype('str').str.slice(0,10)

pmi['月份'] = pmi['日期'].map(lambda x:str(x[:4])+str(x[5:7]))
pmi = pmi.groupby('月份').head(1)
pmi['usa_pmi月变'] = (pmi['usa_pmi'] - pmi['usa_pmi'].shift(1)).shift(-1)
# pmi[['月份','usa_pmi月变']] = pmi[['月份','usa_pmi月变']].shift(1)       #打开后会  当月数据所用的发布时间可能在下个月
pmi['usa_pmi月变方向'] = pmi['usa_pmi月变'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
pmi = pmi[['日期','月份','usa_pmi月变方向']].copy()
pmi = pmi.dropna(axis=0,how='any')
# pmi.to_excel('pmi月变方向{}.xlsx'.format(date_work))




"美国核心PCE物价指数年率报告"
core_pce_price = pd.DataFrame(ak.macro_usa_core_pce_price()).reset_index().rename(columns={'index':'日期'})
core_pce_price['日期'] = core_pce_price['日期'].astype('str').str.slice(0,10)


core_pce_price['月份'] = core_pce_price['日期'].map(lambda x:str(x[:4])+str(x[5:7]))
core_pce_price['后月份'] = core_pce_price['月份'].shift(-1)
core_pce_price['月份异常'] = core_pce_price.apply(lambda x:1 if (x['月份']==x['后月份']) else 0,axis=1)
core_pce_price['月份'] = core_pce_price.apply(lambda x:str(int(x['月份'])-1) if (x['月份异常']==1) else x['月份'],axis=1)
core_pce_price['月份异常'] = core_pce_price.apply(lambda x:1 if (x['月份']==x['后月份']) else 0,axis=1)   #确认没有异常月份


core_pce_price['core_pce_price月变'] =  (core_pce_price['core_pce_price'] - core_pce_price['core_pce_price'].shift(1))
core_pce_price['core_pce_price月变方向'] = core_pce_price['core_pce_price月变'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
core_pce_price = core_pce_price[['日期','月份','core_pce_price月变方向']].copy()
core_pce_price = core_pce_price.dropna(axis=0,how='any')

# core_pce_price.to_excel('core_pce_price月变方向{}.xlsx'.format(date_work))


"美国生产者物价指数(PPI)报告"
ppi = pd.DataFrame(ak.macro_usa_ppi()).reset_index().rename(columns={'index':'日期'})
ppi['日期'] = ppi['日期'].astype('str').str.slice(0,10)

ppi['月份'] = ppi['日期'].map(lambda x:str(x[:4])+str(x[5:7]))
ppi['usa_ppi月变'] =  (ppi['usa_ppi'] - ppi['usa_ppi'].shift(1))
ppi['usa_ppi月变方向'] = ppi['usa_ppi月变'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
ppi = ppi[['日期','月份','usa_ppi月变方向']].copy()
ppi = ppi.dropna(axis=0,how='any')

# ppi.to_excel('ppi月变方向{}.xlsx'.format(date_work))

# "美元指数"
# usd_index = ak.index_investing_global(area="美国", symbol="美元指数", period="每月",
#                                                       start_date="20000101", end_date=date_work)


"investing上直接下载"
# usd_index =  pd.read_csv('美元指数历史数据日.csv')  
usd_index_m =  pd.read_csv('美元指数历史数据月.csv')  
usd_index_m['涨跌幅_b'] = usd_index_m['涨跌幅'].str.replace('%','').astype('float')
usd_index_m['usd_index月变方向'] = usd_index_m['涨跌幅_b'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
usd_index_m['月份'] = usd_index_m['日期'].map(lambda x:x[:4]+x[5:7] if len(x)==11 else x[:4]+'0'+x[5:6] )
"欧元美元"
# eur_usd = ak.currency_hist(symbol="eur-usd", start_date="20050101", end_date="20200117")


"investing上直接下载"
# eur_usd =  pd.read_csv('EUR_USD历史数据.csv')  
eur_usd_m =  pd.read_csv('EUR_USD历史数据月.csv')  

eur_usd_m['涨跌幅_b'] = eur_usd_m['涨跌幅'].str.replace('%','').astype('float')
eur_usd_m['eur_usd月变方向'] = eur_usd_m['涨跌幅_b'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
eur_usd_m['月份'] = eur_usd_m['日期'].map(lambda x:x[:4]+x[5:7] if len(x)==11 else x[:4]+'0'+x[5:6] )


"美国2年期国债收益率"
t_notes = ak.bond_investing_global(country="美国", index_name="美国2年期国债", period="每月", start_date="20060101", end_date=date_work).reset_index()
t_notes['日期'] = t_notes['日期'].astype('str').str.slice(0,10)
t_notes['t_notes月变方向'] = t_notes['涨跌幅'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
t_notes['月份'] = t_notes['日期'].str.replace('-','').str.slice(0,6)

"美国10年期国债收益率"
t_bonds = ak.bond_investing_global(country="美国", index_name="美国10年期国债", period="每月", start_date="20060101", end_date=date_work).reset_index()
t_bonds['日期'] = t_bonds['日期'].astype('str').str.slice(0,10)
t_bonds['t_bonds月变方向'] = t_bonds['涨跌幅'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
t_bonds['月份'] = t_bonds['日期'].str.replace('-','').str.slice(0,6)

"美股指数"

# sp500_index = ak.index_investing_global(area="美国", symbol="标普500指数", 
#                                       period="每月", start_date="20110101", end_date=date_work)
"investing上直接下载"
sp500_index =  pd.read_csv('美国标准普尔500指数历史数据月.csv')  


sp500_index['涨跌幅_b'] = sp500_index['涨跌幅'].str.replace('%','').astype('float')
sp500_index['sp500月变方向'] = sp500_index['涨跌幅_b'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
sp500_index['月份'] = sp500_index['日期'].map(lambda x:x[:4]+x[5:7] if len(x)==11 else x[:4]+'0'+x[5:6] )
"VIX指数"
vix_index =  pd.read_csv('VIX恐慌指数历史数据月.csv') 


vix_index['涨跌幅_b'] = vix_index['涨跌幅'].str.replace('%','').astype('float')
vix_index['vix月变方向'] = vix_index['涨跌幅_b'].map(lambda x: 1 if(x>0) else (-1 if x<0 else 0))
vix_index['月份'] = vix_index['日期'].map(lambda x:x[:4]+x[5:7] if len(x)==11 else x[:4]+'0'+x[5:6] )

"merge"
merge_data = pd.merge(gdp,pmi[['月份','usa_pmi月变方向']],on='月份',how='inner')
merge_data = pd.merge(merge_data,core_pce_price[['月份','core_pce_price月变方向']],on='月份',how='inner')
merge_data = pd.merge(merge_data,ppi[['月份','usa_ppi月变方向']],on='月份',how='inner')
merge_data = pd.merge(merge_data,usd_index_m[['月份','usd_index月变方向']],on='月份',how='inner')
merge_data = pd.merge(merge_data,eur_usd_m[['月份','eur_usd月变方向']],on='月份',how='inner')
merge_data = pd.merge(merge_data,t_notes[['月份','t_notes月变方向']],on='月份',how='inner')
merge_data = pd.merge(merge_data,t_bonds[['月份','t_bonds月变方向']],on='月份',how='inner')
merge_data = pd.merge(merge_data,sp500_index[['月份','sp500月变方向']],on='月份',how='inner')
merge_data = pd.merge(merge_data,vix_index[['月份','vix月变方向']],on='月份',how='inner')


"merge*影响方向"
for i in range(1,merge_data.shape[1]):
    merge_data.iloc[:,i] = merge_data.iloc[:,i]*timing_indivators.loc[i-1,"影响方向"]
    














