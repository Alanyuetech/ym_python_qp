# -*- coding: utf-8 -*-
"""
Created on Tue Dec 21 14:07:25 2021

@author: Administrator
"""

"国内基金当日预估"

import akshare as ak
import pandas as pd
import time 
import numpy as np
import datetime


now_day = datetime.datetime.now().strftime('%Y%m%d')
"净值估算"
fund_value_estimation = ak.fund_value_estimation_em(symbol="全部")
fund_value_estimation.to_excel('净值估算{}.xlsx'.format(now_day))