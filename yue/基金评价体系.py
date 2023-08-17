# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 10:35:58 2022

@author: yue
"""

"基金评价体系"

from yue.fundeva_managers import fundeva_managers
from yue.fundeva_companies import fundeva_companies
from yue.fundeva_funds import fundeva_funds
from yue.fund_change import fundeva_basedata


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
time_start = time.time()
now_day = datetime.datetime.now().strftime('%Y%m%d')
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


time_start = time.time()

"基础数据"
data = fundeva_basedata()

"基金公司"  
fundeva_companies = fundeva_companies()
"基金经理"
fundeva_managers = fundeva_managers(data)
"基金"    
fundeva_funds = fundeva_funds(data)  

"总得分"
fundeva_final_b = pd.merge(fundeva_funds,fundeva_companies,on='company')
fundeva_final_b = pd.merge(fundeva_final_b,fundeva_managers,on='new')





"权重"
b_list = ['项目','原始权重','数据-顺向','数据-MOM','稳健','星期五']    #挑选所用权重
weight_list = pd.read_excel('基金评价体系--权重.xlsx',engine='openpyxl')[b_list]     

for i in b_list[1:]:
    weight_list_b = weight_list[['项目','{}'.format(i)]]
 
    fundeva_final = fundeva_final_b.copy()
    for index,row in weight_list_b.iterrows():
        fundeva_final['{}'.format(row['项目'])] = fundeva_final_b['{}'.format(row['项目'])]*row['{}'.format(i)]    
    
    for ii in ['占净值比例合计','所属行业数量']:
        ans = fundeva_final.copy()  
        zzf = ans.pop('{}'.format(ii))
        ans['{}'.format(ii)] = zzf
        fundeva_final = ans.copy()  
    
    fundeva_final['总得分'] = fundeva_final.iloc[:,4:-2].apply(lambda x:x.sum(), axis=1) 
    fundeva_final = fundeva_final.sort_values(['总得分','基金规模得分'],ascending=[0,0])
    fundeva_final.to_excel('基金评价体系{}{}.xlsx'.format(now_day,i))


    print(i)

time_end = time.time()
time_sum = time_end - time_start
print('运行时间：{:.2f} 秒 '.format(time_sum))





































