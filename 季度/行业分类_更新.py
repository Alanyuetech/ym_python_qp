# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 14:38:14 2020

@author: 86178
"""

import pandas as pd
import numpy as np
import re


data_company=pd.read_csv('持仓_20230128.csv',dtype={'id':str})
data_percent=pd.read_csv('占比_20230128.csv',dtype={'id':str})
data_info=pd.read_excel('info_20230128.xlsx',engine='openpyxl',dtype={'id':str})
data_industry=pd.read_excel('industry岳20230127.xlsx',engine='openpyxl',dtype={'id':str})   #之前为industry.xlsx  20221026



for x in range(len(data_company)):
    for i in range(10):
        try:
            data_company.iloc[x,i]=data_company.iloc[x,i].replace(r" ",'')
        except:
            print('NA')

        
data_experiment=data_company.copy()
data_experiment.dropna(inplace=True)
#data_experiment=data_experiment.iloc[0:10,:]

data_experiment_percent=data_percent.copy()
data_experiment_percent.dropna(inplace=True)#data_experiment_percent=data_experiment_percent.iloc[0:10,:]

data_experiment_percent.reset_index(drop=True,inplace=True)
data_experiment.reset_index(drop=True,inplace=True)

first_try=list()
for x in range(len(data_experiment)):
    i=list(data_experiment.iloc[x,0:10].values)
    for m in i:
        try:
            first_try.append(str(data_industry[data_industry['name']==m]['industry'].values))
        except:
            first_try.append('N')
    
step=10
name=list()
for x in data_experiment['id'].values:
    name.append(str(x))
    
first_try_1_copy=[pd.DataFrame(first_try[i:i+step]) for i in range(0,len(first_try),step)]

first_try_2_copy=pd.DataFrame(columns=name)
first_try_2_copy.reset_index(drop=True,inplace=True)

for x in range(len(first_try_1_copy)):
    first_try_2_copy[str(name[x])]=first_try_1_copy[x].iloc[:,0]
    

first_try_2=data_experiment_percent.T
first_try_2.columns=name
first_try_2.drop(['id'],axis=0,inplace=True)

first_try_2_copy.reset_index(drop=True,inplace=True)
first_try_2.reset_index(drop=True,inplace=True)
first_try_2=first_try_2.replace('---','0%')
final_math=list()

for x in first_try_2_copy:
    bus={}
    for z in first_try_2_copy[x].unique():
        per=list()
        for m in (first_try_2_copy[first_try_2_copy[x]==z]).index:
           per.append(float(str(first_try_2[x][m]).strip('%'))/100)
        bus[z]=sum(per)
    final_math.append(bus)
         

sign=list()
for i in final_math:
    sign_inside=list()
    if max(i.values())<0.1:
        sign.append(['混合'])
    else:
        for x in i:
            if i[x] >=0.1:
                    sign_inside.append(x)
        sign.append(sign_inside)


"此处灵活调整"
data_sign=pd.DataFrame(sign,columns=['行业1','行业2','行业3','行业4','行业5'])
# data_sign=pd.DataFrame(sign,columns=['行业1','行业2','行业3','行业4'])


data_sign['id']=name
data_sign['id']=data_sign['id'].astype(str)
data_sign=pd.merge(data_sign,data_info,on='id',how='inner')

data_sign=data_sign.fillna('--')

for i in range(len(data_sign)):
    for m in range(5):
        data_sign.iloc[i,m]=data_sign.iloc[i,m].replace('[]','海外或港股')
        data_sign.iloc[i,m]=data_sign.iloc[i,m].replace('[','').replace(']','')
        # data_sign.iloc[i,m]=data_sign.iloc[i,m].replace('--','NA')
        data_sign.iloc[i,m]=data_sign.iloc[i,m].replace("'","")
        
# data_sign.to_excel('行业分类.xlsx',index=False)
"第一列全是港股也别管了"
data_sign.to_sql('data_classify',con='mysql+pymysql://root:123456@192.168.10.219/project?charset=utf8',if_exists='replace')
data_sign.to_excel('data_classify.xlsx',index=False)
print('完成')




























































