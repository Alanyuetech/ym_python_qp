# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 13:23:23 2020

@author: 86178
"""

import requests
import re
from selenium import webdriver
import pandas as pd
import numpy as np
import datetime
import pymysql


# sql = 'SELECT * FROM rank_data.`20210720`;'
# con = pymysql.connect(host='192.168.10.167', user='root', password='123456', database='rank_data')
# df = pd.read_sql(sql, con)

# df.drop(['index','Q1', 'Q2', 'Q3', 'Q4','buy'],axis=1,inplace=True)

df=pd.read_excel('20230120.xlsx',engine='openpyxl',dtype={'id': 'str'})    #文件换成最新的每日跑出来的文件


headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Referer':'http://fund.eastmoney.com/',
    }

# def order_for_id(data,num):
#     for m in range(len(data)):
#         data.iloc[m,num]=str(data.iloc[m,num])
#         if len(data.iloc[m,num])<6:
#             data.iloc[m,num]=str(0)+data.iloc[m,num]       
#         if len(data.iloc[m,num])<6:
#             data.iloc[m,num]=str(0)+data.iloc[m,num]
#         if len(data.iloc[m,num])<6:
#             data.iloc[m,num]=str(0)+data.iloc[m,num]
#         if len(data.iloc[m,num])<6:
#             data.iloc[m,num]=str(0)+data.iloc[m,num]
#         if len(data.iloc[m,num])<6:
#             data.iloc[m,num]=str(0)+data.iloc[m,num]
#     return data
# data_kind = order_for_id(data_kind, 0)

# id_list = [x for x in data_kind['id']]

# finish_id = [x for x in items['id']]
# id_list = list(set(id_list).difference(set(finish_id)))

hold_info=list()
index_id=list()
hold_detail=list()
missing=list()
day_detail={}

import threading
import time
lock=threading.Lock()

urls = [x for x in df['id']]

def get_info_one_page(id_num):
    try:
        url = "http://fund.eastmoney.com/{}.html".format(id_num)
        p_stock='<tr>  <td class="alignLeft">   <a href=.*? title=.*?>(.*?)</a>  </td>  <td class="alignRight bold">(.*?)</td>'
        p_size = '<td><a href=".*?">基金规模</a>：(.*?)亿元.*?</td>'
        p_manager = '<td>基金经理：<a href=".*?">(.*?)</a>'
        p_company = '<td><span class=".*?">管 理 人</span>：<a href=".*?">(.*?)</a></td>'
        p_name='<span class="funCur-Tit">基金名称：</span><span class="funCur-FundName">(.*?)</span></div>'
        p_days="class='end_date'>持仓截止日期: (.*?)</span>"
        p_kind = '<td>基金类型：<a href=".*?">(.*?)</a>'
        
        data_middle=[]
        data_middle = requests.get(url,headers=headers)
        
        html=data_middle.content
        html_doc=str(html,'utf-8') #html_doc=html.decode("utf-8","ignore")
        data_find=re.compile(p_stock,re.S)
        data_size = re.compile(p_size,re.S)
        data_manager = re.compile(p_manager,re.S)
        data_company = re.compile(p_company,re.S)
        data_name = re.compile(p_name,re.S)
        data_days=re.compile(p_days,re.S)
        data_kind = re.compile(p_kind,re.S)
        
        all_data=" ".join('%s' %a for a in data_middle)
        
        info_num=re.findall(data_find,html_doc)
        info_num=pd.DataFrame(info_num,columns=['name','percent'])
        info_num['id'] = np.repeat(id_num,len(info_num),axis=0)
        
        size = re.findall(data_size,html_doc)
        manager = re.findall(data_manager,html_doc)
        name=re.findall(data_name,html_doc)
        company_info = re.findall(data_company,html_doc)
        days = re.findall(p_days,html_doc)[0]
        kind = re.findall(data_kind, html_doc)
    
        
        company=list()
        for x in info_num['name']:
            try:
                company.append(x.strip('<'))
            except:
                company.append(x)
                    
        info_num['company']=company
        info_num=info_num.drop('name',axis=1)
        info_detail = pd.DataFrame()
        info_detail['company']=company_info
        info_detail['size']=size
        info_detail['manager'] = manager
        info_detail['name']=name
        info_detail['id']=id_num
        info_detail['kind']=kind
    except:
        
        info_num = pd.DataFrame()
        info_detail = pd.DataFrame()
        days = []
        
    return info_num,info_detail,days
    

def get_url():
    global urls
    lock.acquire()
    if len(urls)==0:
        lock.release()
        return ""
    else:
        url=urls[0]
        del urls[0]
    lock.release()
    return url

class SpiderThread (threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name=name
    def run(self):
        while True:
            url=get_url()
            if url !="":
                try:
                    info_num,info_detail,days=get_info_one_page(url)
                    hold_info.append(info_num)
                    # hold_info.append(url)
                    hold_detail.append(info_detail)
                    day_detail['{}'.format(url)]=days
                    # print(url)
                except:
                    missing.append(url)
                    print(url)
            else:
                break
            

if __name__=='__main__':
    
    thread1 = SpiderThread('thread1')
    thread2 = SpiderThread('thread2')
    thread3 = SpiderThread('thread3') 
    thread4 = SpiderThread('thread4')
     
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()

hold_info_try=hold_info.copy()
hold_info_try=pd.concat(hold_info_try)

data_buy_company = pd.DataFrame()
data_buy_percent = pd.DataFrame()

list_app_id=list()
# list_app_id=pd.DataFrame(list_app_id)
# list_app_id.to_excel('aaa.xlsx')
hold_errs=[]
for i in range(len(hold_info)):#dataframe
    try:
        m=hold_info[i].T
        list_app_id.append(m.iloc[1,0])
        data_buy_company=data_buy_company.append(m.iloc[2,:10],ignore_index=True)
    except:
        # hold_errs.append(i)
        print(i)
data_buy_company['id']=list_app_id  
company_columns=['hold1','hold2','hold3','hold4','hold5','hold6','hold7','hold8','hold9','hold10','id']
data_buy_company.columns=company_columns

list_app_id=list()

for p in range(len(hold_info)):
    try:
        n=hold_info[p].T
        list_app_id.append(n.iloc[1,0])
        data_buy_percent=data_buy_percent.append(n.iloc[0,:10],ignore_index=True)
    except:
        print(n)
        
data_buy_percent['id']=list_app_id
percent_columns=['percent1','percent2','percent3','percent4','percent5','percent6','percent7','percent8','percent9','percent10','id',]
data_buy_percent.columns=percent_columns

day_final=list()
for x in data_buy_company['id']:
    day_final.append(day_detail[str(x)])

data_process = pd.concat(hold_detail,axis=0)
data_process.index=range(len(data_process))


data_buy_company['days']=day_final
data_buy_percent['days']=day_final

hold_final=pd.concat(hold_detail)

import datetime
now = datetime.datetime.now().strftime('%Y%m%d')
hold_final.to_excel('info_{}.xlsx'.format(now))

result = pd.merge(data_buy_company,hold_final,how='left',on='id')
result = pd.merge(data_buy_percent,result,how='left',on='id')

result.to_csv('all_info_{}.csv'.format(now))
data_buy_company = data_buy_company.fillna('---')
data_buy_percent = data_buy_percent.fillna('---')

hold_final.to_csv('{}info.csv'.format(now))
data_buy_company.to_csv('持仓_{}.csv'.format(now))
data_buy_percent.to_csv('占比_{}.csv'.format(now))

hold_final.to_excel('info_result.xlsx',index=False)
data_buy_company.to_excel('company_result.xlsx',index=False)
data_buy_percent.to_excel('percent_result.xlsx',index=False)

# 换一下文件名,将三个CSV文件都存入数据库

# datass=pd.read_csv('持仓_20210726.csv',dtype={'id':str})


data_buy_company.to_sql('company_result',con='mysql+pymysql://root:123456@192.168.10.219/project?charset=utf8',if_exists='replace')

data_buy_percent.to_sql('percent_result',con='mysql+pymysql://root:123456@192.168.10.219/project?charset=utf8',if_exists='replace')

hold_final.to_sql('info_result',con='mysql+pymysql://root:123456@192.168.10.219/project?charset=utf8',if_exists='replace')



# list_app_id[313]
# list_app_id[314]
# list_app_id=pd.DataFrame(list_app_id,columns=['id'])
# list_app_id.drop([313,314],inplace=True)

# data_buy_company.to_excel('fill_1_company.xlsx')
# data_buy_percent.to_excel('fill_1_percent.xlsx')
# data_process.to_excel('fill_1_info.xlsx')

# missing=list()
# for x in data['id'].values:
#     if x not in data_buy_company['id'].values:
#         missing.append(x)
        
# missing=list()
# for x in data['id'].iloc[2001:4000].values:
#     if x not in data_buy_company['id'].values:
#         missing.append(x)
# missing=pd.DataFrame(missing,columns=['id'])
# missing.to_excel('missing_1.xlsx',index=False)


# delta=datetime.timedelta(days=270)
# delta_56=datetime.timedelta(days=56)

# now = datetime.datetime.now()

# now_use=now.strftime('%Y%m%d')
# delta_1=datetime.timedelta(days=1)
# yesterday=now-delta_1
# yesterday=yesterday.strftime('%Y%m%d')


# after_use = (now-delta).strftime('%Y%m%d')
# after_56=(now-delta_56).strftime('%Y%m%d')
# url='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn10000;ddesc;qsd'+after_56+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
# option = webdriver.ChromeOptions()
# option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
# browser=webdriver.Chrome(chrome_options=option)        # 全屏
# browser.get(url)
# element = browser.find_element_by_css_selector('#allfund')
# browser.execute_script("arguments[0].click();",element)
# time.sleep(8)
# data=browser.page_source
# browser.quit()
# p_id_num='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
# id_num=re.findall(p_id_num,data,re.S)
# data_final=pd.DataFrame()
# data_final['id']=id_num

# p_name='<td><a href="http://fund.eastmoney.com/.*?.html" title="(.*?)">.*?</a></td>'
# id_name=re.findall(p_name,data,re.S)
# data_final['name']=id_name


# data_back=data_process.copy()
# data_back.drop(['id'],axis=1,inplace=True)
# data_back_1=pd.merge(data_back,data_final,how='inner',on='name')

# data_back_1.to_excel('1_info.xlsx',index=False)



'''info_company = list()
for id_num in hold_info:
    for inf in hold_info[id_num].iloc[:,1]:
        info_company.append(inf)
        
company_name=set(info_company)
count_num=list()

for name in company_name:
    count=0
    for stock_name in info_company:
        if stock_name == name:
            count+=1
    count_num.append(count)
 
data_use=pd.DataFrame(company_name)
data_use['times']=count_num
            
info_stock.to_excel('持仓百分比.xlsx')
data_use.to_excel('公司出现次数.xlsx')

info_percent=pd.DataFrame()
for i in hold_info:
    info_percent[i]=hold_info[i].iloc[:,0]

data_model = pd.read_excel('行业股份公司划分.xls')
    
    
data_acquire=hold_info.copy()

for x in data_acquire:
    data_acquire[x].drop('percent',axis=1,inplace=True)
    
for x in data_acquire:
    data_acquire[x]=data_acquire[x].T
    
data_final=list()

for x in data_acquire:
    data_final.append(data_acquire[x].values)
    
data_new= pd.DataFrame()
for i in data_final:
        data_new = data_new.append(pd.DataFrame(i), ignore_index=True)
    
data_new.index=data_acquire.keys()
        
list(range(10))    

data_final=pd.DataFrame(data_final) 
data_new.to_excel('持仓.xlsx')'''


















































































