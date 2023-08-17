# -*- coding: utf-8 -*-
"""
Created on Thu Sep 23 13:56:57 2021

@author: Administrator
"""

import akshare as ak
import pandas as pd
import datetime
now_day = datetime.datetime.now().strftime('%Y%m%d')
from datetime import *
def getLastWeekDay(day=datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - timedelta(days=dayStep)
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y%m%d')


"基金代码前面补0"
def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:'00000'+x if len(x)==1 else
                                      ('0000'+x if len(x)==2 else 
                                       ('000'+x if len(x)==3 else
                                        ('00'+x if len(x)==4 else
                                         ('0'+x if len(x)==5 else x)))))
    return fund_id


#########################################################################################################




fund_em_fund_name_df = ak.fund_name_em()
fund_id = fund_em_fund_name_df[['基金代码']]

ans_fund_hold = pd.DataFrame()

year_n = 2023
month_n = 1





fund_id = fund_id_erro.copy()  #第一次从头跑不需要
fund_id = fund_id.rename(columns={1:'基金代码'})



id_num = 0
fund_id_erro = pd.DataFrame()
for id in fund_id.loc[0:,'基金代码']:
    try:
        fund_hold = ak.fund_portfolio_hold_em(symbol="{}".format(id), date="{}".format(year_n))
        
        fund_hold = fund_hold[fund_hold['季度']=='{}年{}季度股票投资明细'.format(year_n,month_n)]       #  这个位置需要变动
        
        fund_hold['基金代码'] = id
        ans_fund_hold = ans_fund_hold.append(fund_hold)
        print(id_num,id)
        id_num += 1
    except:       
        fund_id_erro = fund_id_erro.append(pd.DataFrame([[id_num,id]]))
        print(id_num,'{}  错误'.format(id))
        id_num += 1
        continue   



ans_fund_hold[:].to_excel('基金持仓岳_{}Q{}_{}.xlsx'.format(year_n,month_n,date_work))
fund_id_erro.to_excel('基金持仓岳_{}Q{}_报错代码_{}.xlsx'.format(year_n,month_n,date_work))








##########################################################################################
"将基金持仓横过来"
#直接读取
# ans_fund_hold = pd.read_excel('基金持仓岳_2021Q3_20211026.xlsx',dtype={'基金代码':'str'})[['股票名称','占净值比例','持股数','持仓市值','基金代码']]

ans_fund_hold = pd.read_excel('基金持仓岳_2022Q3_{}.xlsx'.format(date_work),engine='openpyxl',dtype={'基金代码':'str'})[['股票名称','占净值比例','持股数','持仓市值','基金代码']]
ans_fund_hold = bu_zero(ans_fund_hold,'基金代码')
ans_fund_hold_id = ans_fund_hold[['基金代码']].drop_duplicates().reset_index(drop=True)   
 
df = pd.DataFrame()
for index,row in ans_fund_hold_id.iterrows():
    b = ans_fund_hold[ans_fund_hold['基金代码']==row['基金代码']].reset_index(drop=True)   
    df_b = pd.DataFrame(b.values.T, index=b.columns, columns=b.index)#转置
    df_b= df_b.drop(['持股数','持仓市值','基金代码']).reset_index(drop=True)
    df_b['基金代码'] = row['基金代码']
    y_lie = df_b.pop('基金代码')
    df_b.insert(0,'基金代码',y_lie)
    df = df.append(df_b)
    print(index,row['基金代码'])

df_cc = df[df.index==0].reset_index(drop=True)  
df_jz = df[df.index==1].reset_index(drop=True)  
df_hengban =  pd.merge(df_cc,df_jz,how='inner',on='基金代码')

df_hengban.to_excel('基金持仓岳横板_2022Q3_{}.xlsx'.format(date_work))





















