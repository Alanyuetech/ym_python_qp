# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 22:38:08 2021

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

def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    
    
    return lastWorkDay

def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:str(x).zfill(6))
    return fund_id

date_work=getLastWeekDay().strftime('%Y%m%d')

# sql = 'SELECT * FROM rank_data.`{}`;'.format(date_work)
# con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='rank_data')
# df = pd.read_sql(sql, con)


df = pd.read_excel('{}.xlsx'.format(date_work),engine='openpyxl',dtype={'id':'str'}) 
# '''注:抓取速度,抓取50个基金的时间大概为1分半'''

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
nums=[x for x in df['id']]
#获取夏普和标准差
def get_ratio(num):
    url = 'http://fundf10.eastmoney.com/tsdata_'+num+'.html'
    r = requests.get(url,headers=headers)
    r.encoding='utf-8'
    data=r.text
    html=r.content
    
    data = requests.get(url,headers=headers).text
    
    data=data.replace(" ",'')
    data=data.replace('\n','').replace('\r','')
    p_standard_deviation='<td>标准差</td><tdclass=\'num\'>(.*?)</td><tdclass=\'num\'>(.*?)</td><tdclass=\'num\'>(.*?)</td>'
    data_SD=re.findall(p_standard_deviation, data)
    data_SD=[x for x in data_SD[0]]
    
    p_sharp_ratio='<td>夏普比率</td><tdclass=\'num\'>(.*?)</td><tdclass=\'num\'>(.*?)</td><tdclass=\'num\'>(.*?)</td>'
    p_information_ratio='<td>信息比率</td><tdclass="num">(.*?)</td><tdclass="num">(.*?)</td><tdclass="num">(.*?)</td>'
    
    data_Sharp=re.findall(p_sharp_ratio, data)
    data_Sharp=[x for x in data_Sharp[0]]
    
    
    data_info=pd.DataFrame()
    data_info['标准差']=data_SD
    data_info['夏普']=data_Sharp
    #data_info['信息比']=data_inf_ratio
    
    data_one_year=pd.DataFrame(data_info.iloc[0])
    data_one_year=data_one_year.T
    data_one_year['id']=num
    
    return data_one_year


res = list()
res_erro = list()
for i in nums[:]:
    try:
        res.append(get_ratio(i))
        print(i)
    except:
        res_erro.append(i)
        print(i,'错误')


##################################################################################
" 如果有输出代码，说明该代码没有跑出来，要重新跑进去       修改时间：20220112"
res_erro_list = list()
if res_erro != []:
    for i in res_erro:
        try:
            res.append(get_ratio(i))
            print(i)
        except:
            print(i,'错误')
    
    # res_erro_list = pd.concat(res_erro_list)
    # res = pd.concat([res,res_erro_list])
else:
    pass
##################################################################################




res = pd.concat(res)
# res.to_sql('sharp_and_standard',con='mysql+pymysql://root:123456@192.168.10.222/project?charset=utf8',if_exists='replace')
res.to_excel('sharp_and_standard.xlsx',index=False)
print('完成')










