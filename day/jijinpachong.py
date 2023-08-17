# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 19:57:01 2020

@author: 86178
"""

'''
def get_one_page(url):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}  
    data=[]
    chrome_options=webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    browser=webdriver.Chrome(options=chrome_options)
    browser.get(url)
    data.append(browser.page_source)    
    return data


def main(offset):
    url='http://fund.eastmoney.com/daogou/#dt0;ft;rs;sd;ed;pr;cp;rt;tp;rk;se;nx;scminsg;stdesc;pi'+str(offset)+';pn20;zfdiy;shtable'
    data=get_one_page(url)
    return data

datas=[]
for i in range(324):
    datas.append(main(i+1))
all_data=" ".join('%s' %a for a in datas)

p_info='<div class="fund-r fr"><div class="title"><a href=.*? class="fname fl">(.*?)</a><span class="fr">.*?<div class="content"><ul class="ul-info"><li>基金类型：(.*?)</li><li>.*?规
&nbsp;&nbsp;&nbsp;&nbsp;模</a>：(.*?)亿元.*?</li><li>基金经理：<a href="(.*?)">(.*?)</a></li><li>'
info=re.compile(p_info,re.S)
info_num=re.findall(info,all_data)  
items=pd.DataFrame(info_num)
items.columns=['name','kind','size']

for i in range(len(items)):
    if len(items.loc[i]['size'])>10:
        items.loc[i]['size']=0 

name=[]
for x in items['name']:
    name.append(x[-7:-1])
items['id']=name
items['id']=items['id'].astype('str')

items.to_csv('规模.csv',index=0)
'''
def jijinpachong():
        
    import pandas as pd
    import numpy as np 
    import requests
    import re
    from selenium import webdriver
    import time
    import datetime
    import pymysql
    
    delta=datetime.timedelta(days=270)
    delta_56=datetime.timedelta(days=60)
    
    now = datetime.datetime.now()
    
    now_use=now.strftime('%Y%m%d')
    delta_1=datetime.timedelta(days=1)
    yesterday=now-delta_1
    yesterday=yesterday.strftime('%Y%m%d')
    
    def getLastWeekDay(day=datetime.datetime.now()):
        now=day
        if now.isoweekday()==1:
          dayStep=3
        else:
          dayStep=1
        lastWorkDay = now - datetime.timedelta(days=dayStep)
        
        
        return lastWorkDay
    
    date_work=getLastWeekDay().strftime('%Y%m%d')
    
    after_use = (now-delta).strftime('%Y%m%d')
    after_56=(now-delta_56).strftime('%Y%m%d')
    
    url='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_56+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    url_270='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn20000;ddesc;qsd'+after_use+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
    
    
    def essential_infor(url):
        option = webdriver.ChromeOptions()    
        option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
        browser=webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe',chrome_options=option)        # 全屏
        browser.get(url)
        time.sleep(8)
        # element = browser.find_element_by_css_selector('#allfund')   #不报错，就是跑不出来，所以注释掉
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
        
        data_final = pd.DataFrame(columns=['单位净值','累计净值','日增长率','近1周','近1月','近3月','近6月','近1年'	,'近2年'	,'近3年'	,'今年来','成立来','自定义'])
        for i in range(len(bijiao)):
            data_final.iloc[:,i]=bijiao[i]
            
        data_final['id']=id_num
        data_final['days']=days
        data_final['buy']=buy
        return data_final
    
    def read_items(address):
        items=pd.read_csv(address,converters = {u'id':str})
        return items
    
    data_today=essential_infor(url)
    data_D270=essential_infor(url_270)
    
    # con = pymysql.connect(host='192.168.10.219',user='root',password='123456',database='all_info_data')
    # cursor = con.cursor()
    # missing=list()
    # already = list()
    
    data_today_insert = data_today.copy()
    
    # def insert_info(data_today):
    #     i=1
    #     for id_num in range(len(data_today)):
    #         try:
    #             sql = 'INSERT INTO`all_info_data`.`{}` (days,ACC_price,Net_price,p_change) values ({},{},{},{});'.format(data_today.iloc[id_num,13],now_use,data_today.iloc[id_num,1],data_today.iloc[id_num,0],data_today.iloc[id_num,0])
    #             cursor.execute(sql)
    #             con.commit()
    #             already.append(data_today.iloc[id_num,13])
    #             print(data_today.iloc[id_num,13])
    #         except:
    #             missing.append(data_today.iloc[id_num,13])
    #         print(i)
    #         i+=1
            
    #     con.close()
    # insert_info(data_today_insert)
        
        
    
    data_D270.drop([ '单位净值', '累计净值','日增长率', '近1周', '近1月', '近3月', '近6月', '近1年', '近2年', '近3年',
          '今年来', '成立来', 'days','buy'],axis=1,inplace=True)      #报错了，注释掉
    data_D270.columns=['D270','id']
    data_final=pd.merge(data_today,data_D270,how='left',on='id')
    data_final.drop(['成立来','今年来','近3年'],axis=1,inplace=True)
    # items=read_items('info_result.csv')
    items=pd.read_excel('info_20230128.xlsx',engine='openpyxl',dtype={'id':'str'})  #不支持xlsx文件，加engine='openpyxl' #info_result是上上个季度的
    items['id'] = items['id'].map(lambda x:'00000'+x if len(x)==1 else
                                      ('0000'+x if len(x)==2 else 
                                        ('000'+x if len(x)==3 else
                                        ('00'+x if len(x)==4 else
                                          ('0'+x if len(x)==5 else x)))))
    # items.drop(['beizhu'],axis=1,inplace=True)
    
    data_final_today=pd.merge(data_final,items,how='left',on='id')
    
    
    percent_list=['日增长率','近1周','近1月','近3月','近6月','近1年','近2年','自定义','D270']
    def data_process_percent(data_final,nature_list):
        for x in data_final:
            for i in range(len(data_final)):
                if data_final.loc[i,x] =='---':
                    data_final.loc[i,x]=0
                   
        for x in nature_list:
            data_final[x] = data_final[x].str.strip('%').astype(float)/100
            
        data_final=data_final.fillna(0)
        data_final.index=range(len(data_final))
        return data_final
    
    data_final_today=data_process_percent(data_final_today,percent_list)
    
    def data_process_fifth(name_use):
        #name_use.drop(useless_columns,axis=1,inplace=True)
        order=['单位净值', '累计净值','id','name','company','manager','kind','日增长率', '近1周', '近1月', '自定义','近3月', '近6月', 'D270','近1年','近2年', 'days' ,'buy','size']
        name_use=name_use[order]
        name_use.columns=['Net_value','Acc_value','id','name','company','manager','kind','D1','D7','D30','D60','D90','D180','D270','D360','D720','days','buy','size']
        return name_use
    
    data_final_today=data_process_fifth(data_final_today)
    
    
    rename=list()
    for x in data_final_today['buy']:
        if len(x) ==3:
            rename.append('Y')
        else:
            rename.append('N')
    data_final_today['buy']=rename
    data_final_today.drop(['manager','company'],axis=1,inplace=True)
    
    data_final_today.drop(data_final_today[data_final_today['days']==0].index,inplace=True)
    
    data_final_today['Q1'] = data_final_today['D90']
    data_final_today['Q2'] = data_final_today['D180']-data_final_today['D90']
    data_final_today['Q3'] = data_final_today['D270']-data_final_today['D180']
    data_final_today['Q4'] = data_final_today['D360']-data_final_today['D270']
    
    # con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='project')
    # ss_sql = 'SELECT * FROM project.sharp_and_standard;'
    # ss = pd.read_sql(ss_sql,con)
    
    # db_sql = 'SELECT * FROM project.drowback_ranking;'
    # db = pd.read_sql(db_sql, con)


    ss = pd.read_excel('sharp_and_standard.xlsx',engine='openpyxl',dtype={'id':'str'}) 
    db = pd.read_excel('drowback_ranking.xlsx',engine='openpyxl',dtype={'id':'str'})     
        
    
    # ss.drop(['index'],axis=1,inplace=True)
    # db.drop(['index'],axis=1,inplace=True)
    
    
    data_final_today = pd.merge(data_final_today,ss,how='left',on='id')
    data_final_today = pd.merge(data_final_today,db,how='left',on='id')
    
    
    
    # time=max(data_final_today.days)
    # time = datetime.datetime.strptime(time, "%Y-%m-%d").date()
    # time= time.strftime('%Y%m%d')
    
    
    
    # data_final_today.to_sql('{}'.format(date_work),con='mysql+pymysql://root:123456@192.168.10.222/rank_data?charset=utf8',if_exists='replace')
    data_final_today.to_excel('{}_mysql.xlsx'.format(date_work),index=False)
    
    
    
    
    '''以上操作截至到将数据存入数据库中'''
    data_final_today.drop((data_final_today[data_final_today['size']=='--']).index,inplace=True)
    data_final_today.index=range(len(data_final_today))
    def data_size(data_final,num): 
        data_final['size']=data_final['size'].astype('float')
        for i in range(len(data_final)):      
                if data_final.loc[i,'size']<float(num):
                    data_final=data_final.drop(i,axis=0)
        data_final.index=range(len(data_final))
        return data_final
    
    data_final_today=data_size(data_final_today,0.5)
    
    unsuitable=[np.nan,'债券指数', 'QDII', '定开债券', '债券型', 'QDII-指数']
    data_final_today.index=range(len(data_final_today))
    dele_list=list()
    def data_process_second(data_final,unsuitable):
        for x in range(len(data_final)):
            if data_final.loc[x,'kind'] in unsuitable:
                dele_list.append(x)
        data_final=data_final.drop(dele_list,axis=0)
        return data_final
    data_final_today=data_process_second(data_final_today,unsuitable)
    
    data_final_today.drop((data_final_today[data_final_today['name']==0]).index,inplace=True)
    
    black_list=['养老','QDII','月','年','分级','债','标普','纳斯达克','全球','币','C']
    def data_process_third(data_final,black_list):
        for x in black_list:
            data_final=data_final.drop(data_final[(data_final['name'].str.contains(x))].index)
        return data_final
    data_final_today=data_process_third(data_final_today,black_list)
    
        
    def data_process_fourth(data_final):
        index_id=list()
        for x in data_final['name']:
            x=re.sub(r'[a-zA-Z",:{}]', "", x)
            x=re.sub(r'[0-9]',"",x)
            x=x.strip(r'（）')
            x=x.strip('/')
            index_id.append(x)
        data_final['name']=index_id
        name_use=pd.DataFrame(columns=data_final.columns)
        for name_fact in range(len(data_final)):
            if data_final.iloc[name_fact,1] not in name_use.name.values:
                name_use=name_use.append(data_final.iloc[name_fact,:],ignore_index=True)
            
            elif name_use[name_use['name'].str.contains(data_final.iloc[name_fact,1])].size<float(data_final.iloc[name_fact,14]):        
                    name_use.drop(name_use[name_use['name'].str.contains(data_final.iloc[name_fact,1])].index,inplace=True)
                    name_use=name_use.append(data_final.iloc[name_fact,:],ignore_index=True)
            else:
                pass
        return name_use
    
    data_final_today=data_process_fourth(data_final_today)
    
    dele_list=list()
    for i in range(len(data_final_today)):
        if data_final_today.iloc[i,13]=='N':
            dele_list.append(i)
    data_final_today.index=range(len(data_final_today))
    data_final_today.drop(dele_list,inplace=True)
    
    data_final_today.drop((data_final_today[data_final_today['days']==0]).index,inplace=True)
    
    data_final_today.index=range(len(data_final_today))
    
    
    
    
     ##################################################################################   
    
    "修改---留存date_work日期下的数据   20230104"
    # for x in range(len(data_final_today)):
    #     if data_final_today.loc[x,'days']<max(data_final_today.days):
    #         data_final_today.drop(x,inplace=True)
    
    
            
    data_final_today = data_final_today[data_final_today['days']==date_work[4:6]+'-'+date_work[6:]]
        
    ##################################################################################               
            
    
    name_use=['D1','D7','D30','D60','D90','D180','D270','D360','D720']
    '''输出excel文件'''
    def process_data(data,nature):
         data=data.sort_values([nature], ascending = False)
         data[:50].to_excel('{}.xlsx'.format(nature))
        
    
    # data_final_today=data_final_today.sort_values(['D180'],ascending=False)
    # data_final_today[:100].to_excel('D180_100.xlsx')
    
    for i in name_use:
        process_data(data_final_today, i)
         
    import datetime
    
    data_final=pd.merge(data_final,items,how='left',on='id')
    data_final.to_excel('{}.xlsx'.format(date_work),index=False)

if __name__ == '__main__':
    jijinpachong()
    pass