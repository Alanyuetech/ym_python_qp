# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 11:00:40 2021

@author: Administrator
"""


"当日成交额前20名，与大盘指数的相关性测试"
import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime

now_day = datetime.datetime.now().strftime('%Y%m%d')
from datetime import *
def getLastWeekDay(day=datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - timedelta(days=dayStep)
    return lastWorkDay

date_work=getLastWeekDay().strftime('%Y%m%d')


"返回所有美股代码"
usstock_id = pd.DataFrame()
usstock_id = pd.DataFrame(ak.stock_us_spot_em()['代码'])

"拿到美股数据"
usstock_data = pd.DataFrame()
id_count = 0
for id in usstock_id['代码']:
    stock_us_hist_df = ak.stock_us_hist(symbol=id,start_date="20180101", end_date=date_work)
    stock_us_hist_df['代码'] = id
    usstock_data = usstock_data.append(stock_us_hist_df)
    print('{}'.format(id))
    id_count+=1
    if id_count>=10:
        break

usstock_data = usstock_data.sort_values(by=['日期','代码'],ascending=(0,0))


##########################################################################
"报错 改变代理模式"
"返回所有A股代码"
cnstock_id = pd.DataFrame()
cnstock_id = pd.DataFrame(ak.stock_zh_a_spot_em()['代码'])
"拿到A股数据"
cnstock_data = pd.DataFrame()
data_id_erro = pd.DataFrame()
id_count = 0


for id in cnstock_id.loc[0:,'代码']:
    try:
        stock_cn_hist_df = ak.stock_zh_a_hist(symbol=id,start_date="20180101", end_date=date_work)
        stock_cn_hist_df['代码'] = id
        cnstock_data = cnstock_data.append(stock_cn_hist_df)
        print(id_count,'{}'.format(id))
        id_count+=1
    # if id_count>=10:
    #     break
    except:       
        data_id_erro = data_id_erro.append(pd.DataFrame([[id_count,id]]))
        print(id_count,'{}  错误'.format(id))
        id_count+=1
        continue 


# "同上"
# for index,row in cnstock_id.iterrows():
#     stock_cn_hist_df = ak.stock_zh_a_hist(symbol=row['代码'],start_date="20180101", end_date="20210813")
#     stock_cn_hist_df['代码'] = row['代码']
#     cnstock_data = cnstock_data.append(stock_cn_hist_df)
#     print(index,'{}'.format(row['代码']))

"数据处理——获得每日成交额前20 "   
cnstock_data = cnstock_data.sort_values(by=['日期','成交额'],ascending=(0,0))
cnstock_data_d = cnstock_data.groupby(by='日期').head(20).reset_index(drop=True)

"计算每日成交额前20个股票中 涨跌幅>0的个数  即每日涨跌幅正数个数"
cnstock_data_dg0 = pd.DataFrame(cnstock_data_d[cnstock_data_d['涨跌幅']>0].groupby(by='日期').size()).sort_values(by=['日期'],ascending=0).reset_index().rename(columns={0:'正数个数'})

"每日成交额前20的涨跌幅和换手率进行平均"
cnstock_data_d = cnstock_data_d.groupby(by='日期').agg({'涨跌幅':'mean','换手率':'mean'}).sort_values(by=['日期'],ascending=0).reset_index()


"国内指数"
"沪深300:sh000300    上证50:sh000016       中证500:sz399905   "
sh000300 = ak.stock_zh_index_daily_em(symbol="sh000300").sort_values(by='date',ascending=0).reset_index(drop=True)
sh000016 = ak.stock_zh_index_daily_em(symbol="sh000016").sort_values(by='date',ascending=0).reset_index(drop=True)
sz399905 = ak.stock_zh_index_daily_em(symbol="sz399905").sort_values(by='date',ascending=0).reset_index(drop=True)

"国内指数每日涨幅"
sh000300['sh000300'] = sh000300['close']/sh000300['close'].shift(-1) -1
sh000016['sh000016'] = sh000016['close']/sh000016['close'].shift(-1) -1
sz399905['sz399905'] = sz399905['close']/sz399905['close'].shift(-1) -1

"只取日期和每日涨幅，与成交额统计数据 日期列明保持一致"
sh000300 = sh000300[['date','sh000300']].rename(columns={'date':'日期'})
sh000016 = sh000016[['date','sh000016']].rename(columns={'date':'日期'})
sz399905 = sz399905[['date','sz399905']].rename(columns={'date':'日期'})

index_final = pd.merge(left=sh000300,right=sh000016,on='日期')
index_final = pd.merge(left=index_final,right=sz399905,on='日期')

"merge 国内指数每日涨幅"
cnstock_data_d = pd.merge(left=cnstock_data_d,right=index_final,on='日期')

"北向资金净买额"
hgt_data = ak.stock_em_hsgt_hist(symbol="沪股通").sort_values(by='日期',ascending=0).reset_index(drop=True)[['日期','当日成交净买额']].rename(columns={'当日成交净买额':'沪股通'})
sgt_data = ak.stock_em_hsgt_hist(symbol="深股通").sort_values(by='日期',ascending=0).reset_index(drop=True)[['日期','当日成交净买额']].rename(columns={'当日成交净买额':'深股通'})
bx_data = pd.merge(left=hgt_data,right=sgt_data,on='日期')
bx_data['北向_当日成交净买额(亿)'] = (bx_data['沪股通'] + bx_data['深股通'])/100
"日期格式统一"
bx_data['日期'] = bx_data['日期'].astype(str)

"merge 北向资金"
cnstock_data_d = pd.merge(left=cnstock_data_d,right=bx_data,on='日期')

"merge  正数个数"
cnstock_data_d = pd.merge(cnstock_data_d,cnstock_data_dg0,on='日期')

"输出xlsx   总的源数据"
cnstock_data_d.to_excel('日股票成交额前20_涨跌幅&换手率平均{}.xlsx'.format(date_work))  





"准备数据"
ans = cnstock_data_d[['日期','涨跌幅','换手率','北向_当日成交净买额(亿)','正数个数','sh000300','sh000016','sz399905']]
ans = ans.rename(columns={'sh000300':'沪深300','sh000016':'上证50','sz399905':'中证500'})
ans[['沪深300','上证50','中证500']] = ans[['沪深300','上证50','中证500']] * 100

"涨跌幅平均  [%,%] ~ [%,%]  对应的涨跌幅的平均    各个区间段统计"
"正数个数  1~20  对应的涨跌幅的平均    每个数统计"

"如果想要查看每个  累计区间段   的   只需要解开if下的代码单独循环运行，不需要分情况，if下的代码是不分情况的原始代码"


ans_chg = pd.DataFrame(columns=('涨跌幅','沪深300','上证50','中证500','沪深300数据量','上证50数据量','中证500数据量'))
ans_g0n = pd.DataFrame(columns=('正数个数','沪深300','上证50','中证500','沪深300数据量','上证50数据量','中证500数据量'))
ans_hsl = pd.DataFrame(columns=('换手率','沪深300','上证50','中证500','沪深300数据量','上证50数据量','中证500数据量'))

for i in range(-10,0):
    if i == -10:
        ans_chg_b = pd.DataFrame(ans[ans['涨跌幅']<=i].mean()).T[['沪深300','上证50','中证500']]
        ans_chg_b['涨跌幅'] = str('<={}%'.format(i))
        ans_chg_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['沪深300']>=0)]),len(ans[ans['涨跌幅']<=i]),len(ans))
        ans_chg_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['上证50']>=0)]),len(ans[ans['涨跌幅']<=i]),len(ans))
        ans_chg_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['中证500']>=0)]),len(ans[ans['涨跌幅']<=i]),len(ans))
                   
        ans_g0n_b = pd.DataFrame(ans[ans['正数个数']==11+i].mean()).T[['沪深300','上证50','中证500']]
        ans_g0n_b['正数个数'] = str('{}'.format(11+i))
        ans_g0n_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==11+i)&(ans['沪深300']<=0)]),len(ans[(ans['正数个数']==11+i)&(ans['沪深300']>=0)]),len(ans[ans['正数个数']==11+i]),len(ans))
        ans_g0n_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==11+i)&(ans['上证50']<=0)]),len(ans[(ans['正数个数']==11+i)&(ans['上证50']>=0)]),len(ans[ans['正数个数']==11+i]),len(ans))
        ans_g0n_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==11+i)&(ans['中证500']<=0)]),len(ans[(ans['正数个数']==11+i)&(ans['中证500']>=0)]),len(ans[ans['正数个数']==11+i]),len(ans))
        
        ans_hsl_b = pd.DataFrame(ans[ans['换手率']<=i].mean()).T[['沪深300','上证50','中证500']]
        ans_hsl_b['换手率'] = str('<={}%'.format(i))
        ans_hsl_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']<=i)&(ans['沪深300']<=0)]),len(ans[(ans['换手率']<=i)&(ans['沪深300']>=0)]),len(ans[ans['换手率']<=i]),len(ans))
        ans_hsl_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']<=i)&(ans['上证50']<=0)]),len(ans[(ans['换手率']<=i)&(ans['上证50']>=0)]),len(ans[ans['换手率']<=i]),len(ans))
        ans_hsl_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']<=i)&(ans['中证500']<=0)]),len(ans[(ans['换手率']<=i)&(ans['中证500']>=0)]),len(ans[ans['换手率']<=i]),len(ans))        
    
    else:       
        ans_chg_b = pd.DataFrame(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)].mean()).T[['沪深300','上证50','中证500']]
        ans_chg_b['涨跌幅'] = str('{}%<=  <={}%'.format(i-1,i))
        ans_chg_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)]),len(ans))
        ans_chg_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)]),len(ans))
        ans_chg_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)]),len(ans))
                   
        ans_g0n_b = pd.DataFrame(ans[ans['正数个数']==11+i].mean()).T[['沪深300','上证50','中证500']]
        ans_g0n_b['正数个数'] = str('{}'.format(11+i))
        ans_g0n_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==11+i)&(ans['沪深300']<=0)]),len(ans[(ans['正数个数']==11+i)&(ans['沪深300']>=0)]),len(ans[ans['正数个数']==11+i]),len(ans))
        ans_g0n_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==11+i)&(ans['上证50']<=0)]),len(ans[(ans['正数个数']==11+i)&(ans['上证50']>=0)]),len(ans[ans['正数个数']==11+i]),len(ans))
        ans_g0n_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==11+i)&(ans['中证500']<=0)]),len(ans[(ans['正数个数']==11+i)&(ans['中证500']>=0)]),len(ans[ans['正数个数']==11+i]),len(ans))
        
        ans_hsl_b = pd.DataFrame(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)].mean()).T[['沪深300','上证50','中证500']]
        ans_hsl_b['换手率'] = str('{}%<=  <={}%'.format(i-1,i))
        ans_hsl_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)&(ans['沪深300']<=0)]),len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)&(ans['沪深300']>=0)]),len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)]),len(ans))
        ans_hsl_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)&(ans['上证50']<=0)]),len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)&(ans['上证50']>=0)]),len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)]),len(ans))
        ans_hsl_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)&(ans['中证500']<=0)]),len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)&(ans['中证500']>=0)]),len(ans[(ans['换手率']>=i-1)&(ans['换手率']<=i)]),len(ans))
                  
    ans_chg = ans_chg.append(ans_chg_b)
    ans_g0n = ans_g0n.append(ans_g0n_b)
    ans_hsl = ans_hsl.append(ans_hsl_b)


for i in range(0,11):
    if i == 10:        
        ans_chg_b = pd.DataFrame(ans[ans['涨跌幅']>=i].mean()).T[['沪深300','上证50','中证500']]
        ans_chg_b['涨跌幅'] = str('>={}%'.format(i))
        ans_chg_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['沪深300']>=0)]),len(ans[ans['涨跌幅']>=i]),len(ans))
        ans_chg_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['上证50']>=0)]),len(ans[ans['涨跌幅']>=i]),len(ans))
        ans_chg_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['中证500']>=0)]),len(ans[ans['涨跌幅']>=i]),len(ans))
                    
        ans_g0n_b = pd.DataFrame(ans[ans['正数个数']==10+i].mean()).T[['沪深300','上证50','中证500']]
        ans_g0n_b['正数个数'] = str('{}'.format(10+i))
        ans_g0n_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==10+i)&(ans['沪深300']<=0)]),len(ans[(ans['正数个数']==10+i)&(ans['沪深300']>=0)]),len(ans[ans['正数个数']==10+i]),len(ans))
        ans_g0n_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==10+i)&(ans['上证50']<=0)]),len(ans[(ans['正数个数']==10+i)&(ans['上证50']>=0)]),len(ans[ans['正数个数']==10+i]),len(ans))
        ans_g0n_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==10+i)&(ans['中证500']<=0)]),len(ans[(ans['正数个数']==10+i)&(ans['中证500']>=0)]),len(ans[ans['正数个数']==10+i]),len(ans))
        
        ans_hsl_b = pd.DataFrame(ans[ans['换手率']>=i].mean()).T[['沪深300','上证50','中证500']]
        ans_hsl_b['换手率'] = str('>={}%'.format(i))
        ans_hsl_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i)&(ans['沪深300']<=0)]),len(ans[(ans['换手率']>=i)&(ans['沪深300']>=0)]),len(ans[ans['换手率']>=i]),len(ans))
        ans_hsl_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i)&(ans['上证50']<=0)]),len(ans[(ans['换手率']>=i)&(ans['上证50']>=0)]),len(ans[ans['换手率']>=i]),len(ans))
        ans_hsl_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i)&(ans['中证500']<=0)]),len(ans[(ans['换手率']>=i)&(ans['中证500']>=0)]),len(ans[ans['换手率']>=i]),len(ans))
     
    else:
        ans_chg_b = pd.DataFrame(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)].mean()).T[['沪深300','上证50','中证500']]
        ans_chg_b['涨跌幅'] = str('{}%<=  <={}%'.format(i,i+1))
        ans_chg_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)]),len(ans))
        ans_chg_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)]),len(ans))
        ans_chg_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)]),len(ans))
                    
        ans_g0n_b = pd.DataFrame(ans[ans['正数个数']==10+i].mean()).T[['沪深300','上证50','中证500']]
        ans_g0n_b['正数个数'] = str('{}'.format(10+i))
        ans_g0n_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==10+i)&(ans['沪深300']<=0)]),len(ans[(ans['正数个数']==10+i)&(ans['沪深300']>=0)]),len(ans[ans['正数个数']==10+i]),len(ans))
        ans_g0n_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==10+i)&(ans['上证50']<=0)]),len(ans[(ans['正数个数']==10+i)&(ans['上证50']>=0)]),len(ans[ans['正数个数']==10+i]),len(ans))
        ans_g0n_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['正数个数']==10+i)&(ans['中证500']<=0)]),len(ans[(ans['正数个数']==10+i)&(ans['中证500']>=0)]),len(ans[ans['正数个数']==10+i]),len(ans))
        
        ans_hsl_b = pd.DataFrame(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)].mean()).T[['沪深300','上证50','中证500']]
        ans_hsl_b['换手率'] = str('{}%<=  <={}%'.format(i,i+1))
        ans_hsl_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)&(ans['沪深300']<=0)]),len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)&(ans['沪深300']>=0)]),len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)]),len(ans))
        ans_hsl_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)&(ans['上证50']<=0)]),len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)&(ans['上证50']>=0)]),len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)]),len(ans))
        ans_hsl_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)&(ans['中证500']<=0)]),len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)&(ans['中证500']>=0)]),len(ans[(ans['换手率']>=i)&(ans['换手率']<=i+1)]),len(ans))
        
        
    ans_chg = ans_chg.append(ans_chg_b)
    ans_g0n = ans_g0n.append(ans_g0n_b)
    ans_hsl = ans_hsl.append(ans_hsl_b)




"涨跌幅 & 正数个数  两个条件共同作用"
ans_tj2 = pd.DataFrame(columns=('条件','沪深300','上证50','中证500','沪深300数据量','上证50数据量','中证500数据量'))
for j in range(-10,0):
    for i in range(-10,0):
        if i == -10:
            ans_tj2_b = pd.DataFrame(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)].mean()).T[['沪深300','上证50','中证500']]
            ans_tj2_b['条件'] = str('<={}%   {}个'.format(i,11+j))
            ans_tj2_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
        else:
            ans_tj2_b = pd.DataFrame(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)].mean()).T[['沪深300','上证50','中证500']]
            ans_tj2_b['条件'] = str('{}%<=  <={}%   {}个'.format(i-1,i,11+j))
            ans_tj2_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))            
        ans_tj2 = ans_tj2.append(ans_tj2_b)
    for i in range(0,11):
        if i == 10:
            ans_tj2_b = pd.DataFrame(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)].mean()).T[['沪深300','上证50','中证500']]
            ans_tj2_b['条件'] = str('>={}%   {}个'.format(i,11+j))
            ans_tj2_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)]),len(ans))
        else:
            ans_tj2_b = pd.DataFrame(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)].mean()).T[['沪深300','上证50','中证500']]
            ans_tj2_b['条件'] = str('{}%<=  <={}%   {}个'.format(i,i+1,11+j))
            ans_tj2_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)]),len(ans))           
        ans_tj2 = ans_tj2.append(ans_tj2_b)   
        

for j in range(0,11):
   for i in range(-10,0):
        if i == -10:
            ans_tj2_b = pd.DataFrame(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)].mean()).T[['沪深300','上证50','中证500']]
            ans_tj2_b['条件'] = str('<={}%   {}个'.format(i,11+j))
            ans_tj2_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
        else:
            ans_tj2_b = pd.DataFrame(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)].mean()).T[['沪深300','上证50','中证500']]
            ans_tj2_b['条件'] = str('{}%<=  <={}%   {}个'.format(i-1,i,11+j))
            ans_tj2_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']>=i-1)&(ans['涨跌幅']<=i)&(ans['正数个数']==11+j)]),len(ans))            
        ans_tj2 = ans_tj2.append(ans_tj2_b)
   for i in range(0,11):
        if i == 10:
            ans_tj2_b = pd.DataFrame(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)].mean()).T[['沪深300','上证50','中证500']]
            ans_tj2_b['条件'] = str('>={}%   {}个'.format(i,11+j))
            ans_tj2_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['正数个数']==11+j)]),len(ans))
        else:
            ans_tj2_b = pd.DataFrame(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)].mean()).T[['沪深300','上证50','中证500']]
            ans_tj2_b['条件'] = str('{}%<=  <={}%   {}个'.format(i,i+1,11+j))
            ans_tj2_b['沪深300数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['沪深300']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['沪深300']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['上证50数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['上证50']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['上证50']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)]),len(ans))
            ans_tj2_b['中证500数据量'] = '{}/{}/{}/{}'.format(len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['中证500']<=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)&(ans['中证500']>=0)]),len(ans[(ans['涨跌幅']>=i)&(ans['涨跌幅']<=i+1)&(ans['正数个数']==11+j)]),len(ans))           
        ans_tj2 = ans_tj2.append(ans_tj2_b)   
         


ans_chg.to_excel('涨跌幅阶梯统计{}.xlsx'.format(date_work))  
ans_g0n.to_excel('正数个数阶梯统计{}.xlsx'.format(date_work))  
ans_hsl.to_excel('换手率阶梯统计{}.xlsx'.format(date_work))  
ans_tj2.to_excel('涨跌幅&正数个数阶梯统计{}.xlsx'.format(date_work))  




"输出报错的股票代码"
data_id_erro = data_id_erro.reset_index(drop=True)
data_id_erro.to_excel('报错股票代码{}.xlsx'.format(date_work))  

