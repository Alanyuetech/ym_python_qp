# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 10:38:02 2022

@author: Administrator
"""

"基金评价体系--管理人（基金经理）"

def fundeva_managers(data): #传入fund_change的数据

    import akshare as ak
    import pandas as pd
    import time 
    from matplotlib import pyplot as plt 
    import numpy as np
    import datetime
    from dateutil.relativedelta import relativedelta
    
    
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
    
    
    ###########################################################################
    #可以放到fundeva_managers中，是基金经理特有的
    
    "利用akshare数据源找 基金经理+基金公司+累计从业时间+现任基金资产总规模"   #akshare出来的数据可能会有缺失，后续需要改就利用爬虫在网页上拿基金经理的总规模
    data_final = ak.fund_manager().rename(columns={
        '姓名':'name','所属公司':'company','累计从业时间':'time'})[['name','company','time','现任基金资产总规模']]
    data_final['time'] = data_final['time'].apply(lambda x: '{}年又{}天'.format(x//365,x%365))
    data_final['new'] = data_final['name']+data_final['company']
    
    
    #读取fund_change数据后合并
    data_final_result = data.copy()       #在同一个console中运行基金评价体系，可以不用运行
    data_final_result['new'] = data_final_result['manager']+data_final_result['company']
    data_final_result = pd.merge(data_final_result,data_final[['new','time','现任基金资产总规模']],on='new',how='left')
    data_final_result = data_final_result.drop(data_final_result[data_final_result['time'].isna()].index)
    ###########################################################################
    data_final_result = data_final_result.rename(columns={'time':'基金经理工作年限'})
    data_final_result['基金经理工作年限得分'] = data_final_result['基金经理工作年限'].map(lambda x:1 if int(x.split('年')[0])>=10 else(0.75 if int(x.split('年')[0])>=5 else(0.5 if int(x.split('年')[0])>=3 else 0.25)) )
    data_final_result['基金经理管理规模得分'] =  data_final_result['现任基金资产总规模'].map(lambda x:1 if x>=500 else(0.75 if x>=200 else(0.5 if x>=50 else 0.25)))
    
    
    
    
    data_final_result.iloc[:,2:14] = data_final_result.iloc[:,2:14].astype('float')

    
    "基金经理平均"
    fund_manager_ave = data_final_result.groupby('new').agg('mean').reset_index()
    ave_goal_list=['D90','D180','D360','D720','标准差','夏普','最大回撤']
    for i in ave_goal_list:
        if (i!='标准差') and (i!='最大回撤'): 
            fund_manager_ave['基金经理平均{}得分'.format(i)] =  1-fund_manager_ave['{}'.format(i)].rank(ascending=0)/len(fund_manager_ave)
        else:
            fund_manager_ave['基金经理平均{}得分'.format(i)] =  fund_manager_ave['{}'.format(i)].rank(ascending=0)/len(fund_manager_ave)
        
    
    fund_manager_ave = fund_manager_ave[['new','基金经理工作年限得分','基金经理管理规模得分','基金经理平均D90得分','基金经理平均D180得分','基金经理平均D360得分','基金经理平均D720得分',
                                         '基金经理平均标准差得分','基金经理平均夏普得分','基金经理平均最大回撤得分']]
    "基金经理代表"
    fund_manager_goal = data_final_result.sort_values('D360',ascending=0).groupby('new').head(1)
    for i in ave_goal_list:
        if (i!='标准差') and (i!='最大回撤'):        
            fund_manager_goal['基金经理代表基金{}得分'.format(i)] =  1-fund_manager_goal['{}'.format(i)].rank(ascending=0)/len(fund_manager_goal)
        else:
            fund_manager_goal['基金经理代表基金{}得分'.format(i)] =  fund_manager_goal['{}'.format(i)].rank(ascending=0)/len(fund_manager_goal)
            
    goal_list = [ 'first','second', 'third', 'fourth','fifth','sixth', 'seventh', 'eighth']
    for i in goal_list:
        fund_manager_goal['{}得分'.format(i)] = fund_manager_goal['{}'.format(i)].map(lambda x:1 if x>=fund_manager_goal['{}'.format(i)].quantile(0.75) else 0)
        
    fund_manager_goal['经理8个季度得分'] = fund_manager_goal.iloc[:,-8:].apply(lambda x:x.sum(), axis=1)/8
    fund_manager_goal = fund_manager_goal[['new','基金经理代表基金D90得分','基金经理代表基金D180得分','基金经理代表基金D360得分',
                                           '基金经理代表基金D720得分','基金经理代表基金标准差得分','基金经理代表基金夏普得分',
                                           '基金经理代表基金最大回撤得分','经理8个季度得分']]

     
      
    fund_manager_df = pd.merge(fund_manager_ave,fund_manager_goal,on='new')
    
    
    
    return fund_manager_df


if __name__ == '__main__':
    fund_manager_df = fundeva_managers()
    pass    

































