#!/usr/bin/env python

import psycopg2
import sys

try:
    pg_conn = psycopg2.connect("dbname='ldv80' user='ldv80' host='localhost' connect_timeout=10")
except psycopg2.DatabaseError as err:
    print "Unable connect to PostgreSQL"
    print str(err)
    sys.exit(1)

pg_cursor = pg_conn.cursor()
query = "SELECT temp from get_sensor_last_data('28FF846AA31503F4')"

try:
    pg_cursor.execute(query)
except psycopg2.Error as err:
    print str(err)
    pg_cursor.close()
    pg_conn.close()
    sys.exit(1)

rows = pg_cursor.fetchall()
temp = float(rows[0][0])
if temp < 16.0:
    print "Alarm! Temp into the hall is " + str(temp)

pg_cursor.close()
pg_conn.close()
