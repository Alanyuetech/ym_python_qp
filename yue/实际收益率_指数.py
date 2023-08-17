# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 14:22:03 2021

@author: Administrator
"""


import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np


"确定当前时间"
timeStamp=time.time()
now_time = time.strftime('%Y%m%d',time.localtime(timeStamp))

start_date = str('20070101')

"获取美国历史实际收益率"
dfii10 = pd.read_excel('DFII10.xls')

dfii10['日期'] = dfii10['observation_date']

"美股三大指数数据——时间跨度为2007年至今"  "美股数据需要代理开全局"

spx_index = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))

dow_index = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
                                      period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))

naq_index = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
                                      period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))



def get_dfii10_index(ans_index):

    "合并"
    ans = pd.merge(left=ans_index, right=dfii10,how="inner",on='日期')[['日期','收盘','DFII10']].rename(columns={'收盘':'指数','DFII10':'实际收益率'})
    
    # ans['下一日指数'] = ans['指数'].shift(1)
    # ans['下一日实际收益率'] = ans['实际收益率'].shift(1)
    # ans['上一日实际收益率'] = ans['实际收益率'].shift(-1)
    # ans['单日实际收益率涨跌'] = (ans['实际收益率']-ans['上一日实际收益率'])/abs(ans['上一日实际收益率'])
    
    # "去掉正负无穷大"
    # ans_inf = ans.replace([np.inf,-np.inf],'无穷大')  #替换
    # ans_inf = ans_inf.drop(ans_inf[ans_inf['单日实际收益率涨跌']=='无穷大'].index)   #删除
    
    
    "计算实际收益率 的  标准差"
    std_1d = ans['实际收益率'].std()
    mean_1d = ans['实际收益率'].mean()
    
    "1~3个标准差之外的的数据"
    ans_std_1 = ans[(ans['实际收益率']>=mean_1d+1*std_1d)|(ans['实际收益率']<=mean_1d-1*std_1d)]
    ans_std_2 = ans[(ans['实际收益率']>=mean_1d+2*std_1d)|(ans['实际收益率']<=mean_1d-2*std_1d)] 
    ans_std_3 = ans[(ans['实际收益率']>=mean_1d+3*std_1d)|(ans['实际收益率']<=mean_1d-3*std_1d)]
    
    "未来1~30日指数收益率"
    ans_1_30 = ans[['日期','指数']]
    for i in range(1,31):
        ans_1_30['未来{}.日指数'.format(i)] = ans_1_30['指数'].shift(i)
        ans_1_30['未来{}.日指数涨幅'.format(i)] = ans_1_30['指数']/ans_1_30['未来{}.日指数'.format(i)]  -  1
    
    
    "实际收益率  处于1，2，3个标准差之外  对应的指数未来1~30天的涨幅"
    ansstd1_ans130 = pd.merge(left=ans_1_30,right=ans_std_1[['日期','实际收益率']],how='left',on='日期')
    ansstd1_ans130 = ansstd1_ans130.dropna(subset=['实际收益率'])
    
    ansstd2_ans130 = pd.merge(left=ans_1_30,right=ans_std_2[['日期','实际收益率']],how='left',on='日期')
    ansstd2_ans130 = ansstd2_ans130.dropna(subset=['实际收益率'])
    
    ansstd3_ans130 = pd.merge(left=ans_1_30,right=ans_std_3[['日期','实际收益率']],how='left',on='日期')
    ansstd3_ans130 = ansstd3_ans130.dropna(subset=['实际收益率'])
    
    "1~3个标准差所有平均数据"
    avg_std1 = pd.DataFrame(ansstd1_ans130.mean()).reset_index().rename(columns={0:'1个标准差','index':'聚合列名'})
    avg_std2 = pd.DataFrame(ansstd2_ans130.mean()).reset_index().rename(columns={0:'2个标准差','index':'聚合列名'})
    avg_std3 = pd.DataFrame(ansstd3_ans130.mean()).reset_index().rename(columns={0:'3个标准差','index':'聚合列名'})
    
    "1~3个标准差所有平均数据列入一张表中"
    avg_std = pd.merge(left=avg_std1,right=avg_std2,on='聚合列名')
    avg_std = pd.merge(left=avg_std,right=avg_std3,on='聚合列名')
    
    "只保留1~30涨幅平均"
    avg_std = avg_std.loc[(avg_std['聚合列名'].str.contains('涨幅'))|(avg_std['聚合列名'].str.contains('单日'))].reset_index(drop=True)
    "百分数显示"
    avg_std['1个标准差'] = avg_std['1个标准差'].apply(lambda x: format(x, '.2%'))
    avg_std['2个标准差'] = avg_std['2个标准差'].apply(lambda x: format(x, '.2%'))
    avg_std['3个标准差'] = avg_std['3个标准差'].apply(lambda x: format(x, '.2%'))
   
    return avg_std


"循环三大指数"
name = locals()
for k in ['纳斯达克综合指数','标普500指数','道琼斯指数']:
  
    if k == '纳斯达克综合指数':
        ans_index = naq_index
        name_index = 'naq_index_jh'
    elif k == '标普500指数':
        ans_index = spx_index
        name_index = 'spx_index_jh'
    else:
        ans_index = dow_index
        name_index = 'dow_index_jh'
        
    "动态变量，将值放入不同的指数命名下的df"       
    name[name_index] = get_dfii10_index(ans_index)
    
    


"def 里面保存了  ans_inf,avg_std1,avg_std2,avg_std3  拿出来单独形成DataFrame    "
"把def里的一些变量重新运行一下"
data_list = pd.Series()
data_list['实际收益率平均值'] = mean_1d
data_list['实际收益率标准差'] = std_1d
data_list['总数据量'] = len(ans)
data_list['1个标准差外的数据量'] = len(ans_std_1)
data_list['2个标准差外的数据量'] = len(ans_std_2)
data_list['3个标准差外的数据量'] = len(ans_std_3)

data_list['小于1个标准差数据量'] = len(ans_std_1.drop(ans_std_1[ans_std_1['实际收益率']<mean_1d-1*std_1d].index))
data_list['大于1个标准差数据量'] = len(ans_std_1.drop(ans_std_1[ans_std_1['实际收益率']>mean_1d+1*std_1d].index))
data_list['小于2个标准差数据量'] = len(ans_std_2.drop(ans_std_2[ans_std_2['实际收益率']<mean_1d-2*std_1d].index))
data_list['大于2个标准差数据量'] = len(ans_std_2.drop(ans_std_2[ans_std_2['实际收益率']>mean_1d+2*std_1d].index))
data_list['小于3个标准差数据量'] = len(ans_std_3.drop(ans_std_3[ans_std_3['实际收益率']<mean_1d-3*std_1d].index))
data_list['大于3个标准差数据量'] = len(ans_std_3.drop(ans_std_3[ans_std_3['实际收益率']>mean_1d+3*std_1d].index))

data_list['小于1个std占1个std外总量的比'] = format(data_list["小于1个标准差数据量"]/data_list["1个标准差外的数据量"],'.2%')
data_list['大于1个std占1个std外总量的比'] = format(data_list["大于1个标准差数据量"]/data_list["1个标准差外的数据量"],'.2%')
data_list['小于2个std占2个std外总量的比'] = format(data_list["小于2个标准差数据量"]/data_list["2个标准差外的数据量"],'.2%')
data_list['大于2个std占2个std外总量的比'] = format(data_list["大于2个标准差数据量"]/data_list["2个标准差外的数据量"],'.2%')
data_list['小于3个std占3个std外总量的比'] = format(data_list["小于3个标准差数据量"]/data_list["3个标准差外的数据量"],'.2%')  #三个标准差外没有数据
data_list['大于3个std占3个std外总量的比'] = format(data_list["大于3个标准差数据量"]/data_list["3个标准差外的数据量"],'.2%')



