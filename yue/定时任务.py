# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 10:03:32 2022

@author: 666
"""

"定时任务"
import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from yue.move_file import move_file
from day.index_import_1 import index_import
from day.hs300zhangdiefu import hs300zhangdiefu
from day.jijinpachong import jijinpachong
from yue.stock_max_latest_yue import stock_max_latest_yue
from yue.holding_fund_ranking import holding_fund_ranking_1
def func():
    
    index_import()
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('index_import  finish :',ts)
    
def func2():
    
    hs300zhangdiefu()
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('沪深300涨幅 finish',ts)

def func3():
  
    jijinpachong()
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('基金爬虫 finish',ts)

def func4():

    stock_max_latest_yue()
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('股票最高值和最近值 finish：',ts)

def func5():

    holding_fund_ranking_1()
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('持仓基金所在排名：',ts)
    
def func6():

    move_file()
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    print('move_file finish：',ts)

    
def dojob():
    #创建调度器：BlockingScheduler
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    #添加任务,定时
    # scheduler.add_job(func, 'cron', day_of_week='mon-fri', hour=7, minute=10,second=10,end_date='2222-05-30')
    # scheduler.add_job(func2, 'cron', day_of_week='mon-fri', hour=7, minute=10,second=10,end_date='2222-05-30')
    # scheduler.add_job(func3, 'cron', day_of_week='mon-fri', hour=7, minute=10,second=10,end_date='2222-05-30')
    # scheduler.add_job(func4, 'cron', day_of_week='mon-fri', hour=7, minute=10,second=10,end_date='2222-05-30')
    # scheduler.add_job(func5, 'cron', day_of_week='mon-fri', hour=8, minute=10,second=10,end_date='2222-05-30')    
 
    
    # scheduler.add_job(func, 'cron', day_of_week='tue-sat', hour=8, minute=35,second=10,end_date='2222-05-30')
    # scheduler.add_job(func2, 'cron', day_of_week='tue-sat', hour=8, minute=38,second=10,end_date='2222-05-30')
    # scheduler.add_job(func3, 'cron', day_of_week='tue-sat', hour=8, minute=45,second=10,end_date='2222-05-30')
    # scheduler.add_job(func4, 'cron', day_of_week='tue-sat', hour=8, minute=55,second=10,end_date='2222-05-30')
    # scheduler.add_job(func5, 'cron', day_of_week='tue-sat', hour=9, minute=35,second=10,end_date='2222-05-30') 
    

    scheduler.add_job(func, 'cron', day_of_week='tue-sat', hour=6, minute=10,second=10,end_date='2222-05-30')
    scheduler.add_job(func2, 'cron', day_of_week='tue-sat', hour=6, minute=13,second=10,end_date='2222-05-30')
    scheduler.add_job(func3, 'cron', day_of_week='tue-sat', hour=6, minute=25,second=10,end_date='2222-05-30')
    scheduler.add_job(func4, 'cron', day_of_week='tue-sat', hour=6, minute=35,second=10,end_date='2222-05-30')
    scheduler.add_job(func5, 'cron', day_of_week='tue-sat', hour=7, minute=30,second=10,end_date='2222-05-30') 
    scheduler.add_job(func6, 'cron', day_of_week='tue-sat', hour=7, minute=40,second=10,end_date='2222-05-30') 
    
    scheduler.start()
    
      
dojob()
