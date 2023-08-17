# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 14:04:17 2020

@author: 86178
"""

import time
import datetime
from selenium import webdriver
import pandas as pd
import re
def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    
    
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y%m%d')
# 获取页面数据
def essential_infor(url):
    # chrome_options=webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    # browser=webdriver.Chrome(options=chrome_options)
    
    
    option = webdriver.ChromeOptions()    
    option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    browser=webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe',chrome_options=option) # 全屏
    
    

    browser.get(url)
    data=browser.page_source
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}
    
    p_title='<td><a href=.*?title="(.*?)">.*?</a>'
    title=re.findall(p_title,data,re.S)
    
    p_id='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
    id=re.findall(p_id,data,re.S)
    
    p_id_num='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
    id_num=re.findall(p_id_num,data,re.S)
    
    p_web='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href="(.*?)">.*?</a></td><td>'
    web=re.findall(p_web,data,re.S)
    
    p_days='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>.*?</a></td><td><a href=.*? title=.*?>.*?/a></td><td>(.*?)</td>'
    days=re.findall(p_days,data,re.S)
    
    p_info='<td class=.*?>(.*?)</td>'
    info=re.findall(p_info,data,re.S)
    
    
    title.pop()
    bijiao=[[],[],[],[],[],[],[],[],[],[],[],[],[]]
    
    
    for i in range(len(info)):
        bijiao[i%13].append(info[i])
    
    data_final=pd.DataFrame(data=bijiao,index=['单位净值','累计净值','日增长率','近1周','近1月','近3月','近6月','近1年'	,'近2年'	,'近3年'	,'今年来','成立来','自定义'],columns=title)
    data_final=data_final.T
    data_final['id']=id_num
    data_final['days']=days
    browser.quit()
    return data_final

# 计算时间周期
delta=datetime.timedelta(days=14)
now = datetime.datetime.now()
After=(now-delta).strftime('%Y%m%d')
now_use=now.strftime('%Y%m%d')
one=datetime.timedelta(days=1)
time_delta=list()
z=1
for i in range(26):
    z+=14
    time_delta.append(z)

def p_weeks_monday(p_weeks):
    week_n = now.weekday()
    n_monday = now - datetime.timedelta(days=week_n)   
    pweeks_monday = (n_monday - datetime.timedelta(days=p_weeks*7)).strftime('%Y%m%d')
    return pweeks_monday

start_monday = p_weeks_monday(3)
end_monday = p_weeks_monday(1)

url1='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;s6yzf;pn50000;ddesc;qsd{};qed{};qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'.format(start_monday,end_monday)

data1=essential_infor(url1)
data_middel=data1[['自定义','id']]
data_middel.columns=[time_delta[0],'id']
data_middel.index=data1.index

After=now-2*delta-one

for i in range(2,27):
    url='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;sqjzf;pn50000;ddesc;qsd'+After.strftime('%Y%m%d')+';qed'+now.strftime('%Y%m%d')+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    data=essential_infor(url)
    data.columns=['单位净值', '累计净值', '日增长率', '近1周', '近1月', '近3月', '近6月', '近1年', '近2年', '近3年','今年来', '成立来', 'week'+str(i), 'id', 'days']
    data_middel=pd.merge(data_middel,data[['week'+str(i),'id']],how='left',on='id')      # 之前是用inner   出现data_middel 和 data1的size不同，尝试改成left
    After=After-delta



import numpy as np

# for x in data_middel:
#     for i in range(len(data_middel)):
#         if data_middel.loc[i,x] =='---':
#             data_middel.loc[i,x]=0
           
# for x in list(data_middel.columns):
#     data_middel[x] = data_middel[x].str.strip('%').astype(float)/100     
data_middel=data_middel.fillna(0)

data_middel.index=data1.index
data_middel['id']=data1['id']


# 获取本地的基金数据
def read_items(address):
    items=pd.read_csv(address,converters = {u'id':str})
    return items


# items=read_items('info_result.csv')
items=pd.read_excel('info_20230128.xlsx',engine='openpyxl',dtype={'id':'str'})   #info_result是上上个季度的
items['id'] = items['id'].map(lambda x:'00000'+x if len(x)==1 else
                                  ('0000'+x if len(x)==2 else 
                                    ('000'+x if len(x)==3 else
                                    ('00'+x if len(x)==4 else
                                      ('0'+x if len(x)==5 else x)))))
data_final=pd.merge(data_middel,items,how='left',on='id')
# data_final.drop(['beizhu'],axis=1,inplace=True)



for x in data_final:
    for i in range(len(data_final)):
        if data_final.loc[i,x] =='--':
            data_final.loc[i,x]=0
           

'''以下是以基金的策略筛选'''

# sxmd = pd.read_excel('两周源数据  20210903.xlsx',dtype={'id':'str'})
# sxmd['id'] = sxmd['id'].map(lambda x:'00000'+x if len(x)==1 else
#                                   ('0000'+x if len(x)==2 else 
#                                    ('000'+x if len(x)==3 else
#                                     ('00'+x if len(x)==4 else
#                                      ('0'+x if len(x)==5 else x)))))
# sxmd_id = pd.DataFrame(sxmd['id'])

# data_final = pd.merge(left=sxmd_id,right=data_final,on='id')




def data_process_first(data_final):        
    data_final=data_final.fillna(0)
    data_final.index=range(len(data_final))
    
    data_final['size']=data_final['size'].astype('float')
    for i in range(len(data_final)):
        if data_final.loc[i,'size']<float(0.5):
            data_final=data_final.drop(i,axis=0)
    data_final.index=range(len(data_final))
    return data_final

data_final=data_process_first(data_final)

unsuitable=['债券指数', 'QDII', '定开债券', '债券型', 'QDII-指数','股票-FOF','混合-FOF','联接基金','FOF']
def data_process_second(data_final,unsuitable):
    for x in range(len(data_final)):
        if data_final.loc[x,'kind'] in unsuitable:
            data_final=data_final.drop([x],axis=0)
    return data_final
data_final=data_process_second(data_final,unsuitable)

black_list=['QDII','月','年','分级','债','标普','纳斯达克','全球','币','C']
def data_process_third(data_final,black_list):
    for x in black_list:
        data_final=data_final.drop(data_final[(data_final['name'].str.contains(x))].index)
    return data_final
data_final=data_process_third(data_final,black_list)      

data_final.to_excel('两周累计爬取.xlsx')

def data_process_fourth(data_final):
    index_id=list()
    for x in data_final['name']:
        x=re.sub(r'[a-zA-Z",:{}]', "", x)
        x=re.sub(r'[0-9]',"",x)
        x=x.strip(r'（）')
        x=x.strip('/')
        index_id.append(x)
    data_final['name']=index_id
    
    name_use=pd.DataFrame(columns=data_final.columns)
    for name_fact in range(len(data_final)):
        if data_final.iloc[name_fact,12] not in name_use.name.values:
            name_use=name_use.append(data_final.iloc[name_fact,:],ignore_index=True)
        
        elif name_use[name_use['name'].str.contains(data_final.iloc[name_fact,12])].size<data_final.iloc[name_fact,14]:        
                name_use.drop(name_use[name_use['name'].str.contains(data_final.iloc[name_fact,12])].index,inplace=True)
                name_use=name_use.append(data_final.iloc[name_fact,:],ignore_index=True)
        else:
            pass
    return name_use

data_final=data_process_fourth(data_final)  
data_final.to_excel('两周累计爬取_筛选{}.xlsx'.format(date_work),index=False)
























