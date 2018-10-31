#!/usr/bin/env python
import fcntl, sys
import socket
import psycopg2
import datetime

TCP_IP = '192.168.153.1'
TCP_PORT = 8082
BUFFER_SIZE = 4096
MESSAGE = "Hello, World!"

pid_file = '/var/run/ldv80/get_sensor_data.pid'
fp = open(pid_file, 'w')
try:
    fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    print "Another instance is running"
    sys.exit(0)

try:
	pg_conn = psycopg2.connect("dbname='ldv80' user='ldv80' host='localhost' connect_timeout=10")
except psycopg2.DatabaseError, err:
	print "Unable to connect to the postgresql database"
        print str(err)
	exit(1)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(180.0)

try:
	s.connect((TCP_IP, TCP_PORT))
except:
    print "Unable to connect to the host " + TCP_IP
    pg_conn.close()
    exit(1)

pg_cur = pg_conn.cursor()

i = 0
while i < 16:
	
    data = s.recv(BUFFER_SIZE)
#    print "DATA BEGIN..."
#    print (str(data))
#    print "DATA END..."

    s_lines = data.split('\r\n')
#   print str(s_lines)
#    print "s_lines begin"
    for row in s_lines:
        if len(row) <7:
            break
#        print str(row)
        tokens = row.split(' ')
        s_address = tokens[0]
        s_value = tokens[1]
        try:
            f_value = float(s_value)
        except:
            continue

        if len(s_address) != 16 or (f_value < -100.0 or f_value > 100.0):
            print("Wrong data: ", s_address, s_value)
            continue

        now = str(datetime.datetime.now())
        query = "insert into onewire_sensors (date,address,value) values('" + now + "','" + tokens[0] + "','" +tokens[1] +"')"
#        print "query=", query
	try:
	    pg_cur.execute(query)
	except psycopg2.Error as e:
            print "Can't execute query: " + e.pgerror
#    print "s_lines end"            
    i += 1

s.close()
pg_conn.commit()
pg_cur.close()
pg_conn.close()
