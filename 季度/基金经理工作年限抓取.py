# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 14:20:38 2021

@author: 86178
"""

import pandas as pd
import numpy as np
import re
import requests
from selenium import webdriver
import time


data_comeout=list()
for x in range(66):            #当前全部基金经理有62页
    url = 'http://fund.eastmoney.com/manager/default.html#dt14;mcreturnjson;ftall;pn50;pi{};scabbname;stasc'.format(x+1)
    option = webdriver.ChromeOptions()    
    option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    browser=webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe',chrome_options=option) # 全屏
 
    browser.get(url)
    data = browser.page_source
    data_comeout.append(data)
    browser.quit()

all_data = " ".join('%s' %a for a in data_comeout)


all_data = all_data.replace(' ',"").replace('\n',"").replace('\t',"")

p_info = '<ahref="//fund.eastmoney.com/manager/.*?.html"title=".*?">(.*?)</a>'
one = re.findall(p_info, all_data)

p_com = '<td><ahref="//fund.eastmoney.com/company/.*?.html">(.*?)</a></td>'
two = re.findall(p_com, all_data)

p_year = '<tdclass="hypzxqxrjjtdl">.*?</a></td><td>(.*?)</td>'
three = re.findall(p_year, all_data)

data_final = pd.DataFrame()
data_final['name']=one
data_final['company']=two
data_final['time']=three
data_final.to_sql('manager_number',con='mysql+pymysql://root:123456@192.168.10.219/project?charset=utf8',if_exists='replace')
data_final.to_excel('manager_number.xlsx',index=False)

# data_301 = pd.read_excel('20210322du.xlsx')
# data_final['new'] = data_final['name']+data_final['company']
# data_301['new'] = data_301['manager']+data_301['company']
# data_final.drop(['name','company'],inplace=True,axis=1)
# data_final_301 = pd.merge(data_301,data_final,how='inner',on='new')
# data_final_301.drop(['new'],axis=1,inplace=True)

# data_final_301.to_excel('20210322du.xlsx')














































