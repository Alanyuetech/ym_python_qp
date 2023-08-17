'''抓取基金历史数据计算回撤'''
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
one_year_l = (now - relativedelta(years=+1)).strftime('%Y%m%d')
two_year_l = (now - relativedelta(years=+2)).strftime('%Y%m%d')
thr_year_l = (now - relativedelta(years=+3)).strftime('%Y%m%d')
hal_year_l = (now - relativedelta(months=+6)).strftime('%Y%m%d')

def getUrl(fscode):
  head = 'http://fund.eastmoney.com/pingzhongdata/'
  tail = '.js?v='+ time.strftime("%Y%m%d%H%M%S",time.localtime())
  return head+fscode+tail


def drowdown(num,time_year):
    #用requests获取到对应的文件
    content = requests.get(getUrl('{}').format(num))
    
    #使用execjs获取到相应的数据
    jsContent = execjs.compile(content.text)
    
    name = jsContent.eval('fS_name')
    code = jsContent.eval('fS_code')
    
    #单位净值走势
    netWorthTrend = jsContent.eval('Data_netWorthTrend')
    #累计净值走势
    ACWorthTrend = jsContent.eval('Data_ACWorthTrend')
    netWorth = []
    Change = []
    ACWorth = []
    #提取出里面的净值
    
    for dayWorth in netWorthTrend:
            netWorth.append(dayWorth['y'])
            Change.append((dayWorth['equityReturn']))
            
    for dayACWorth in ACWorthTrend:
        ACWorth.append(dayACWorth[1])
        
    days=[]
    for day in netWorthTrend:
        time_day=float(day['x']/1000)
        timeArray = time.localtime(time_day)
        otherStyleTime = time.strftime("%Y%m%d", timeArray) 
        days.append(otherStyleTime)
        
    if len(days) != len(ACWorth):
        if None in ACWorth:
            ACWorth.remove(None)
        del ACWorth[len(days) : ]
    data_use=pd.DataFrame()
    data_use['days']=days
    data_use['累计净值']=ACWorth
    data_use['单位净值']=netWorth
    data_use['涨跌幅']=Change
    data_use = data_use.dropna()
    
    result = list()
    middle = 1
    for x in range(1,len(data_use)):
        middle = middle * (data_use.iloc[x,3]/100+1)
        result.append(middle)
    
    result.insert(0, 1)
    data_use['price'] = result
    
    ran = data_use[data_use['days']>=time_year]    # 调整日期，多长时间的最大回撤
    
    result_f = [x for x in ran['price']]
    
    back_list = list()
    for i in range(len(result_f)):
        back_list.append((result_f[i] - min(result_f[i:]))/result_f[i])
    
    if back_list:
        pass
    else:
        back_list=[np.nan]
                         
    return max(back_list)


# con = pymysql.connect(host='192.168.10.219', user='root', password='123456', database='project')
# # data_id_sql = 'SELECT * FROM rank_data.`20210720`;'
# data_id_sql = 'SELECT * FROM rank_data.`20221124`;'
# data_id = pd.read_sql(data_id_sql,con)
# data_id = [x for x in data_id['id']]

data_id = pd.read_excel('{}.xlsx'.format(date_work),engine='openpyxl',dtype={'id':'str'})    #每周修改，用当天的，把文件从文件夹中复制出来
data_id = [x for x in data_id['id']]


##############################################################################################################################################
result_drowdownb = list()
result_drowdown1 = list()
result_drowdown2 = list()
result_drowdown3 = list()

time_start = time.time()


    
# result_drowdownb = result_drowdownb[:7610] 
# result_drowdown1 = result_drowdown1[:7610]
# result_drowdown2 = result_drowdown2[:7610]
# result_drowdown3 = result_drowdown3[:7610]  


for x in data_id[:]:      #如果遇到报错，就看result_drowdown的size  直接写到：前
    result_drowdownb.append(drowdown('{}'.format(x),hal_year_l))
    result_drowdown1.append(drowdown('{}'.format(x),one_year_l))
    result_drowdown2.append(drowdown('{}'.format(x),two_year_l))
    result_drowdown3.append(drowdown('{}'.format(x),thr_year_l))
    print(x)
    
  


time_end = time.time()
time_sum = time_end - time_start
print('运行时间：{:.2f} 秒 '.format(time_sum))


data_final = pd.DataFrame() 
data_final['id'] = data_id
data_final['最大回撤'] = result_drowdown1
data_final['半年最大回撤'] = result_drowdownb
data_final['两年最大回撤'] = result_drowdown2
data_final['三年最大回撤'] = result_drowdown3   

# data_final.to_sql('drowback_ranking',con='mysql+pymysql://root:123456@192.168.10.222/project?charset=utf8',if_exists='replace')

data_final.to_excel('drowback_ranking.xlsx',index=False)
print('完成')


# data_final = pd.read_excel('最大回撤20220301.xlsx',engine='openpyxl')
# data_final.to_excel('最大回撤{}.xlsx'.format(now_day))   

##############################################################################################################################################

"另外输出半年最大回撤  文件形式       修改时间：20220210"

# result_drowdownb = list()

# for x in data_id[:]:      #如果遇到报错，就看result_drowdown的size  直接写到：前
#     result_drowdownb.append(drowdown('{}'.format(x),hal_year_l))
#     print(x)
    
# data_final = pd.DataFrame() 
# data_final['id'] = data_id
# data_final['半年最大回撤'] = result_drowdownb
# data_final.to_excel('半年最大回撤{}.xlsx'.format(now_day))   
# print('完成')


##############################################################################################################################################


# reuslt_drw = pd.DataFrame(result_drowdown,columns=['max'])
# reuslt_drw['id'] = nums[391:]
# reuslt_drw.to_excel('huiche5.xlsx')

# res=drowdown('001656')

# headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'}
# data = requests.get('http://fund.eastmoney.com/519183.html',headers=headers)
# data.encoding = 'utf-8'
# data=data.text
# data = data.replace('\n','').replace('\r','').replace(' ','')
# import re
# p_info='<tr><tdstyle="padding:2px;">(.*?)</td>'
# final=re.findall(p_info,data)

# max_data = max(final)
# if max_data>'2020-03-14' and max_data<'2021-03-14':
#     max_data = max_data.strftime('%Y%m%d')
#     print('yes')
# else:
#     print('no')

# import time
# max_data=max_data.replace('-', '')















