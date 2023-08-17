# -*- coding: utf-8 -*-
"""
Created on Fri Aug  6 15:24:30 2021

@author: Administrator
"""

import pandas as pd
import numpy as np 
import time
import datetime
import pymysql
con = pymysql.connect(host='192.168.10.167', user='root', password='123456', database='all_info_data')
def get_oneid(id):
    
    sql = 'SELECT * FROM all_info_data.`{}`;'.format(id)
    data = pd.read_sql(sql,con)
    data=data[data[data['days']=='20180102'].index[0]:][:]
    data['id']=id
    return data


all_info=[]
"用excel，数据拿到id,data为df格式，id列下为字符串格式"

# data_id = [x for x in data['id']]


data_id=['004224']


for i in data_id:
    one_info=get_oneid(i)
    all_info.append(one_info)
    
all_datas=pd.DataFrame()
all_datas=pd.concat(all_info)