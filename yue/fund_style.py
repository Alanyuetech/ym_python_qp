# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 13:11:32 2022

@author: Administrator
"""


def fund_style_ana(fund_id):
    "基金三分类——成长，平衡，防御"
    
    
    import akshare as ak 
    import pandas as pd
    import numpy as np
    import requests
    import time
    import execjs
    import time 
    import re
    import pymysql
    import datetime
    from dateutil.relativedelta import relativedelta
    from collections import Counter
    
    def bu_zero(fund_id,id_id):
        "基金代码前面补0"
        "fund_id：df名称  id_id:需要修改的列"
        fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:str(x).zfill(6))
        return fund_id
    
    
    # fund_id = pd.read_excel('20220824du.xlsx',engine='openpyxl',dtype={'id':'str'})[['id']]
    fund_id = bu_zero(fund_id,'id')
    
    
    now_day = datetime.datetime.now().strftime('%Y%m%d')
    
    def getLastWeekDay(day=datetime.datetime.now()):
        now=day
        if now.isoweekday()==1:
          dayStep=3
        else:
          dayStep=1
        lastWorkDay = now - datetime.timedelta(days=dayStep)
        return lastWorkDay
    date_work=getLastWeekDay().strftime('%Y%m%d')
    
    now = datetime.datetime.now()
    
    one_wek_l = (now - relativedelta(weeks=+1)).strftime('%Y%m%d')
    one_mon_l = (now - relativedelta(months=+1)).strftime('%Y%m%d')
    two_mon_l = (now - relativedelta(months=+2)).strftime('%Y%m%d')
    thr_mon_l = (now - relativedelta(months=+3)).strftime('%Y%m%d')
    six_mon_l = (now - relativedelta(months=+6)).strftime('%Y%m%d')
    egt_mon_l = (now - relativedelta(months=+8)).strftime('%Y%m%d')
    ten_mon_l = (now - relativedelta(months=+10)).strftime('%Y%m%d')
    one_year_l = (now - relativedelta(years=+1)).strftime('%Y%m%d')
    
    
    time_list = pd.DataFrame([['one_wek_l','one_mon_l','two_mon_l','thr_mon_l','six_mon_l','egt_mon_l','ten_mon_l','one_year_l']
                 ,[one_wek_l,one_mon_l,two_mon_l,thr_mon_l,six_mon_l,egt_mon_l,ten_mon_l,one_year_l]]).T.rename(columns={0:'时间跨度',1:'时间'})
    
     
    sz_index = ak.index_zh_a_hist(symbol="000001", period="daily", start_date='20210701', end_date=date_work).rename(columns={'收盘':'上证'})[['日期','上证']]
    cyb_index = ak.index_zh_a_hist(symbol="399006", period="daily", start_date='20210701', end_date=date_work).rename(columns={'收盘':'创业板'})[['日期','创业板']]
    sz_index['日期'] = sz_index['日期'].str.replace('-','').astype('int')
    cyb_index['日期'] = cyb_index['日期'].str.replace('-','').astype('int')   
    
    stock_index = pd.merge(sz_index,cyb_index,on='日期')
    stock_index['上证chp'] = 100*(stock_index.iloc[-1,1]/ stock_index['上证'] - 1)
    stock_index['创业板chp'] = 100*(stock_index.iloc[-1,2]/ stock_index['创业板'] - 1)
    
    
    stock_index_ana = pd.DataFrame(columns=('时间跨度','上证chp','创业板chp','创-上','时间区间'))
    for index,row in time_list.iterrows():
        stock_index_ana.loc[index,'时间跨度'] = row['时间跨度']
        stock_index_ana.loc[index,'上证chp'] = stock_index.iloc[-(len(stock_index[stock_index['日期']>=int(row['时间'])])+1),3]  
        stock_index_ana.loc[index,'创业板chp'] = stock_index.iloc[-(len(stock_index[stock_index['日期']>=int(row['时间'])])+1),4]
        stock_index_ana.loc[index,'创-上'] = stock_index_ana.loc[index,'创业板chp']-stock_index_ana.loc[index,'上证chp']
        stock_index_ana.loc[index,'时间区间'] = '{}~{}'.format( row['时间'],date_work)
        print(index,row['时间跨度'])
        
    
    stock_index_ana['|创-上|'] = stock_index_ana['创-上'].abs()
    
    stock_index_f = stock_index_ana.sort_values('|创-上|',ascending=0).head(4).reset_index(drop=True)
    
    
    for index,row in fund_id[:].iterrows():
        # print(index,row['id'])
    
        fund_data_b = ak.fund_open_fund_info_em(fund=row['id'], indicator="累计净值走势")
        "防止float和双精度格式冲突"
        fund_data_b['累计净值'] = fund_data_b['累计净值'].astype(float)
        "净值日期 转变为 int "
        fund_data_b['净值日期'] = fund_data_b['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
        
        if fund_data_b.loc[0,'净值日期']<int(one_year_l):
        
            fund_data_b['累计净值chp'] = 100*(fund_data_b.iloc[-1,1]/ fund_data_b['累计净值'] - 1)
            for index_1,row_1 in stock_index_f.iterrows():
                # print(index_1,row_1['时间跨度'])
                
                fund_id.loc[index,'{}'.format(row_1['时间跨度'])] = fund_data_b.iloc[-(len(fund_data_b[fund_data_b['净值日期']>=int(time_list[time_list['时间跨度']==row_1['时间跨度']].iloc[0,1])])+1),2]
                if (fund_id.loc[index,'{}'.format(row_1['时间跨度'])]-row_1['上证chp'])*(fund_id.loc[index,'{}'.format(row_1['时间跨度'])]-row_1['创业板chp'])>0:           
                    if abs((fund_id.loc[index,'{}'.format(row_1['时间跨度'])]-row_1['上证chp']))<abs((fund_id.loc[index,'{}'.format(row_1['时间跨度'])]-row_1['创业板chp'])):
                        fund_id.loc[index,'{}标签'.format(row_1['时间跨度'])] = '防御'
                    else:
                        fund_id.loc[index,'{}标签'.format(row_1['时间跨度'])] = '成长'
                elif (fund_id.loc[index,'{}'.format(row_1['时间跨度'])]-row_1['上证chp'])*(fund_id.loc[index,'{}'.format(row_1['时间跨度'])]-row_1['创业板chp'])<0:
                    thr_p = row_1['|创-上|']/5
                    if abs(fund_id.loc[index,'{}'.format(row_1['时间跨度'])]-row_1['上证chp'])<=thr_p:
                        fund_id.loc[index,'{}标签'.format(row_1['时间跨度'])] = '防御'
                    elif abs(fund_id.loc[index,'{}'.format(row_1['时间跨度'])]-row_1['创业板chp'])<=thr_p:
                        fund_id.loc[index,'{}标签'.format(row_1['时间跨度'])] = '成长'
                    else:
                        fund_id.loc[index,'{}标签'.format(row_1['时间跨度'])] = '平衡'
                else:
                    pass
                
                print(index_1,row_1['时间跨度'])
            
        else:
            pass
        
        print(index,row['id'])
    
    fund_id_bscount = fund_id.iloc[:,[0,2,4,6,8]].copy()
    fund_id_bscount['list'] = fund_id_bscount.iloc[:,1:].apply(lambda x:x.tolist(),axis=1)
    fund_id_bscount['成长'] = fund_id_bscount['list'].apply(lambda x:x.count('成长'))
    fund_id_bscount['防御'] = fund_id_bscount['list'].apply(lambda x:x.count('防御'))
    fund_id_bscount['平衡'] = fund_id_bscount['list'].apply(lambda x:x.count('平衡'))
    
    fund_id_bscount['风格分类'] = np.nan
    fund_id_bscount['风格分类'] = fund_id_bscount.iloc[:,-4:-1].apply(lambda x: str(pd.DataFrame(x)[pd.DataFrame(x).iloc[:,0]>2].index.tolist()
                                                                                ).replace('[','').replace(']','').replace("'",''),axis=1)
    
    
    fund_id_bscount['风格分类'] = fund_id_bscount.iloc[:,-4:].apply(lambda x:'平衡' if ((x['成长']*x['防御']*x['平衡'])==2)|((x['成长']==2)&(x['防御']==2)) else('成长' if (x['成长']==2)&(x['平衡']==2) else ('防御' if (x['防御']==2)&(x['平衡']==2) else x['风格分类']  ) ),axis=1)
    
    
    return fund_id_bscount






if __name__ == '__main__':
    aaaa = fund_style_ana()
    pass    







