# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 09:59:27 2021

@author: Administrator
"""


"国内基金 与  股指期货   触发时间   研究"
import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
import statsmodels.api as sm
from statsmodels.formula.api import ols
import matplotlib.pyplot as plt

"确定当前时间"
timeStamp=time.time()
now_time = time.strftime('%Y%m%d',time.localtime(timeStamp))

start_date = str('20171220')  #20180101的时间往前几天，可以保证1月1日有涨跌幅


# "主力连续合约历史数据"
# IF0_data = ak.futures_main_sina(symbol="IF0").sort_values(by='日期',ascending=0).reset_index(drop=True).rename(columns={'收盘价':'IF0'})
# IH0_data = ak.futures_main_sina(symbol="IH0").sort_values(by='日期',ascending=0).reset_index(drop=True).rename(columns={'收盘价':'IH0'})
# IC0_data = ak.futures_main_sina(symbol="IC0").sort_values(by='日期',ascending=0).reset_index(drop=True).rename(columns={'收盘价':'IC0'})


"美股三大指数数据——时间跨度为2007年至今"  "美股数据需要代理开全局"

spx_data = ak.index_investing_global(country="美国", index_name="标普500指数", 
                                      period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))

"道琼斯数据可能显示的是当日凌晨时点的数据，和交易软件上的收盘价不同"
# dow_data = ak.index_investing_global(country="美国", index_name="道琼斯指数", 
#                                       period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))


# naq_data = ak.index_investing_global(country="美国", index_name="纳斯达克综合指数", 
#                                       period="每日", start_date="{}".format(start_date), end_date="{}".format(now_time))


mg_data = spx_data

########################################################################################################

"国内指数  cnindex_data"  "国内数据需要pac模式"
"沪深300:sh000300    上证50:sh000016       中证500:sz399905   "
# "查找国内指数代码——正常不用运行"
# aaa = ak.stock_zh_index_spot()

cnindex_data = ak.stock_zh_index_daily_em(symbol="sz399905").sort_values(by='date',ascending=0).reset_index(drop=True)
# cyb_index = ak.stock_zh_index_daily_em(symbol="sz399006").sort_values(by='date',ascending=0).reset_index(drop=True)

"以上为数据准备"

########################################################################################################



"北向资金"
hgt = ak.stock_hsgt_hist_em(symbol="沪股通").sort_values(by='日期',ascending=0)[['日期','当日成交净买额']].rename(columns={'当日成交净买额':'沪股通'})
hgt = hgt.rename(columns={'沪股通':'沪股通(亿)'})
hgt['日期'] = hgt['日期'].astype(str)

sgt = ak.stock_hsgt_hist_em(symbol="深股通").sort_values(by='日期',ascending=0)[['日期','当日成交净买额']].rename(columns={'当日成交净买额':'深股通'})
sgt = sgt.rename(columns={'深股通':'深股通(亿)'})
sgt['日期'] = sgt['日期'].astype(str)

north_bound = pd.merge(left=hgt,right=sgt,how='outer',on='日期')
north_bound['当日成交净买额(亿)'] = north_bound['沪股通(亿)'] + north_bound['深股通(亿)']


"固定格式：1列求和 2列求和  ~~  5列求和"
for i in range(1,6):
    north_bound['前{}日成交净买额(亿)'.format(i)] = north_bound['当日成交净买额(亿)'].shift(-i)
for i in range(1,6):
    north_bound['p{}d成交净买额(亿)'.format(i)] = north_bound.iloc[:,4:4+i].sum(axis=1)

north_bound = north_bound[north_bound['日期']>="2018-01-01"]

"美股前一天涨跌幅"  
mg_index = mg_data.reset_index().rename(columns={'收盘':'mg_index'})
mg_index = mg_index.sort_values(by='日期',ascending=0)[['日期','mg_index']]
mg_index['日期'] = mg_index['日期'].astype(str)

"固定格式：过去1~5日涨跌幅"
for i in range(1,6):
    mg_index['前{}日mg_index'.format(i)] = mg_index['mg_index'].shift(-i)
    mg_index['p{}dmg_index涨跌幅'.format(i)] = mg_index['mg_index']/mg_index['前{}日mg_index'.format(i)] - 1
    
"整体向前调整一天"
for i in range(1,6):
    mg_index['p{}dmg_index涨跌幅'.format(i)] = mg_index['p{}dmg_index涨跌幅'.format(i)].shift(-1)
    
mg_index = mg_index[mg_index['日期']>="2018-01-01"]


# naq_index = naq_index.reset_index().rename(columns={'收盘':'naq_index'})
# naq_index = naq_index.sort_values(by='日期',ascending=0)[['日期','naq_index']]
# naq_index['日期'] = naq_index['日期'].astype(str)

"国内指数涨幅"
cnindex = cnindex_data[['date','close']].rename(columns={'date':'日期','close':'cnindex'})
cnindex['cnindex涨跌幅'] = cnindex['cnindex']/cnindex['cnindex'].shift(-1) - 1
cnindex['前一日'] = cnindex['日期'].shift(-1)
cnindex = cnindex[cnindex['日期']>="2018-01-01"]
# cyb_index = cyb_index[['date','close']].rename(columns={'date':'日期','close':'cyb_index'})

"合并数据"
ans = pd.merge(left=cnindex[['日期','cnindex','cnindex涨跌幅']],
               right=north_bound[['日期','当日成交净买额(亿)','p1d成交净买额(亿)','p2d成交净买额(亿)','p3d成交净买额(亿)','p4d成交净买额(亿)','p5d成交净买额(亿)']],how='outer',on='日期')
ans = pd.merge(left=ans,right=mg_index[['日期','p1dmg_index涨跌幅','p2dmg_index涨跌幅'
                                         ,'p3dmg_index涨跌幅','p4dmg_index涨跌幅','p5dmg_index涨跌幅']],how='outer',on='日期')
ans_data = ans[ans['日期']>="2018-01-01"].sort_values(by='日期',ascending=0).reset_index(drop=True)




"数据填充"

"北向资金pnd是不包含当天的，所以缺失的数据可以直接用后一天的数据填充"
ans_data[['p1d成交净买额(亿)','p2d成交净买额(亿)','p3d成交净买额(亿)','p4d成交净买额(亿)','p5d成交净买额(亿)']] = ans_data[['p1d成交净买额(亿)','p2d成交净买额(亿)','p3d成交净买额(亿)','p4d成交净买额(亿)','p5d成交净买额(亿)']].fillna(method='ffill')

"涨跌幅pnd是 的计算是基于当天的指数数据的，所以缺失的数据要用后一天的数据填充"
ans_data[['p1dmg_index涨跌幅','p2dmg_index涨跌幅','p3dmg_index涨跌幅','p4dmg_index涨跌幅','p5dmg_index涨跌幅']] = ans_data[['p1dmg_index涨跌幅','p2dmg_index涨跌幅','p3dmg_index涨跌幅','p4dmg_index涨跌幅','p5dmg_index涨跌幅']].fillna(method='ffill')   #ffill 和 bfill 灵活使用

"删除 cnindex没有数据的行"
ans_data = ans_data.drop(ans_data[np.isnan(ans_data['cnindex'])].index).reset_index(drop=True)

"计算前 n日 北向资金、美股涨跌幅  对于国内指数 的影响  "
std_cnindex = ans_data['cnindex涨跌幅'].std()
mean_cnindex = ans_data['cnindex涨跌幅'].mean()

"国内指数涨跌幅一个标准差外"
cnindex_std_1 = ans_data[(ans_data['cnindex涨跌幅']>=mean_cnindex+1*std_cnindex)|(ans_data['cnindex涨跌幅']<=mean_cnindex-1*std_cnindex)]
cnindex_std_1_count = len(cnindex_std_1)   #1个标准差外的数量
cnindex_std_1_l0 = ans_data[ans_data['cnindex涨跌幅']<=mean_cnindex-1*std_cnindex]
cnindex_std_1_g0 = ans_data[ans_data['cnindex涨跌幅']>=mean_cnindex+1*std_cnindex]  

">=std   <=-std   相关数据的平均值"
cnindex_std_1_l0_mean = cnindex_std_1_l0.mean()
cnindex_std_1_g0_mean = cnindex_std_1_g0.mean()



########################################################################################################




"pnd成交净买额——单列研究"

"p1d成交净买额>= n亿  ，国内指数涨跌幅的平均"
cnindex_mean_p1djmg_v_max=0
for i in range(0,100):
    locals()['cnindex_mean_p1djmg'+str(i)] = ans_data[ans_data['p1d成交净买额(亿)']>=i]
    locals()['cnindex_mean_p1djmg'+str(i)+'_v'] = ans_data[ans_data['p1d成交净买额(亿)']>=i].mean()
    cnindex_mean_p1djmg_v_max = max(cnindex_mean_p1djmg_v_max,locals()['cnindex_mean_p1djmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p1djmg_v_max==locals()['cnindex_mean_p1djmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i
        max_num = len(locals()['cnindex_mean_p1djmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p1djmg'+str(i)][locals()['cnindex_mean_p1djmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p1d成交净买额>={}亿  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p1djmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p1d成交净买额<=-n亿 ，国内指数涨跌幅的平均"
cnindex_mean_p1djmg_v_min=0.0
for i in range(0,40):
    locals()['cnindex_mean_p1djmg'+str(-i)] = ans_data[ans_data['p1d成交净买额(亿)']<=-i]
    locals()['cnindex_mean_p1djmg'+str(-i)+'_v'] = ans_data[ans_data['p1d成交净买额(亿)']<=-i].mean()
    cnindex_mean_p1djmg_v_min = min(cnindex_mean_p1djmg_v_min,locals()['cnindex_mean_p1djmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p1djmg_v_min==locals()['cnindex_mean_p1djmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i
         min_num = len(locals()['cnindex_mean_p1djmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p1djmg'+str(-i)][locals()['cnindex_mean_p1djmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p1d成交净买额<={}亿  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_p1djmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')



"p2d成交净买额>=n亿，国内指数涨跌幅的平均"
cnindex_mean_p2djmg_v_max=0
for i in range(0,100):
    locals()['cnindex_mean_p2djmg'+str(i)] = ans_data[ans_data['p2d成交净买额(亿)']>=i]
    locals()['cnindex_mean_p2djmg'+str(i)+'_v'] = ans_data[ans_data['p2d成交净买额(亿)']>=i].mean()
    cnindex_mean_p2djmg_v_max = max(cnindex_mean_p2djmg_v_max,locals()['cnindex_mean_p2djmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p2djmg_v_max==locals()['cnindex_mean_p2djmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i
        max_num = len(locals()['cnindex_mean_p2djmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p2djmg'+str(i)][locals()['cnindex_mean_p2djmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p2d成交净买额>={}亿  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p2djmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p2d成交净买额<=-n亿，国内指数涨跌幅的平均"
cnindex_mean_p2djmg_v_min=0.0
for i in range(0,40):
    locals()['cnindex_mean_p2djmg'+str(-i)] = ans_data[ans_data['p2d成交净买额(亿)']<=-i]
    locals()['cnindex_mean_p2djmg'+str(-i)+'_v'] = ans_data[ans_data['p2d成交净买额(亿)']<=-i].mean()
    cnindex_mean_p2djmg_v_min = min(cnindex_mean_p2djmg_v_min,locals()['cnindex_mean_p2djmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p2djmg_v_min==locals()['cnindex_mean_p2djmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i
         min_num = len(locals()['cnindex_mean_p2djmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p2djmg'+str(-i)][locals()['cnindex_mean_p2djmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p2d成交净买额<={}亿  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_p2djmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')




"p3d成交净买额>=n亿，国内指数涨跌幅的平均"
cnindex_mean_p3djmg_v_max=0
for i in range(0,150):
    locals()['cnindex_mean_p3djmg'+str(i)] = ans_data[ans_data['p3d成交净买额(亿)']>=i]
    locals()['cnindex_mean_p3djmg'+str(i)+'_v'] = ans_data[ans_data['p3d成交净买额(亿)']>=i].mean()
    cnindex_mean_p3djmg_v_max = max(cnindex_mean_p3djmg_v_max,locals()['cnindex_mean_p3djmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p3djmg_v_max==locals()['cnindex_mean_p3djmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i
        max_num = len(locals()['cnindex_mean_p3djmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p3djmg'+str(i)][locals()['cnindex_mean_p3djmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p3d成交净买额>={}亿  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p3djmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p3d成交净买额<=-n亿，国内指数涨跌幅的平均"
cnindex_mean_p3djmg_v_min=0.0
for i in range(0,100):
    locals()['cnindex_mean_p3djmg'+str(-i)] = ans_data[ans_data['p3d成交净买额(亿)']<=-i]
    locals()['cnindex_mean_p3djmg'+str(-i)+'_v'] = ans_data[ans_data['p3d成交净买额(亿)']<=-i].mean()
    cnindex_mean_p3djmg_v_min = min(cnindex_mean_p3djmg_v_min,locals()['cnindex_mean_p3djmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p3djmg_v_min==locals()['cnindex_mean_p3djmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i
         min_num = len(locals()['cnindex_mean_p3djmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p3djmg'+str(-i)][locals()['cnindex_mean_p3djmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p3d成交净买额<={}亿  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_p3djmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')


"p4d成交净买额>=n亿，国内指数涨跌幅的平均"
cnindex_mean_p4djmg_v_max=0
for i in range(0,200):
    locals()['cnindex_mean_p4djmg'+str(i)] = ans_data[ans_data['p4d成交净买额(亿)']>=i]
    locals()['cnindex_mean_p4djmg'+str(i)+'_v'] = ans_data[ans_data['p4d成交净买额(亿)']>=i].mean()
    cnindex_mean_p4djmg_v_max = max(cnindex_mean_p4djmg_v_max,locals()['cnindex_mean_p4djmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p4djmg_v_max==locals()['cnindex_mean_p4djmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i
        max_num = len(locals()['cnindex_mean_p4djmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p4djmg'+str(i)][locals()['cnindex_mean_p4djmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p4d成交净买额>={}亿  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p4djmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p4d成交净买额<=-n亿，国内指数涨跌幅的平均"
cnindex_mean_p4djmg_v_min=0.0
for i in range(0,100):
    locals()['cnindex_mean_p4djmg'+str(-i)] = ans_data[ans_data['p4d成交净买额(亿)']<=-i]
    locals()['cnindex_mean_p4djmg'+str(-i)+'_v'] = ans_data[ans_data['p4d成交净买额(亿)']<=-i].mean()
    cnindex_mean_p4djmg_v_min = min(cnindex_mean_p4djmg_v_min,locals()['cnindex_mean_p4djmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p4djmg_v_min==locals()['cnindex_mean_p4djmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i
         min_num = len(locals()['cnindex_mean_p4djmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p4djmg'+str(-i)][locals()['cnindex_mean_p4djmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p4d成交净买额<={}亿  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_p4djmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')



"p5d成交净买额>=n亿，国内指数涨跌幅的平均"
cnindex_mean_p5djmg_v_max=0
for i in range(0,200):
    locals()['cnindex_mean_p5djmg'+str(i)] = ans_data[ans_data['p5d成交净买额(亿)']>=i]
    locals()['cnindex_mean_p5djmg'+str(i)+'_v'] = ans_data[ans_data['p5d成交净买额(亿)']>=i].mean()
    cnindex_mean_p5djmg_v_max = max(cnindex_mean_p5djmg_v_max,locals()['cnindex_mean_p5djmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p5djmg_v_max==locals()['cnindex_mean_p5djmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i
        max_num = len(locals()['cnindex_mean_p5djmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p5djmg'+str(i)][locals()['cnindex_mean_p5djmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p5d成交净买额>={}亿  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p5djmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p5d成交净买额<=-n亿，国内指数涨跌幅的平均"
cnindex_mean_p5djmg_v_min=0.0
for i in range(0,150):
    locals()['cnindex_mean_p5djmg'+str(-i)] = ans_data[ans_data['p5d成交净买额(亿)']<=-i]
    locals()['cnindex_mean_p5djmg'+str(-i)+'_v'] = ans_data[ans_data['p5d成交净买额(亿)']<=-i].mean()
    cnindex_mean_p5djmg_v_min = min(cnindex_mean_p5djmg_v_min,locals()['cnindex_mean_p5djmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p5djmg_v_min==locals()['cnindex_mean_p5djmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i
         min_num = len(locals()['cnindex_mean_p5djmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p5djmg'+str(-i)][locals()['cnindex_mean_p5djmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p5d成交净买额<={}亿  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_p5djmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')



########################################################################################################





"pndmg_index涨跌幅——单列研究"

"p1dmg_index涨跌幅>=n%，国内指数涨跌幅的平均"
cnindex_mean_p1dmg_v_max=0
for i in range(0,20):
    locals()['cnindex_mean_p1dmg'+str(i)] = ans_data[ans_data['p1dmg_index涨跌幅']>=i*0.001]
    locals()['cnindex_mean_p1dmg'+str(i)+'_v'] = ans_data[ans_data['p1dmg_index涨跌幅']>=i*0.001].mean()
    cnindex_mean_p1dmg_v_max = max(cnindex_mean_p1dmg_v_max,locals()['cnindex_mean_p1dmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p1dmg_v_max==locals()['cnindex_mean_p1dmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i*0.001
        max_num = len(locals()['cnindex_mean_p1dmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p1dmg'+str(i)][locals()['cnindex_mean_p1dmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p1dmg_index涨跌幅>={:.2%}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p1dmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p1dmg_index涨跌幅<=-n%，国内指数涨跌幅的平均"
cnindex_mean_p1dmg_v_min=0.0
for i in range(0,20):
    locals()['cnindex_mean_p1dmg'+str(-i)] = ans_data[ans_data['p1dmg_index涨跌幅']<=-i]
    locals()['cnindex_mean_p1dmg'+str(-i)+'_v'] = ans_data[ans_data['p1dmg_index涨跌幅']<=-i].mean()
    cnindex_mean_p1dmg_v_min = min(cnindex_mean_p1dmg_v_min,locals()['cnindex_mean_p1dmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p1dmg_v_min==locals()['cnindex_mean_p1dmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i*0.001
         min_num = len(locals()['cnindex_mean_p1dmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p1dmg'+str(-i)][locals()['cnindex_mean_p1dmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p1dmg_index涨跌幅<={:.2%}  该范围内cnindex下涨概率：{:.2%}'.format(cnindex_mean_p1dmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')


"p2dmg_index涨跌幅>=n%，国内指数涨跌幅的平均"
cnindex_mean_p2dmg_v_max=0
for i in range(0,10):
    locals()['cnindex_mean_p2dmg'+str(i)] = ans_data[ans_data['p2dmg_index涨跌幅']>=i*0.001]
    locals()['cnindex_mean_p2dmg'+str(i)+'_v'] = ans_data[ans_data['p2dmg_index涨跌幅']>=i*0.001].mean()
    cnindex_mean_p2dmg_v_max = max(cnindex_mean_p2dmg_v_max,locals()['cnindex_mean_p2dmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p2dmg_v_max==locals()['cnindex_mean_p2dmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i*0.001
        max_num = len(locals()['cnindex_mean_p2dmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p2dmg'+str(i)][locals()['cnindex_mean_p2dmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p2dmg_index涨跌幅>={:.2%}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p2dmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p2dmg_index涨跌幅<=-n%，国内指数涨跌幅的平均"
cnindex_mean_p2dmg_v_min=0.0
for i in range(0,40):
    locals()['cnindex_mean_p2dmg'+str(-i)] = ans_data[ans_data['p2dmg_index涨跌幅']<=-i]
    locals()['cnindex_mean_p2dmg'+str(-i)+'_v'] = ans_data[ans_data['p2dmg_index涨跌幅']<=-i].mean()
    cnindex_mean_p2dmg_v_min = min(cnindex_mean_p2dmg_v_min,locals()['cnindex_mean_p2dmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p2dmg_v_min==locals()['cnindex_mean_p2dmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i*0.001
         min_num = len(locals()['cnindex_mean_p2dmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p2dmg'+str(-i)][locals()['cnindex_mean_p2dmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p2dmg_index涨跌幅<={:.2%}  该范围内cnindex下涨概率：{:.2%}'.format(cnindex_mean_p2dmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')


"p3dmg_index涨跌幅>=n%，国内指数涨跌幅的平均"
cnindex_mean_p3dmg_v_max=0
for i in range(0,20):
    locals()['cnindex_mean_p3dmg'+str(i)] = ans_data[ans_data['p3dmg_index涨跌幅']>=i*0.001]
    locals()['cnindex_mean_p3dmg'+str(i)+'_v'] = ans_data[ans_data['p3dmg_index涨跌幅']>=i*0.001].mean()
    cnindex_mean_p3dmg_v_max = max(cnindex_mean_p3dmg_v_max,locals()['cnindex_mean_p3dmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p3dmg_v_max==locals()['cnindex_mean_p3dmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i*0.001
        max_num = len(locals()['cnindex_mean_p3dmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p3dmg'+str(i)][locals()['cnindex_mean_p3dmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p3dmg_index涨跌幅>={:.2%}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p3dmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p3dmg_index涨跌幅<=-n%，国内指数涨跌幅的平均"
cnindex_mean_p3dmg_v_min=0.0
for i in range(0,50):
    locals()['cnindex_mean_p3dmg'+str(-i)] = ans_data[ans_data['p3dmg_index涨跌幅']<=-i]
    locals()['cnindex_mean_p3dmg'+str(-i)+'_v'] = ans_data[ans_data['p3dmg_index涨跌幅']<=-i].mean()
    cnindex_mean_p3dmg_v_min = min(cnindex_mean_p3dmg_v_min,locals()['cnindex_mean_p3dmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p3dmg_v_min==locals()['cnindex_mean_p3dmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i*0.001
         min_num = len(locals()['cnindex_mean_p3dmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p3dmg'+str(-i)][locals()['cnindex_mean_p3dmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p3dmg_index涨跌幅<={:.2%}  该范围内cnindex下涨概率：{:.2%}'.format(cnindex_mean_p3dmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')



"p4dmg_index涨跌幅>=n%，国内指数涨跌幅的平均"
cnindex_mean_p4dmg_v_max=0
for i in range(0,20):
    locals()['cnindex_mean_p4dmg'+str(i)] = ans_data[ans_data['p4dmg_index涨跌幅']>=i*0.001]
    locals()['cnindex_mean_p4dmg'+str(i)+'_v'] = ans_data[ans_data['p4dmg_index涨跌幅']>=i*0.001].mean()
    cnindex_mean_p4dmg_v_max = max(cnindex_mean_p4dmg_v_max,locals()['cnindex_mean_p4dmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p4dmg_v_max==locals()['cnindex_mean_p4dmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i*0.001
        max_num = len(locals()['cnindex_mean_p4dmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p4dmg'+str(i)][locals()['cnindex_mean_p4dmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p4dmg_index涨跌幅>={:.2%}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p4dmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p4dmg_index涨跌幅<=-n%，国内指数涨跌幅的平均"
cnindex_mean_p4dmg_v_min=0.0
for i in range(0,50):
    locals()['cnindex_mean_p4dmg'+str(-i)] = ans_data[ans_data['p4dmg_index涨跌幅']<=-i]
    locals()['cnindex_mean_p4dmg'+str(-i)+'_v'] = ans_data[ans_data['p4dmg_index涨跌幅']<=-i].mean()
    cnindex_mean_p4dmg_v_min = min(cnindex_mean_p4dmg_v_min,locals()['cnindex_mean_p4dmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p4dmg_v_min==locals()['cnindex_mean_p4dmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i*0.001
         min_num = len(locals()['cnindex_mean_p4dmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p4dmg'+str(-i)][locals()['cnindex_mean_p4dmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p4dmg_index涨跌幅<={:.2%}  该范围内cnindex下涨概率：{:.2%}'.format(cnindex_mean_p4dmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')



"p5dmg_index涨跌幅>=n%，国内指数涨跌幅的平均"
cnindex_mean_p5dmg_v_max=0
for i in range(0,30):
    locals()['cnindex_mean_p5dmg'+str(i)] = ans_data[ans_data['p5dmg_index涨跌幅']>=i*0.001]
    locals()['cnindex_mean_p5dmg'+str(i)+'_v'] = ans_data[ans_data['p5dmg_index涨跌幅']>=i*0.001].mean()
    cnindex_mean_p5dmg_v_max = max(cnindex_mean_p5dmg_v_max,locals()['cnindex_mean_p5dmg'+str(i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p5dmg_v_max==locals()['cnindex_mean_p5dmg'+str(i)+'_v']['cnindex涨跌幅']:
        max_loc = i*0.001
        max_num = len(locals()['cnindex_mean_p5dmg'+str(i)])
        max_num_g0 = len(locals()['cnindex_mean_p5dmg'+str(i)][locals()['cnindex_mean_p5dmg'+str(i)]['cnindex涨跌幅']>=0])
print('国内指数涨跌幅平均最大值{:.2%}   出现在：p5dmg_index涨跌幅>={:.2%}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_p5dmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
"p5dmg_index涨跌幅<=-n%，国内指数涨跌幅的平均"
cnindex_mean_p5dmg_v_min=0.0
for i in range(0,100):
    locals()['cnindex_mean_p5dmg'+str(-i)] = ans_data[ans_data['p5dmg_index涨跌幅']<=-i]
    locals()['cnindex_mean_p5dmg'+str(-i)+'_v'] = ans_data[ans_data['p5dmg_index涨跌幅']<=-i].mean()
    cnindex_mean_p5dmg_v_min = min(cnindex_mean_p5dmg_v_min,locals()['cnindex_mean_p5dmg'+str(-i)+'_v']['cnindex涨跌幅'])  
    if cnindex_mean_p5dmg_v_min==locals()['cnindex_mean_p5dmg'+str(-i)+'_v']['cnindex涨跌幅']:
         min_loc = -i*0.001
         min_num = len(locals()['cnindex_mean_p5dmg'+str(-i)])
         min_num_l0 = len(locals()['cnindex_mean_p5dmg'+str(-i)][locals()['cnindex_mean_p5dmg'+str(-i)]['cnindex涨跌幅']<=0])
print('国内指数涨跌幅平均最小值{:.2%}   出现在：p5dmg_index涨跌幅<={:.2%}  该范围内cnindex下涨概率：{:.2%}'.format(cnindex_mean_p5dmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')


########################################################################################################

"循环尺度   pnd_i*c_n"
c_n = 1

"pnd成交净买额——5列组合研究"
"p1d~p5d 每一列的  max  min  中位数  平均数"

pnd_max = pd.DataFrame(ans_data.max()).rename(columns={0:'max'}).drop(['日期']).reset_index()
pnd_min = pd.DataFrame(ans_data.min()).rename(columns={0:'min'}).drop(['日期']).reset_index()
pnd_median = pd.DataFrame(ans_data.median()).rename(columns={0:'median'}).reset_index()
pnd_mean = pd.DataFrame(ans_data.mean()).rename(columns={0:'mean'}).reset_index()
pnd_skew = pd.DataFrame(ans_data.skew()).rename(columns={0:'skew'}).reset_index()
pnd_kurt = pd.DataFrame(ans_data.kurt()).rename(columns={0:'kurt'}).reset_index()
pnd_std = pd.DataFrame(ans_data.std()).rename(columns={0:'std'}).reset_index()

pnd_sta = pd.merge(left=pnd_max,right=pnd_min,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_median,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_mean,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_skew,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_kurt,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_std,on='index')

for i in range(1,6):
    locals()['p{}d_cje_mean'.format(i)] = round(pnd_mean[pnd_mean['index']=='p{}d成交净买额(亿)'.format(i)].reset_index(drop=True).loc[0,'mean'])
     
    
"p1d~p5d成交净买额<=n亿 ，国内指数涨跌幅的平均"
cnindex_mean_pndjmg_v_min=0.0
cnindex_mean_pndjmg_dp_max = 0.0
for p1d_i in range(7,12):
    for p2d_i in range(12,17):
        for p3d_i in range(32,37):
            for p4d_i in range(32,37):
                for p5d_i in range(2,7):
                        locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)] = ans_data[(ans_data['p1d成交净买额(亿)']<=p1d_cje_mean-p1d_i*c_n)&(ans_data['p2d成交净买额(亿)']<=p2d_cje_mean-p2d_i*c_n)&(ans_data['p3d成交净买额(亿)']<=p3d_cje_mean-p3d_i*c_n)&(ans_data['p4d成交净买额(亿)']<=p4d_cje_mean-p4d_i*c_n)&(ans_data['p5d成交净买额(亿)']<=p5d_cje_mean-p5d_i*c_n)]
                        locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v'] = ans_data[(ans_data['p1d成交净买额(亿)']<=p1d_cje_mean-p1d_i*c_n)&(ans_data['p2d成交净买额(亿)']<=p2d_cje_mean-p2d_i*c_n)&(ans_data['p3d成交净买额(亿)']<=p3d_cje_mean-p3d_i*c_n)&(ans_data['p4d成交净买额(亿)']<=p4d_cje_mean-p4d_i*c_n)&(ans_data['p5d成交净买额(亿)']<=p5d_cje_mean-p5d_i*c_n)].mean()
                        "国内指数涨跌幅平均最小"
                        cnindex_mean_pndjmg_v_min = min(cnindex_mean_pndjmg_v_min,locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅'])   
                        if cnindex_mean_pndjmg_v_min==locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅']:
                             min_loc = str(p1d_cje_mean-p1d_i*c_n)+'_'+str(p2d_cje_mean-p2d_i*c_n)+'_'+str(p3d_cje_mean-p3d_i*c_n)+'_'+str(p4d_cje_mean-p4d_i*c_n)+'_'+str(p5d_cje_mean-p5d_i*c_n)
                             min_num = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)])
                             min_num_l0 = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']<=0])
                             min_num_name = str(p1d_i*c_n)+'_'+str(p2d_i*c_n)+'_'+str(p3d_i*c_n)+'_'+str(p4d_i*c_n)+'_'+str(p5d_i*c_n)
                        "国内指数下跌概率最大"
                        cnindex_mean_pndjmg_dp_max = max(cnindex_mean_pndjmg_dp_max,len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']<=0])/len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]))
                        if cnindex_mean_pndjmg_dp_max==len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']<=0])/len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]):
                            dp_max_loc = str(p1d_cje_mean-p1d_i*c_n)+'_'+str(p2d_cje_mean-p2d_i*c_n)+'_'+str(p3d_cje_mean-p3d_i*c_n)+'_'+str(p4d_cje_mean-p4d_i*c_n)+'_'+str(p5d_cje_mean-p5d_i*c_n)
                            dp_min_num = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)])
                            dp_min_num_l0 = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']<=0])
                            cnindex_mean_pndjmg = locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅']
                            dp_min_num_name = str(p1d_i*c_n)+'_'+str(p2d_i*c_n)+'_'+str(p3d_i*c_n)+'_'+str(p4d_i*c_n)+'_'+str(p5d_i*c_n)
print('国内指数涨跌幅平均最小值{:.2%}   出现在:{}  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_pndjmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')
print('国内指数下跌概率最大值{:.2%}   出现在:{}  该范围内国内指数涨跌幅平均值：{:.2%}'.format(cnindex_mean_pndjmg_dp_max,dp_max_loc,cnindex_mean_pndjmg))
print('出现国内指数下跌概率最大值时数据量：{}/{}'.format(dp_min_num,len(ans_data)))
print('')

 
"p1d~p5d成交净买额>=n亿 ，国内指数涨跌幅的平均"
cnindex_mean_pndjmg_v_max=0.0
cnindex_mean_pndjmg_up_max = 0.0
for p1d_i in range(18,23):
    for p2d_i in range(18,23):
        for p3d_i in range(8,13):
            for p4d_i in range(18,23):
                for p5d_i in range(18,23):
                        locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)] = ans_data[(ans_data['p1d成交净买额(亿)']>=p1d_cje_mean+p1d_i*c_n)&(ans_data['p2d成交净买额(亿)']>=p2d_cje_mean+p2d_i*c_n)&(ans_data['p3d成交净买额(亿)']>=p3d_cje_mean+p3d_i*c_n)&(ans_data['p4d成交净买额(亿)']>=p4d_cje_mean+p4d_i*c_n)&(ans_data['p5d成交净买额(亿)']>=p5d_cje_mean+p5d_i*c_n)]
                        locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v'] = ans_data[(ans_data['p1d成交净买额(亿)']>=p1d_cje_mean+p1d_i*c_n)&(ans_data['p2d成交净买额(亿)']>=p2d_cje_mean+p2d_i*c_n)&(ans_data['p3d成交净买额(亿)']>=p3d_cje_mean+p3d_i*c_n)&(ans_data['p4d成交净买额(亿)']>=p4d_cje_mean+p4d_i*c_n)&(ans_data['p5d成交净买额(亿)']>=p5d_cje_mean+p5d_i*c_n)].mean()
                        "国内指数涨跌幅平均最大"
                        cnindex_mean_pndjmg_v_max = max(cnindex_mean_pndjmg_v_max,locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅'])   
                        if cnindex_mean_pndjmg_v_max==locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅']:
                             max_loc = str(p1d_cje_mean+p1d_i*c_n)+'_'+str(p2d_cje_mean+p2d_i*c_n)+'_'+str(p3d_cje_mean+p3d_i*c_n)+'_'+str(p4d_cje_mean+p4d_i*c_n)+'_'+str(p5d_cje_mean+p5d_i*c_n)
                             max_num = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)])
                             max_num_g0 = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']>=0])
                             max_num_name = str(p1d_i*c_n)+'_'+str(p2d_i*c_n)+'_'+str(p3d_i*c_n)+'_'+str(p4d_i*c_n)+'_'+str(p5d_i*c_n)
                        "国内指数上涨概率最大"
                        cnindex_mean_pndjmg_up_max = max(cnindex_mean_pndjmg_up_max,len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']>=0])/len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]))
                        if cnindex_mean_pndjmg_up_max==len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']>=0])/len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]):
                            up_max_loc = str(p1d_cje_mean+p1d_i*c_n)+'_'+str(p2d_cje_mean+p2d_i*c_n)+'_'+str(p3d_cje_mean+p3d_i*c_n)+'_'+str(p4d_cje_mean+p4d_i*c_n)+'_'+str(p5d_cje_mean+p5d_i*c_n)
                            up_max_num = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)])
                            up_max_num_g0 = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']>=0])
                            cnindex_mean_pndjmg = locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅']
                            dp_max_num_name = str(p1d_i*c_n)+'_'+str(p2d_i*c_n)+'_'+str(p3d_i*c_n)+'_'+str(p4d_i*c_n)+'_'+str(p5d_i*c_n)
print('国内指数涨跌幅平均最大值{:.2%}   出现在:{}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_pndjmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
print('')
print('国内指数上涨概率最大值{:.2%}   出现在:{}  该范围内国内指数涨跌幅平均值：{:.2%}'.format(cnindex_mean_pndjmg_up_max,up_max_loc,cnindex_mean_pndjmg))
print('出现国内指数上涨概率最大值时数据量：{}/{}'.format(up_max_num,len(ans_data)))
print('')


print('出现平均最小值时pnd_i排布：{}'.format(min_num_name))
print('出现国内指数下跌概率最大值时pnd_i排布：{}'.format(dp_min_num_name))
print('出现平均最大值时pnd_i排布：{}'.format(max_num_name))
print('出现国内指数上涨概率最大值时pnd_i排布：{}'.format(dp_max_num_name))




########################################################################################################



"pndmg_index——5列组合研究"
"p1d~p5d 每一列的  max  min  中位数  平均数"

pnd_max = pd.DataFrame(ans_data.max()).rename(columns={0:'max'}).drop(['日期']).reset_index()
pnd_min = pd.DataFrame(ans_data.min()).rename(columns={0:'min'}).drop(['日期']).reset_index()
pnd_median = pd.DataFrame(ans_data.median()).rename(columns={0:'median'}).reset_index()
pnd_mean = pd.DataFrame(ans_data.mean()).rename(columns={0:'mean'}).reset_index()
pnd_skew = pd.DataFrame(ans_data.skew()).rename(columns={0:'skew'}).reset_index()
pnd_kurt = pd.DataFrame(ans_data.kurt()).rename(columns={0:'kurt'}).reset_index()
pnd_std = pd.DataFrame(ans_data.std()).rename(columns={0:'std'}).reset_index()

pnd_sta = pd.merge(left=pnd_max,right=pnd_min,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_median,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_mean,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_skew,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_kurt,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_std,on='index')

for i in range(1,6):
    locals()['p{}d_mg_mean'.format(i)] = round(pnd_mean[pnd_mean['index']=='p{}dmg_index涨跌幅'.format(i)].reset_index(drop=True).loc[0,'mean'])
     
    
"p1d~p5dmg_index涨跌幅<=n ，国内指数涨跌幅的平均"  
cnindex_mean_pndmg_v_min=0.0
cnindex_mean_pndmg_dp_max = 0.0
for p1d_i in range(0,3):
    for p2d_i in range(0,3):
        for p3d_i in range(0,3):
            for p4d_i in range(0,5):
                for p5d_i in range(0,5):
                        locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)] = ans_data[(ans_data['p1dmg_index涨跌幅']<=p1d_mg_mean-p1d_i*0.001)&(ans_data['p2dmg_index涨跌幅']<=p2d_mg_mean-p2d_i*0.001)&(ans_data['p3dmg_index涨跌幅']<=p3d_mg_mean-p3d_i*0.001)&(ans_data['p4dmg_index涨跌幅']<=p4d_mg_mean-p4d_i*0.001)&(ans_data['p5dmg_index涨跌幅']<=p5d_mg_mean-p5d_i*0.001)]
                        locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v'] = ans_data[(ans_data['p1dmg_index涨跌幅']<=p1d_mg_mean-p1d_i*0.001)&(ans_data['p2dmg_index涨跌幅']<=p2d_mg_mean-p2d_i*0.001)&(ans_data['p3dmg_index涨跌幅']<=p3d_mg_mean-p3d_i*0.001)&(ans_data['p4dmg_index涨跌幅']<=p4d_mg_mean-p4d_i*0.001)&(ans_data['p5dmg_index涨跌幅']<=p5d_mg_mean-p5d_i*0.001)].mean()
                        "国内指数涨跌幅平均最小"
                        cnindex_mean_pndmg_v_min = min(cnindex_mean_pndmg_v_min,locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅'])   
                        if cnindex_mean_pndmg_v_min==locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅']:
                             min_loc = str(p1d_mg_mean-p1d_i*0.001)+'_'+str(p2d_mg_mean-p2d_i*0.001)+'_'+str(p3d_mg_mean-p3d_i*0.001)+'_'+str(p4d_mg_mean-p4d_i*0.001)+'_'+str(p5d_mg_mean-p5d_i*0.001)
                             min_num = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)])
                             min_num_l0 = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']<=0])
                        "国内指数下跌概率最大"
                        cnindex_mean_pndmg_dp_max = max(cnindex_mean_pndmg_dp_max,len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']<=0])/len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]))
                        if cnindex_mean_pndmg_dp_max==len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']<=0])/len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]):
                            dp_max_loc = str(p1d_mg_mean-p1d_i*0.001)+'_'+str(p2d_mg_mean-p2d_i*0.001)+'_'+str(p3d_mg_mean-p3d_i*0.001)+'_'+str(p4d_mg_mean-p4d_i*0.001)+'_'+str(p5d_mg_mean-p5d_i*0.001)
                            dp_min_num = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)])
                            dp_min_num_l0 = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']<=0])
                            cnindex_mean_pndmg = locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅']
                        
print('国内指数涨跌幅平均最小值{:.2%}   出现在:{}  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_pndmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')
print('国内指数下跌概率最大值{:.2%}   出现在:{}  该范围内国内指数涨跌幅平均值：{:.2%}'.format(cnindex_mean_pndmg_dp_max,dp_max_loc,cnindex_mean_pndmg))
print('出现国内指数下跌概率最大值时数据量：{}/{}'.format(dp_min_num,len(ans_data)))
print('')
 
"p1d~p5dmg_index涨跌幅>=n ，国内指数涨跌幅的平均"
cnindex_mean_pndmg_v_max=0.0
cnindex_mean_pndmg_up_max = 0.0
for p1d_i in range(0,5):
    for p2d_i in range(0,5):
        for p3d_i in range(0,10):
            for p4d_i in range(0,8):
                for p5d_i in range(0,8):
                        locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)] = ans_data[(ans_data['p1dmg_index涨跌幅']>=p1d_mg_mean+p1d_i*0.001)&(ans_data['p2dmg_index涨跌幅']>=p2d_mg_mean+p2d_i*0.001)&(ans_data['p3dmg_index涨跌幅']>=p3d_mg_mean+p3d_i*0.001)&(ans_data['p4dmg_index涨跌幅']>=p4d_mg_mean+p4d_i*0.001)&(ans_data['p5dmg_index涨跌幅']>=p5d_mg_mean+p5d_i*0.001)]
                        locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v'] = ans_data[(ans_data['p1dmg_index涨跌幅']>=p1d_mg_mean+p1d_i*0.001)&(ans_data['p2dmg_index涨跌幅']>=p2d_mg_mean+p2d_i*0.001)&(ans_data['p3dmg_index涨跌幅']>=p3d_mg_mean+p3d_i*0.001)&(ans_data['p4dmg_index涨跌幅']>=p4d_mg_mean+p4d_i*0.001)&(ans_data['p5dmg_index涨跌幅']>=p5d_mg_mean+p5d_i*0.001)].mean()
                        "国内指数涨跌幅平均最大"
                        cnindex_mean_pndmg_v_max = max(cnindex_mean_pndmg_v_max,locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅'])   
                        if cnindex_mean_pndmg_v_max==locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅']:
                             max_loc = str(p1d_mg_mean+p1d_i*0.001)+'_'+str(p2d_mg_mean+p2d_i*0.001)+'_'+str(p3d_mg_mean+p3d_i*0.001)+'_'+str(p4d_mg_mean+p4d_i*0.001)+'_'+str(p5d_mg_mean+p5d_i*0.001)
                             max_num = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)])
                             max_num_g0 = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']>=0])
                        "国内指数上涨概率最大"
                        cnindex_mean_pndmg_up_max = max(cnindex_mean_pndmg_up_max,len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']>=0])/len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]))
                        if cnindex_mean_pndmg_up_max==len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']>=0])/len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]):
                            up_max_loc = str(p1d_mg_mean+p1d_i*0.001)+'_'+str(p2d_mg_mean+p2d_i*0.001)+'_'+str(p3d_mg_mean+p3d_i*0.001)+'_'+str(p4d_mg_mean+p4d_i*0.001)+'_'+str(p5d_mg_mean+p5d_i*0.001)
                            up_max_num = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)])
                            up_max_num_g0 = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)]['cnindex涨跌幅']>=0])
                            cnindex_mean_pndmg = locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+str(p4d_i)+str(p5d_i)+'_v']['cnindex涨跌幅']
                        
print('国内指数涨跌幅平均最大值{:.2%}   出现在:{}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_pndmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
print('')
print('国内指数上涨概率最大值{:.2%}   出现在:{}  该范围内国内指数涨跌幅平均值：{:.2%}'.format(cnindex_mean_pndmg_up_max,up_max_loc,cnindex_mean_pndmg))
print('出现国内指数上涨概率最大值时数据量：{}/{}'.format(up_max_num,len(ans_data)))
print('')





########################################################################################################
"三日研究"


"循环尺度   pnd_i*c_n"
c_n = 1

"pnd成交净买额——5列组合研究"
"p1d~p5d 每一列的  max  min  中位数  平均数"

pnd_max = pd.DataFrame(ans_data.max()).rename(columns={0:'max'}).drop(['日期']).reset_index()
pnd_min = pd.DataFrame(ans_data.min()).rename(columns={0:'min'}).drop(['日期']).reset_index()
pnd_median = pd.DataFrame(ans_data.median()).rename(columns={0:'median'}).reset_index()
pnd_mean = pd.DataFrame(ans_data.mean()).rename(columns={0:'mean'}).reset_index()
pnd_skew = pd.DataFrame(ans_data.skew()).rename(columns={0:'skew'}).reset_index()
pnd_kurt = pd.DataFrame(ans_data.kurt()).rename(columns={0:'kurt'}).reset_index()
pnd_std = pd.DataFrame(ans_data.std()).rename(columns={0:'std'}).reset_index()

pnd_sta = pd.merge(left=pnd_max,right=pnd_min,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_median,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_mean,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_skew,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_kurt,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_std,on='index')

for i in range(1,4):
    locals()['p{}d_cje_mean'.format(i)] = round(pnd_mean[pnd_mean['index']=='p{}d成交净买额(亿)'.format(i)].reset_index(drop=True).loc[0,'mean'])
     
    
"p1d~p5d成交净买额<=n亿 ，国内指数涨跌幅的平均"
cnindex_mean_pndjmg_v_min=0.0
cnindex_mean_pndjmg_dp_max = 0.0
for p1d_i in range(0,10):
    for p2d_i in range(0,10):
        for p3d_i in range(0,10):
            locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)] = ans_data[(ans_data['p1d成交净买额(亿)']<=p1d_cje_mean-p1d_i*c_n)&(ans_data['p2d成交净买额(亿)']<=p2d_cje_mean-p2d_i*c_n)&(ans_data['p3d成交净买额(亿)']<=p3d_cje_mean-p3d_i*c_n)]
            locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v'] = ans_data[(ans_data['p1d成交净买额(亿)']<=p1d_cje_mean-p1d_i*c_n)&(ans_data['p2d成交净买额(亿)']<=p2d_cje_mean-p2d_i*c_n)&(ans_data['p3d成交净买额(亿)']<=p3d_cje_mean-p3d_i*c_n)].mean()
            "国内指数涨跌幅平均最小"
            cnindex_mean_pndjmg_v_min = min(cnindex_mean_pndjmg_v_min,locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅'])   
            if cnindex_mean_pndjmg_v_min==locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅']:
                 min_loc = str(p1d_cje_mean-p1d_i*c_n)+'_'+str(p2d_cje_mean-p2d_i*c_n)+'_'+str(p3d_cje_mean-p3d_i*c_n)
                 min_num = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)])
                 min_num_l0 = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']<=0])
                 min_num_name = str(p1d_i*c_n)+'_'+str(p2d_i*c_n)+'_'+str(p3d_i*c_n)
            "国内指数下跌概率最大"
            cnindex_mean_pndjmg_dp_max = max(cnindex_mean_pndjmg_dp_max,len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']<=0])/len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]))
            if cnindex_mean_pndjmg_dp_max==len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']<=0])/len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]):
                dp_max_loc = str(p1d_cje_mean-p1d_i*c_n)+'_'+str(p2d_cje_mean-p2d_i*c_n)+'_'+str(p3d_cje_mean-p3d_i*c_n)
                dp_min_num = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)])
                dp_min_num_l0 = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']<=0])
                cnindex_mean_pndjmg = locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅']
                dp_min_num_name = str(p1d_i*c_n)+'_'+str(p2d_i*c_n)+'_'+str(p3d_i*c_n)
print('国内指数涨跌幅平均最小值{:.2%}   出现在:{}  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_pndjmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')
print('国内指数下跌概率最大值{:.2%}   出现在:{}  该范围内国内指数涨跌幅平均值：{:.2%}'.format(cnindex_mean_pndjmg_dp_max,dp_max_loc,cnindex_mean_pndjmg))
print('出现国内指数下跌概率最大值时数据量：{}/{}'.format(dp_min_num,len(ans_data)))
print('')

 
"p1d~p5d成交净买额>=n亿 ，国内指数涨跌幅的平均"
cnindex_mean_pndjmg_v_max=0.0
cnindex_mean_pndjmg_up_max = 0.0
for p1d_i in range(0,10):
    for p2d_i in range(0,10):
        for p3d_i in range(0,10):
            locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)] = ans_data[(ans_data['p1d成交净买额(亿)']>=p1d_cje_mean+p1d_i*c_n)&(ans_data['p2d成交净买额(亿)']>=p2d_cje_mean+p2d_i*c_n)&(ans_data['p3d成交净买额(亿)']>=p3d_cje_mean+p3d_i*c_n)]
            locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v'] = ans_data[(ans_data['p1d成交净买额(亿)']>=p1d_cje_mean+p1d_i*c_n)&(ans_data['p2d成交净买额(亿)']>=p2d_cje_mean+p2d_i*c_n)&(ans_data['p3d成交净买额(亿)']>=p3d_cje_mean+p3d_i*c_n)].mean()
            "国内指数涨跌幅平均最大"
            cnindex_mean_pndjmg_v_max = max(cnindex_mean_pndjmg_v_max,locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅'])   
            if cnindex_mean_pndjmg_v_max==locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅']:
                 max_loc = str(p1d_cje_mean+p1d_i*c_n)+'_'+str(p2d_cje_mean+p2d_i*c_n)+'_'+str(p3d_cje_mean+p3d_i*c_n)
                 max_num = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)])
                 max_num_g0 = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']>=0])
                 max_num_name = str(p1d_i*c_n)+'_'+str(p2d_i*c_n)+'_'+str(p3d_i*c_n)
            "国内指数上涨概率最大"
            cnindex_mean_pndjmg_up_max = max(cnindex_mean_pndjmg_up_max,len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']>=0])/len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]))
            if cnindex_mean_pndjmg_up_max==len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']>=0])/len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]):
                up_max_loc = str(p1d_cje_mean+p1d_i*c_n)+'_'+str(p2d_cje_mean+p2d_i*c_n)+'_'+str(p3d_cje_mean+p3d_i*c_n)
                up_max_num = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)])
                up_max_num_g0 = len(locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']>=0])
                cnindex_mean_pndjmg = locals()['cnindex_mean_pndjmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅']
                dp_max_num_name = str(p1d_i*c_n)+'_'+str(p2d_i*c_n)+'_'+str(p3d_i*c_n)
print('国内指数涨跌幅平均最大值{:.2%}   出现在:{}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_pndjmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
print('')
print('国内指数上涨概率最大值{:.2%}   出现在:{}  该范围内国内指数涨跌幅平均值：{:.2%}'.format(cnindex_mean_pndjmg_up_max,up_max_loc,cnindex_mean_pndjmg))
print('出现国内指数上涨概率最大值时数据量：{}/{}'.format(up_max_num,len(ans_data)))
print('')


print('出现平均最小值时pnd_i排布：{}'.format(min_num_name))
print('出现国内指数下跌概率最大值时pnd_i排布：{}'.format(dp_min_num_name))
print('出现平均最大值时pnd_i排布：{}'.format(max_num_name))
print('出现国内指数上涨概率最大值时pnd_i排布：{}'.format(dp_max_num_name))




########################################################################################################
"三日研究"


"pndmg_index——5列组合研究"
"p1d~p5d 每一列的  max  min  中位数  平均数"

pnd_max = pd.DataFrame(ans_data.max()).rename(columns={0:'max'}).drop(['日期']).reset_index()
pnd_min = pd.DataFrame(ans_data.min()).rename(columns={0:'min'}).drop(['日期']).reset_index()
pnd_median = pd.DataFrame(ans_data.median()).rename(columns={0:'median'}).reset_index()
pnd_mean = pd.DataFrame(ans_data.mean()).rename(columns={0:'mean'}).reset_index()
pnd_skew = pd.DataFrame(ans_data.skew()).rename(columns={0:'skew'}).reset_index()
pnd_kurt = pd.DataFrame(ans_data.kurt()).rename(columns={0:'kurt'}).reset_index()
pnd_std = pd.DataFrame(ans_data.std()).rename(columns={0:'std'}).reset_index()

pnd_sta = pd.merge(left=pnd_max,right=pnd_min,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_median,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_mean,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_skew,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_kurt,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_std,on='index')

for i in range(1,4):
    locals()['p{}d_mg_mean'.format(i)] = round(pnd_mean[pnd_mean['index']=='p{}dmg_index涨跌幅'.format(i)].reset_index(drop=True).loc[0,'mean'])
     
    
"p1d~p5dmg_index涨跌幅<=n ，国内指数涨跌幅的平均"  
cnindex_mean_pndmg_v_min=0.0
cnindex_mean_pndmg_dp_max = 0.0
for p1d_i in range(0,3):
    for p2d_i in range(0,5):
        for p3d_i in range(0,10):
            locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)] = ans_data[(ans_data['p1dmg_index涨跌幅']<=p1d_mg_mean-p1d_i*0.001)&(ans_data['p2dmg_index涨跌幅']<=p2d_mg_mean-p2d_i*0.001)&(ans_data['p3dmg_index涨跌幅']<=p3d_mg_mean-p3d_i*0.001)]
            locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v'] = ans_data[(ans_data['p1dmg_index涨跌幅']<=p1d_mg_mean-p1d_i*0.001)&(ans_data['p2dmg_index涨跌幅']<=p2d_mg_mean-p2d_i*0.001)&(ans_data['p3dmg_index涨跌幅']<=p3d_mg_mean-p3d_i*0.001)].mean()
            "国内指数涨跌幅平均最小"
            cnindex_mean_pndmg_v_min = min(cnindex_mean_pndmg_v_min,locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅'])   
            if cnindex_mean_pndmg_v_min==locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅']:
                 min_loc = str(p1d_mg_mean-p1d_i*0.001)+'_'+str(p2d_mg_mean-p2d_i*0.001)+'_'+str(p3d_mg_mean-p3d_i*0.001)
                 min_num = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)])
                 min_num_l0 = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']<=0])
                 min_num_name = str(p1d_i)+'_'+str(p2d_i)+'_'+str(p3d_i)
            "国内指数下跌概率最大"
            cnindex_mean_pndmg_dp_max = max(cnindex_mean_pndmg_dp_max,len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']<=0])/len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]))
            if cnindex_mean_pndmg_dp_max==len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']<=0])/len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]):
                dp_max_loc = str(p1d_mg_mean-p1d_i*0.001)+'_'+str(p2d_mg_mean-p2d_i*0.001)+'_'+str(p3d_mg_mean-p3d_i*0.001)
                dp_min_num = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)])
                dp_min_num_l0 = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']<=0])
                cnindex_mean_pndmg = locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅']
                dp_min_num_name = str(p1d_i)+'_'+str(p2d_i)+'_'+str(p3d_i)
                
print('国内指数涨跌幅平均最小值{:.2%}   出现在:{}  该范围内cnindex下跌概率：{:.2%}'.format(cnindex_mean_pndmg_v_min,min_loc,min_num_l0/min_num))
print('出现平均最小值时数据量：{}/{}'.format(min_num,len(ans_data)))
print('')
print('国内指数下跌概率最大值{:.2%}   出现在:{}  该范围内国内指数涨跌幅平均值：{:.2%}'.format(cnindex_mean_pndmg_dp_max,dp_max_loc,cnindex_mean_pndmg))
print('出现国内指数下跌概率最大值时数据量：{}/{}'.format(dp_min_num,len(ans_data)))
print('')
 
"p1d~p5dmg_index涨跌幅>=n ，国内指数涨跌幅的平均"
cnindex_mean_pndmg_v_max=0.0
cnindex_mean_pndmg_up_max = 0.0
for p1d_i in range(0,5):
    for p2d_i in range(0,10):
        for p3d_i in range(0,15):
            locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)] = ans_data[(ans_data['p1dmg_index涨跌幅']>=p1d_mg_mean+p1d_i*0.001)&(ans_data['p2dmg_index涨跌幅']>=p2d_mg_mean+p2d_i*0.001)&(ans_data['p3dmg_index涨跌幅']>=p3d_mg_mean+p3d_i*0.001)]
            locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v'] = ans_data[(ans_data['p1dmg_index涨跌幅']>=p1d_mg_mean+p1d_i*0.001)&(ans_data['p2dmg_index涨跌幅']>=p2d_mg_mean+p2d_i*0.001)&(ans_data['p3dmg_index涨跌幅']>=p3d_mg_mean+p3d_i*0.001)].mean()
            "国内指数涨跌幅平均最大"
            cnindex_mean_pndmg_v_max = max(cnindex_mean_pndmg_v_max,locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅'])   
            if cnindex_mean_pndmg_v_max==locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅']:
                 max_loc = str(p1d_mg_mean+p1d_i*0.001)+'_'+str(p2d_mg_mean+p2d_i*0.001)+'_'+str(p3d_mg_mean+p3d_i*0.001)
                 max_num = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)])
                 max_num_g0 = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']>=0])
                 max_num_name = str(p1d_i)+'_'+str(p2d_i)+'_'+str(p3d_i)
            "国内指数上涨概率最大"
            cnindex_mean_pndmg_up_max = max(cnindex_mean_pndmg_up_max,len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']>=0])/len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]))
            if cnindex_mean_pndmg_up_max==len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']>=0])/len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]):
                up_max_loc = str(p1d_mg_mean+p1d_i*0.001)+'_'+str(p2d_mg_mean+p2d_i*0.001)+'_'+str(p3d_mg_mean+p3d_i*0.001)
                up_max_num = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)])
                up_max_num_g0 = len(locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)][locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)]['cnindex涨跌幅']>=0])
                cnindex_mean_pndmg = locals()['cnindex_mean_pndmg'+str(p1d_i)+str(p2d_i)+str(p3d_i)+'_v']['cnindex涨跌幅']
                dp_max_num_name = str(p1d_i)+'_'+str(p2d_i)+'_'+str(p3d_i)
print('国内指数涨跌幅平均最大值{:.2%}   出现在:{}  该范围内cnindex上涨概率：{:.2%}'.format(cnindex_mean_pndmg_v_max,max_loc,max_num_g0/max_num))
print('出现平均最大值时数据量：{}/{}'.format(max_num,len(ans_data)))
print('')
print('国内指数上涨概率最大值{:.2%}   出现在:{}  该范围内国内指数涨跌幅平均值：{:.2%}'.format(cnindex_mean_pndmg_up_max,up_max_loc,cnindex_mean_pndmg))
print('出现国内指数上涨概率最大值时数据量：{}/{}'.format(up_max_num,len(ans_data)))
print('')


print('出现平均最小值时pnd_i排布：{}'.format(min_num_name))
print('出现国内指数下跌概率最大值时pnd_i排布：{}'.format(dp_min_num_name))
print('出现平均最大值时pnd_i排布：{}'.format(max_num_name))
print('出现国内指数上涨概率最大值时pnd_i排布：{}'.format(dp_max_num_name))



########################################################################################################

"当日研究"

ans_data_od = ans_data[['日期','cnindex涨跌幅','当日成交净买额(亿)','p1dmg_index涨跌幅']]

pnd_max = pd.DataFrame(ans_data_od.max()).rename(columns={0:'max'}).drop(['日期']).reset_index()
pnd_min = pd.DataFrame(ans_data_od.min()).rename(columns={0:'min'}).drop(['日期']).reset_index()
pnd_median = pd.DataFrame(ans_data_od.median()).rename(columns={0:'median'}).reset_index()
pnd_mean = pd.DataFrame(ans_data_od.mean()).rename(columns={0:'mean'}).reset_index()
pnd_skew = pd.DataFrame(ans_data_od.skew()).rename(columns={0:'skew'}).reset_index()
pnd_kurt = pd.DataFrame(ans_data_od.kurt()).rename(columns={0:'kurt'}).reset_index()
pnd_std = pd.DataFrame(ans_data_od.std()).rename(columns={0:'std'}).reset_index()

pnd_sta = pd.merge(left=pnd_max,right=pnd_min,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_median,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_mean,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_skew,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_kurt,on='index')
pnd_sta = pd.merge(left=pnd_sta,right=pnd_std,on='index')


"只用均值作为基准值"

p0d_cje_mean = round(pnd_mean[pnd_mean['index']=='当日成交净买额(亿)'].reset_index(drop=True).loc[0,'mean'])
p1d_mg_mean = round(pnd_mean[pnd_mean['index']=='p1dmg_index涨跌幅'].reset_index(drop=True).loc[0,'mean'])

"设置变量"
cnindex_mean_p0dcje = pd.DataFrame(columns=('当日成交净买额(亿)','cnindex涨跌幅','数据量','同涨同跌数据量'))
cnindex_mean_p1dmg = pd.DataFrame(columns=('p1dmg_index涨跌幅','cnindex涨跌幅','数据量','同涨同跌数据量'))
cje_n = 10
mg_n = 0.001

for p1d_i in range(-10,1):
    "北向资金  <="
    cnindex_mean_p0dcje_bd = pd.DataFrame(ans_data_od[ans_data_od['当日成交净买额(亿)']<=p0d_cje_mean+p1d_i*cje_n].mean()).T
    cnindex_mean_p0dcje_bd['数据量'] = '{}/{}'.format(len(ans_data_od[ans_data_od['当日成交净买额(亿)']<=p0d_cje_mean+p1d_i*10]),len(ans_data_od))
    cnindex_mean_p0dcje_bd['同涨同跌数据量'] = '{}/{}'.format(len(ans_data_od[(ans_data_od['当日成交净买额(亿)']<=p0d_cje_mean+p1d_i*cje_n)&(ans_data_od['cnindex涨跌幅']<=0)]),len(ans_data_od[ans_data_od['当日成交净买额(亿)']<=p0d_cje_mean+p1d_i*cje_n]))
    cnindex_mean_p0dcje_bd['当日成交净买额(亿)'] = '<={}'.format(p0d_cje_mean+p1d_i*cje_n)
    cnindex_mean_p0dcje_bd['cnindex涨跌幅'] = format(cnindex_mean_p0dcje_bd.loc[0,'cnindex涨跌幅'],'.2%')
    cnindex_mean_p0dcje_bd = cnindex_mean_p0dcje_bd[['当日成交净买额(亿)','cnindex涨跌幅','数据量','同涨同跌数据量']]
    cnindex_mean_p0dcje = cnindex_mean_p0dcje.append(cnindex_mean_p0dcje_bd)

    "美股涨跌幅  <="
    cnindex_mean_p1dmg_bd = pd.DataFrame(ans_data_od[ans_data_od['p1dmg_index涨跌幅']<=p1d_mg_mean+p1d_i*mg_n].mean()).T
    cnindex_mean_p1dmg_bd['数据量'] = '{}/{}'.format(len(ans_data_od[ans_data_od['p1dmg_index涨跌幅']<=p1d_mg_mean+p1d_i*mg_n]),len(ans_data_od))
    cnindex_mean_p1dmg_bd['同涨同跌数据量'] = '{}/{}'.format(len(ans_data_od[(ans_data_od['p1dmg_index涨跌幅']<=p1d_mg_mean+p1d_i*mg_n)&(ans_data_od['cnindex涨跌幅']<=0)]),len(ans_data_od[ans_data_od['p1dmg_index涨跌幅']<=p1d_mg_mean+p1d_i*mg_n]))
    cnindex_mean_p1dmg_bd['p1dmg_index涨跌幅'] = '<={:.2%}'.format(p1d_mg_mean+p1d_i*mg_n)
    cnindex_mean_p1dmg_bd['cnindex涨跌幅'] = format(cnindex_mean_p1dmg_bd.loc[0,'cnindex涨跌幅'],'.2%')
    cnindex_mean_p1dmg_bd = cnindex_mean_p1dmg_bd[['p1dmg_index涨跌幅','cnindex涨跌幅','数据量','同涨同跌数据量']]
    cnindex_mean_p1dmg = cnindex_mean_p1dmg.append(cnindex_mean_p1dmg_bd)
    
    
    
for p1d_i in range(0,11):
    "北向资金  >="
    cnindex_mean_p0dcje_bu = pd.DataFrame(ans_data_od[ans_data_od['当日成交净买额(亿)']>=p0d_cje_mean+p1d_i*cje_n].mean()).T
    cnindex_mean_p0dcje_bu['数据量'] = '{}/{}'.format(len(ans_data_od[ans_data_od['当日成交净买额(亿)']>=p0d_cje_mean+p1d_i*cje_n]),len(ans_data_od))
    cnindex_mean_p0dcje_bu['同涨同跌数据量'] = '{}/{}'.format(len(ans_data_od[(ans_data_od['当日成交净买额(亿)']>=p0d_cje_mean+p1d_i*cje_n)&(ans_data_od['cnindex涨跌幅']>=0)]),len(ans_data_od[ans_data_od['当日成交净买额(亿)']>=p0d_cje_mean+p1d_i*cje_n]))
    cnindex_mean_p0dcje_bu['当日成交净买额(亿)'] = '>={}'.format(p0d_cje_mean+p1d_i*cje_n)
    cnindex_mean_p0dcje_bu['cnindex涨跌幅'] = format(cnindex_mean_p0dcje_bu.loc[0,'cnindex涨跌幅'],'.2%')
    cnindex_mean_p0dcje_bu = cnindex_mean_p0dcje_bu[['当日成交净买额(亿)','cnindex涨跌幅','数据量','同涨同跌数据量']]
    cnindex_mean_p0dcje = cnindex_mean_p0dcje.append(cnindex_mean_p0dcje_bu)
    
    "美股涨跌幅  >="
    cnindex_mean_p1dmg_bu = pd.DataFrame(ans_data_od[ans_data_od['p1dmg_index涨跌幅']>=p1d_mg_mean+p1d_i*mg_n].mean()).T
    cnindex_mean_p1dmg_bu['数据量'] = '{}/{}'.format(len(ans_data_od[ans_data_od['p1dmg_index涨跌幅']>=p1d_mg_mean+p1d_i*mg_n]),len(ans_data_od))
    cnindex_mean_p1dmg_bu['同涨同跌数据量'] = '{}/{}'.format(len(ans_data_od[(ans_data_od['p1dmg_index涨跌幅']>=p1d_mg_mean+p1d_i*mg_n)&(ans_data_od['cnindex涨跌幅']>=0)]),len(ans_data_od[ans_data_od['p1dmg_index涨跌幅']>=p1d_mg_mean+p1d_i*mg_n]))
    cnindex_mean_p1dmg_bu['p1dmg_index涨跌幅'] = '>={:.2%}'.format(p1d_mg_mean+p1d_i*mg_n)
    cnindex_mean_p1dmg_bu['cnindex涨跌幅'] = format(cnindex_mean_p1dmg_bu.loc[0,'cnindex涨跌幅'],'.2%')
    cnindex_mean_p1dmg_bu = cnindex_mean_p1dmg_bu[['p1dmg_index涨跌幅','cnindex涨跌幅','数据量','同涨同跌数据量']]
    cnindex_mean_p1dmg = cnindex_mean_p1dmg.append(cnindex_mean_p1dmg_bu)
 
    
    
    








































