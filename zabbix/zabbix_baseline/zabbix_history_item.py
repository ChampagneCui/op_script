#!/bin/env python
import sys
import time
import pymysql
from datetime import datetime
from pyzabbix import ZabbixAPI

zapi = ZabbixAPI("http://x.x.x.x/zabbix")
# Login to the Zabbix API
zapi.login("root", "password")


def get_history(item_id,time_till,time_from):
    # Query item's history (integer) data
    history = zapi.history.get(itemids=[item_id], time_from=time_from, time_till=time_till, output="extend",)

    # If nothing was found, try getting it from history (float) data
    if not len(history):
        history = zapi.history.get(itemids=[item_id], time_from=time_from, time_till=time_till, output="extend",history=0)
    save2mysql(history)


def save2mysql(history):
    db = pymysql.connect("localhost", "root", "password", "res")
    cursor = db.cursor()
    print(history)
    for i in history:
        sql = """INSERT IGNORE INTO zabbix_item_history(`itemid`, `value`, `timestamp`) VALUES (%s,%s,%s);""" %(i['itemid'],i['value'],i['clock'])
        print(sql)
        cursor.execute(sql)
    db.commit()
    db.close()


if __name__ == "__main__":
    item_id=sys.argv[1]

    # Create a time range
    #time_till = 1517383836
    time_till = time.mktime(datetime.now().timetuple())
    time_from = time_till - 180
    get_history(item_id,time_till,time_from)
