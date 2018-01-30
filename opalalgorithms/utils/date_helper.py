"""Utils to help manipulate dates easily within the different algorithms"""
import time

date_format = '%Y-%m-%d %H:%M:%S'


def is_date_between(start, end, date):
    stime = time.mktime(time.strptime(start, date_format))
    etime = time.mktime(time.strptime(end, date_format))
    ptime = time.mktime(time.strptime(date, date_format))
    return stime < ptime < etime


def is_date_greater(start, date):
    stime = time.mktime(time.strptime(start, date_format))
    ptime = time.mktime(time.strptime(date, date_format))
    return stime < ptime

