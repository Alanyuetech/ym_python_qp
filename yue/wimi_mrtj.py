# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 13:13:15 2021

@author: Administrator
"""
def wimi_mrtj():     
    "WIMI  每日统计"
    
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
    
    
    df_info = pd.DataFrame(columns=('idd','ftnn_bs'))
    df_info.loc[0,'idd'] = 'WIMI'
    df_info.loc[1,'idd'] = 'MLGO'
    df_info.loc[2,'idd'] = 'HOLO'
    # df_info.loc[3,'idd'] = 'VENAR'
    
    def mrtj(idd):
        
        "取时间格式"
        time_gsh = pd.read_excel('所有时间成列-夏令时.xlsx',engine='openpyxl')
        
        
        
        "取每日的  WIMI--笔数 文件"
        ans_b = pd.read_excel('{}{}--笔数.xlsx'.format(idd,date_work),engine='openpyxl',dtype={'时间':'str'})
        
        # "调整时间格式为  21:30"
        # ans_b['时间'] = ans_b['时间'].map(lambda x:x.strftime('%H')+':'+x.strftime('%M')+':00')
        
        "按每一分钟聚合"
        ansb_min_sum = ans_b.groupby(by='时间').agg({'笔数*系数':'sum'}).reset_index()
        # ansb_min_sum = ans_b.groupby(by='时间').agg({'笔数':'sum'}).reset_index()
        "去掉01:01:00  中第一个0，方便和time_gsh进行合并"
        ansb_min_sum['时间'] = ansb_min_sum['时间'].map(lambda x:x if x[0:1]!='0' else x[1:])
        
        "左连所有的时间——每一分钟都有数据行"
        ansb_min_sum = pd.merge(left=time_gsh, right=ansb_min_sum,how='left',on='时间').rename(columns={'笔数*系数':'每分钟笔数'})
        # ansb_min_sum = pd.merge(left=time_gsh, right=ansb_min_sum,how='left',on='时间').rename(columns={'笔数':'每分钟笔数'})
        
        "每5行进行求和"
        ansb_5min_sum = ansb_min_sum.groupby(ansb_min_sum.index // 5).agg({'时间':'last', '每分钟笔数':'sum'}).rename(columns={'每分钟笔数':'每5分钟笔数'})
        
        "1分钟聚合   5分钟聚合   进行合并"
        ansb_final = pd.merge(left=ansb_min_sum,right=ansb_5min_sum,how='left',on='时间')
        # "生成文件"
        # ansb_final.to_excel('笔数{}.xlsx'.format(date_work))
        
        ################################################################################################
        
        "取每日的  WIMI--股数 文件"
        ans_g = pd.read_excel('{}{}--股数.xlsx'.format(idd,date_work),engine='openpyxl',dtype={'时间':'str'})
        
        "按每一分钟聚合"
        ansg_min_sum = ans_g.groupby(by='时间').agg({'成交':'sum'}).reset_index()
        "去掉01:01:00  中第一个0，方便和time_gsh进行合并"
        ansg_min_sum['时间'] = ansg_min_sum['时间'].map(lambda x:x if x[0:1]!='0' else x[1:])   
        
        "左连所有的时间——每一分钟都有数据行"
        ansg_min_sum = pd.merge(left=time_gsh, right=ansg_min_sum,how='left',on='时间').rename(columns={'成交':'每分钟股数'})
        
        "每5行进行求和"
        ansg_5min_sum = ansg_min_sum.groupby(ansg_min_sum.index // 5).agg({'时间':'last', '每分钟股数':'sum'}).rename(columns={'每分钟股数':'每5分钟股数'})
        
        "1分钟聚合   5分钟聚合   进行合并"
        ansg_final = pd.merge(left=ansg_min_sum,right=ansg_5min_sum,how='left',on='时间')
        
        ans = pd.merge(left=ansb_final,right=ansg_final,on='时间')
        # "生成文件" 
        # ansg_final.to_excel('股数{}.xlsx'.format(date_work))
        ################################################################################################
        
        "按每一分钟聚合"
        ansg_min_count = ans_g.groupby(by='时间').agg({'成交':'count'}).reset_index()
        "去掉01:01:00  中第一个0，方便和time_gsh进行合并"
        ansg_min_count['时间'] = ansg_min_count['时间'].map(lambda x:x if x[0:1]!='0' else x[1:])   
        
        "左连所有的时间——每一分钟都有数据行"
        ansg_min_count = pd.merge(left=time_gsh, right=ansg_min_count,how='left',on='时间').rename(columns={'成交':'每分钟笔数(通达信)'})
        
        "每5行进行求和"
        ansg_5min_count = ansg_min_count.groupby(ansg_min_count.index // 5).agg({'时间':'last', '每分钟笔数(通达信)':'sum'}).rename(columns={'每分钟笔数(通达信)':'每5分钟笔数(通达信)'})
        
        "1分钟聚合   5分钟聚合   进行合并"
        ansg2_final = pd.merge(left=ansg_min_count,right=ansg_5min_count,how='left',on='时间')



        ################################################################################################        
        
        ans = pd.merge(left=ans,right=ansg2_final,on='时间')
        ans.to_excel('{}笔数&股数{}.xlsx'.format(idd,date_work))
        print(idd)
    
        
    for index,row in df_info.iterrows():
        mrtj(row['idd'])


if __name__ == '__main__':
    wimi_mrtj()
    pass    


















