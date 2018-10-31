#!/usr/bin/env python
import psycopg2
import datetime
import sys


def set_var(pg_cur, var_name, var_value):
    try:
        query = "update variables set value = '"+var_value+"' where name = '"+var_name+"'"
    except:
        print "Error update variable"
    pg_cur.execute(query)
    return

weekdays = (1, 2, 4, 8, 16, 32, 64)

try:
    pg_conn = psycopg2.connect("dbname='ldv80' user='ldv80' host='localhost' connect_timeout=10")
except psycopg2.DatabaseError, err:
    print "Unable to connect to the postgreSQL"
    print str(err)
    sys.exit(1)

pg_cursor = pg_conn.cursor()

query = "select name, start_at, end_at, weekday_mask, var_name, var_value,start_range, end_range from schedules_on_order"
try:
    pg_cursor.execute(query)
except psycopg2.Error, err:
    print str(err)

now = datetime.datetime.now()
wday = datetime.datetime.now().weekday()

rows = pg_cursor.fetchall()
for row in rows:
    start_at = row[1]
    end_at = row[2]

    start_range = row[6]
    if start_range is None:
        start_range = datetime.datetime.now().date()
    
    end_range = row[7]
    if end_range is None:
        end_range = datetime.datetime.now().date()
    start_atDate = datetime.datetime.combine(start_range, start_at)
    end_atDate = datetime.datetime.combine(end_range, end_at)
    
    if end_atDate < start_atDate:
        end_atDate += datetime.timedelta(days=1)
    if now >= start_atDate and now < end_atDate and row[3] & weekdays[wday]:
        set_var(pg_cursor, row[4], row[5])
        print str(row)

pg_conn.commit()
pg_cursor.close()
pg_conn.close()   

