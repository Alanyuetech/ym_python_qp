# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 15:13:14 2022

@author: 666
"""

import yfinance as yf

stock = yf.Ticker("GPC")

# get stock info
stock_info = stock.info

# get historical market data
hist = stock.history(period="max")

# show actions (dividends, splits)
stock_actions = stock.actions

# show dividends
stock_dividends = stock.dividends

# show splits
stock.splits

# show financials
stock_financials = stock.financials
stock_quarterly_financials = stock.quarterly_financials

# show major holders
stock.major_holders

# show institutional holders
stock.institutional_holders

# show balance sheet
stock_balance_sheet = stock.balance_sheet
stock_quarterly_balance_sheet = stock.quarterly_balance_sheet

# show cashflow
stock.cashflow
stock.quarterly_cashflow

# show earnings
stock_earnings = stock.earnings
stock_quarterly_earnings = stock.quarterly_earnings

# show sustainability
stock.sustainability

# show analysts recommendations
stock_recommendations = stock.recommendations

# show next event (earnings, etc)
stock.calendar

# show ISIN code - *experimental*
# ISIN = International Securities Identification Number
stock.isin

# show options expirations
stock.options

# show news
stock.news

# get option chain for specific expiration
opt = stock.option_chain('YYYY-MM-DD')
# data available via: opt.calls, opt.puts


from scipy.stats import f 

print(f.ppf(.025,119,119))
print(f.ppf(.975,119,119))

from scipy.stats import chi2
print(chi2.ppf(.05,9))

from scipy.stats import t 
print((1-t.cdf(2.664,34))*2)






