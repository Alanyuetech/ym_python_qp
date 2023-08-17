# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 14:28:44 2022

@author: Administrator
"""


"基金评价体系--基金"

def fundeva_funds(data): 
    
    import akshare as ak
    import pandas as pd
    import time 
    from matplotlib import pyplot as plt 
    import numpy as np
    import datetime
    from dateutil.relativedelta import relativedelta
    from yue.ave import fund_data
    import pymysql
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
    
    
    "含有  基金成立日期,基金经理"
    fund_df = pd.DataFrame()
    for i in ['股票型基金','混合型基金']:
        fund_scale_open_sina_df = ak.fund_scale_open_sina(symbol=i)
        fund_scale_open_sina_df['基金代码'] = fund_scale_open_sina_df['基金代码'].astype('str')
        fund_scale_open_sina_df['id'] = fund_scale_open_sina_df['基金代码']
        # fund_scale_open_sina_df['成立日期'] = fund_scale_open_sina_df['成立日期'].astype('str')
        fund_df = fund_df.append(fund_scale_open_sina_df)
        
    
        
    data_final_result = data.copy()  
    
    
    data_final_result['new'] = data_final_result['manager']+data_final_result['company']    
    data_final_result = pd.merge(data_final_result,fund_df[['id','成立日期']],on='id')
    
    data_final_result['基金规模得分'] = data_final_result['size'].map(lambda x:1 if float(x)>1 else 0)
    two_years_ago = datetime.datetime.strptime(str(int(datetime.date.today().strftime('%Y%m%d'))-20000),'%Y%m%d').date()
    data_final_result['成立年限得分'] = data_final_result['成立日期'].map(lambda x:1 if x>two_years_ago else 0)
    
    
    ave_goal_list=['D90','D180','D360','D720','标准差','夏普','最大回撤']
    for i in ave_goal_list:
        if (i!='标准差') and (i!='最大回撤'):  
            data_final_result['基金{}得分'.format(i)] =  1-data_final_result['{}'.format(i)].rank(ascending=0)/len(data_final_result)
        else:
            data_final_result['基金{}得分'.format(i)] =  data_final_result['{}'.format(i)].rank(ascending=0)/len(data_final_result)
          
    goal_list = [ 'first','second', 'third', 'fourth','fifth','sixth', 'seventh', 'eighth']
    for i in goal_list:
        data_final_result['{}得分'.format(i)] = data_final_result['{}'.format(i)].map(lambda x:1 if x>=data_final_result['{}'.format(i)].quantile(0.75) else 0)
        
    data_final_result['基金8个季度得分'] = data_final_result.iloc[:,-8:].apply(lambda x:x.sum(), axis=1)/8  
    
    
    
    "AVE"
    fund_data_hz = pd.read_excel('国内基金数据AVE_XX{}.xlsx'.format(date_work),engine='openpyxl',dtype={'id':'str'})
    data_final_result = pd.merge(data_final_result,fund_data_hz[['p1yp60日增长率和ave','p1yp120日增长率和ave','p1yp180日增长率和ave',
                                                                 'p1yp240日增长率和ave','id']],on='id',how='left')
    ave_list = ['p1yp60日增长率和ave','p1yp120日增长率和ave','p1yp180日增长率和ave','p1yp240日增长率和ave']
    for i in ave_list:
        data_final_result['{}得分'.format(i)] = data_final_result['{}'.format(i)].map(lambda x:1 if x>=data_final_result['{}'.format(i)].quantile(0.80) else 0)
    data_final_result['ave合计'] = data_final_result.iloc[:,-4:].apply(lambda x:x.sum(), axis=1)  
    data_final_result['ave得分'] = data_final_result['ave合计'].apply(lambda x:1 if x==4 else 0)  
    
    "week间隔"
    fund_week_jg = pd.read_excel('两周时间段爬取{}.xlsx'.format(date_work),engine='openpyxl',dtype={'id':'str'}).iloc[:,:-6]
    col = fund_week_jg.pop('id')
    fund_week_jg.insert(loc= 0 , column= 'id', value= col)
    fund_week_jg = fund_week_jg.rename(columns={15:'15'})
    
    fund_week_jg.iloc[:,1:] = fund_week_jg.iloc[:,1:].applymap(lambda x:float(x.strip('%')) if x!='---' else np.nan)
    week_jg_list = list(fund_week_jg.iloc[:,1:].columns.values)
    for i in week_jg_list:
        fund_week_jg['{}得分'.format(i)] = fund_week_jg['{}'.format(i)].map(lambda x:1 if x>=fund_week_jg['{}'.format(i)].quantile(0.30) else 0)
    fund_week_jg['week_间隔合计'] = fund_week_jg.iloc[:,-26:].apply(lambda x:x.sum(), axis=1)  
    fund_week_jg['week_间隔得分'] = fund_week_jg['week_间隔合计'].apply(lambda x:1 if x==26 else 0)    
    data_final_result =  pd.merge(data_final_result,fund_week_jg[['id','week_间隔得分']],on='id',how='left')
    
    
    "week累计"
    fund_week_lj = pd.read_excel('两周累计爬取_筛选{}.xlsx'.format(date_work),engine='openpyxl',dtype={'id':'str'}).iloc[:,:-6]
    col = fund_week_lj.pop('id')
    fund_week_lj.insert(loc= 0 , column= 'id', value= col)
    fund_week_lj = fund_week_lj.rename(columns={15:'15'})
    
    fund_week_lj.iloc[:,1:] = fund_week_lj.iloc[:,1:].applymap(lambda x:float(x.strip('%')) if x!='---' else np.nan)
    week_lj_list = list(fund_week_lj.iloc[:,1:].columns.values)
    for i in week_lj_list:
        fund_week_lj['{}得分'.format(i)] = fund_week_lj['{}'.format(i)].map(lambda x:1 if x>=fund_week_lj['{}'.format(i)].quantile(0.80) else 0)
    fund_week_lj['week_累积合计'] = fund_week_lj.iloc[:,-26:].apply(lambda x:x.sum(), axis=1)  
    fund_week_lj['week_累积得分'] = fund_week_lj['week_累积合计'].apply(lambda x:1 if x==26 else 0)    
    data_final_result =  pd.merge(data_final_result,fund_week_lj[['id','week_累积得分']],on='id',how='left')
    
    
    "季度调仓能力"
    
    stock_id = pd.read_excel('对比基金持仓股票分析-岳20230127--持股数前500.xlsx',engine='openpyxl',dtype={'id':'str'}).iloc[:,1:]
    stock_id = bu_zero(stock_id,'股票代码')
    stock_id['基金季度调仓能力得分'] = 1
    
    fund_hold =  pd.read_excel('当季持仓聚合前源数据-岳20230127.xlsx',engine='openpyxl',dtype={'id':'str'})
    fund_hold = bu_zero(fund_hold,'基金代码')
    fund_hold_b = fund_hold.copy()
    fund_hold = pd.merge(fund_hold,stock_id[['股票代码','基金季度调仓能力得分']],on='股票代码',how='left')
    fund_hold_quarter_adjust = fund_hold.groupby('基金代码').agg('sum').reset_index()[['基金代码','基金季度调仓能力得分']].rename(columns={'基金代码':'id'})
    fund_hold_quarter_adjust['基金季度调仓能力得分'] = fund_hold_quarter_adjust['基金季度调仓能力得分']/10
    data_final_result =  pd.merge(data_final_result,fund_hold_quarter_adjust,on='id',how='left')
    
    
    "基金重仓集中度"
    fund_hold_b_heavy_concentration = fund_hold_b.groupby('基金代码').agg('sum').reset_index()[['基金代码','占净值比例']].rename(columns={'基金代码':'id','占净值比例':'占净值比例合计'})
    "基金行业分散度"
    fund_hold_b_industry_dispersion = fund_hold_b.groupby(['基金代码','所属行业']).agg('count').reset_index().groupby(['基金代码']).agg('count').reset_index()[['基金代码','所属行业']].rename(columns={'基金代码':'id','所属行业':'所属行业数量'})
    
    
    
    
    data_final_result = pd.merge(data_final_result,fund_hold_b_heavy_concentration,on='id',how='left')
    data_final_result = pd.merge(data_final_result,fund_hold_b_industry_dispersion,on='id',how='left')
    
    data_final_result = data_final_result[['name','id','new','company','基金规模得分','成立年限得分','基金D90得分','基金D180得分','基金D360得分','基金D720得分'
                                           ,'基金标准差得分','基金夏普得分','基金最大回撤得分','基金8个季度得分','ave得分','week_间隔得分','week_累积得分','基金季度调仓能力得分','占净值比例合计','所属行业数量']]
    
  
    
    
    return data_final_result        
        
        
    
    
if __name__ == '__main__':
    fundeva_funds = fundeva_funds()
    pass    