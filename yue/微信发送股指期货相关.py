# -*- coding: utf-8 -*-
"""
Created on Mon Oct 25 11:07:11 2021

@author: Administrator
"""

"微信自动发送信息"
from wxpy import *

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

"股指期货实时行情"
cffex_text = ak.match_main_contract(exchange="cffex")
while True:
    time.sleep(3)
    data = ak.futures_zh_spot(subscribe_list=cffex_text, market="FF", adjust=False)
    data_sj = data.loc[data['symbol'].str.contains('沪深','上证','中证')]
    data_sj = data[['symbol','time','current_price','hold','volume']]
    print(data_sj)






"初始化机器人，扫码登陆"
bot = Bot()
"搜索名称含有 游否  的男性深圳好友"
my_friend = bot.friends().search('尧西西')[0]