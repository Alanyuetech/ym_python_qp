# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 15:10:00 2021

@author: Administrator
"""

"国内基金 与  股指期货   对冲比率   研究"
import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt

"主力连续合约历史数据"
IF0_data = ak.futures_main_sina(symbol="IF0").sort_values(by='日期',ascending=0).reset_index(drop=True).rename(columns={'收盘价':'IF0'})
IH0_data = ak.futures_main_sina(symbol="IH0").sort_values(by='日期',ascending=0).reset_index(drop=True).rename(columns={'收盘价':'IH0'})
IC0_data = ak.futures_main_sina(symbol="IC0").sort_values(by='日期',ascending=0).reset_index(drop=True).rename(columns={'收盘价':'IC0'})


"测试数据"
tt = '001643'  #样例
fund_data = ak.fund_em_open_fund_info(fund=tt, indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True).rename(columns={'净值日期':'日期'})
fund_data['日期'] = fund_data['日期'].astype(str)

ans = pd.merge(left=IF0_data[['日期','IF0']],right=IH0_data[['日期','IH0']],on='日期')
ans = pd.merge(left=ans,right=IC0_data[['日期','IC0']],on='日期')
ans = pd.merge(left=ans,right=fund_data[['日期','累计净值']],on='日期')


ans = pd.merge(left=IF0_data[['日期','IF0']],right=fund_data[['日期','累计净值']],on='日期')

"方式1"
y = ans[['累计净值']]
x = ans[['IF0']]    #  'IF0','IH0','IC0'
x = sm.add_constant(x)
model = sm.OLS(y,x).fit()
predictions = model.predict(x)
print_model = model.summary()

print(print_model)

"方式2"
model = ols('累计净值~IF0+IH0+IC0',data=ans).fit()
model.summary()
print(model.summary())



"画图"
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

predicts = model.predict() # 模型的预测值
plt.scatter(ans[['IF0']], y, label='实际值') # 散点图
plt.scatter(ans[['IH0']], y, label='实际值') # 散点图
plt.scatter(ans[['IC0']], y, label='实际值') # 散点图
plt.plot(x, predicts, color = 'black', label='预测值')
plt.legend() # 显示图例，即每条线对应 label 中的内容
plt.show() # 显示图形








"国内指数"  "国内数据需要pac模式"
hs300_data = ak.stock_zh_index_daily_em(symbol="sh000300").sort_values(by='date',ascending=0).reset_index(drop=True)
hs300_data = hs300_data[['date','close']].rename(columns={'date':'日期','close':'沪深300收盘'})
hs300_data['指数增长率'] = hs300_data['沪深300收盘']/hs300_data['沪深300收盘'].shift(-1) -1

"信托持仓"  
cc_data =  pd.read_excel('信托持仓20210824.xlsx',dtype={'基金代码':'str'})
"基金代码前面补0"
cc_data['基金代码'] = cc_data['基金代码'].map(lambda x:'00000'+x if len(x)==1 else
                                  ('0000'+x if len(x)==2 else 
                                   ('000'+x if len(x)==3 else
                                    ('00'+x if len(x)==4 else
                                     ('0'+x if len(x)==5 else x)))))

beta_df = pd.DataFrame(columns={'基金代码','基金名称','beta_value'})
for i in range(0,len(cc_data)):
    locals()['data_'+str(cc_data.loc[i,'基金代码'])] = ak.fund_em_open_fund_info(fund=cc_data.loc[i,'基金代码'], indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True).rename(columns={'净值日期':'日期'})
    locals()['data_'+str(cc_data.loc[i,'基金代码'])]['累计净值'] = locals()['data_'+str(cc_data.loc[i,'基金代码'])]['累计净值'].astype(float)
    locals()['data_'+str(cc_data.loc[i,'基金代码'])]['日增长率'] = locals()['data_'+str(cc_data.loc[i,'基金代码'])]['累计净值']/locals()['data_'+str(cc_data.loc[i,'基金代码'])]['累计净值'].shift(-1) -1
    locals()['data_'+str(cc_data.loc[i,'基金代码'])]['日期'] = locals()['data_'+str(cc_data.loc[i,'基金代码'])]['日期'].astype(str)
    locals()['data_index_'+str(cc_data.loc[i,'基金代码'])] = pd.merge(left=locals()['data_'+str(cc_data.loc[i,'基金代码'])][['日期','日增长率']],right=hs300_data[['日期','指数增长率']],on='日期')
    locals()['data_index_'+str(cc_data.loc[i,'基金代码'])] = locals()['data_index_'+str(cc_data.loc[i,'基金代码'])].dropna(axis=0,how='any')
    cov_hs300_fund = np.cov(locals()['data_index_'+str(cc_data.loc[i,'基金代码'])]['指数增长率'] ,locals()['data_index_'+str(cc_data.loc[i,'基金代码'])]['日增长率'] )
    cov_hs300_fund = pd.DataFrame(cov_hs300_fund)
    beta_value = cov_hs300_fund.loc[0,1]/cov_hs300_fund.loc[0,0]   
    data_by = pd.DataFrame([[str(cc_data.loc[i,'基金代码']),str(cc_data.loc[i,'基金名称']),beta_value]]).rename(columns={0:'基金代码',1:'基金名称',2:'beta_value'})
    beta_df = beta_df.append(data_by)
beta_df = beta_df.reset_index(drop=True)
beta_df = pd.merge(left=beta_df,right=cc_data[['基金代码','比例']],on='基金代码')

beta_cc = sum(beta_df['比例'] * beta_df['beta_value'])













# "内盘历史行情数据"
# IF0_data = ak.get_futures_daily(start_date="20200818", end_date="20210818", market="CFFEX")
# IF0_data = IF0_data[IF0_data['variety']=='IF']






























