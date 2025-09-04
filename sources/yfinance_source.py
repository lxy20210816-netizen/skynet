#!/usr/bin/env python
#coding:utf-8

import yfinance as yf

qqq = yf.Ticker("QQQ")
pe_ratio = qqq.info.get("trailingPE", "N/A")
print(f"QQQ 市盈率：{pe_ratio}")
