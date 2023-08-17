# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 09:43:17 2022

@author: Administrator
"""

"WIMI 每日"

import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from yue.move_file import move_file
from yue.wimi_bishu import wimi_bishu
from yue.wimi_mrtj import wimi_mrtj
from yue.wimi_zzgs import wimi_zzgs

wimi_bishu(773,162,211)
wimi_mrtj()
wimi_zzgs()