#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
import math
import da
import re
import datetime
import browser
from decimal import *
import config
from config import const_root_local,init_log,dbr,dbw
import comm

#http://www.cnblogs.com/kingwolfofsky/archive/2011/08/14/2138081.html

def get_current_hhmm():
    return int(datetime.datetime.now().strftime('%Y%m%d%H%M')[8:])

def load_high_stocks():
    #'high_date_90=trade_date and high_date_188=trade_date and close=high and open<>close';
    results = dbr.select('stock_base_infos',where="high_date_90=trade_date and high_date_188=trade_date")
    return list(results)

def load_buy_stocks(stock_nos):
    results = dbr.select('stock_base_infos',where="stock_no in $stock_nos ",vars=locals())
    return list(results)

def get_local_file_name():
    strHM = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    strHM = strHM[0:-1] #10分钟一次
    return '%s/dailym/%s.txt' %(const_root_local,strHM)

regex = re.compile("_[a-z]{2}([\d]+)=")
def parse_data(lfile):
    with open(lfile,'rb') as f:
        lines = f.readlines()
        f.close()

    rows=[]
    for a in lines:
        fields = a.split(',')
        if(len(fields)<30):continue

        stockno = regex.findall(fields[0])
        if not stockno: break

        raise_drop = Decimal(fields[3]) - Decimal(fields[1])
        raise_drop_rate = raise_drop / Decimal(fields[1]) if Decimal(fields[1]) != 0 else 0

        r = web.storage(stock_no=stockno[0],open_price=fields[1],high_price=fields[4],
            low_price=fields[5],close_price=fields[3],last_close=fields[1],
            volume=fields[8],amount=fields[9] ,
            raise_drop=raise_drop, raise_drop_rate=raise_drop_rate,
            is_new_high= fields[4]==fields[3],
            is_new_low= fields[5]==fields[3],
            date=fields[30],time=fields[31])

        #print r
        rows.append(r)
    #rows = [r for r in rows if r['new_high'] ]  当前价就是今天的最高价
    return rows

def run():
    #if not comm.is_trade_time() : return
    lfile = get_local_file_name()

    #generate url
    stocks = load_high_stocks() + load_buy_stocks(['600290']) #load_buy_stocks 额外指定已购买的
    params = ['%s%s'%(s.pinyin2,s.stock_no)  for s in stocks]
    params = list(set(params))
    url = config.const_base_url + ','.join(params)

    browser.downad_and_save(url,lfile)
    rows = parse_data(lfile)

    #10点前的high_price是一个重要的参考点?
    tmp =[r for r in rows if r.is_new_high and r.raise_drop_rate>0]
    sorted(tmp, cmp=lambda x,y : cmp(x.raise_drop_rate, y.raise_drop_rate))
    print '\r'.join(['%s,%s' % (r.stock_no,r.raise_drop_rate) for r in tmp])
    #print rows


if __name__ == '__main__':
    #a = load_buy_stocks(['600290','000897'])
    #stocks + a
    #print datetime.datetime.now().strftime('%Y%m%d%H%M')[0:-1]
    run()
    #parse_data('D:\\gaotp\\stocks\\daily\\20131111_0.txt')


