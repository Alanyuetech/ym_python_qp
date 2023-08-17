# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 13:04:31 2022

@author: 666
"""

"将文件移动到文件夹，若没有文件夹则创建"
def move_file():

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
    now_day = datetime.datetime.now().strftime('%Y%m%d')
    
    
    import os
    import shutil
    # 创建的目录
    path = "D:\\ym_python_new\\生产文件\\2023\\{}".format(date_work)
    if not os.path.exists(path):
        os.makedirs(path)
        
    shutil.move("D1.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D1.xlsx".format(date_work))
    shutil.move("D7.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D7.xlsx".format(date_work))
    shutil.move("D30.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D30.xlsx".format(date_work))
    shutil.move("D60.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D60.xlsx".format(date_work))
    shutil.move("D90.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D90.xlsx".format(date_work))
    shutil.move("D180.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D180.xlsx".format(date_work))
    shutil.move("D270.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D270.xlsx".format(date_work))
    shutil.move("D360.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D360.xlsx".format(date_work))
    shutil.move("D720.xlsx", "D:\\ym_python_new\\生产文件\\2023\\{}\\D720.xlsx".format(date_work))
    shutil.move("HS300涨幅{}.xlsx".format(date_work), "D:\\ym_python_new\\生产文件\\2023\\{}\\HS300涨幅{}.xlsx"
                .format(date_work,date_work))
    shutil.move("max_latest{}.xlsx".format(date_work), "D:\\ym_python_new\\生产文件\\2023\\{}\\max_latest{}.xlsx"
                .format(date_work,date_work))
    # shutil.move("hk_max_latest{}.xlsx".format(date_work), "D:\\ym_python_new\\生产文件\\2023\\{}\\hk_max_latest{}.xlsx"
    #             .format(date_work,date_work))
    shutil.move("{}.xlsx".format(date_work), "D:\\ym_python_new\\生产文件\\2023\\{}\\{}.xlsx"
                .format(date_work,date_work))
    shutil.move("持仓基金排名{}.xlsx".format(date_work), "D:\\ym_python_new\\生产文件\\2023\\{}\\持仓基金排名{}.xlsx"
                .format(date_work,date_work))
    
    


if __name__ == '__main__':
    move_file()
    pass