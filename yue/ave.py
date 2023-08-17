# -*- coding: utf-8 -*-
"""
Created on Thu Aug 19 14:54:53 2021

@author: Administrator
"""



"AVE "

    
    
"拿出每个基金的历史 累计净值走势   修改时间：20220302  "  
def fund_data(fundid):
    
    import akshare as ak
    import pandas as pd
    import time 
    import numpy as np
    import datetime
    # "单个基金历史 累计净值走势"
    # tt = '001643'  #样例
    # fund_data = ak.fund_open_fund_info_em(fund=tt, indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    fund_data_b = ak.fund_open_fund_info_em(fund=fundid, indicator="累计净值走势").sort_values(['净值日期'],ascending=[0]).reset_index(drop=True)
    "防止float和双精度格式冲突"
    fund_data_b['累计净值'] = fund_data_b['累计净值'].astype(float)
    "净值日期 转变为 int "
    fund_data_b['净值日期'] = fund_data_b['净值日期'].map(lambda x:int(x.strftime('%Y%m%d')))
    "计算  日增长率"
    fund_data_b['前一日累计净值'] = fund_data_b['累计净值'].shift(-1)
    fund_data_b['日增长率'] = fund_data_b['累计净值']/fund_data_b['前一日累计净值'] - 1
    "拿数据从  20180101  开始"
    fund_data_b = fund_data_b[fund_data_b['净值日期']>=20180101].sort_values(by='净值日期',ascending=False).reset_index(drop=True)
    
    
    "过去60个交易日  日增长率 求和"
    fund_data_b['p60日增长率和'] = np.nan
    sum_data=list()
    fund_data_b['日增长率'] = fund_data_b['日增长率'].astype(float)
    for i in range(len(fund_data_b)-60):
        fund_data_b.loc[i,'p60日增长率和'] = sum(fund_data_b.loc[i:60+i,'日增长率'])
    
      
    "过去120个交易日  日增长率 求和"
    fund_data_b['p120日增长率和'] = np.nan
    for i in range(len(fund_data_b)-120):
        fund_data_b.loc[i,'p120日增长率和'] = sum(fund_data_b.loc[i:120+i,'日增长率'])
    
    
      
    "过去180个交易日  日增长率 求和"
    fund_data_b['p180日增长率和'] = np.nan
    for i in range(len(fund_data_b)-180):
        fund_data_b.loc[i,'p180日增长率和'] = sum(fund_data_b.loc[i:180+i,'日增长率'])
    
    
      
    "过去240个交易日  日增长率 求和"
    fund_data_b['p240日增长率和'] = np.nan
    for i in range(len(fund_data_b)-240):
        fund_data_b.loc[i,'p240日增长率和'] = sum(fund_data_b.loc[i:240+i,'日增长率'])
    
    
    
    
    "过去一年p60  日增长率求和  的平均值"
    fund_data_b['p1yp60日增长率和ave'] = 0
    fund_data_b['p1yp120日增长率和ave'] = 0
    fund_data_b['p1yp180日增长率和ave'] = 0
    fund_data_b['p1yp240日增长率和ave'] = 0
    
    fund_data_b['p1yp60日增长率和水上概率'] = 0
    fund_data_b['p1yp120日增长率和水上概率'] = 0
    fund_data_b['p1yp180日增长率和水上概率'] = 0
    fund_data_b['p1yp240日增长率和水上概率'] = 0
    
    fund_data_b['p1yp60日增长率和skewness'] = 0
    fund_data_b['p1yp120日增长率和skewness'] = 0
    fund_data_b['p1yp180日增长率和skewness'] = 0
    fund_data_b['p1yp240日增长率和skewness'] = 0   
    
    fund_data_b['p1yp60日增长率和kurtosis'] = 0
    fund_data_b['p1yp120日增长率和kurtosis'] = 0
    fund_data_b['p1yp180日增长率和kurtosis'] = 0
    fund_data_b['p1yp240日增长率和kurtosis'] = 0  
    
    
    fund_data_b['p1yp60日增长率和var'] = 0
    fund_data_b['p1yp120日增长率和var'] = 0
    fund_data_b['p1yp180日增长率和var'] = 0
    fund_data_b['p1yp240日增长率和var'] = 0    
    
    for index_1,row_i in fund_data_b[:2].iterrows():
        pass
        fund_data_b.loc[index_1,'p1yp60日增长率和ave'] = fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p60日增长率和'].mean()
        fund_data_b.loc[index_1,'p1yp120日增长率和ave'] = fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p120日增长率和'].mean()
        fund_data_b.loc[index_1,'p1yp180日增长率和ave'] = fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p180日增长率和'].mean()
        fund_data_b.loc[index_1,'p1yp240日增长率和ave'] = fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p240日增长率和'].mean()
    
            
        "总个数"
        len_1yp60= len(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])][['p60日增长率和']].dropna(axis=0,how='all'))
        len_1yp120= len(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])][['p120日增长率和']].dropna(axis=0,how='all'))
        len_1yp180= len(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])][['p180日增长率和']].dropna(axis=0,how='all'))
        len_1yp240= len(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])][['p240日增长率和']].dropna(axis=0,how='all'))
        fund_data_b.loc[index_1,'p1yp60日增长率和水上概率'] = len(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])&(fund_data_b['p60日增长率和']>=0)])/len_1yp60 if len_1yp60!=0 else '报错'
        fund_data_b.loc[index_1,'p1yp120日增长率和水上概率'] = len(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])&(fund_data_b['p120日增长率和']>=0)])/len_1yp120 if len_1yp120!=0 else '报错'
        fund_data_b.loc[index_1,'p1yp180日增长率和水上概率'] = len(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])&(fund_data_b['p180日增长率和']>=0)])/len_1yp180 if len_1yp180!=0 else '报错'
        fund_data_b.loc[index_1,'p1yp240日增长率和水上概率'] = len(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])&(fund_data_b['p240日增长率和']>=0)])/len_1yp240 if len_1yp240!=0 else '报错'
    
    
        "统计量"
        "skewness"
        fund_data_b.loc[index_1,'p1yp60日增长率和skewness'] = pd.Series(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p60日增长率和'].dropna(axis=0,how='all')).skew()
        fund_data_b.loc[index_1,'p1yp120日增长率和skewness'] = pd.Series(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p120日增长率和'].dropna(axis=0,how='all')).skew()
        fund_data_b.loc[index_1,'p1yp180日增长率和skewness'] = pd.Series(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p180日增长率和'].dropna(axis=0,how='all')).skew()
        fund_data_b.loc[index_1,'p1yp240日增长率和skewness'] = pd.Series(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p240日增长率和'].dropna(axis=0,how='all')).skew()

        "kurtosis"
        fund_data_b.loc[index_1,'p1yp60日增长率和kurtosis'] = pd.Series(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p60日增长率和'].dropna(axis=0,how='all')).kurt()
        fund_data_b.loc[index_1,'p1yp120日增长率和kurtosis'] = pd.Series(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p120日增长率和'].dropna(axis=0,how='all')).kurt()
        fund_data_b.loc[index_1,'p1yp180日增长率和kurtosis'] = pd.Series(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p180日增长率和'].dropna(axis=0,how='all')).kurt()
        fund_data_b.loc[index_1,'p1yp240日增长率和kurtosis'] = pd.Series(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p240日增长率和'].dropna(axis=0,how='all')).kurt()
    
        "方差"
        fund_data_b.loc[index_1,'p1yp60日增长率和var'] = np.var(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p60日增长率和'].dropna(axis=0,how='all'))
        fund_data_b.loc[index_1,'p1yp120日增长率和var'] = np.var(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p120日增长率和'].dropna(axis=0,how='all'))
        fund_data_b.loc[index_1,'p1yp180日增长率和var'] = np.var(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p180日增长率和'].dropna(axis=0,how='all'))
        fund_data_b.loc[index_1,'p1yp240日增长率和var'] = np.var(fund_data_b[(fund_data_b['净值日期']>row_i['净值日期']-10000)&(fund_data_b['净值日期']<=row_i['净值日期'])]['p240日增长率和'].dropna(axis=0,how='all'))
        
    
    
    
    # "计算未来D30  D90  涨跌幅"    
    # fund_data_b['f30累计净值'] = fund_data_b['累计净值'].shift(30)
    # fund_data_b['f90累计净值'] = fund_data_b['累计净值'].shift(90)
    # fund_data_b['D30'] = (fund_data_b['f30累计净值']-fund_data_b['累计净值'])/fund_data_b['累计净值']
    # fund_data_b['D90'] = (fund_data_b['f90累计净值']-fund_data_b['累计净值'])/fund_data_b['累计净值']
    
    # "只取如下时间段的数据"
    # fund_data_b = fund_data_b[(fund_data_b['净值日期']==20190630)|(fund_data_b['净值日期']==20190830)|
    #                       (fund_data_b['净值日期']==20191030)|(fund_data_b['净值日期']==20191230)|
    #                       (fund_data_b['净值日期']==20200228)|(fund_data_b['净值日期']==20200430)|
    #                       (fund_data_b['净值日期']==20200630)|(fund_data_b['净值日期']==20200831)|
    #                       (fund_data_b['净值日期']==20201030)|(fund_data_b['净值日期']==20201230)|
    #                       (fund_data_b['净值日期']==20210226)|(fund_data_b['净值日期']==20210430)|
    #                       (fund_data_b['净值日期']==20210630)]
    
    fund_data_b = fund_data_b.head(1)[['净值日期','p1yp60日增长率和ave','p1yp120日增长率和ave','p1yp180日增长率和ave','p1yp240日增长率和ave'
                                       ,'p1yp60日增长率和水上概率','p1yp120日增长率和水上概率','p1yp180日增长率和水上概率','p1yp240日增长率和水上概率'
                                       ,'p1yp60日增长率和skewness','p1yp120日增长率和skewness','p1yp180日增长率和skewness','p1yp240日增长率和skewness'
                                       ,'p1yp60日增长率和kurtosis','p1yp120日增长率和kurtosis','p1yp180日增长率和kurtosis','p1yp240日增长率和kurtosis'
                                       ,'p1yp60日增长率和var','p1yp120日增长率和var','p1yp180日增长率和var','p1yp240日增长率和var']]
    fund_data_b['id'] = fundid     
    return fund_data_b


if __name__ == '__main__':
    fund_data_b = fund_data()
    pass    
    
 