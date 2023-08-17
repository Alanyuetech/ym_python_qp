# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 15:03:15 2022

@author: Administrator
"""

"基金评价体系--基金基础数据"

def fundeva_basedata():

    
    
    import pandas as pd
    import numpy as np
    import requests
    import re
    from selenium import webdriver
    import time
    import datetime
    import pymysql
    import akshare as ak
    from dateutil.relativedelta import relativedelta
    from yue.fund_style import fund_style_ana
    
    
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
    
    delta_56=datetime.timedelta(days=60)
    delta=datetime.timedelta(days=270)
    
    now = datetime.datetime.now()
    now_use=now.strftime('%Y%m%d')
    delta_1=datetime.timedelta(days=1)
    yesterday=now-delta_1
    yesterday=yesterday.strftime('%Y%m%d')
    
    after_56=(now-delta_56).strftime('%Y%m%d')
    
    
    url='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+after_56+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    
    
    '''每日基金的基本信息'''
    def essential_infor(url):
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
        
        data_final = pd.DataFrame(columns=['单位净值','累计净值','D1','D7','D30','D90','D180','D360','D720','近3年','今年来','成立来','D60'])
        for i in range(len(bijiao)):
            data_final.iloc[:,i]=bijiao[i]
            
        data_final['id']=id_num
        data_final['days']=days
        data_final['buy']=buy
        return data_final
    
    
    def read_items(address):
        items=pd.read_excel(address,converters = {u'id':str})
        return items
    
    def order_for_id(data,num):
        for m in range(len(data)):
            data.iloc[m,num]=str(data.iloc[m,num])
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]       
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]
            if len(data.iloc[m,num])<6:
                data.iloc[m,num]=str(0)+data.iloc[m,num]
        return data
    
    # 排序及处理，筛选策略
    data_today=essential_infor(url)
    data_today.drop(['单位净值','累计净值','成立来','近3年'],axis=1,inplace=True)
    
    # con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='rank_data')
    # # sql_item = 'SELECT * FROM project.funds_for_sell_this_week;'  #size有问题
    # sql_item = 'SELECT * FROM project.info_result;'
    # item = pd.read_sql(sql_item,con)
    # con.close()
    # item.drop(['index'],axis=1,inplace=True)
    
    item = pd.read_excel('info_result.xlsx',engine='openpyxl',dtype={'id':'str'})
    item = bu_zero(item,'id')
    
    order = ['company','size','manager','name','id','kind']
    item = item[order]
    
    data_today=pd.merge(data_today,item,how='inner',on='id')
    
    "按基金名称删除某些基金"
    de_list=list()
    name_list=['全球','标普','分级','纳斯达克','币','月','年']
    
    for i in name_list:
        for x in range(len(data_today)):
            if i in data_today.loc[x,'name']:
                de_list.append(x)
                
    data_today.reset_index(inplace=True,drop=True)
    data_today.drop(de_list,inplace=True)
    data_today = data_today.reset_index(drop=True)
    data_process=data_today.copy()
    for i in range(len(data_process)):
        data_process.loc[i,'name']=re.sub(r'[a-zA-Z",:{}]', "", data_process.loc[i,'name'])  
    use=[x for x in data_process['name']]
    use_list=list()
    for name in set(use):
        if use.count(name)>1:
            use_list.append(name)
    
    dell_list=list()
    for i in use_list:
        res=data_today[data_process['name'] ==i].index
        for x in res:
            if 'C' in data_today.loc[x]['name']:
                dell_list.append(x)                                  
    
    data_today.drop(dell_list,inplace=True)                            #删除名字带C的
    
    
    
    '''按月爬取数据'''
    delta_360=datetime.timedelta(days=360)
    delta_30=datetime.timedelta(days=30)
    
    data_year_month=list()
    for x in range(25):
        data_start_time=now-x*delta_30
        data_year_month.append(data_start_time.strftime('%Y%m%d'))
    
    def essential_infor_month(url,date):
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
        data_use.columns=['{}'.format(date),'id']
        return data_use
    
    
    
    data_final_month=list()
    for x in range(len(data_year_month)):
        start_time_time=data_year_month[-x]
        end_time_time=data_year_month[0]
        url='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+start_time_time+';qed'+end_time_time+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
        data_month_info=essential_infor_month(url, start_time_time)
        data_final_month.append(data_month_info)
    
    
    
    
    data_final_result=pd.DataFrame(data_final_month[0])
    for number in range(1,len(data_final_month)):
        data_final_result=pd.merge(data_final_result,data_final_month[number],how='left',on='id')
    data_final_result.drop(data_year_month[0],axis=1,inplace=True)
    
    '''order = ['id','20200103', '20200202', '20200303', '20200402', '20200502',
           '20200601', '20200701', '20200731', '20200830', '20200929', '20201029',
           '20201128']
    data_final_result=data_final_result[order]'''
        
    data_final_result=pd.merge(data_final_result,data_today,how='inner',on='id')
    data_final_result.columns
    # data_final_result.drop((data_final_result[data_final_result['D360'] == '---']).index,inplace=True)    #会把D360没有数据的删掉
    data_final_result.index=range(len(data_final_result))
    
    #######################################################################################
    
    
    
    # for x in range(len(data_final_result)):
    #     if data_final_result.loc[x,'days']<max(data_final_result.days):
    #        data_final_result.drop(x,inplace=True)
    
    
    "修改以上的逻辑   保留最近一天的数据    修改日期：20221114"
    # data_final_result = data_final_result[data_final_result['days']==yesterday[-4:-2]+'-'+yesterday[-2:]]    
    # data_final_result = data_final_result[data_final_result['days']==date_work[-4:-2]+'-'+date_work[-2:]]
    

    
    
    #######################################################################################
    
    data_final_result.columns=['id', 'M24','M23','M22','M21','M20','M19','M18',
                               'M17','M16','M15','M14','M13','M12', 'M11', 'M10', 'M9', 'M8',
           'M7', 'M6', 'M5', 'M4', 'M3', 'M2',
           'M1', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720','近年来', 'D60',
           'days', 'buy', 'company', 'size', 'manager', 'name','kind']
    
    order_final=['id', 'M24','M23','M22','M21','M20','M19','M18',
                               'M17','M16','M15','M14','M13','M12', 'M11', 'M10', 'M9', 'M8',
           'M7', 'M6', 'M5', 'M4', 'M3', 'M2',
           'M1', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720','近年来', 'D60',
           'days', 'buy', 'company', 'size', 'manager', 'name','kind']
    data_final_result=data_final_result[order_final]
    
    for column in data_final_result.iloc[:,1:33]:
        data_final_result[column]=data_final_result[data_final_result[column]!='---'] [column].str.strip('%').astype(float)
    
    data_final_result.reset_index(inplace=True,drop=True)    
    unsuitable=['QDII','QDII-指数','债券型-长债','债券型-混合债','债券型-可转债','债券型-中短债','联接基金','股票指数','FOF']
    delel_list=list()
    for x in range(len(data_final_result)):
        if data_final_result.loc[x,'kind'] in unsuitable:
            delel_list.append(x)
    data_final_result.drop(delel_list,inplace=True)
    
    
    season = data_final_result.iloc[:,1:24]
    
    season_final=pd.DataFrame()
    season_final['first']=season.loc[:,'M3']
    season_final['second']=season.loc[:,'M6']-season.loc[:,'M3']
    season_final['third']=season.loc[:,'M9']-season.loc[:,'M6']
    season_final['fourth']=season.loc[:,'M12']-season.loc[:,'M9']
    season_final['fifth']=season.loc[:,'M15']-season.loc[:,'M12']
    season_final['sixth']=season.loc[:,'M18']-season.loc[:,'M15']
    season_final['seventh']=season.loc[:,'M21']-season.loc[:,'M18']
    season_final['eighth']=season.loc[:,'M24']-season.loc[:,'M21']
    
    season_final['id']=data_final_result['id']
         
    data_final_result=pd.merge(data_final_result,season_final,how='left',on='id')
    data_final_result.columns
    order_season=['name', 'id', 'D90', 'D180', 'D360', 'D720',
           'first','second', 'third', 'fourth','fifth','sixth', 'seventh', 'eighth', 'days', 'buy', 'company', 'size', 'manager', 'kind']
    
    data_final_result=data_final_result[order_season]
    # data_final_result=data_final_result.fillna('---')
    
    # data_final_result.iloc[:,1:14] = data_final_result.iloc[:,1:14].astype('str')
    
    "标准差，夏普"
    
    # sql = 'SELECT * FROM project.sharp_and_standard;'
    # con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='rank_data')
    # df_sharp = pd.read_sql(sql, con)
    
    df_sharp = pd.read_excel('sharp_and_standard.xlsx',engine='openpyxl',dtype={'id':'str'})
    
    "最大回撤--多个时间"
    # con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='project')
    # sql_drowback = 'SELECT * FROM project.drowback_ranking;'
    # drowback = pd.read_sql(sql_drowback, con)
    
    drowback = pd.read_excel('drowback_ranking.xlsx',engine='openpyxl',dtype={'id':'str'})
    
    data_final_result = pd.merge(data_final_result,df_sharp[['id','标准差','夏普']],on='id',how='left')
    data_final_result = pd.merge(data_final_result,drowback[['id','最大回撤']],on='id',how='left')
    
    data_final_result['标准差']=data_final_result[data_final_result['标准差']!='--']['标准差'].str.strip('%').astype(float)
    data_final_result['夏普']=data_final_result[data_final_result['夏普']!='--']['夏普'].str.strip('%').astype(float)
    
   
    return data_final_result
    
    
        
    
    
if __name__ == '__main__':
    fundeva_basedata = fundeva_basedata()
    pass        
    
    
    
    
    
    
    
    
    