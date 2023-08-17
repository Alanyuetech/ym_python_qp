# -*- coding: utf-8 -*-
"""
Created on Mon Oct 18 16:16:15 2021

@author: Administrator
"""

"基金持仓股票分析"


import akshare as ak
import pandas as pd
import time 
from matplotlib import pyplot as plt 
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
import xlsxwriter
import openpyxl
from openpyxl.styles import PatternFill,Font,Alignment


def getLastWeekDay(day=datetime.datetime.now()):
    now=day
    if now.isoweekday()==1:
      dayStep=3
    else:
      dayStep=1
    lastWorkDay = now - datetime.timedelta(days=dayStep)
    return lastWorkDay
date_work=getLastWeekDay().strftime('%Y%m%d')



"基金代码前面补0"
def bu_zero(fund_id,id_id):
    "基金代码前面补0"
    "fund_id：df名称  id_id:需要修改的列"
    fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:'00000'+x if len(x)==1 else
                                      ('0000'+x if len(x)==2 else 
                                       ('000'+x if len(x)==3 else
                                        ('00'+x if len(x)==4 else
                                         ('0'+x if len(x)==5 else x)))))
    return fund_id


"基金重仓股：股票，报告期，基金覆盖家数，持股总数，持股总市值"
# fund_report_stock_cninfo_df = ak.fund_report_stock_cninfo(date="20210630")
# fund_report_stock_cninfo_df = bu_zero(fund_report_stock_cninfo_df,'股票代码')
"股票对应行业"
stock_industry = pd.read_excel('全部A股.xlsx',engine='openpyxl',dtype={'代码':'str'})[['代码','名称','所属行业']]
stock_industry = bu_zero(stock_industry,'代码')
"基金对应基金公司"
company = pd.read_excel('基金-公司-经理-类型.xlsx',engine='openpyxl',dtype={'id':'str'})[['id','company','name']]
company = bu_zero(company,'id')


"近两个季度持仓   q2时间早于q3时间"
q2 =  pd.read_excel('基金持仓岳_2022Q3_20221025.xlsx',engine='openpyxl',dtype={'股票代码':'str','基金代码':'str'})
q3 =  pd.read_excel('基金持仓岳_2022Q4_20230127.xlsx',engine='openpyxl',dtype={'股票代码':'str','基金代码':'str'})

"不是全部持仓，需要只用前十持仓对比两个季度，运行如下代码，如果全部持仓，则不运行"
q2 = q2.sort_values(['基金代码','占净值比例'],ascending=[1,0]).groupby(by='基金代码').head(10).reset_index(drop=True)
q3 = q3.sort_values(['基金代码','占净值比例'],ascending=[1,0]).groupby(by='基金代码').head(10).reset_index(drop=True)


q2_id = pd.DataFrame(q2['基金代码'].drop_duplicates()).reset_index(drop=True) 
q3_id = pd.DataFrame(q3['基金代码'].drop_duplicates()).reset_index(drop=True) 
q2_id = bu_zero(q2_id,'基金代码')
q3_id = bu_zero(q3_id,'基金代码')



###############################################################################################
"两个季度对比"
###############################################################################################

"两个季度共有基金代码"
fund_id = pd.merge(q2_id,q3_id,how='inner')

"两个季度持仓中共有代码数据"
q2 = pd.merge(left=fund_id,right=q2,how='left',on='基金代码')
q3 = pd.merge(left=fund_id,right=q3,how='left',on='基金代码')


"基金~股票    聚合"
q2_fund_stock_data = q2.groupby(by=['基金代码','股票代码']).agg({'占净值比例':'sum','持股数':'sum','持仓市值':'sum'}).reset_index()
q3_fund_stock_data = q3.groupby(by=['基金代码','股票代码']).agg({'占净值比例':'sum','持股数':'sum','持仓市值':'sum'}).reset_index()
"改表头"
q2_fund_stock_data = q2_fund_stock_data.rename(columns={'占净值比例':'上季度占净值比例','持股数':'上季度持股数','持仓市值':'上季度持仓市值'})
"两个季度共有基金，持仓  outer---merge"
fund_stock_data = pd.merge(q3_fund_stock_data,q2_fund_stock_data,on=['基金代码','股票代码'],how='outer')
"从无到有、从有到无的数据  nan替换为0"
fund_stock_data = fund_stock_data.fillna(0)
"替换有问题的数据"
fund_stock_data = fund_stock_data.replace('---',0)
"数值数据切换为数值float"
fund_stock_data[['占净值比例','持股数','持仓市值','上季度占净值比例','上季度持股数',
                 '上季度持仓市值']] = fund_stock_data[['占净值比例','持股数','持仓市值','上季度占净值比例','上季度持股数','上季度持仓市值']].astype('float')    

"计算增减持数据"
fund_stock_data['占净值比例变动'] = fund_stock_data['占净值比例']- fund_stock_data['上季度占净值比例']
fund_stock_data['持股数变动'] = fund_stock_data['持股数']- fund_stock_data['上季度持股数']
fund_stock_data['持仓市值变动'] = fund_stock_data['持仓市值']- fund_stock_data['上季度持仓市值']

"公司，行业添加"
fund_stock_data = pd.merge(fund_stock_data,company,how='left',left_on='基金代码',right_on='id').rename(columns={'company':'基金公司','name':'基金名称'}).drop(columns=['id'])
fund_stock_data = pd.merge(fund_stock_data,stock_industry,how='left',left_on='股票代码',right_on='代码').rename(columns={'名称':'股票名称'}).drop(columns=['代码'])

"输出基金维度的明细"
fund_stock_data.to_excel('基金持仓股票分析明细-岳{}.xlsx'.format(date_work))





"基金公司~股票   聚合"
company_data_td10_jz = pd.DataFrame()
company_data_td10_cg = pd.DataFrame()
company_data_td10_cc = pd.DataFrame()

company_data = fund_stock_data[['基金公司','股票代码','股票名称','所属行业','占净值比例变动','持股数变动','持仓市值变动']]
company_data = company_data.groupby(by=['基金公司','股票代码','股票名称','所属行业']).agg({'占净值比例变动':'sum','持股数变动':'sum','持仓市值变动':'sum'}).reset_index()


xx = pd.DataFrame([['jz','占净值比例变动'],['cg','持股数变动'],['cc','持仓市值变动']])

for index,row in xx.iterrows():
    company_data = company_data.sort_values(['基金公司','{}'.format(row[1])],ascending=[1,1])
    company_data_td10_b = company_data[['基金公司','股票代码','股票名称','所属行业','{}'.format(row[1])]].groupby(by='基金公司').head(10)  #后10
    locals()['company_data_td10_'+'{}'.format(row[0])] = locals()['company_data_td10_'+'{}'.format(row[0])].append(company_data_td10_b)
    company_data_td10_b = company_data[['基金公司','股票代码','股票名称','所属行业','{}'.format(row[1])]].groupby(by='基金公司').tail(10)    #前10
    locals()['company_data_td10_'+'{}'.format(row[0])] = locals()['company_data_td10_'+'{}'.format(row[0])].append(company_data_td10_b).sort_values(['基金公司','{}'.format(row[1])],ascending=[1,1]).reset_index(drop=True)
       

# company_data = company_data.sort_values(['基金公司','占净值比例变动'],ascending=[1,1])
# company_data_td10_b = company_data[['基金公司','股票代码','股票名称','占净值比例变动']].groupby(by='基金公司').head(10)
# company_data_td10_jz = company_data_td10_jz.append(company_data_td10_b)
# company_data_td10_b = company_data[['基金公司','股票代码','股票名称','占净值比例变动']].groupby(by='基金公司').tail(10)
# company_data_td10_jz = company_data_td10_jz.append(company_data_td10_b).sort_values(['基金公司','占净值比例变动'],ascending=[1,1]).reset_index(drop=True)

# company_data = company_data.sort_values(['基金公司','持股数变动'],ascending=[1,1])
# company_data_td10_b = company_data[['基金公司','股票代码','股票名称','持股数变动']].groupby(by='基金公司').head(10)
# company_data_td10_cg = company_data_td10_cg.append(company_data_td10_b)
# company_data_td10_b = company_data[['基金公司','股票代码','股票名称','持股数变动']].groupby(by='基金公司').tail(10)
# company_data_td10_cg = company_data_td10_cg.append(company_data_td10_b).sort_values(['基金公司','持股数变动'],ascending=[1,1]).reset_index(drop=True)

# company_data = company_data.sort_values(['基金公司','持仓市值变动'],ascending=[1,1])
# company_data_td10_b = company_data[['基金公司','股票代码','股票名称','持仓市值变动']].groupby(by='基金公司').head(10)
# company_data_td10_cc = company_data_td10_cc.append(company_data_td10_b)
# company_data_td10_b = company_data[['基金公司','股票代码','股票名称','持仓市值变动']].groupby(by='基金公司').tail(10)
# company_data_td10_cc = company_data_td10_cc.append(company_data_td10_b).sort_values(['基金公司','持仓市值变动'],ascending=[1,1]).reset_index(drop=True)

company_data_td10 = pd.concat([company_data_td10_jz,company_data_td10_cg,company_data_td10_cc], axis=1)

"输出公司维度的明细"
company_data_td10.to_excel('对比基金公司持仓股票分析-岳{}.xlsx'.format(date_work))




##########################
"按公司和行业聚合  先去掉前十中的负数   行业出现次数>=2  "
# company_data_td10_jz = company_data_td10_jz[company_data_td10_jz['占净值比例变动']>=0]      # >=0
# df_jz = company_data_td10_jz.groupby(by=['基金公司','所属行业']).agg({'占净值比例变动':'sum'}).sort_values(['基金公司','占净值比例变动'],ascending=[1,0])
# fz = company_data_td10_jz.groupby(['基金公司','所属行业']).agg('count')
# fz = fz[fz['占净值比例变动']>=2].reset_index()[['基金公司','所属行业']]
# df_jz = pd.merge(fz,df_jz,on=['基金公司','所属行业'],how='left')[['基金公司','所属行业','占净值比例变动']].sort_values(['基金公司','占净值比例变动'],ascending=[1,0])

# company_data_td10_cg = company_data_td10_cg[company_data_td10_cg['持股数变动']>=0]          # >=0
# df_cg = company_data_td10_cg.groupby(by=['基金公司','所属行业']).agg({'持股数变动':'sum'}).sort_values(['基金公司','持股数变动'],ascending=[1,0])
# fz = company_data_td10_cg.groupby(['基金公司','所属行业']).agg('count')
# fz = fz[fz['持股数变动']>=2].reset_index()[['基金公司','所属行业']]
# df_cg = pd.merge(fz,df_cg,on=['基金公司','所属行业'],how='left')[['基金公司','所属行业','持股数变动']].sort_values(['基金公司','持股数变动'],ascending=[1,0])

# company_data_td10_cc = company_data_td10_cc[company_data_td10_cc['持仓市值变动']>=0]      # >=0
# df_cc = company_data_td10_cc.groupby(by=['基金公司','所属行业']).agg({'持仓市值变动':'sum'}).sort_values(['基金公司','持仓市值变动'],ascending=[1,0])
# fz = company_data_td10_cc.groupby(['基金公司','所属行业']).agg('count')
# fz = fz[fz['持仓市值变动']>=2].reset_index()[['基金公司','所属行业']]
# df_cc = pd.merge(fz,df_cc,on=['基金公司','所属行业'],how='left')[['基金公司','所属行业','持仓市值变动']].sort_values(['基金公司','持仓市值变动'],ascending=[1,0])

# df_jz.to_excel('占净值比例变动-{}.xlsx'.format(date_work))
# df_cg.to_excel('持股数变动-{}.xlsx'.format(date_work))
# df_cc.to_excel('持仓市值变动-{}.xlsx'.format(date_work))
# ##########################




"行业~股票   聚合"
industry_data_td10_jz = pd.DataFrame()
industry_data_td10_cg = pd.DataFrame()
industry_data_td10_cc = pd.DataFrame()

industry_data = fund_stock_data[['所属行业','股票代码','股票名称','占净值比例变动','持股数变动','持仓市值变动']]
industry_data = industry_data.groupby(by=['所属行业','股票代码','股票名称']).agg({'占净值比例变动':'sum','持股数变动':'sum','持仓市值变动':'sum'}).reset_index()

for index,row in xx.iterrows():
    industry_data = industry_data.sort_values(['所属行业','{}'.format(row[1])],ascending=[1,1])
    industry_data_td10_b = industry_data[['所属行业','股票代码','股票名称','{}'.format(row[1])]].groupby(by='所属行业').head(10)
    locals()['industry_data_td10_'+'{}'.format(row[0])] = locals()['industry_data_td10_'+'{}'.format(row[0])].append(industry_data_td10_b)
    industry_data_td10_b = industry_data[['所属行业','股票代码','股票名称','{}'.format(row[1])]].groupby(by='所属行业').tail(10)
    locals()['industry_data_td10_'+'{}'.format(row[0])] = locals()['industry_data_td10_'+'{}'.format(row[0])].append(industry_data_td10_b).sort_values(['所属行业','{}'.format(row[1])],ascending=[1,1]).reset_index(drop=True)
       

# industry_data = industry_data.sort_values(['所属行业','占净值比例变动'],ascending=[1,1])
# industry_data_td10_b = industry_data[['所属行业','股票代码','股票名称','占净值比例变动']].groupby(by='所属行业').head(10)
# industry_data_td10_jz = industry_data_td10_jz.append(industry_data_td10_b)
# industry_data_td10_b = industry_data[['所属行业','股票代码','股票名称','占净值比例变动']].groupby(by='所属行业').tail(10)
# industry_data_td10_jz = industry_data_td10_jz.append(industry_data_td10_b).sort_values(['所属行业','占净值比例变动'],ascending=[1,1]).reset_index(drop=True)

# industry_data = industry_data.sort_values(['所属行业','持股数变动'],ascending=[1,1])
# industry_data_td10_b = industry_data[['所属行业','股票代码','股票名称','持股数变动']].groupby(by='所属行业').head(10)
# industry_data_td10_cg = industry_data_td10_cg.append(industry_data_td10_b)
# industry_data_td10_b = industry_data[['所属行业','股票代码','股票名称','持股数变动']].groupby(by='所属行业').tail(10)
# industry_data_td10_cg = industry_data_td10_cg.append(industry_data_td10_b).sort_values(['所属行业','持股数变动'],ascending=[1,1]).reset_index(drop=True)

# industry_data = industry_data.sort_values(['所属行业','持仓市值变动'],ascending=[1,1])
# industry_data_td10_b = industry_data[['所属行业','股票代码','股票名称','持仓市值变动']].groupby(by='所属行业').head(10)
# industry_data_td10_cc = industry_data_td10_cc.append(industry_data_td10_b)
# industry_data_td10_b = industry_data[['所属行业','股票代码','股票名称','持仓市值变动']].groupby(by='所属行业').tail(10)
# industry_data_td10_cc = industry_data_td10_cc.append(industry_data_td10_b).sort_values(['所属行业','持仓市值变动'],ascending=[1,1]).reset_index(drop=True)

industry_data_td10 = pd.concat([industry_data_td10_jz,industry_data_td10_cg,industry_data_td10_cc], axis=1)

"输出行业维度的明细"
industry_data_td10.to_excel('对比所属行业持仓股票分析-岳{}.xlsx'.format(date_work))


"只聚合行业"
industry_only = fund_stock_data[['所属行业','占净值比例变动','持股数变动','持仓市值变动']].groupby(by='所属行业').agg({'占净值比例变动':'sum','持股数变动':'sum','持仓市值变动':'sum'}).reset_index()
industry_only.to_excel('对比所属行业分析-岳{}.xlsx'.format(date_work))


"股票     聚合"
fund_stock_data_stock = fund_stock_data[['股票代码','股票名称','所属行业','占净值比例变动','持股数变动','持仓市值变动']].groupby(by=['股票代码','股票名称','所属行业']).agg({'占净值比例变动':'sum','持股数变动':'sum','持仓市值变动':'sum'}).reset_index()
fund_stock_data_stock.to_excel('对比基金持仓股票分析-岳{}.xlsx'.format(date_work))
#对比基金持仓股票分析 按  持股数变动  输出前500个股票
fund_stock_data_stock_500 = fund_stock_data_stock.sort_values('持股数变动',ascending=0).head(500)
fund_stock_data_stock_500[['股票代码','股票名称','所属行业','持股数变动']].to_excel('对比基金持仓股票分析-岳{}--持股数前500.xlsx'.format(date_work))




###############################################################################################
"单个季度分析"
q3_data = pd.merge(q3,company,how='left',left_on='基金代码',right_on='id').rename(columns={'company':'基金公司','name':'基金名称'}).drop(columns=['id'])
q3_data = pd.merge(q3_data,stock_industry,how='left',left_on='股票代码',right_on='代码').drop(columns=['代码','名称'])
"如果有数字报错，无法将str 和 float 相加  运行如下代码进行替换"
q3_data['持仓市值'] = q3_data['持仓市值'].astype('str').str.replace('---','0').astype('float')
q3_data.to_excel('当季持仓聚合前源数据-岳{}.xlsx'.format(date_work))


###############################################################################################
"股票  ~聚合"
q3_stock = q3[['股票代码','股票名称','占净值比例','持股数','持仓市值']]
q3_stock = q3_stock.groupby(by=['股票代码','股票名称']).agg({'占净值比例':'sum','持股数':'sum','持仓市值':'sum'}).reset_index()
q3_stock.to_excel('当季持仓股票聚合-岳{}.xlsx'.format(date_work))





"基金公司~股票   聚合"
q3_company_data_td10_jz = pd.DataFrame()
q3_company_data_td10_cg = pd.DataFrame()
q3_company_data_td10_cc = pd.DataFrame()

q3_company_data = q3_data[['基金公司','股票代码','股票名称','所属行业','占净值比例','持股数','持仓市值']]
q3_company_data = q3_company_data.groupby(by=['基金公司','股票代码','股票名称','所属行业']).agg({'占净值比例':'sum','持股数':'sum','持仓市值':'sum'}).reset_index()


xx = pd.DataFrame([['jz','占净值比例'],['cg','持股数'],['cc','持仓市值']])

for index,row in xx.iterrows():
    q3_company_data = q3_company_data.sort_values(['基金公司','{}'.format(row[1])],ascending=[1,1])
    q3_company_data_td10_b = q3_company_data[['基金公司','股票代码','股票名称','所属行业','{}'.format(row[1])]].groupby(by='基金公司').head(10)  #后10
    locals()['q3_company_data_td10_'+'{}'.format(row[0])] = locals()['q3_company_data_td10_'+'{}'.format(row[0])].append(q3_company_data_td10_b)  
    q3_company_data_td10_b = q3_company_data[['基金公司','股票代码','股票名称','所属行业','{}'.format(row[1])]].groupby(by='基金公司').tail(10)  #前10
    locals()['q3_company_data_td10_'+'{}'.format(row[0])] = locals()['q3_company_data_td10_'+'{}'.format(row[0])].append(q3_company_data_td10_b).sort_values(['基金公司','{}'.format(row[1])],ascending=[1,1]).reset_index(drop=True)
       

q3_company_data_td10 = pd.concat([q3_company_data_td10_jz,q3_company_data_td10_cg,q3_company_data_td10_cc], axis=1)

"输出公司维度的明细"
q3_company_data_td10.to_excel('当季基金公司持仓股票分析-岳{}.xlsx'.format(date_work))


##########################
"按公司和行业聚合  先去掉前十中的负数   行业出现次数>=2"
# q3_company_data_td10_jz = q3_company_data_td10_jz[q3_company_data_td10_jz['占净值比例']>=0]
# df_jz = q3_company_data_td10_jz.groupby(by=['基金公司','所属行业']).agg({'占净值比例':'sum'}).sort_values(['基金公司','占净值比例'],ascending=[1,0])
# fz = q3_company_data_td10_jz.groupby(['基金公司','所属行业']).agg('count')
# fz = fz[fz['占净值比例']>=2].reset_index()[['基金公司','所属行业']]
# df_jz = pd.merge(fz,df_jz,on=['基金公司','所属行业'],how='left')[['基金公司','所属行业','占净值比例']].sort_values(['基金公司','占净值比例'],ascending=[1,0])

# q3_company_data_td10_cg = q3_company_data_td10_cg[q3_company_data_td10_cg['持股数']>=0]
# df_cg = q3_company_data_td10_cg.groupby(by=['基金公司','所属行业']).agg({'持股数':'sum'}).sort_values(['基金公司','持股数'],ascending=[1,0])
# fz = q3_company_data_td10_cg.groupby(['基金公司','所属行业']).agg('count')
# fz = fz[fz['持股数']>=2].reset_index()[['基金公司','所属行业']]
# df_cg = pd.merge(fz,df_cg,on=['基金公司','所属行业'],how='left')[['基金公司','所属行业','持股数']].sort_values(['基金公司','持股数'],ascending=[1,0])

# q3_company_data_td10_cc = q3_company_data_td10_cc[q3_company_data_td10_cc['持仓市值']>=0]
# df_cc = q3_company_data_td10_cc.groupby(by=['基金公司','所属行业']).agg({'持仓市值':'sum'}).sort_values(['基金公司','持仓市值'],ascending=[1,0])
# fz = q3_company_data_td10_cc.groupby(['基金公司','所属行业']).agg('count')
# fz = fz[fz['持仓市值']>=2].reset_index()[['基金公司','所属行业']]
# df_cc = pd.merge(fz,df_cc,on=['基金公司','所属行业'],how='left')[['基金公司','所属行业','持仓市值']].sort_values(['基金公司','持仓市值'],ascending=[1,0])

# df_jz.to_excel('占净值比例-{}.xlsx'.format(date_work))
# df_cg.to_excel('持股数-{}.xlsx'.format(date_work))
# df_cc.to_excel('持仓市值-{}.xlsx'.format(date_work))
##########################



"行业~股票   聚合"
q3_industry_data_td10_jz = pd.DataFrame()
q3_industry_data_td10_cg = pd.DataFrame()
q3_industry_data_td10_cc = pd.DataFrame()

q3_industry_data = q3_data[['所属行业','股票代码','股票名称','占净值比例','持股数','持仓市值']]
q3_industry_data = q3_industry_data.groupby(by=['所属行业','股票代码','股票名称']).agg({'占净值比例':'sum','持股数':'sum','持仓市值':'sum'}).reset_index()

for index,row in xx.iterrows():
    q3_industry_data = q3_industry_data.sort_values(['所属行业','{}'.format(row[1])],ascending=[1,1])
    q3_industry_data_td10_b = q3_industry_data[['所属行业','股票代码','股票名称','{}'.format(row[1])]].groupby(by='所属行业').head(10)
    locals()['q3_industry_data_td10_'+'{}'.format(row[0])] = locals()['q3_industry_data_td10_'+'{}'.format(row[0])].append(q3_industry_data_td10_b)
    q3_industry_data_td10_b = q3_industry_data[['所属行业','股票代码','股票名称','{}'.format(row[1])]].groupby(by='所属行业').tail(10)
    locals()['q3_industry_data_td10_'+'{}'.format(row[0])] = locals()['q3_industry_data_td10_'+'{}'.format(row[0])].append(q3_industry_data_td10_b).sort_values(['所属行业','{}'.format(row[1])],ascending=[1,1]).reset_index(drop=True)
       

q3_industry_data_td10 = pd.concat([q3_industry_data_td10_jz,q3_industry_data_td10_cg,q3_industry_data_td10_cc], axis=1)

"输出行业维度的明细"
q3_industry_data_td10.to_excel('当季所属行业持仓股票分析-岳{}.xlsx'.format(date_work))

"只聚合行业"
q3_industry_only = q3_data[['所属行业','占净值比例','持股数','持仓市值']].groupby(by='所属行业').agg({'占净值比例':'sum','持股数':'sum','持仓市值':'sum'}).reset_index()
q3_industry_only.to_excel('当季所属行业分析-岳{}.xlsx'.format(date_work))







