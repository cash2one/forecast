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
import emailsmtp

loger = init_log("suggest")

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
    strHM = strHM[0:-1] #10����һ��
    return '%s/dailym/%s.txt' %(const_root_local,strHM)

def get_suggest_local_file_name():
    strHM = datetime.datetime.now().strftime('%Y%m%d_%H%M')
    strHM = strHM[0:-1] #10����һ��
    return '%s/suggest/%s.htm' %(const_root_local,strHM)


def run():
    if not comm.is_trade_time() :
        print "it's not tradding time !"
        return
    buy_stocknos = ['600290','002290']

    lfile = get_local_file_name()
    loger.info(lfile)

    #generate url
    observe_stocks = load_high_stocks()
    stocks = observe_stocks + load_buy_stocks(buy_stocknos) #load_buy_stocks ����ָ���ѹ����
    params = ['%s%s'%(s.pinyin2,s.stock_no)  for s in stocks]
    params = list(set(params))
    url = config.const_base_url + ','.join(params)

    browser.downad_and_save(url,lfile)
    rows = comm.parse_daily_data(lfile)
    for r in rows:
        r.should_sell = 'sell' if float(r.close_price) < float(r.last_close)*0.98 else '...'
        r.last = [s for s in stocks if s.stock_no == r.stock_no][0]

    content = str(send_reports_withT(rows))
    with open(get_suggest_local_file_name(),'w') as f:
        f.write(content)
        f.close()
    #send email
    subject='stock_%s' % (datetime.datetime.now().strftime('%m%d_%H%M')[0:-1])
    emailsmtp.sendmail(subject,content,['462042991@qq.com']) #,'5632646@qq.com'


def send_reports_withT(rows):
    render_suggest = web.template.frender('templates/suggest.html')
    rows = sorted(rows, cmp=lambda x,y : cmp(y.raise_drop_rate, x.raise_drop_rate))
    data = web.storage(stocks=rows,
        total_count = len(rows),
        last_close_up_count = len( [r for r in rows if r.last.close > r.last.open]),
        today_current_up_count = len( [r for r in rows if r.close_price > r.open_price]),
        today_new_high_count = len( [r for r in rows if r.is_new_high]) ,
        title = "%s %s" % (rows[0].date,rows[0].time)
        )
    return render_suggest(data)


import time
if __name__ == '__main__':
    while True:
        run()
        time.sleep(600)

    #a = load_buy_stocks(['600290','000897'])
    #stocks + a
    #print datetime.datetime.now().strftime('%Y%m%d%H%M')[0:-1]

    #parse_data('D:\\gaotp\\stocks\\daily\\20131111_0.txt')


