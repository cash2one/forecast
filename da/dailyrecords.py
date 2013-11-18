#!/usr/bin/env python
# -*- coding: utf-8 -*-
import web
import datetime
from config import dbr,dbw,const_root_local,init_log


def update(pk_id,**kv):
    dbw.update('stock_daily_records',where='pk_id=$pk_id',vars=locals(),**kv)

def update_marketcode(date):
    dbw.query("update `stock_daily_records` a, stock_base_infos b set a.stock_market_no=b.market_code where a.date='"+ date.strftime('%Y%m%d') +"' and a.stock_no = b.stock_no")

def load_by_date(date):
    return dbr.select('stock_daily_records',what='pk_id,stock_no',where='date=$date',vars=locals())

def load_pkids(date):
    pkids = {}
    rows = load_by_date(date)
    for r in rows:
        pkids[r.stock_no] = r.pk_id
    return pkids

def load_by_stockno(stock_no):
    return list(dbr.select('stock_daily_records',where="stock_no=$stock_no and volume>0", order="date desc",vars=locals()))

def import_date_sums(str_date):
    sql = '''SELECT 'all' as stock_plate,count(*) as stock_count,
        avg(open_price) as open,avg(high_price) as high,avg(low_price) as low,avg(close_price) as close,avg(volume) as volume,avg(amount) as amount
        FROM `stock_daily_records` where date='%s' ''' % (str_date)
    #rows = dbr.query(sql)
    #insert_date_sum(str_date,rows)

    sql = '''SELECT stock_market_no as stock_plate,count(*) as stock_count,
        avg(open_price) as open,avg(high_price) as high,avg(low_price) as low,avg(close_price) as close,avg(volume) as volume,avg(amount) as amount
        FROM `stock_daily_records` where date='%s' and stock_market_no is not null group by stock_market_no''' % (str_date)
    rows = dbr.query(sql)
    insert_date_sum(str_date,rows)

    sql = '''SELECT stock_market_no as stock_plate,count(*) as stock_count
        FROM `stock_daily_records` where date='%s' and stock_market_no is not null and raise_drop>0 group by stock_market_no  ''' % (str_date)
    rows = dbr.query(sql)
    for r in rows:
        stock_plate = r.stock_plate
        dbw.update('date_sums',price_up_count=r.stock_count, where="trade_date=$str_date and stock_plate=$stock_plate",vars=locals())
    dbw.query("update date_sums set price_up_percent=price_up_count/stock_count where trade_date='%s'" % (str_date) )


def insert_date_sum(trade_date,rows):
    dbw.delete("date_sums",where="trade_date=$trade_date",vars=locals())
    for r in rows:
        dbw.insert('date_sums',trade_date=trade_date,stock_plate=r.stock_plate,
        stock_count=r.stock_count,avg_open=r.open,avg_close=r.close,
        avg_high=r.high,avg_low=r.low,avg_volume=r.volume,
        avg_amount=r.amount,create_date=datetime.datetime.now())


def load_max_min(stock_no,days):
    high = dbr.select('stock_daily_records',
        what="date,high_price",
        where="stock_no=$stock_no and TO_DAYS(NOW())-TO_DAYS(date) < $days",
        offset=0,limit=1,
        order="high_price desc",
        vars=locals())[0]
    low = dbr.select('stock_daily_records',
        what="date,low_price",
        where="stock_no=$stock_no and TO_DAYS(NOW())-TO_DAYS(date) < $days",
        offset=0,limit=1,
        order="low_price asc",
        vars=locals())[0]
    return {'high_date_%s'%(days):high.date,
    'high_price_%s'%(days):high.high_price,
    'low_date_%s'%(days):low.date,
    'low_price_%s'%(days):low.low_price}

    return web.storage(days=days,
        high_date=high.date,high_price=high.high_price,
        low_date=low.date,low_price=low.low_price)

