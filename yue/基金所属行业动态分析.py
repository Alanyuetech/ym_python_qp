# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 14:50:15 2022

@author: Administrator
"""

"基金所属行业动态分析"

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

'恒生指数'
time_range = (datetime.datetime.now()-datetime.timedelta(days=360)).strftime('%Y%m%d')   # 数据容量，设置为一个月，再根据 d_outlier 具体抽取基金 和 行业etf的数据

# 替代--官网下载最新的数据
hsi = pd.read_csv('恒生科技指数历史数据.csv')[['日期','涨跌幅']].rename(columns={'涨跌幅':'800700'}) 
hsi['日期'] = hsi['日期'].map(lambda x: int(x.split('-')[0]+(x.split('-')[1] if len(x.split('-')[1])==2 else '0{}'.format(x.split('-')[1]))+(x.split('-')[2] if len(x.split('-')[2])==2 else '0{}'.format(x.split('-')[2]))) )
hsi['800700'] = hsi['800700'].astype('str').str.replace('%','').astype('float')/100

# #每日自己添加
# hsi = pd.read_excel('恒生科技指数历史数据.xlsx',engine='openpyxl')[['日期','涨跌幅']].rename(columns={'涨跌幅':'800700'}) 
# hsi['日期'] = hsi['日期'].map(lambda x:int(x.strftime('%Y%m%d')) )




for d_o in [10,20,40,60]:

    d_outlier = d_o
    
    
    "输入参数"
    n_maxind = 3   #行业上限数量
    p_max = 0.05   #p值上限
    # d_outlier = 10   #挑选基金异常值的时间范围
    outlier_min = -1.5    #基金及行业ETF 异常值下限
    outlier_max = 1.5     #基金及行业ETF 异常值上限
    
    
    industry = pd.read_excel('industry岳20230127.xlsx',engine='openpyxl',dtype={'code':'str'})   
    etf_id = pd.read_excel('行业etf代码.xlsx',engine='openpyxl',dtype={'etf':'str'})
    fund_id = pd.read_excel('白名单ID.xlsx',engine='openpyxl',dtype={'id':'str'})[['id']]  #正常是白名单ID   偶尔改成其他的文件单独跑其他的持仓
    fund_name = pd.read_excel('基金名称.xlsx',engine='openpyxl')
    
    etf_id = bu_zero(etf_id,'etf')
    fund_id = bu_zero(fund_id,'id')
    fund_name = bu_zero(fund_name,'基金代码')
    
    "基金持仓股票对应行业"
    fund_hold = pd.read_excel('基金持仓岳_2022Q4_20230127.xlsx',engine='openpyxl')[['股票代码','股票名称','占净值比例','持股数','持仓市值','季度','基金代码']]   
    fund_hold = bu_zero(fund_hold,'基金代码')  
    
    
    
    "merge"
    fund = pd.merge(fund_id,fund_hold,left_on='id',right_on='基金代码',how='left')
    fund = pd.merge(fund,industry,left_on='股票代码',right_on='code',how='left')
    
    
    fund = fund .drop(['id','code','name'], 1) 
    
    "补港股"
    fund = fund.dropna(axis=0,how='all')
    fund = fund.fillna('港股')
    
    fund = pd.merge(fund,etf_id,left_on='industry',right_on='行业',how='left')
    fund['行业'] = fund.apply(lambda x:'恒生科技指数' if x['industry']=='港股'   else x['行业'],axis=1)
    fund['etf'] = fund.apply(lambda x: '800700' if x['industry']=='港股'    else x['etf'],axis=1)
    
    
    "无法匹配对应行业etf的删除"
    fund = fund.dropna(axis=0,how='any')
    
    
    
    
    fund_group = fund.groupby(['基金代码','etf']).agg('sum').reset_index().sort_values(['基金代码','占净值比例']
                                                                                   ,ascending=[1,0]).groupby(by='基金代码').head(n_maxind).reset_index()
     
    etf_id_drdup = etf_id[['etf']].drop_duplicates().reset_index(drop=True)
    
    etf_data = pd.DataFrame()
    for index,row in etf_id_drdup.iterrows():
        etf_data_b = ak.fund_open_fund_info_em(fund=row['etf'], indicator="单位净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
        etf_data_b['净值日期'] = etf_data_b['净值日期'].astype('str').str.replace('-','').astype('int')
        etf_data_b = etf_data_b[['净值日期','日增长率']].rename(columns={'净值日期':'日期','日增长率':'{}'.format(row['etf'])})
        etf_data_b = etf_data_b[etf_data_b['日期']>=int(time_range)]
        if index == 0:
            etf_data = etf_data_b.copy()
        else:
            etf_data = pd.merge(etf_data,etf_data_b,how='left',on='日期')
        print(index,row['etf'])
        
    etf_data.to_excel('etf{}.xlsx'.format(date_work))
    etf_data = pd.merge(etf_data,hsi,how='left',on='日期')
    
    
    
    def linear_ana(data):
        "线性回归--数据合并"
        
        # "dfs合并需要回归的数据，首列因变量，后续为自变量"
        # dfs = [dv,indv]
        # merge_data = reduce(lambda x,y:pd.merge(x,y,on='日期',how='left'),dfs)
        data = data.sort_values('日期')
        data = data.dropna(axis=0,how='any') 
    
        "回归"
    
        datas = data.copy()
        y = datas.iloc[:, 1] # 因变量为第 2 列数据
        x = datas.iloc[:, 2:] # 自变量为第 3 列到第 n 列数据
        # x = sm.add_constant(x) # 若模型中有截距，必须有这一步
        model = sm.OLS(y, x).fit() # 构建最小二乘模型并拟合
        # print(model.summary()) # 输出回归结果  
        p_values = pd.DataFrame(model.pvalues).reset_index().rename(columns={'index':'etf',0:'p值'})
        r_squared = model.rsquared
        return [p_values,r_squared]
    
    def fund_id_data(f_id):
        f_id_data = ak.fund_open_fund_info_em(fund=f_id, indicator="单位净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
        f_id_data['净值日期'] = f_id_data['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
        f_id_data = f_id_data.rename(columns={'净值日期':'日期','日增长率':'fund日增长率'})
        f_id_data = f_id_data[['日期','fund日增长率']]
        return f_id_data
    
    
    
    def etf_combination(residue_idtry_etf,n):    #排列组合生成每组n个所有剩余行业etf的组合
        etf_comb = list()
        for aaaa in combinations(residue_idtry_etf,n):
            aaa = ','.join(aaaa)
            etf_comb.append(aaa)
        etf_comb = pd.DataFrame(etf_comb).rename(columns=({0:'etf_comb'}))
        return etf_comb
    
    
    
    ######################################################################################################################
    
    
    
    def hold_ana(f_id):
        "持仓分析"
        "基金数据"
        f_id_data = fund_id_data(f_id)
        "etf数据" 
        df = fund_group[fund_group['基金代码']==f_id][['基金代码','etf']].reset_index(drop=True)
        etf_list = list(df['etf'])
        etf_list.insert(0,'日期')
        etf_part = etf_data[etf_list]
        # etf_part = etf_data[['日期','{}'.format(df.loc[0,'etf']),'{}'.format(df.loc[1,'etf']),'{}'.format(df.loc[2,'etf'])]].copy()
        dfs = pd.merge(f_id_data,etf_part,how='left',on='日期')
        dfs = dfs.sort_values(['日期'],ascending=[0]).head(d_outlier)
        "回归出p值"
        hold_anayliz = linear_ana(dfs)[0]
        hold_anayliz = hold_anayliz[hold_anayliz['p值']<=p_max]
        hold_anayliz['fund_id'] = f_id
        return hold_anayliz
    
    
    
    
    fund_hold_ana = pd.DataFrame()
    for index,row in fund_id.iterrows():
        try:
            hold_anayliz_b = hold_ana(row['id'])
            fund_hold_ana = fund_hold_ana.append(hold_anayliz_b)
            
            print(index,row['id'])
        except:
            print(index,row['id'],'错误')
    
    
    
    ###############################################################
    "利用异常值进行第二轮补位"
    def outlier_supplement_industry(f_id,n):     #n: 异常值补充个数
        f_id_data = fund_id_data(f_id)    
        ensure_idtry = fund_hold_ana[fund_hold_ana['fund_id']==f_id]  #已确定的行业
        ensure_idtry_etf = list(ensure_idtry['etf'])   #已确定的行业--列表格式  
        residue_idtry = etf_data.copy()               #复制所有行业etf数据 
        residue_idtry = residue_idtry.drop(ensure_idtry_etf,axis=1)     #删除已确定的行业
        residue_fund_merge = pd.merge(f_id_data,residue_idtry,how='left',on='日期').sort_values('日期',ascending=0).head(d_outlier)
        residue_fund_merge_outlier = residue_fund_merge[(residue_fund_merge['fund日增长率']>outlier_max)
                                                        |(residue_fund_merge['fund日增长率']<outlier_min)]
        residue_fund_merge_outlier = residue_fund_merge_outlier.iloc[:,2:]
        
        if len(residue_fund_merge_outlier)==0:   #如果无法筛选出异常值-----基金本身没有异常值
            outlier_anayliz=pd.DataFrame()   
            return outlier_anayliz        
        else:
            pass
        #  基金有异常值，看行业etf的异常值
        residue_fund_merge_outlier = residue_fund_merge_outlier.applymap(
            lambda x:1 if (x>=outlier_min)&(x<=outlier_max) else 0)        #异常值范围内赋值1，符合异常值赋值0
        residue_fund_merge_outlier = pd.DataFrame(residue_fund_merge_outlier.agg('sum'))
        residue_fund_merge_outlier = residue_fund_merge_outlier[residue_fund_merge_outlier[0]==0]  #筛选出全部日期 都和基金同步异常的行业etf
        
        if len(residue_fund_merge_outlier)==0:   #如果无法筛选出异常值------行业etf没有异常值
            outlier_anayliz=pd.DataFrame()   
            return outlier_anayliz        
        else:
            pass    
        
        #  如果后续需要修改，将全部异常设定为部分异常，则需要将基金异常也保留--iloc[:,2:]改为iloc[:,1:]--根据一定的比例对行业etf进行保留
        
        ensure_idtry_etf.insert(0,'日期')                                                 #已确定行业+日期
        ensure_idtry_data = etf_data[ensure_idtry_etf]                                     #已确定行业+日期的数据
        dfs = pd.merge(f_id_data,ensure_idtry_data,how='left',on='日期').sort_values('日期',ascending=0).head(d_outlier) #合并 基金+已确定行业的数据
        outlier_idtry_all = residue_fund_merge_outlier.reset_index()['index'].tolist()      #所有异常行业--列表格式     
        "筛选出的异常值 与 异常值补充个数  进行比较和判断"
        if len(residue_fund_merge_outlier)<=n:
            outlier_idtry_all.insert(0,'日期')
            etf_comb_data = etf_data[outlier_idtry_all]           
            dfs = pd.merge(dfs,etf_comb_data,how='left',on='日期').sort_values('日期',ascending=0).head(d_outlier)    #合并 基金+已确定行业+异常行业的数据
            outlier_anayliz_b=pd.DataFrame() 
            outlier_anayliz_b,r_squared = linear_ana(dfs)[0],linear_ana(dfs)[1] 
            outlier_anayliz_b['fund_id'] = f_id  
            outlier_anayliz_b['R_2'] = r_squared
            outlier_anayliz_b = outlier_anayliz_b[outlier_anayliz_b['p值']<=p_max]
            outlier_anayliz = pd.DataFrame()
            outlier_anayliz =outlier_anayliz.append(outlier_anayliz_b)         
        
        else:
            etf_comb = etf_combination(outlier_idtry_all,n)                              #所有异常行业--排列组合
            outlier_anayliz = pd.DataFrame()
            for index_1,row_1 in etf_comb.iterrows():
                etf_comb_list = row_1['etf_comb'].split(",")
                etf_comb_list.insert(0,'日期')
                etf_comb_data = etf_data[etf_comb_list]  
                dfs_n = pd.merge(dfs,etf_comb_data,how='left',on='日期').sort_values('日期',ascending=0).head(d_outlier)    #合并 基金+已确定行业+异常行业的数据
                outlier_anayliz_b=pd.DataFrame() 
                outlier_anayliz_b,r_squared = linear_ana(dfs_n)[0],linear_ana(dfs_n)[1] 
                outlier_anayliz_b['fund_id'] = f_id  
                outlier_anayliz_b['R_2'] = r_squared
                outlier_anayliz_b = outlier_anayliz_b[outlier_anayliz_b['p值']<=p_max]
                outlier_anayliz =outlier_anayliz.append(outlier_anayliz_b)
                print('异常行业组合：',index_1,row_1['etf_comb'])
        
        
        
        outlier_anayliz = outlier_anayliz[outlier_anayliz['R_2']==outlier_anayliz['R_2'].max()]  #拿到 R^2 最大的一组回归结果
        outlier_anayliz = outlier_anayliz[-outlier_anayliz.etf.isin(ensure_idtry_etf)]  #删掉持仓确定的 行业
        return outlier_anayliz
    
    "持仓分析后可以使用的行业"
    industry_num = fund_hold_ana.groupby('fund_id').agg('count').reset_index()[['fund_id','etf']].rename(columns={'etf':'etf数量'})
    industry_num = pd.merge(fund_id,industry_num,left_on='id',right_on='fund_id',how='left')[['id','etf数量']].rename(columns={'id':'fund_id'})
    industry_num = industry_num.fillna(0)
    
    
    fund_outlier_ana = pd.DataFrame()
    for index,row in industry_num.iterrows():
        if row['etf数量']!=n_maxind:
            n_outsuppl = n_maxind - int(row['etf数量'])   #异常值补充个数
            outlier_anayliz = outlier_supplement_industry(row['fund_id'],n_outsuppl)
            fund_outlier_ana = fund_outlier_ana.append(outlier_anayliz)       
                  
            print(index,row['fund_id'],n_outsuppl)
        else:
            pass
    
    
    fund_hold_ana['标签'] = '持仓阶段'
    fund_outlier_ana['标签'] = '异常值补位'
    
    if len(fund_outlier_ana)!=0:
        fund_hold_outlier_ana = fund_hold_ana.append(fund_outlier_ana[['etf','p值','fund_id','标签']])  #合并持仓分析 和 异常值补位 后得到的行业etf
    else:
        fund_hold_outlier_ana = fund_hold_ana.copy()
    
    
    
    "从剩余行业中进行第三轮补位"
    def supplement_industry(f_id,n):     #n: 补充个数
        f_id_data = fund_id_data(f_id)    
        ensure_idtry = fund_hold_outlier_ana[fund_hold_outlier_ana['fund_id']==f_id]  #已确定的行业
        ensure_idtry_etf = list(ensure_idtry['etf'])   #已确定的行业--列表格式  
        residue_idtry = etf_data.copy()               #复制所有行业etf数据 
        residue_idtry = residue_idtry.drop(ensure_idtry_etf,axis=1)     #删除已确定的行业
        # residue_fund_merge = pd.merge(f_id_data,residue_idtry,how='left',on='日期').sort_values('日期',ascending=0).head(d_outlier)
        
        
        residue_idtry_etf =  residue_idtry.iloc[:,1:].columns.values.tolist()                 #剩余行业--列表格式  
        etf_comb = etf_combination(residue_idtry_etf,n)                         #剩余行业--排列组合
        
        ensure_idtry_etf.insert(0,'日期')                                                 #已确定行业+日期
        ensure_idtry_data = etf_data[ensure_idtry_etf]                                     #已确定行业+日期的数据
        dfs = pd.merge(f_id_data,ensure_idtry_data,how='left',on='日期').sort_values('日期',ascending=0).head(d_outlier)    #合并 基金+已确定行业的数据
        
        for index_1,row_1 in etf_comb.iterrows():
            etf_comb_list = row_1['etf_comb'].split(",")
            etf_comb_list.insert(0,'日期')
            etf_comb_data = etf_data[etf_comb_list]  
            dfs_n = pd.merge(dfs,etf_comb_data,how='left',on='日期').sort_values('日期',ascending=0).head(d_outlier)    #合并 基金+已确定行业+补位行业的数据
            
            final_anayliz_b,r_squared = linear_ana(dfs_n)[0],linear_ana(dfs_n)[1] 
            final_anayliz_b['fund_id'] = f_id  
            final_anayliz_b['R_2'] = r_squared
            final_anayliz_b = final_anayliz_b[final_anayliz_b['p值']<=p_max]
            final_anayliz = pd.DataFrame()
            final_anayliz = final_anayliz.append(final_anayliz_b)     
            
          
        final_anayliz = final_anayliz[final_anayliz['R_2']==final_anayliz['R_2'].max()]  #拿到 R^2 最大的一组回归结果
        final_anayliz = final_anayliz[-final_anayliz.etf.isin(ensure_idtry_etf)]  #删掉持仓确定的 行业
        return final_anayliz
    
    
    
    "异常值补位后可以使用的行业"
    industry_outlier_num = fund_hold_outlier_ana.groupby('fund_id').agg('count').reset_index()[['fund_id','etf']].rename(columns={'etf':'etf数量'})
    industry_outlier_num = pd.merge(fund_id,industry_outlier_num,left_on='id',right_on='fund_id',how='left')[['id','etf数量']].rename(columns={'id':'fund_id'})
    industry_outlier_num = industry_outlier_num.fillna(0)
    
    
    fund_final_ana = pd.DataFrame()
    for index,row in industry_outlier_num.iterrows():
        if row['etf数量']!=n_maxind:
            n_suppl = n_maxind - int(row['etf数量'])   #最终补充个数
            final_anayliz = supplement_industry(row['fund_id'],n_suppl)
            fund_final_ana = fund_final_ana.append(final_anayliz)       
                  
            print(index,row['fund_id'],n_suppl)
        else:
            pass
    
    
    fund_final_ana['标签'] = '最终补位'
    
    if len(fund_final_ana)!=0:               
        fund_hold_outlier_final_ana = fund_hold_outlier_ana.append(fund_final_ana[['etf','p值','fund_id','标签']])  #合并持仓分析 和 异常值补位 后得到的行业etf
    else:
        fund_hold_outlier_final_ana = fund_hold_outlier_ana.copy()
    
    fund_hold_outlier_final_ana = fund_hold_outlier_final_ana.sort_values('fund_id',ascending=1)
    fund_hold_outlier_final_ana_count = fund_hold_outlier_final_ana[['fund_id','etf']].groupby('fund_id').agg('count').reset_index()
    fund_hold_outlier_final_ana_count = pd.merge(fund_hold_outlier_final_ana_count,fund_id,how='right',left_on='fund_id',right_on='id')[['id','etf']]
    fund_hold_outlier_final_ana_count['etf'] = fund_hold_outlier_final_ana_count['etf'].fillna(0)
    fund_hold_outlier_final_ana = pd.merge(fund_hold_outlier_final_ana,fund_name,left_on='etf',right_on='基金代码',how='left').rename(columns={'基金名称':'etf名称'})
    fund_hold_outlier_final_ana = pd.merge(fund_hold_outlier_final_ana,fund_id,left_on='fund_id',right_on='id',how='right')
    fund_hold_outlier_final_ana['ETF名称'] = fund_hold_outlier_final_ana.apply(lambda x:'混合' if pd.isna(x['fund_id']) else x['etf名称'] ,axis=1)
    fund_hold_outlier_final_ana['fund_id'] = fund_hold_outlier_final_ana['id']
    fund_hold_outlier_final_ana = pd.merge(fund_hold_outlier_final_ana,fund_name,left_on='fund_id',right_on='基金代码',how='left')
    fund_hold_outlier_final_ana = fund_hold_outlier_final_ana[['fund_id','基金名称','etf','ETF名称','标签','p值']]
    
    
    
    
    
    fund_hold_outlier_final_ana.to_excel('基金所属行业动态分析{}_{}.xlsx'.format(d_outlier,date_work))



time_end = time.time()
time_sum = time_end - time_start
print('运行时间：{:.2f} 秒 '.format(time_sum))




