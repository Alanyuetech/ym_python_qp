# -*- coding: utf-8 -*-
"""
Created on Wed Jul 13 09:57:25 2022

@author: Administrator
"""


import pandas as pd
import numpy as np
import requests
import re
from selenium import webdriver
import time
import datetime
import pymysql
import akshare as ak
from functools import reduce
from dateutil.relativedelta import relativedelta


'''每日基金的基本信息'''
def essential_infor(url,bs):
    # option = webdriver.ChromeOptions()
    # option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    # browser=webdriver.Chrome(chrome_options=option)        # 全屏
    
    option = webdriver.ChromeOptions()    
    option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    browser=webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe',chrome_options=option)        # 全屏

    browser.get(url)
    # element = browser.find_element_by_css_selector('#allfund')
    # browser.execute_script("arguments[0].click();",element)
    # time.sleep(8)
    data=browser.page_source
    browser.quit()

    p_id_num='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
    id_num=re.findall(p_id_num,data,re.S)
    p_info='<td class=.*?>(.*?)</td>'
    info=re.findall(p_info,data,re.S)
    


    p_id_num='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
    id_num=re.findall(p_id_num,data,re.S)
    
    p_name='<tbody>.*?<td><a href=.*?>.*?</a></td><td><a href=".*?" title="(.*?)">.*?</a></td>'
    name=re.findall(p_name,data,re.S)
    
    bijiao=[[],[],[],[],[],[],[],[],[],[],[],[],[]]
    for i in range(len(info)):
        bijiao[i%13].append(info[i])
    
    # data_final = pd.DataFrame(columns=['单位净值','累计净值','D1','D7','D30','D90','D180','D360','D720','近3年','今年来','成立来','{}'.format(bs)])
    

    
    # for i in range(len(bijiao)):
    #     data_final.iloc[:,i]=bijiao[i]
        
        
        
        
    data_final = pd.DataFrame(columns=['{}'.format(bs)])   
    data_final['{}'.format(bs)]=bijiao[12]
    
    
    
    
    
    data_final['id']=id_num
    bb = data_final[['id','{}'.format(bs)]].copy()

    return bb


def essential_infor_month(url,bs):
    # option = webdriver.ChromeOptions()
    # option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    # browser=webdriver.Chrome(chrome_options=option) 
    
    option = webdriver.ChromeOptions()    
    option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    browser=webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe',chrome_options=option)        # 全屏
 
    
    browser.get(url)
    '''element = browser.find_element_by_css_selector('#allfund')
    browser.execute_script("arguments[0].click();",element)
    time.sleep(8)'''
    data=browser.page_source
    browser.quit()
    p_buy = '<td><a .*? class="buy(.*?)"'
    buy = re.findall(p_buy, data)
    p_id_num='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
    id_num=re.findall(p_id_num,data,re.S)
    p_info='<td class=.*?>(.*?)</td>'
    info=re.findall(p_info,data,re.S)
    
    p_days='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>.*?</a></td><td><a href=.*? title=.*?>.*?/a></td><td>(.*?)</td>'
    days=re.findall(p_days,data,re.S)
    p_buy = '<td><a .*? class="buy(.*?)"'
    buy = re.findall(p_buy, data)
    p_id_num='<td><input id=.*? type="checkbox"></td><td>.*?</td><td><a href=.*?>(.*?)</a></td><td>'
    id_num=re.findall(p_id_num,data,re.S)
    
    p_name='<tbody>.*?<td><a href=.*?>.*?</a></td><td><a href=".*?" title="(.*?)">.*?</a></td>'
    name=re.findall(p_name,data,re.S)
    
    bijiao=[[],[],[],[],[],[],[],[],[],[],[],[],[]]
    for i in range(len(info)):
        bijiao[i%13].append(info[i])
    
    data_final = pd.DataFrame(columns=['单位净值','累计净值','日增长率','近1周','近1月','近3月','近6月','近1年'	,'近2年'	,'近3年'	,'今年来','成立来','自定义'])
    for i in range(len(bijiao)):
        data_final.iloc[:,i]=bijiao[i]
        
    data_final['id']=id_num
    data_final['days']=days
    data_final['buy']=buy
    data_use=pd.DataFrame(data_final[['自定义','id']])
    data_use.columns=['{}'.format(bs),'id']
    data_use = data_use[['id','{}'.format(bs)]]
    return data_use



def max_drawback(stock_data):
    
    "可能存在 应该使用loc[index,row]的问题，不行就直接用for循环"
    "找当前日期前的最大值，算出截至当日的最大回撤，算出整个区间段内的最大回撤"
    stock_data['前最大值'] = stock_data.apply(lambda x:stock_data[stock_data['净值日期']<x['净值日期']]['累计净值'].max(),axis=1)
    stock_data['截至当日最大回撤'] = 100*(1 - stock_data['累计净值']/stock_data['前最大值'])
    max_db = round(stock_data['截至当日最大回撤'].max(),2)
       
    # "for 循环   备用"
    # for index,row in stock_data.iterrows():
    #     stock_data.loc[index,'前最大值'] = stock_data[stock_data['净值日期']<row['净值日期']]['累计净值'].max()
    # for index,row in stock_data.iterrows():                 
    #     stock_data.loc[index,'截至当日最大回撤'] = 100*(1 - row['累计净值']/row['前最大值'])
    # max_db = round(stock_data['截至当日最大回撤'].max(),2)
    
    
    return max_db
################################################################################################################################################



time_list = ['20200301','20200801','20201001','20210301','20210801','20211001','20220101','20220301','20220501']

for base_time_i in  time_list:
    base_time = base_time_i
     
    base_time_time = datetime.datetime.strptime(base_time, '%Y%m%d')
    
    after_7 = (base_time_time-datetime.timedelta(days=7)).strftime('%Y%m%d')
    after_30 = (base_time_time-datetime.timedelta(days=30)).strftime('%Y%m%d')
    after_60 = (base_time_time-datetime.timedelta(days=60)).strftime('%Y%m%d')
    after_90 = (base_time_time-datetime.timedelta(days=90)).strftime('%Y%m%d')
    after_180 = (base_time_time-datetime.timedelta(days=180)).strftime('%Y%m%d')
    after_270 = (base_time_time-datetime.timedelta(days=270)).strftime('%Y%m%d')
    after_360 = (base_time_time-datetime.timedelta(days=360)).strftime('%Y%m%d')
    after_720 = (base_time_time-datetime.timedelta(days=720)).strftime('%Y%m%d')
    
    url_7='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_7+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_30='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_30+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_60='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_60+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_90='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_90+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_180='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_180+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_270='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_270+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_360='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_360+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_720='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_720+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'


    # for url_bs in ['7','30','60','90','180','270','360','720']:
        
    #     ans_data = essential_infor(locals()['url_{}'.format(url_bs)],'D{}'.format(url_bs))
    #     ans_data.to_excel('data_{}_D{}.xlsx'.format(base_time,url_bs))
    #     print(base_time_i,'url_{}'.format(url_bs))


    for url_bs in ['7','30','60','90','180','270','360','720']:
        
        locals()['D{}'.format(url_bs)] = essential_infor(locals()['url_{}'.format(url_bs)],'D{}'.format(url_bs))
        print(base_time_i,'url_{}'.format(url_bs))
        
    dfs = [D7,D30,D60,D90,D180,D270,D360,D720]
    ans_data = reduce(lambda x,y:pd.merge(x,y,on='id',how='outer'),dfs)
    
    ans_data.to_excel('基金历史节点数据_{}.xlsx'.format(base_time))
    print('完成  {}'.format(base_time))


################################################################################################################################################

time_list = ['20200101','20200601','20210101','20210601','20220101']

for base_time_i in  time_list:
    
    base_time = base_time_i
     
    base_time_time = datetime.datetime.strptime(base_time, '%Y%m%d')

    time_m3 = (base_time_time-datetime.timedelta(days=90)).strftime('%Y%m%d')
    time_m6 = (base_time_time-datetime.timedelta(days=180)).strftime('%Y%m%d')
    time_m9 = (base_time_time-datetime.timedelta(days=270)).strftime('%Y%m%d')
    time_m12 = (base_time_time-datetime.timedelta(days=360)).strftime('%Y%m%d')    



    url_m3='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+time_m3+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_m6='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+time_m6+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_m9='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+time_m9+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_m12='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+time_m12+';qed'+base_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'


    for url_bs in ['m3','m6','m9','m12']:
        
        locals()['{}'.format(url_bs)] = essential_infor_month(locals()['url_{}'.format(url_bs)],'time_{}'.format(url_bs))
        print(base_time_i,'time_{}'.format(url_bs))

    dfs = [m3,m6,m9,m12]
    ans_data = reduce(lambda x,y:pd.merge(x,y,on='id',how='outer'),dfs)



    ans_data['time_m3'] = ans_data['time_m3'].astype('str').str.replace('%','').replace('---',np.nan).astype('float')
    ans_data['time_m6'] = ans_data['time_m6'].astype('str').str.replace('%','').replace('---',np.nan).astype('float')
    ans_data['time_m9'] = ans_data['time_m9'].astype('str').str.replace('%','').replace('---',np.nan).astype('float')
    ans_data['time_m12'] = ans_data['time_m12'].astype('str').str.replace('%','').replace('---',np.nan).astype('float')



    ans_data['first'] = ans_data['time_m3']
    ans_data['second'] = ans_data['time_m6'] - ans_data['time_m3']
    ans_data['third'] = ans_data['time_m9'] - ans_data['time_m6']
    ans_data['fourth'] = ans_data['time_m12'] - ans_data['time_m9']



    for index,row  in ans_data[:].iterrows():
        
        fund_data = ak.fund_open_fund_info_em(fund=row['id'], indicator='累计净值走势').sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
        fund_data['净值日期'] = fund_data['净值日期'].astype('str').str.replace('-','')
        try:
            ans_data.loc[index,'最大回撤'] = max_drawback(fund_data[(fund_data['净值日期']<=base_time)&(fund_data['净值日期']>=time_m6)])
        except:
            ans_data.loc[index,'最大回撤'] = '成立日时间 大于 基准时间'

    ans_data.to_excel('基金历史节点数据-季度_{}.xlsx'.format(base_time))
    print('完成  {}'.format(base_time))



################################################################################################################################################































