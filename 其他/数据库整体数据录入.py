# -*- coding: utf-8 -*-
"""
Created on Fri Jun 25 15:11:23 2021

@author: 86178
"""
import pandas as pd
import requests
import time
import execjs
import time 
import re
import pymysql


def getUrl(fscode):
  head = 'http://fund.eastmoney.com/pingzhongdata/'
  tail = '.js?v='+ time.strftime("%Y%m%d%H%M%S",time.localtime())
  return head+fscode+tail
def get_info(num):
    # num = '000828'
        #用requests获取到对应的文件
    content = requests.get(getUrl('{}').format(num))
    
    #使用execjs获取到相应的数据
    jsContent = execjs.compile(content.text)
    
    name = jsContent.eval('fS_name')
    code = jsContent.eval('fS_code')
    
    #单位净值走势
    netWorthTrend = jsContent.eval('Data_netWorthTrend')
    #累计净值走势
    ACWorthTrend = jsContent.eval('Data_ACWorthTrend')
    netWorth = []
    Change = []
    ACWorth = []
    #提取出里面的净值
    
    for dayWorth in netWorthTrend:
            netWorth.append(dayWorth['y'])
            Change.append((dayWorth['equityReturn']))
            
    for dayACWorth in ACWorthTrend:
        ACWorth.append(dayACWorth[1])
        
    days=[]
    for day in netWorthTrend:
        time_day=float(day['x']/1000)
        timeArray = time.localtime(time_day)
        otherStyleTime = time.strftime("%Y%m%d", timeArray) 
        days.append(otherStyleTime)
        
    if len(days) != len(ACWorth):
        if None in ACWorth:
            ACWorth.remove(None)
    data_use=pd.DataFrame()
    data_use['days']=days
    data_use['ACC_price']=ACWorth
    data_use['Net_price']=netWorth
    data_use['p_change']=Change
    data_use = data_use.dropna()
    
    result = list()
    middle = 1
    for x in range(1,len(data_use)):
        middle = middle * (data_use.iloc[x,3]/100+1)
        result.append(middle)
    
    result.insert(0, data_use.iloc[0,1])
    data_use['price'] = result
    data_use.to_sql('{}'.format(num),con='mysql+pymysql://root:123456@192.168.10.167/all_info_data?charset=utf8',if_exists='replace')
    
    print('finish+',num)


con = pymysql.connect(host='192.168.10.167', user='root', password='123456', database='all_info_data')
sql = 'SELECT * FROM rank_data.`20210624`;'
data = pd.read_sql(sql,con)


data_id = [x for x in data['id']]
for i in data_id:
    get_info(i)
    
    
    
    
    
"运行在中间的时候重新开始"
for i in data_id[4763:]:
    get_info(i)
    
# pd.DataFrame(data_id).to_excel('data_id.xlsx')




















