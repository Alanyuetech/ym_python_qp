# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 13:11:56 2021

@author: Administrator
"""

"行业数据 —————— 基金涨跌幅   对应关系研究"

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

from numpy.linalg import lstsq # 解超定方程
from numpy.linalg import solve # 解线性方程

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


##############################################################################################################
"同花顺行业板块"

concept_name_ths = ak.stock_board_industry_name_ths()

##############################################################################################################

"净值估算"
fund_value_estimation = ak.fund_em_value_estimation(symbol='全部')
fund_value_estimation.to_excel('净值估算{}.xlsx'.format(now_day))
##############################################################################################################

"所有概念名称       当前所有概念表现"
concept_data = ak.stock_board_concept_name_em()
concept_name = concept_data[['板块名称']]


# "所有概念板块 成分股"
# concept_stock = pd.DataFrame()
# for index,row  in concept_name.iterrows():
#     concept_stock_b = ak.stock_board_concept_cons_em(symbol="{}".format(row['板块名称']))
#     concept_stock_b['板块名称'] = row['板块名称']
#     concept_stock = concept_stock.append(concept_stock_b)
#     print(row['板块名称'])

# concept_stock.to_excel('概念板块成分股{}.xlsx'.format(date_work))

"所有概念板块  指数  日频指数数据"

ans = pd.DataFrame()

for index,row  in concept_name.iterrows():
    ans_b = ak.stock_board_concept_hist_em(symbol="{}".format(row['板块名称']), adjust="").sort_values(by='日期',ascending=False).reset_index(drop=True)              
    ans_b['概念板块'] = row['板块名称']
    ans = ans.append(ans_b)
    print(row['板块名称'])
    
ans.to_excel('概念板块指数日频数据{}.xlsx'.format(date_work))


# "具体概念板块"
# ans_concept = ak.stock_board_concept_hist_em(symbol="白酒", adjust="")



##############################################################################################################
"本季度内所有基金的日频数据"

"基金列表"
fund_id = pd.read_excel('临时AVE_测试0813.xlsx',dtype={'id':'str'})
fund_id = bu_zero(fund_id,'id')

fund_data_hz = pd.DataFrame()
start = time.time()
"拿出每个基金的历史 累计净值走势"
for index,row  in fund_id.iterrows():
    fund_data = ak.fund_em_open_fund_info(fund=row['id'], indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    fund_data['id'] = row['id']
    fund_data['累计净值'] =  fund_data['累计净值'].astype('float')
    fund_data['基金涨跌幅'] = fund_data['累计净值']/fund_data['累计净值'].shift(-1) - 1
    fund_data_hz = fund_data_hz.append(fund_data)
    print(index,row['id'])
end = time.time()
print(end-start)
fund_data_hz = fund_data_hz.reset_index(drop=True)
fund_data_hz = fund_data_hz[fund_data_hz['净值日期'].astype('str')>='2021-08-31'].reset_index(drop=True)

    
##############################################################################################################
"行业ETF数据————作为行业"
concept_etf = pd.read_excel('行业指数基金.xlsx',dtype={'id':'str'})
concept_etf = bu_zero(concept_etf,'id')

concept_data_hz = pd.DataFrame()
"拿出每个基金的历史 累计净值走势"
for index,row  in concept_etf.iterrows():
    concept_data = ak.fund_em_open_fund_info(fund=row['id'], indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    concept_data['id'] = row['id']
    concept_data['累计净值'] =  concept_data['累计净值'].astype('float')
    concept_data['行业涨跌幅'] = concept_data['累计净值']/concept_data['累计净值'].shift(-1) - 1
    concept_data_hz = concept_data_hz.append(concept_data)
    print(index,row['id'])

concept_data_hz = concept_data_hz.reset_index(drop=True)
concept_data_hz = concept_data_hz[concept_data_hz['净值日期'].astype('str')>='2021-08-31'].reset_index(drop=True)



"方程组"




"超定方程组 求近似解"
a = np.mat([[2, 1], [1, 2]])#系数矩阵
b = np.mat([10, 0]).T    #常数项列矩阵
x = solve(a, b)    #求解正常方程组







a = np.mat([[2, 1],[1, 1], [1, 2]])#系数矩阵
b = np.mat([10,1,0]).T    #常数项列矩阵
x = lstsq(a, b)   #求解超定方程组




















