# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 13:03:00 2021

@author: 86178
"""



import pandas as pd
import requests
import time
import execjs
import time 
import re
import numpy as np
import datetime
import pymysql
from bs4 import BeautifulSoup as bs

# sql = 'SELECT * FROM rank_data.`20221025`;'
# con = pymysql.connect(host='192.168.10.166', user='root', password='123456', database='rank_data')
# df = pd.read_sql(sql, con)

df = pd.read_excel('20230120.xlsx',engine='openpyxl',dtype={'id':'str'}) 

# df.drop(['index','Q1', 'Q2', 'Q3', 'Q4','buy'],axis=1,inplace=True)

data_id = [x for x in df['id']]

result_final = list()
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}  



############修改：20221026############

data_id_df = pd.DataFrame(data_id)
# for x in data_id:
for index,row in data_id_df[:].iterrows():
    
    # url = 'http://fundf10.eastmoney.com/jjjl_{}.html'.format(x)
    url = 'http://fundf10.eastmoney.com/jjjl_{}.html'.format(row[0])      
    data = requests.get(url,headers=headers).text

    soup = bs(data,'lxml')
    list1 = soup.find_all(class_='w782 comm jloff')
    list2 = list()
    for i in list1:
        list2.append(i)


    exp = bs(str(list2[0]),'lxml')
    list3 = exp.find_all(name='td')
    exp_list = list()
    for l in list3:
        exp_list.append((str(l)))

    for m in range(len(exp_list)):
        exp_list[m] = re.sub(u"\\(.*?\\)|\\{.*?\\}|\\<.*?\\>|\\<.*?\\>", "", exp_list[m])
        
    result = pd.DataFrame(columns=['起始时间','截至时间','经理','持有时间','收益'])
    list_num = [exp_list[i:i+5] for i in range(0, len(exp_list), 5)]
    for r in range(len(list_num)):
        result.loc[r] = list_num[r]
    result_final.append(result)
    
    
    print(index,row[0])
############修改：20221026############    




for num in range(len(result_final)):
    result_final[num]['id'] = data_id[num]
    
result_final = pd.concat(result_final)

result_final.to_sql('manager_history',con='mysql+pymysql://root:123456@192.168.10.219/project?charset=utf8',if_exists='replace')
result_final.to_excel('manager_history.xlsx',index=False)
































