# -*- coding: utf-8 -*-
"""
Created on Fri Feb 26 16:21:21 2021

@author: 86178
"""

import pandas as pd
import numpy as np
import requests
import re
from selenium import webdriver
import time
import datetime
import pymysql
import yfinance as yf
from dateutil.relativedelta import relativedelta

# 测试
#info = yf.download('AAAU','2021-07-01','2021-07-02')
#info = yf.download('AAAU')

data = list()
def get_fund(url):
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'}      # 全屏
    # dtl = {'ak': ak,'address': address,'output': output}
    infom=requests.get(url,headers=headers).text
    return infom
   


urls = ['https://finviz.com/screener.ashx?v=141&f=ind_exchangetradedfund&r={}'.format(x) for x in range(1,2024,20)]
for i in range(102):
    data.append(get_fund(urls[i]))
    
    
final_data = list()
final_name = list()
    
info = re.compile('class="screener-link">(.*?)</a></td>')
p_name = re.compile('class="screener-link-primary">(.*?)</a></td>')
for x in range(len(data)):
    data[x] = data[x].replace('\n','').replace('\r','').replace(' ','')
    data[x] = data[x].strip()
    
    res=info.findall(data[x])
    name   = p_name.findall(data[x])
    final_data.append(res)
    final_name.append(name)
    

data_final = pd.DataFrame()

for i in range(len(final_data)):
    for x in range(len(final_data[i])):
        final_data[i][x]=final_data[i][x].replace('<spanclass="is-green">','').replace('</span>','').replace('<spanclass="is-red">','')
    
bijiao=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]

for i in range(len(final_data)):
    for x in range(len(final_data[i])):
        bijiao[x%15].append(final_data[i][x])
    
    
data_final = pd.DataFrame(columns=['No.','Perf Week','Perf Month','Perf Quart','Perf Half','Perf Year','Perf YTD','Volatility W','Volatility M','Recom','Avg Volume','Rel Volume','Price','Change','Volume'])
for i in range(len(bijiao)):
    data_final.iloc[:,i]=bijiao[i]
    

name = list()
for i in range(len(final_name)):
    for x in final_name[i]:
        name.append(x)
    
data_final['name']=name
data_final.to_excel('美股etf数据0813.xlsx',index=False)

'''抓取时间20分钟'''


# def get_data(num):
#     return yf.download(num)

# def calculation(num):
#     data = yf.download(num)
#     time.sleep(4)
#     now = datetime.datetime.now()
#     delta=datetime.timedelta(days=365)
#     time_before = now - delta
    
#     data = data[data.index>time_before]
    
#     res = list()
#     for numb in range(1,len(data)):
#         res.append(np.log(data.iloc[numb,4]/data.iloc[numb-1,4]))
#     return np.std(res)*np.sqrt(365)



def calculation(time_list,num,delta):
    
    info = yf.download(num)
    
    time_before_list = list()
    for i in range(len(time_list)):
        time = datetime.datetime.strptime(time_list[i],"%Y%m%d")
        time_before = time - delta
        time_before_list.append(time_before)
    
    drowback_result = list()
    for n in range(len(time_list)):
        result = pd.merge(info[info.index>time_before_list[n]],info[info.index<time_list[n]],how='inner')
        result = [x for x in result['Close']]
        drowback = list()
        for m in range(len(result)-1):
            drowback.append((result[m]-min(result[m+1:]))/result[m])
        if len(drowback)!=0:
            drowback_result.append(max(drowback))
    
    drowback_result = pd.DataFrame(drowback_result,columns=([num]))
    if len(drowback_result)!=0:
        time_line = time_list[-len(drowback_result):]
    else:
        time_line = []
    drowback_result.index = time_line

    print(num)
    
    data = info
    now = datetime.datetime.now()
    delta_year=datetime.timedelta(days=365)
    time_before = now - delta_year
    
    data = data[data.index>time_before]
    
    res = list()
    for numb in range(1,len(data)):
        res.append(np.log(data.iloc[numb,4]/data.iloc[numb-1,4]))
        
    std_num = np.std(res)*np.sqrt(365)
    return drowback_result,std_num

# res_stand = list()
# for num in name:
#     res_stand.append(calculation(num))
# data_final['波动率'] = res_stand

data_final=pd.read_excel('美股etf数据0802.xlsx')
id_list = [x for x in data_final['name']]
time_list = [datetime.datetime.now().strftime('%Y%m%d')]
delta = datetime.timedelta(days=365)

# def calculation(time_list,num,delta):
#     info = yf.download(num)
    
#     time_before_list = list()
#     for i in range(len(time_list)):
#         time = datetime.datetime.strptime(time_list[i],"%Y%m%d")
#         time_before = time - delta
#         time_before_list.append(time_before)
    
#     drowback_result = list()
#     for n in range(len(time_list)):
#         result = pd.merge(info[info.index>time_before_list[n]],info[info.index<time_list[n]],how='inner')
#         result = [x for x in result['Close']]
#         drowback = list()
#         for m in range(len(result)-1):
#             drowback.append((result[m]-min(result[m+1:]))/result[m])
#         if len(drowback)!=0:
#             drowback_result.append(max(drowback))
    
    
#     drowback_result = pd.DataFrame(drowback_result,columns=([num]))
#     if len(drowback_result)!=0:
#         time_line = time_list[-len(drowback_result):]
#     else:
#         time_line = []
#     drowback_result.index = time_line

#     print(num)
#     return drowback_result



result_dict = {}

for i in range(len(id_list)):
    try:
        result_dict[id_list[i]] = calculation(time_list,id_list[i], delta)
        del id_list[i]
    except:
        print('erro')
        continue

exp = list()
exp_std_list = list()
for i in result_dict:
    exp.append(result_dict[i][0].iloc[0,0])
    exp_std_list.append(result_dict[i][1])
    
final_info = pd.DataFrame()
final_info['drowback'] = exp
final_info['std'] = exp_std_list
final_info['id'] = result_dict.keys() 
final_info.to_excel('最大回撤和标准差（全部）.xlsx')

final_info = pd.merge(final_info,data_final,how='right',on='name')
final_info.to_sql('std_drowback',con='mysql+pymysql://root:123456@192.168.10.167/base_etf?charset=utf8',if_exists='replace')



















