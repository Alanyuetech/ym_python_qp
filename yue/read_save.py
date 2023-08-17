# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
# import numpy as np
import datetime
# import requests as req
import tushare as ts


# def getLastWeekDay(day=datetime.datetime.now()):
#     now=day
#     if now.isoweekday()==1:
#       dayStep=3
#     else:
#       dayStep=1
#     lastWorkDay = now - datetime.timedelta(days=dayStep)
#     return lastWorkDay
# date_work=getLastWeekDay().strftime('%Y%m%d')

# 各大指数涨幅情况
def get_index():
    # 获得各大指数上一个交易日涨跌幅
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    SH = ts.get_hist_data('sh', start='2022-10-10', end=end_date).iloc[1, :]
    SH = format((SH.iloc[2] - SH.iloc[0]) / SH.iloc[0], '.2%')
    SZ = ts.get_hist_data('sz', start='2022-10-10', end=end_date).iloc[1, :]
    SZ = format((SZ.iloc[2] - SZ.iloc[0]) / SZ.iloc[0], '.2%')
    CYB = ts.get_hist_data('cyb', start='2022-10-10', end=end_date).iloc[1, :]
    CYB = format((CYB.iloc[2] - CYB.iloc[0]) / CYB.iloc[0], '.2%')
    HS300 = ts.get_hist_data('hs300', start='2022-10-10', end=end_date).iloc[1, :]
    HS300 = format((HS300.iloc[2] - HS300.iloc[0]) / HS300.iloc[0], '.2%')
    # 生成表格
    index_data = [[SH, SZ, CYB, HS300]]
    index = pd.DataFrame(index_data, columns=['上证指数', '深圳成指', '创业板指', '沪深300'])
    return index


# 单因子数据读取
def read_rank(path, quantity, factor, industry):
    # 数据读取与提取
    data = pd.read_excel(io=path, dtype={'id':str})
    data = data[['id', 'name', 'kind', 'D1', 'D7', 'D30', 'D60', 'D90', 'D180', 'D270', 'D360', 'D720', 'days', 'buy',
                 'size'
                 ]][0:quantity]
    # 数据格式确认
    data['D1'] = data['D1'].apply(lambda x: format(x, '.2%'))
    data['D7'] = data['D7'].apply(lambda x: format(x, '.2%'))
    data['D30'] = data['D30'].apply(lambda x: format(x, '.2%'))
    data['D60'] = data['D60'].apply(lambda x: format(x, '.2%'))
    data['D90'] = data['D90'].apply(lambda x: format(x, '.2%'))
    data['D180'] = data['D180'].apply(lambda x: format(x, '.2%'))
    data['D270'] = data['D270'].apply(lambda x: format(x, '.2%'))
    data['D360'] = data['D360'].apply(lambda x: format(x, '.2%'))
    data['D720'] = data['D720'].apply(lambda x: format(x, '.2%'))
    # 行业数据补入
    data = pd.merge(data, industry, on='id')
    # 索引重置
    rank = list([x for x in range(1, quantity + 1)])
    data.index = rank
    data.index.name = f'{factor}排名'
    return data


# 基金主配行业读取
def read_industry(path):
    id_industry = pd.read_excel(io=path,engine='openpyxl', dtype={'id': str}, usecols=[1, 39, 40, 41])
    return id_industry


# 数据写入
def write_excel(path, industry_path):
    # 储存路径生成
    date = datetime.datetime.now().strftime('%Y-%m-%d')
    save_path = f'{path}\\{date}.xlsx'
    # 行业数据读取
    industry = read_industry(industry_path)
    ## 数据写入
    # 创建写入器
    writer = pd.ExcelWriter(save_path, engine='openpyxl')
    # 写入上一个交易日各大指数涨跌幅
    index = get_index()
    index.to_excel(writer, startrow=0, header=True, index=False)
    # 生成读取目录及循环读取与储存
    observation_factors = ['D1', 'D7', 'D30', 'D60', 'D90', 'D180', 'D270', 'D360', 'D720']
    start_row = 4
    for factor in observation_factors:
        if factor == 'D90' or factor == 'D180':
            data = read_rank(f'{path}\\{factor}.xlsx', 50, factor, industry)

            data.to_excel(writer, startrow=int(start_row), header=True, index=True)
            start_row += 54
        else:
            data = read_rank(f'{path}\\{factor}.xlsx', 30, factor, industry)
            data.to_excel(writer, startrow=int(start_row), header=True, index=True)
            start_row += 34
        print(f'{factor}写入完成！！！')
    writer.save()
    writer.close()


if __name__ == '__main__':
    path = r'D:\ym_python_new\production_file\2022\20221111'
    industry_path = r'D:\ym_python_new\20221109du.xlsx'
    write_excel(path, industry_path)












































