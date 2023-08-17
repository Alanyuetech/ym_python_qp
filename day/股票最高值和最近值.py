# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 13:03:07 2021

@author: 86178
"""


import pandas as pd
import tushare as ts
import numpy as np
import datetime
import requests
import re
import time

delta = delta_one_year = datetime.timedelta(days=180)
sz = pd.read_csv('全部A股.csv',dtype={'代码': 'str'})
cyb = pd.read_csv('创业板.csv',dtype={'代码': 'str'})
kcb = pd.read_csv('科创板.csv',dtype={'代码': 'str'})

def order_for_id(data,num):
    for m in range(len(data)):
        data.iloc[m,num]=str(data.iloc[m,num])
        if len(data.iloc[m,num])<6:
            data.iloc[m,num]=str(0)+data.iloc[m,num]       
        if len(data.iloc[m,num])<6:
            data.iloc[m,num]=str(0)+data.iloc[m,num]
        if len(data.iloc[m,num])<6:
            data.iloc[m,num]=str(0)+data.iloc[m,num]
        if len(data.iloc[m,num])<6:
            data.iloc[m,num]=str(0)+data.iloc[m,num]
        if len(data.iloc[m,num])<6:
            data.iloc[m,num]=str(0)+data.iloc[m,num]
    return data


sz = order_for_id(sz, 1)
cyb = order_for_id(cyb, 1)
kcb = order_for_id(kcb, 1)

sz_list = [x for x in sz['代码']]
cyb_list = [x for x in cyb['代码']]
kcb_list = [x for x in kcb['代码']]


def max_close_11percents(num):
    exp = ts.get_hist_data(num)
    try:
        exp['date'] = exp.index
        exp.reset_index(inplace=True,drop=True)
        now = datetime.datetime.now()
        use_time = now-delta
        use_time = use_time.strftime('%Y-%m-%d')
        
        exp = exp[exp['date']>use_time]
        price_list = [x for x in exp['close']]
        
        for i in range(len(price_list)-1):
            if price_list[i+1]/price_list[i]>1.11:
                price = price_list[i+1] - price_list[i]
                price_list[:i+1] = [x+price for x in price_list[:i+1]]
        
        exp['close'] = price_list
        day = exp.loc[exp['close'].idxmax(),'date']
        close = exp.loc[exp['close'].idxmax(),'close']
        latest = exp.loc[0,'close']
        res = pd.DataFrame([day],columns=['date'])
        res['max_close'] = [close]
        res['latest'] = latest
        res['id'] = [num]
    except:
        res = pd.DataFrame()
    return res


def max_close_21percents(num):
    exp = ts.get_hist_data(num)
    try:
        exp['date'] = exp.index
        exp.reset_index(inplace=True,drop=True)
        now = datetime.datetime.now()
        use_time = now-delta
        use_time = use_time.strftime('%Y-%m-%d')
        
        exp = exp[exp['date']>use_time]
        price_list = [x for x in exp['close']]
        
        for i in range(len(price_list)-1):
            if price_list[i+1]/price_list[i]>1.21:
                price = price_list[i+1] - price_list[i]
                price_list[:i+1] = [x+price for x in price_list[:i+1]]
        
        exp['close'] = price_list
        day = exp.loc[exp['close'].idxmax(),'date']
        close = exp.loc[exp['close'].idxmax(),'close']
        latest = exp.loc[0,'close']
        res = pd.DataFrame([day],columns=['date'])
        res['max_close'] = [close]
        res['latest'] = latest
        res['id'] = [num]
    except:
        res = pd.DataFrame()
    return res

def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    
    
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y%m%d')

#import os
#os.environ['http_proxy'] = 'http://127.0.0.1:1080'        #先不要运行这两句，运行不了再运行
#os.environ['https_proxy'] = 'https://127.0.0.1:1080'

max_latest_A = list()
for search_num in sz_list:
    use = max_close_11percents(search_num)
    max_latest_A.append(use)

oth_list = cyb_list + kcb_list
max_latest_oth = list()
for search_num in oth_list:
    use = max_close_21percents(search_num)
    max_latest_oth.append(use)

name_list_A = sz[['代码','名称']]
name_list_oth = pd.concat([cyb[['代码','名称']],kcb[['代码','名称']]])
name_list_A.columns=['id','name']
name_list_oth.columns = ['id','name']

'''抓取所有A股股票的市值'''
max_latest_A = pd.concat(max_latest_A)
max_latest_oth = pd.concat(max_latest_oth)
max_latest_A = pd.merge(max_latest_A,name_list_A,how='left',on='id')
max_latest_oth = pd.merge(max_latest_oth,name_list_oth,how='left',on='id')

A_id_list = list()
A_name_list = list()
A_price_list = list()

for num in range(227):
    url_for_A = 'http://10.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407839167742232578_1624430313017&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1624430313018'.format(num+1)
    
    data = requests.get(url_for_A).text
    p_A_parter = '"f12":"(.*?)","f13":.*?,"f14":"(.*?)".*?"f20":(.*?),'
    exp = re.findall(p_A_parter,data)

    for info in exp:
        A_id_list.append(info[0])
        A_name_list.append(info[1])
        if len(info[2])>3:
            A_price_list.append(info[2])
        else:
            A_price_list.append(0)
        
        
result_A = pd.DataFrame(A_id_list,columns=['id'])
# result_A['name'] = A_name_list
result_A['market_value'] = [float(x) for x in A_price_list]
result_A = result_A.drop_duplicates(subset=['id'],keep='first')

max_latest_A = pd.merge(max_latest_A,result_A,how='left',on='id')
max_latest_oth = pd.merge(max_latest_oth,result_A,how='left',on='id')   #市值加入到oth文件
max_latest_A.to_excel('A股max_latest{}.xlsx'.format(date_work),index=False)
max_latest_oth.to_excel('oth股max_latest{}.xlsx'.format(date_work),index=False)
'''以上包括A股科创及科创版的股票最高值与最近一个交易日数据'''



# '''抓取所有港股信息,港股市值'''
# import yfinance as yf

# p_parter = '{"f12":"(.*?)","f14":"(.*?)"}'
# result = list()
# for num in range(1,228):
#     url = 'https://96.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112407235435102812313_1624342351277&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:128+t:3,m:128+t:4,m:128+t:1,m:128+t:2&fields=f12,f14&_=1624342351529'.format(num)
#     res = requests.get(url).text
#     result.append(re.findall(p_parter, res))

# id_list = list()
# name_list = list()

# for i in range(len(result)):
#     for x in range(20):
#         try:
#             id_list.append(result[i][x][0][1:])
#             name_list.append(result[i][x][1])
#         except:
#             print(i)


# result_frame = pd.DataFrame(id_list,columns=['id'])
# result_frame['name'] = name_list

# headers={
#     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
#     'Cookie':'qgqp_b_id=d95dc61b8dfc838639e60415d7dfbbfe; st_si=78001780166796; st_asi=delete; HAList=d-hk-06122%2Cd-hk-00745%2Cd-hk-00336%2Cd-hk-03868%2Cd-hk-01752; st_pvi=04073110256380; st_sp=2021-06-22%2013%3A46%3A20; st_inirUrl=http%3A%2F%2Fquote.eastmoney.com%2Fhk%2F00593.html; st_sn=22; st_psi=20210623103733960-113200301322-1903844839',
#     'Host': 'push2.eastmoney.com',
#     'Referer': 'http://quote.eastmoney.com/'
#     }
# result_list = list() 
# p_HK_price = '"f117":(.*?),'
# for id_num in id_list[:]:
#     now = round(time.time() * 1000)
#     now02 = now - 26
#     url = 'http://push2.eastmoney.com/api/qt/stock/get?secid=116.{}&fields=f18,f59,f51,f52,f57,f58,f106,f105,f62,f108,f177,f43,f46,f60,f44,f45,f47,f48,f49,f113,f114,f115,f85,f84,f169,f170,f161,f163,f164,f171,f126,f168,f162,f116,f55,f92,f71,f50,f167,f117,f86,f172,f174,f175&ut=e1e6871893c6386c5ff6967026016627&fltt=2&invt=2&cb=jQuery.jQuery26623753828877605_{}&_={}'.format(('0'+id_num),now,now02)
      
#     res = requests.get(url,headers=headers).text
#     result_price = re.findall(p_HK_price, res)
#     result_list.append(result_price)
    
# HK_price_list = list()
# for x in range(len(result_list)):
#     if len(result_list[x])>0:
#         if len(result_list[x][0])>4:
#             HK_price_list.append(float(result_list[x][0]))
#         else:
#             HK_price_list.append(0.0)
#     else:
#         HK_price_list.append(0.0)
        

# result_frame['market_value'] = HK_price_list
# passed_HK = result_frame

# half_year = (datetime.datetime.now() - datetime.timedelta(days=180))
# passed_HK = pd.read_excel('港股名单.xlsx',engine='openpyxl')#录入港股数据名单   #不支持xlsx文件，加engine='openpyxl'

# '''抓取港股的股票最高和最近'''
# def order_for_id_HK(data,num):
#     for m in range(len(data)):
#         data.iloc[m,num]=str(data.iloc[m,num])
#         if len(data.iloc[m,num])<4:
#             data.iloc[m,num]=str(0)+data.iloc[m,num]       
#         if len(data.iloc[m,num])<4:
#             data.iloc[m,num]=str(0)+data.iloc[m,num]
#         if len(data.iloc[m,num])<4:
#             data.iloc[m,num]=str(0)+data.iloc[m,num]
#     return data
# passed_HK = order_for_id_HK(passed_HK, 3)
# passed_HK = passed_HK.dropna()

# result_for_HK = list()

# for name in passed_HK['id']:
#     try:
#         exp = yf.download('{}.HK'.format(name))
#         exp['date'] = exp.index
#         exp.reset_index(inplace=True,drop=True) 
#         use = exp.loc[[(exp[exp['date'] > half_year]['Adj Close']).idxmax(),len(exp)-2]]     #
#         use = use[['Close']].T
#         use.columns=['max','latest']
#         use['id'] = [name]
#         result_for_HK.append(use)
#     except:
#         print("111")
#         continue

# final = pd.concat(result_for_HK)
# final = pd.merge(final,result_frame,on='id',how='left')
# # final.index = passed_HK['id']+passed_HK['name']
# final.to_excel('HK_max_latest{}.xlsx'.format(date_work))













# ##########################################################################################
# "港股最近半年最大值、最近一日收盘价"
# import akshare as ak
# import pandas as pd
# import time 
# import numpy as np
# import datetime
# from dateutil.relativedelta import relativedelta
# from openpyxl import load_workbook
# import xlsxwriter
# import openpyxl
# from openpyxl.styles import PatternFill,Font,Alignment


# def getLastWeekDay(day=datetime.datetime.now()):
#     now=day
#     if now.isoweekday()==1:
#       dayStep=3
#     else:
#       dayStep=1
#     lastWorkDay = now - datetime.timedelta(days=dayStep)
#     return lastWorkDay
# date_work=getLastWeekDay().strftime('%Y%m%d')

# "基金代码前面补0"
# def bu_zero(fund_id,id_id):
#     "基金代码前面补0"
#     "fund_id：df名称  id_id:需要修改的列"
#     fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:'00000'+x if len(x)==1 else
#                                       ('0000'+x if len(x)==2 else 
#                                        ('000'+x if len(x)==3 else
#                                         ('00'+x if len(x)==4 else
#                                          ('0'+x if len(x)==5 else x)))))
#     return fund_id


# half_year = (getLastWeekDay() - datetime.timedelta(days=180)).strftime('%Y%m%d')

# "返回所有港股代码"
# hk_stock_id = ak.stock_hk_spot_em()
# "所有港股前一日收盘，180天最大收盘价"
# hk_stock = pd.DataFrame()
# hk_id_erro = pd.DataFrame()
# for index,row in hk_stock_id.iterrows():
#     try:
#         hk_stock_b = ak.stock_hk_hist(symbol="{}".format(row['代码']), start_date="{}".format(half_year),
#                                             end_date="{}".format(date_work), adjust="")[['日期','收盘']].sort_values(by='日期',ascending=0).reset_index(drop=True)
#         hk_stock_b_all = hk_stock_b.head(1)  #取最近一个交易日
#         hk_stock_b_all['max180'] = hk_stock_b['收盘'].max()  #180天内最大的收盘价
#         hk_stock_b_all['代码'] = row['代码']
#         hk_stock = hk_stock.append(hk_stock_b_all)
#         print(index,row['代码'])
#     except:       
#         hk_id_erro = hk_id_erro.append(pd.DataFrame([[index,row['代码']]]))
#         print(index,'{}  错误'.format(row['代码']))
#         continue   

# hk_stock = hk_stock.reset_index(drop=True)

# "获取港股市值"

# hk_stock_mk_id = ak.stock_hk_eniu_indicator(symbol="hk01093", indicator="港股")[['stock_id','stock_number']].reset_index(drop=True)
# hk_stock_mk = pd.DataFrame()
# hk_stock_mk_erro = pd.DataFrame()
# for index,row in hk_stock_mk_id.iterrows():
#     try:
#         hk_stock_mk_b = ak.stock_hk_eniu_indicator(symbol="{}".format(row['stock_id']), indicator="市值").sort_values(by='date',ascending=0).reset_index(drop=True).head(1)
#         hk_stock_mk_b['stock_id'] = row['stock_id']
#         hk_stock_mk = hk_stock_mk.append(hk_stock_mk_b)
#         print(index,row['stock_id'])
#     except:       
#         hk_stock_mk_erro = hk_stock_mk_erro.append(pd.DataFrame([[index,row['stock_id']]]))
#         print(index,'{}  错误'.format(row['stock_id']))
#         continue   
    
    
# hk_stock_mk = pd.merge(hk_stock_mk,hk_stock_mk_id,on='stock_id',how='left')    
# hk_stock = pd.merge(hk_stock,hk_stock_mk,left_on='代码',right_on='stock_number',how='left')
# hk_stock = hk_stock[['代码','日期','收盘','max180','market_value']]
















