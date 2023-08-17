# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 13:39:34 2022

@author: Administrator
"""


"基金评价体系--基金公司"
def fundeva_companies():
    import akshare as ak
    import pandas as pd
    import numpy as np
    
    import difflib
    def bu_zero(fund_id,id_id):
        "基金代码前面补0"
        "fund_id：df名称  id_id:需要修改的列"
        fund_id['{}'.format(id_id)] = fund_id['{}'.format(id_id)].map(lambda x:str(x).zfill(6))
        return fund_id

    "基金公司规模"

    fund_companies = ak.fund_aum_em()
    fund_companies = fund_companies[['序号','基金公司','全部管理规模']].sort_values('全部管理规模',ascending=0)
    fund_companies = fund_companies.dropna(axis=0,how='any')
    fund_companies['基金公司规模得分'] = fund_companies['序号'].map(lambda x:1 if x<=20 else(0.75 if (x>20)&(x<=50) else(0.5 if (x>50)&(x<=100) else 0.25)))
    
    stock_id = pd.read_excel('对比基金持仓股票分析-岳20230127--持股数前500.xlsx',engine='openpyxl',dtype={'id':'str'})
    stock_id = bu_zero(stock_id,'股票代码')
    
    "基金公司前十持仓"
    
    
    company_hold =  pd.read_excel('当季持仓聚合前源数据-岳20230127.xlsx',engine='openpyxl',dtype={'id':'str'})
    company_hold = bu_zero(company_hold,'基金代码')
    company_hold_stock = company_hold.groupby(['基金公司','股票代码','股票名称']).agg({'持股数':'sum'}).sort_values(['基金公司','持股数'],ascending=[1,0]).groupby(by='基金公司').head(10).reset_index()
    company_hold_stock = pd.merge(company_hold_stock,stock_id[['股票代码','所属行业','持股数变动']],on='股票代码')
    company_hold_stock['基金公司季度调仓能力得分'] = 1
    company_hold_stock_sum = company_hold_stock[['基金公司','基金公司季度调仓能力得分']].groupby('基金公司').agg({'基金公司季度调仓能力得分':'sum'})
    company_hold_stock_sum['基金公司季度调仓能力得分'] = company_hold_stock_sum['基金公司季度调仓能力得分']/10
    company_hold_stock_sum = company_hold_stock_sum.reset_index()
    
    "基金公司匹配"
    company_name =  pd.read_excel('基金公司名称对应.xlsx',engine='openpyxl',dtype={'id':'str'})   #写好基金公司的全名和简写的爬虫可以替换为对应文件
   
    fund_companies = pd.merge(fund_companies,company_name,left_on='基金公司',right_on='基金公司1')
    fund_companies = pd.merge(fund_companies,company_hold_stock_sum,left_on='基金公司2',right_on='基金公司')
    fund_companies = fund_companies[['基金公司2','基金公司规模得分','基金公司季度调仓能力得分']].rename(columns={'基金公司2':'company'})

    return fund_companies


if __name__ == '__main__':
    fund_companies = fundeva_companies()
    pass    











