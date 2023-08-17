# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 11:20:14 2020

@author: 86178
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
from dateutil.relativedelta import relativedelta
from yue.fund_style import fund_style_ana

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
after_270 = (now-delta).strftime('%Y%m%d')
after_450 = (now-datetime.timedelta(days=450)).strftime('%Y%m%d')
after_540 = (now-datetime.timedelta(days=540)).strftime('%Y%m%d')
after_630 = (now-datetime.timedelta(days=630)).strftime('%Y%m%d')
after_3y = (datetime.datetime.strptime(now_use,'%Y%m%d')-relativedelta(years=+3)).strftime('%Y%m%d')
after_5y = (datetime.datetime.strptime(now_use,'%Y%m%d')-relativedelta(years=+5)).strftime('%Y%m%d')


url='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+after_56+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
url_270='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+after_270+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
url_450='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+after_450+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
url_540='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+after_540+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
url_630='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+after_630+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
url_3y='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+after_3y+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'
url_5y='http://fund.eastmoney.com/data/fundranking.html#tall;c0;r;szzf;pn50000;ddesc;qsd'+after_5y+';qed'+now_use+';qdii;zq;gg;gzbd;gzfs;bbzt;sfbb'


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
data_today.drop(['单位净值','累计净值','成立来','今年来','近3年'],axis=1,inplace=True)


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

data_today=pd.merge(data_today,item,how='left',on='id')


"原始270"

data_270 = essential_infor(url_270)
data_270.drop(['单位净值', '累计净值', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720', '近3年',
       '今年来', '成立来', 'days', 'buy'],inplace=True,axis=1)
data_270.columns = ['D270','id']

for nums in range(len(data_270)):
    data_270.iloc[nums,0] =data_270.iloc[nums,0].strip('%')
    

###################################################################
"添加 450 540  630 等时间段    修改时间：20211229"

for i in range(450,720,90):
    locals()['data_'+str(i)] = essential_infor(locals()['url_'+str(i)])
    locals()['data_'+str(i)].drop(['单位净值', '累计净值', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720', '近3年',
           '今年来', '成立来', 'days', 'buy'],inplace=True,axis=1)
    locals()['data_'+str(i)].columns = ['D{}'.format(i),'id']

    for nums in range(len(locals()['data_'+str(i)])):
        locals()['data_'+str(i)].iloc[nums,0] =locals()['data_'+str(i)].iloc[nums,0].strip('%')





"添加 3y 5y 时间段     修改时间：20220802"
for i in ['3y','5y']:
    locals()['data_'+str(i)] = essential_infor(locals()['url_'+str(i)])
    locals()['data_'+str(i)].drop(['单位净值', '累计净值', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720', '近3年',
           '今年来', '成立来', 'days', 'buy'],inplace=True,axis=1)
    locals()['data_'+str(i)].columns = ['{}'.format(i),'id']

    for nums in range(len(locals()['data_'+str(i)])):
        locals()['data_'+str(i)].iloc[nums,0] =locals()['data_'+str(i)].iloc[nums,0].strip('%')

        

##################################################################

dela_list=list()
for x in range(len(data_today)):
    if data_today.iloc[x,12]=='---' or data_today.iloc[x,12]=='--' or float(data_today.iloc[x,12])<=0.5 or len(data_today.iloc[x,10])>5 or type(data_today.iloc[x,14])==float:
        dela_list.append(x)                                    
        
data_today.drop(dela_list,inplace=True)                               #限制size

de_list=list()
name_list=['全球','标普','分级','纳斯达克','币','月','年']

for i in name_list:
    for x in range(len(data_today)):
        if i in data_today.iloc[x,14]:
            de_list.append(x)
            
data_today.reset_index(inplace=True,drop=True)
data_today.drop(de_list,inplace=True)




data_process=data_today.copy()
for i in range(len(data_process)):
    data_process.iloc[i,14]=re.sub(r'[a-zA-Z",:{}]', "", data_process.iloc[i,14])
    
    
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
               




tak=list()
res=data_today[data_today['D360']!='---'] ['D360'].str.strip('%').astype(float)/100      #res 中只有D360有数据的，没有数据的没统计
res=pd.DataFrame(res)

# for x in res.index:
#     if res.loc[x,'D360']<0.3:
#         tak.append(x)

data_today.drop(tak,inplace=True)
# con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='rank_data')
# sql_info = 'SELECT * FROM project.funds_for_sell_this_week;'
# data_kind = pd.read_sql(sql_info,con)
# data_kind.drop(['name', 'company', 'size', 'manager'],axis=1,inplace=True)      #funds_for_sell_this_week 中的数据比较落后 其中的数据内容 info_result 的数据一样

'''按月爬取数据'''
delta_360=datetime.timedelta(days=360)
delta_30=datetime.timedelta(days=30)

data_year_month=list()
for x in range(13):
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


"修改以上的逻辑   保留最近一天的数据    修改日期：20220106"

data_final_result = data_final_result[data_final_result['days']==yesterday[-4:-2]+'-'+yesterday[-2:]]




#######################################################################################

data_final_result.columns=['id', 'M12', 'M11', 'M10', 'M9', 'M8',
       'M7', 'M6', 'M5', 'M4', 'M3', 'M2',
       'M1', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720', 'D60',
       'days', 'buy', 'company', 'size', 'manager', 'name','kind']

order_final=['name','id', 'M12', 'M11', 'M10', 'M9', 'M8',
       'M7', 'M6', 'M5', 'M4', 'M3', 'M2',
       'M1', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720', 'D60',
       'days', 'buy', 'company', 'size', 'manager','kind']
data_final_result=data_final_result[order_final]

for column in data_final_result.iloc[:,2:22]:
    data_final_result[column]=data_final_result[data_final_result[column]!='---'] [column].str.strip('%').astype(float)

data_final_result.reset_index(inplace=True,drop=True)    
unsuitable=['QDII','QDII-指数','债务型','联接基金','股票指数']
delel_list=list()
for x in range(len(data_final_result)):
    if data_final_result.loc[x,'kind'] in unsuitable:
        delel_list.append(x)
data_final_result.drop(delel_list,inplace=True)
season = data_final_result.iloc[:,2:14]

season_final=pd.DataFrame()
season_final['first']=season.iloc[:,9]
season_final['second']=season.iloc[:,6]-season.iloc[:,9]
season_final['third']=season.iloc[:,3]-season.iloc[:,6]
season_final['fourth']=season.iloc[:,0]-season.iloc[:,3]
season_final['id']=data_final_result['id']


    
        
data_final_result=pd.merge(data_final_result,season_final,how='left',on='id')
data_final_result.columns
order_season=['name', 'id', 'M12', 'M11', 'M10', 'M9', 'M8', 'M7', 'M6', 'M5', 'M4',
       'M3', 'M2', 'M1', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720',
       'D60','first','second', 'third', 'fourth', 'days', 'buy', 'company', 'size', 'manager', 'kind']

data_final_result=data_final_result[order_season]
data_final_result=data_final_result.fillna('---')
data_final_result = pd.merge(data_final_result,data_270,on='id',how='left')


###################################################
"与 data_final_result 合并      修改时间：20211229"
for i in range(450,720,90):
     data_final_result = pd.merge(data_final_result,locals()['data_'+str(i)],on='id',how='left')
     
for i in ['3y','5y']:
     data_final_result = pd.merge(data_final_result,locals()['data_'+str(i)],on='id',how='left')   
     
# data_final_result = pd.merge(data_final_result,data_450,on='id',how='left')
# data_final_result = pd.merge(data_final_result,data_540,on='id',how='left')
# data_final_result = pd.merge(data_final_result,data_630,on='id',how='left')


##################################################

#最近一个工作日
def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay

for i in range(len(data_final_result)):
    for x in range(2,26):
        data_final_result.iloc[i,x] = str(data_final_result.iloc[i,x]) +'%'
    
for i in range(len(data_final_result)):
    for x in range(32,data_final_result.shape[1]):
        data_final_result.iloc[i,x] = str(data_final_result.iloc[i,x]) +'%'

    
# data_final_result['D270'] = data_final_result['D270'] + '%'
###################################################
# "添加  %      修改时间：20211229"
# for i in range(450,720,90):
#      data_final_result['D{}'.format(i)] = data_final_result['D{}'.format(i)] + '%'

# for i in ['3y','5y']:
#      data_final_result['{}'.format(i)] = data_final_result['{}'.format(i)] + '%'
# data_final_result['D450'] = data_final_result['D450'] + '%'
# data_final_result['D540'] = data_final_result['D540'] + '%'
# data_final_result['D630'] = data_final_result['D630'] + '%'

###################################################
date_work=getLastWeekDay().strftime('%Y%m%d')
# data_final_result.to_sql(date_work,con='mysql+pymysql://baseroot:123456@192.168.10.166/filtering_data?charset=utf8',if_exists='replace',index=False)
# classify = pd.read_csv('industry_classify.csv')


# con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='rank_data')
# sql_classify = 'SELECT * FROM project.data_classify;'
# classify = pd.read_sql(sql_classify,con)
# con.close()


classify = pd.read_excel('data_classify.xlsx',engine='openpyxl',dtype={'id':'str'})

# for m in range(len(classify)):
#     classify.iloc[m,4]=str(classify.iloc[m,4])
#     if len(classify.iloc[m,4])<6:
#         classify.iloc[m,4]=str(0)+classify.iloc[m,4]
#     if len(classify.iloc[m,4])<6:
#         classify.iloc[m,4]=str(0)+classify.iloc[m,4]
#     if len(classify.iloc[m,4])<6:
#        classify.iloc[m,4]=str(0)+classify.iloc[m,4]
#     if len(classify.iloc[m,4])<6:
#         classify.iloc[m,4]=str(0)+classify.iloc[m,4]
#     if len(classify.iloc[m,4])<6:
#        classify.iloc[m,4]=str(0)+classify.iloc[m,4]

classify.drop(['name', 'company', 'size', 'manager',
       'kind'],axis=1,inplace=True)
# classify.drop(['index'],axis=1,inplace=True)
#获取分类
data_final_result_classify = pd.merge(data_final_result,classify,how='left',on='id')

#基金经理信息
data_comeout=list()
for x in range(53):
    url = 'http://fund.eastmoney.com/manager/default.html#dt14;mcreturnjson;ftall;pn50;pi{};scabbname;stasc'.format(x+1)
    option = webdriver.ChromeOptions()    
    option.add_argument('--headless')# 隐藏滚动条, 应对一些特殊页面
    browser=webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver.exe',chrome_options=option) # 全屏
 
    browser.get(url)
    data = browser.page_source
    data_comeout.append(data)
    browser.quit()

######   下方 data_final  可能爬不到所有的数据，导致和 data_final_301 拼接时出现缺失

# all_data = " ".join('%s' %a for a in data_comeout)
# all_data = all_data.replace(' ',"").replace('\n',"").replace('\t',"")

# p_info = '<ahref="//fund.eastmoney.com/manager/.*?.html"title=".*?">(.*?)</a>'
# one = re.findall(p_info, all_data)

# p_com = '<td><ahref="//fund.eastmoney.com/company/.*?.html">(.*?)</a></td>'
# two = re.findall(p_com, all_data)

# p_year = '<tdclass="hypzxqxrjjtdl">.*?</a></td><td>(.*?)</td>'
# three = re.findall(p_year, all_data)

# data_final = pd.DataFrame()
# data_final['name']=one
# data_final['company']=two
# data_final['time']=three

###########################################################################
"修改上方可能出现的错误，利用akshare数据源找 基金经理+基金公司+累计从业时间"
data_final = ak.fund_manager().rename(columns={
    '姓名':'name','所属公司':'company','累计从业时间':'time'})[['name','company','time']]
data_final['time'] = data_final['time'].apply(lambda x: '{}年又{}天'.format(x//365,x%365))

###########################################################################


data_301 = data_final_result_classify.copy()


data_301['new'] = data_301['manager']+data_301['company']
data_301['new'] = data_301['new'].str.replace("等","")

data_final['new'] = data_final['name'] + data_final['company']
data_final.drop(['name','company'],inplace=True,axis=1)

data_final_301 = pd.merge(data_301,data_final,how='inner',on='new')


data_final_301.drop(['new'],axis=1,inplace=True)

# sql = 'SELECT * FROM project.sharp_and_standard;'
# con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='rank_data')
# df_sharp = pd.read_sql(sql, con)
# con.close()


df_sharp = pd.read_excel('sharp_and_standard.xlsx',engine='openpyxl',dtype={'id':'str'})


data_final_301 = pd.merge(data_final_301,df_sharp,how='left',on='id')

# data_final_301.to_excel('2021415.xlsx')



# #获取限额情况
# headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'}      
# data_final_finish = list()
# for x in data_final_301['id']:
#     url = 'http://fund.eastmoney.com/{}.html'.format(x)
#     text = requests.get(url,headers=headers)
#     text.encoding='utf-8'
#     text_con=text.text
#     p_trading_state = '<span class="itemTit">交易状态：</span><span class="staticCell">(.*?)</span></div>'
#     data = re.findall(p_trading_state, text_con)
#     data_final_finish.append(data)
#     print('finish',x)
#     text.close()
    
 #获取限额情况   
    
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'}      
data_final_finish = list()  
data_final_301_b = data_final_301.copy() 



# data_final_301_b = data_final_301[1737:].copy()  


  
for index,row in data_final_301_b[:].iterrows():
    # time.sleep(2)
    url = 'http://fund.eastmoney.com/{}.html'.format(row['id'])
    text = requests.get(url,headers=headers)
    text.encoding='utf-8'
    text_con=text.text
    p_trading_state = '<span class="itemTit">交易状态：</span><span class="staticCell">(.*?)</span></div>'
    data = re.findall(p_trading_state, text_con)
    data_final_finish.append(data)
    print('finish',index,row['id'])
    text.close()
    
    
    
try:
    for info in range(len(data_final_finish)):
        data_final_finish[info]=data_final_finish[info][0].replace('<span class="staticCell">','').replace('<span>','').replace('</span>','').replace('>','')
except:
    print("finish")

data_final_301['限额情况'] = data_final_finish
#读取持仓   


'更新持仓后，修改下方时间名称'


hold_company = pd.read_csv('持仓_20230128.csv',dtype={'id':str})    
hold_percent = pd.read_csv('占比_20230128.csv',dtype={'id':str})   #  持仓10里面多了好多0
################################################################################################



# "每个季度跑一次，其他时间直接全部运行就可以了"
# "基金前十持仓占比按行业汇总 >=10% 统计"


# data_industry=pd.read_excel('industry岳20230127.xlsx',engine='openpyxl',dtype={'id':str})




# industry_data = pd.DataFrame()
# fund_id = pd.DataFrame(hold_company['id'])
# for index,row in fund_id.iterrows():
#     industry_data_c = hold_company[hold_company['id']==row['id']][['id','hold1','hold2','hold3', 'hold4', 
#                                                                     'hold5', 'hold6', 'hold7', 'hold8', 'hold9', 'hold10']].T.reset_index()
#     industry_data_c = industry_data_c.drop(industry_data_c[industry_data_c['index']=='id'].index)
#     industry_data_c = industry_data_c.drop(industry_data_c.columns[[0]],axis=1)
#     industry_data_c['id'] = row['id']
#     industry_data_c = industry_data_c.reset_index()
#     industry_data_c.columns=['index','hold','id']
    
#     industry_data_p = hold_percent[hold_percent['id']==row['id']][['id','percent1','percent2','percent3', 'percent4', 
#                                                                     'percent5', 'percent6', 'percent7', 'percent8', 'percent9', 'percent10']].T.reset_index()
#     industry_data_p = industry_data_p.drop(industry_data_p[industry_data_p['index']=='id'].index)
#     industry_data_p = industry_data_p.drop(industry_data_p.columns[[0]],axis=1)
#     industry_data_p['id'] = row['id']
#     industry_data_p = industry_data_p.reset_index()
#     industry_data_p.columns=['index','percent','id']
    
#     industry_data_b = pd.merge(industry_data_c,industry_data_p,on=['index','id'],how='inner')
#     industry_data = industry_data.append(industry_data_b)
#     print(index,row['id'])


# industry_data = pd.merge(industry_data,data_industry[['name','industry']],left_on='hold',right_on='name',how='left')
# industry_data = industry_data.drop(industry_data[industry_data['industry'].isna()].index)
# industry_data['percent'] = industry_data['percent'].str.replace('%','').replace('---','0').astype('float')
# industry_data = industry_data.groupby(by=['id','industry']).agg({'percent':'sum'}).sort_values(['id','percent'],ascending=[1,0]).reset_index()

# industry_data = industry_data[industry_data['percent']>=5].reset_index(drop=True)
# industry_data['percent'] = industry_data['percent'].astype('str')
# industry_data['percent'] = industry_data['percent'].map(lambda x:x[0:6])
# industry_data['industry'] = industry_data['industry']+industry_data['percent']
# industry_data = industry_data[['id','industry']]



# industry_data_fundid = pd.DataFrame(industry_data['id'].drop_duplicates() ).reset_index()[['id']]
# industry_data_df = pd.DataFrame()
# for index,row in industry_data_fundid.iterrows():
#     industry_data_df_b = pd.DataFrame()

#     industry_data_df_b = industry_data[industry_data['id']=='{}'.format(row['id'])][['industry']].reset_index(drop=True).T.reset_index(drop=True)
#     industry_data_df_b['id'] = row['id']
    
#     columns = list(industry_data_df_b)
#     columns.insert(0, columns.pop(columns.index('id')))  
#     industry_data_df_b = industry_data_df_b.loc[:, columns]
    

#     industry_data_df = pd.concat([industry_data_df, industry_data_df_b],axis=0)
#     print(index,row['id'])



# industry_data_df.to_excel("行业分类岳{}.xlsx".format(date_work))    #手动在excel中分列，分为10列  调整行名为industry1~10





# # 下方不要运行了，使用手动分列完成最后的 行业分类岳{}

# # industry_data['industry'] =industry_data['industry']+','

# # industry_data = industry_data.groupby('id').agg({'industry':'sum'}).reset_index()
# # industry_data['industry1'] = industry_data['industry'].map(lambda x:x.split(',')[0])
# # industry_data['industry2'] = industry_data['industry'].map(lambda x:x.split(',')[1])
# # industry_data['industry3'] = industry_data['industry'].map(lambda x:x.split(',')[2])      # 从这里开始可能报错，直接运行最后的excel输出就可以了
# # industry_data['industry4'] = industry_data['industry'].map(lambda x:x.split(',')[3])
# # industry_data['industry5'] = industry_data['industry'].map(lambda x:x.split(',')[4])
# # industry_data.to_excel("行业分类岳{}.xlsx".format(now_use))



#######################################################################

hold_company = order_for_id(hold_company, 10)
hold_percent = order_for_id(hold_percent, 10)

data_final_301 = pd.merge(data_final_301,hold_company,how='left',on='id')
data_final_301 = pd.merge(data_final_301,hold_percent,how='left',on='id')

# con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='project')
# sql_drowback = 'SELECT * FROM project.drowback_ranking;'
# drowback = pd.read_sql(sql_drowback, con)

drowback = pd.read_excel('drowback_ranking.xlsx',engine='openpyxl',dtype={'id':'str'})

data_final_301 = pd.merge(data_final_301,drowback,how='left',on='id')
# data_final_301.drop(['index_x','index_y'],axis=1,inplace=True)
#命名处理
# data_final_301.drop(['ranking'],axis=1,inplace=True)
order = ['name', 'id', 'M12', 'M11', 'M10', 'M9', 'M8', 'M7', 'M6', 'M5', 'M4',
       'M3', 'M2', 'M1', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720',
       'D60', 'first', 'second', 'third', 'fourth', 'days', 'buy', 'company',
       'size', 'manager', 'kind', 'D270','D450','D540','D630','3y','5y', '行业1', '行业2',
       '行业3', '行业4', 'time', '标准差', '夏普', '最大回撤','半年最大回撤', '两年最大回撤', '三年最大回撤','限额情况', 'hold1', 'hold2',
       'hold3', 'hold4', 'hold5', 'hold6', 'hold7', 'hold8', 'hold9', 'hold10',
       'percent1', 'percent2', 'percent3', 'percent4', 'percent5', 'percent6',
       'percent7', 'percent8', 'percent9', 'percent10']
data_final_301 = data_final_301[order]
data_final_301.columns = ['name', 'id', 'M12', 'M11', 'M10', 'M9', 'M8', 'M7', 'M6', 'M5', 'M4',
       'M3', 'M2', 'M1', 'D1', 'D7', 'D30', 'D90', 'D180', 'D360', 'D720',
       'D60', 'first', 'second', 'third', 'fourth', 'days', 'buy', 'company',
       'size', 'manager', 'kind', 'D270','D450','D540','D630','3y','5y','行业1', '行业2',
       '行业3', '行业4', 'time', '标准差', '夏普', '最大回撤','半年最大回撤', '两年最大回撤', '三年最大回撤','限额情况', 'hold1', 'hold2',
       'hold3', 'hold4', 'hold5', 'hold6', 'hold7', 'hold8', 'hold9', 'hold10',
       'percent1', 'percent2', 'percent3', 'percent4', 'percent5', 'percent6',
       'percent7', 'percent8', 'percent9', 'percent10']
data_final_301=data_final_301.drop_duplicates(keep='first')


# data_final_301.to_excel('{}du.xlsx'.format(date_work),index=False)
# data_final_301.to_sql('{}_du'.format(date_work),con='mysql+pymysql://root:123456@192.168.10.222/dunansi?charset=utf8',if_exists='replace')
data_final_301.to_excel('{}du_mysql.xlsx'.format(date_work),index=False)


# data_final_301 =  pd.read_excel('20211103du.xlsx',engine='openpyxl',dtype={'id':'str'})  #测试
industry_data = pd.read_excel('行业分类岳20230127.xlsx',engine='openpyxl',dtype={'id':'str'})
data_final_301 = pd.merge(data_final_301,industry_data,on='id',how='left')
data_final_301 = data_final_301.drop(['行业1','行业2','行业3','行业4'], 1)   #删除原有的 行业1~5
"调整行业列位置"
data_final_301_order = ['name', 'id', 'M12', 'M11', 'M10', 'M9', 'M8', 'M7', 'M6', 'M5', 'M4', 'M3', 'M2', 'M1', 'D1', 'D7', 
         'D30', 'D90', 'D180', 'D360', 'D720', 'D60', 'first', 'second', 'third', 'fourth', 'days', 'buy', 'company',
         'size', 'manager', 'kind', 'D270','D450','D540','D630','3y','5y', 'time', 'industry1', 'industry2','industry3', '标准差', '夏普', '最大回撤','半年最大回撤', '两年最大回撤', '三年最大回撤', '限额情况', 
         'hold1', 'hold2', 'hold3', 'hold4', 'hold5', 'hold6', 'hold7', 'hold8', 'hold9', 'hold10', 'percent1', 'percent2',
         'percent3', 'percent4', 'percent5', 'percent6', 'percent7', 'percent8', 'percent9', 'percent10']
data_final_301 = data_final_301[data_final_301_order]     

fund_style_anal = fund_style_ana(data_final_301[['id']])

data_final_301 = pd.merge(data_final_301,fund_style_anal,on='id')
data_final_301.to_excel('{}du.xlsx'.format(date_work),index=False)


















