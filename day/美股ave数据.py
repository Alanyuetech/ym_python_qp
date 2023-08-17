# -*- coding: utf-8 -*-
"""
Created on Wed May 12 11:09:37 2021

@author: Administrator
"""
import requests
import yfinance as yf
import numpy as np
import pandas as pd
import time
ave_sum=list()

timeStamp=time.time()
end_times=time.strftime('%Y-%m-%d',time.localtime(timeStamp))
end_time = time.strftime('%Y-%m-%d',time.localtime(timeStamp))
start_year = int(time.strftime('%Y',time.localtime(timeStamp))) - 1
month_day = time.strftime('-%m-%d',time.localtime(timeStamp))
start_time = '{}{}'.format(start_year,month_day)
# pro = ts.pro_api('b0aff7024a93fbe840a8b9fe37a9b765961dc2e643a6a1f94acfb2c5')

def get_ave(id):
    
    data = yf.download(id,start=start_time, end=end_times)
    # data = data.iloc[:219,:]
    
    
    
    result = list()
    # for i in range(len(data)-1):
    #     result.append(np.log(data['Close'][i]/data['close'][i+1]))
    #     pass
    
    data = data.iloc[:,:]
    data.reset_index(inplace=True,drop=True)
    result = list()
    for i in range(1,len(data)):
        result.append(np.log(data['Close'][i]/data['Close'][i-1]))
        pass
    sum_data=list()
    for i in range(len(result)-20):
        # print(i)
        sum_data.append(sum(result[i:20+i]))
    ave_sum.append(np.average(sum_data))
    
df=pd.read_excel('545ETF基金名单20210422.xlsx')
id_list=df['id']
allid=[]

for i in range(len(id_list)):
    get_ave(id_list[i])
    print(id_list[i])
    allid.append(id_list[i])
    
ave_data=pd.DataFrame(ave_sum,columns=['AVE'])
ave_data['id']=allid
ave_data.to_excel('美股近219天ave数据0816.xlsx',index=False)