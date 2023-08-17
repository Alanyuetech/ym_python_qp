# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 13:52:17 2022

@author: Administrator
"""

"自动进程"

import akshare as ak
import pandas as pd
import time 
import matplotlib as mpl
from matplotlib import pyplot as plt 
import numpy as np
import datetime
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
import xlsxwriter
import openpyxl
from openpyxl.styles import PatternFill,Font,Alignment
import statsmodels.api as sm
import yfinance as yf
from functools import reduce
import random


for i in range(1000000000000):
    
    fund_id = str(random.randint(0,999999)).zfill(6)
    print(i,fund_id)
    time.sleep(2*random.random())