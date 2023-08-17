# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 13:59:49 2022

@author: Administrator
"""


import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
import xlsxwriter
import openpyxl
from openpyxl.styles import PatternFill,Font,Alignment
from functools import reduce
import statsmodels.api as sm
from itertools import *
import torch
import torch.nn as nn

def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay
date_work=getLastWeekDay().strftime('%Y%m%d')

def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:str(x).zfill(6))
    return fund_id



sz50 = ak.index_zh_a_hist(symbol="000016", period="daily", start_date="19700101", end_date="22220101").rename(columns={'涨跌幅':'sz50涨跌幅'})
zz1000 = ak.index_zh_a_hist(symbol="000852", period="daily", start_date="19700101", end_date="22220101").rename(columns={'涨跌幅':'zz1000涨跌幅'})
index_data = pd.merge(sz50[['日期','sz50涨跌幅']],zz1000[['日期','zz1000涨跌幅']],on='日期').sort_values('日期',ascending=0).reset_index(drop=True)


#######################################################################################################################################

class LinearRegressionModel(nn.Module):
    def __init__(self,input_dim,output_dim):
        super(LinearRegressionModel,self).__init__()
        self.linear = nn.Linear(input_dim,output_dim)   #用到哪一层
    
    def forward(self,x):
        out = self.linear(x)    #前向传播如何走
        return out  
    
input_dim = 1
output_dim = 1
model = LinearRegressionModel(input_dim,output_dim)
    
epochs = 10000000
learning_rate = 0.00001
optimizer = torch.optim.SGD(model.parameters(),lr=learning_rate)    
criterion = nn.MSELoss()


for epoch in range(epochs):
    epoch += 1
    inputs = torch.from_numpy(np.array(index_data.loc[:4300,'zz1000涨跌幅']).reshape(-1,1))   #转格式为tensor
    labels = torch.from_numpy(np.array(index_data.loc[:4300,'sz50涨跌幅']).reshape(-1,1))       #转格式为tensor
    
    optimizer.zero_grad()
    
    outputs = model(inputs.float())
    
    loss = criterion(outputs, labels.float())
    
    loss.backward()
    
    optimizer.step()
    if epoch % 1000 ==0:
        print("epoch{} , loss {}".format(epoch,loss.item()))
    
    
    
    
predicted = pd.DataFrame(model(torch.from_numpy(np.array(index_data.loc[:,'zz1000涨跌幅'])
                                                .reshape(-1,1)).float().requires_grad_()).data.numpy(),columns=['预测']).reset_index()
predicted = pd.merge(predicted,index_data.loc[4301:,'sz50涨跌幅'].reset_index(drop=True).reset_index(),on='index')
predicted['error'] = predicted['预测']- predicted['sz50涨跌幅']
predicted_avg = predicted.mean()
predicted_std = predicted.std()  
    




#######################################################################################################################################











































    
    
    
    
    
    
    
    
    


