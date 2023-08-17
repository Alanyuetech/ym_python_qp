# -*- coding: utf-8 -*-
"""
Created on Mon Dec 27 10:29:44 2021

@author: Administrator
"""

"季度换股"


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
now_day = datetime.datetime.now().strftime('%Y%m%d')


start_date = 20110101
end_date = 20211231



def q_start_date(start_date,end_date):
    "获取时间段内每个季度的开始日期和结束日期"
    q_s_date = pd.DataFrame(columns=['季度初','季度末'])
    q_s_date_y = pd.DataFrame(columns=['日期'])
    s_year = start_date//10000  #取年
    e_year = end_date//10000   #取年
    for i in range(s_year,e_year+1):                                                #创建年份的df
        q_s_date_y.loc[i,'日期'] = str(i)
    
    q_listd_std = pd.DataFrame(columns=['季度初'],data = ['0101','0401','0701','1001'])    #创建季度的df
    q_listd_end = pd.DataFrame(columns=['季度末'],data = ['0331','0630','0930','1231'])    #创建季度的df
    
    for i in range(0,4):                                                            #  年份 + 季度
        q_s_date_bb = pd.DataFrame(columns=['季度初','季度末'])
        q_s_date_bb['季度初'] = q_s_date_y['日期']+q_listd_std.loc[i,'季度初']
        q_s_date_bb['季度末'] = q_s_date_y['日期']+q_listd_end.loc[i,'季度末']
        q_s_date = pd.concat([q_s_date,q_s_date_bb])
        
    q_s_date = q_s_date.sort_values(by=['季度初'],ascending=1).reset_index(drop=True)  
    q_s_date['季度初'] = q_s_date['季度初'].astype('int')    
    q_s_date['季度末'] = q_s_date['季度末'].astype('int')    
    return q_s_date



"读取股票代码列表"
stock_list = pd.read_excel('美股200亿以上筛选.xlsx',engine='openpyxl')
stock_list = stock_list.rename(columns={'代码':'stock_id'})
stock_50b_list = stock_list[stock_list['总市值-亿']>=200]    #此处修改 >200亿   >500亿


"所有美股"
us_stock =  ak.stock_us_spot_em()
us_stock['stock_id'] = us_stock['代码'].str.split('.',expand=True)[1]  #分列
stock_50b_list = pd.merge(stock_50b_list,us_stock[['代码','stock_id']],how='left',on='stock_id')


stock_50b_list.drop(stock_50b_list[pd.isna(stock_50b_list['代码'])].index, inplace=True)   #删除没有没有代码的股票
stock_50b_list = stock_50b_list.reset_index(drop=True)


# stock_50b_list= stock_50b_list.loc[308:,:]

"近 N 年股票数据"   "时间较快，不用留档"
stock_data = pd.DataFrame()
for index,row in stock_50b_list.iterrows():
    stock_data_b = ak.stock_us_hist(symbol='{}'.format(row['代码']), start_date="20091220", end_date=now_day, adjust="hfq")
    stock_data_b['代码']=row['代码']
    stock_data = stock_data.append(stock_data_b)
    print(index,row['代码'])


ans_data = pd.merge(stock_data[['日期','收盘','成交量','换手率','代码']],stock_50b_list[['名称','所属行业','代码']],how='left',on='代码')
# ans_data['流通市值c'] = ans_data['收盘'] *(100*ans_data['成交量']/ans_data['换手率'])     #100 换手率从百分比变为小数


q_data = q_start_date(start_date,end_date)
q_data['换手率lmavg'] = ''
q_data['季度内涨跌幅'] = ''
q_data['代码'] = ''
"成交量    换手率   过去m年的序列   过去p个月的平均   处于前 n% 的位置，未来一个季度的涨跌幅"
def factor_analysis(ans_data,stock_id,m,p,n):
    ans = ans_data[ans_data['代码']==stock_id]
    ans['日期'] = ans['日期'].astype('str').str.replace('-','').astype('int')
    q_data_b = q_data[q_data['季度初']>=(ans.head(1).reset_index(drop=True).loc[0,'日期']+10000)]
    # q_data_b = q_data.copy()
    q_data_b['代码'] = stock_id
    for index,row in q_data_b.iterrows():
        ans_ly = ans[(ans['日期']<row['季度初'])&(ans['日期']>=(row['季度初']-10000*m))].reset_index(drop=True)    #季度初 前m年     
        
        lnm = int((datetime.datetime.strptime(str(row['季度初']),'%Y%m%d')+relativedelta(months=-p)).strftime('%Y%m%d'))
        ans_lm = ans[(ans['日期']<row['季度初'])&(ans['日期']>=lnm)]         #季度初 前n月   
        
        ans_lm_avg = ans_lm['换手率'].mean()
        a=100-n
        n_ans_ly = np.percentile(ans_ly['换手率'], a)                       #前 n%  分位数
        if ans_lm_avg>=n_ans_ly:
            q_data_b.loc[index,'换手率lmavg'] = '{}%:{:.2f} > {:.2f}'.format(n,ans_lm_avg,n_ans_ly)
        else:
            pass
        ans_a = ans[(ans['日期']>=q_data_b.loc[index,'季度初'])&(ans['日期']<=q_data_b.loc[index,'季度末'])].reset_index(drop=True)
        q_data_b.loc[index,'季度内涨跌幅'] = ans_a.tail(1).reset_index(drop=True).loc[0,'收盘']/ans_a.head(1).reset_index(drop=True).loc[0,'收盘'] - 1  
    return q_data_b




" 单组参数测试   m=1  n=25"                             "修改时间：20211231"
###########################################################################


df = pd.DataFrame()
for index,row in stock_50b_list.iterrows():
    q_data_b = pd.DataFrame()
    q_data_b = factor_analysis(ans_data,row['代码'],1,1,25)
    df = pd.concat([df,q_data_b])
    print(index,row['代码'])



df['季度内涨跌幅'] = df['季度内涨跌幅'].astype('float')
df_avg_v = df['季度内涨跌幅'].mean()                         #  计算所有股票所有季度的平均值


df_drop = df[df['换手率lmavg']!=''].reset_index(drop=True)   # 保留 lm > ly 计算出未来一季度内涨跌幅的行
df_drop['季度内涨跌幅'] = df_drop['季度内涨跌幅'].astype('float')
df_drop_avg_v = df_drop['季度内涨跌幅'].mean()               # 保留 lm > ly 计算出 所有  未来一季度内涨跌幅的 平均值


"按照季度进行分组统计 "
df_qgroup = df.groupby(['季度初','季度末']).agg('mean').reset_index()
df_drop_qgroup = df_drop.groupby(['季度初','季度末']).agg('mean').reset_index().rename(columns={'季度内涨跌幅':'季度内涨跌幅Q'})
df_qgroup['季度标识'] =  df_qgroup['季度初'].apply(lambda x:'一季度' if str(x)[4:]=='0101' else ('二季度' if str(x)[4:]=='0401' else ('三季度' if str(x)[4:]=='0701' else '四季度' )))
df_drop_qgroup['季度标识'] =  df_drop_qgroup['季度初'].apply(lambda x:'一季度' if str(x)[4:]=='0101' else ('二季度' if str(x)[4:]=='0401' else ('三季度' if str(x)[4:]=='0701' else '四季度' )))


q_group = pd.merge(df_qgroup,df_drop_qgroup,how='left',on=['季度初','季度末','季度标识'])
q_group['lm>ly后超额表现'] = q_group['季度内涨跌幅Q'] - q_group['季度内涨跌幅']                          #  有因子季度涨幅平均 - 无因子季度涨幅平均
q_group_avg =  pd.DataFrame(q_group.mean()).T[['季度内涨跌幅','季度内涨跌幅Q','lm>ly后超额表现']]

###########################################################################




" 循环测试 "                                            "修改时间：20211231"
###########################################################################
" 封装  测试用代码 "
" 调整 股票活跃度因子条件 ———— 调整 过去m年  过去p个月平均  前n% "
def group_test(m,p,n):

    "跑所有的数据——并根据m n 打标签"
    df = pd.DataFrame()
    for index,row in stock_50b_list.iterrows():
        q_data_b = pd.DataFrame()
        q_data_b = factor_analysis(ans_data,row['代码'],m,p,n)
        df = pd.concat([df,q_data_b])
    
    
    df['季度内涨跌幅'] = df['季度内涨跌幅'].astype('float')
    df_avg_v = df['季度内涨跌幅'].mean()                         #  计算所有股票所有季度的平均值
    
    
    df_drop = df[df['换手率lmavg']!=''].reset_index(drop=True)   # 保留 lm > ly 计算出未来一季度内涨跌幅的行
    df_drop['季度内涨跌幅'] = df_drop['季度内涨跌幅'].astype('float')
    df_drop_avg_v = df_drop['季度内涨跌幅'].mean()               # 保留 lm > ly 计算出 所有  未来一季度内涨跌幅的 平均值
    
    
    "按照季度进行分组统计 "
    df_qgroup = df.groupby(['季度初','季度末']).agg('mean').reset_index()
    df_drop_qgroup = df_drop.groupby(['季度初','季度末']).agg('mean').reset_index().rename(columns={'季度内涨跌幅':'季度内涨跌幅Q'})
    df_qgroup['季度标识'] =  df_qgroup['季度初'].apply(lambda x:'一季度' if str(x)[4:]=='0101' else ('二季度' if str(x)[4:]=='0401' else ('三季度' if str(x)[4:]=='0701' else '四季度' )))
    df_drop_qgroup['季度标识'] =  df_drop_qgroup['季度初'].apply(lambda x:'一季度' if str(x)[4:]=='0101' else ('二季度' if str(x)[4:]=='0401' else ('三季度' if str(x)[4:]=='0701' else '四季度' )))
    
    
    q_group = pd.merge(df_qgroup,df_drop_qgroup,how='left',on=['季度初','季度末','季度标识'])
    q_group['lm>ly后超额表现'] = q_group['季度内涨跌幅Q'] - q_group['季度内涨跌幅']                          #  有因子季度涨幅平均 - 无因子季度涨幅平均
    q_group_avg =  pd.DataFrame(q_group.mean()).T[['季度内涨跌幅','季度内涨跌幅Q','lm>ly后超额表现']]
    
    
    result = q_group_avg.copy()
    result.loc[0,'所有股票所有季度平均'] = df_avg_v
    result.loc[0,'加入因子平均'] = df_drop_avg_v
    result = result.rename(columns={'季度内涨跌幅':'季度分组44季度平均','季度内涨跌幅Q':'加入因子季度分组44季度平均'})
    result.loc[0,'数据标识'] = '未来一个季度涨跌幅'
    result.loc[0,'参数标识'] = '{}年排序_{}月平均_{}%百分位'.format(m,p,n)
    result.loc[0,'因子筛选数量'] = '{} / {} ：{:.2f} %'.format(df_drop['代码'].count(),df['代码'].count(),100*df_drop['代码'].count()/df['代码'].count())
    
    return  result

group_test_all = pd.DataFrame()

for m in range(1,2):
    for p in range(1,2):
        for n in range(10,60,10):
            group_test_b = group_test(m,p,n)
            group_test_all = pd.concat([group_test_all,group_test_b])
            print('过去 {} 年 ，过去 {} 月平均 ，前 {}%   '.format(m,p,n))
    
    

























###########################################################################






"比较基准——————使用纳斯达克综合指数作为比较基准      需要开代理"
###########################################################################

"纳斯达克指数  季度涨跌幅   再进行平均"                       "修改时间：20211230"
index_data = ak.index_investing_global(country='美国', index_name='纳斯达克综合指数',period='每日', start_date=str(start_date), end_date=str(end_date))[['日期','收盘']]
index_data['日期'] = index_data['日期'].astype('str').str.replace('-','').astype('int')
index_data_q = q_group[['季度初','季度末','季度标识']]
index_data_q['指数季度涨幅'] = np.nan
for index,row in index_data_q.iterrows():
    ans_index_b = index_data[(index_data['日期']>=row['季度初'])&(index_data['日期']<=row['季度末'])].sort_values(by='日期',ascending=1).reset_index(drop=True)
    index_data_q.loc[index,'指数季度涨幅'] = ans_index_b.tail(1).reset_index(drop=True).loc[0,'收盘']/ans_index_b.head(1).reset_index(drop=True).loc[0,'收盘'] - 1 
    print(index,row['季度初'])
index_data_q_avg_v = index_data_q['指数季度涨幅'].mean()



###########################################################################

