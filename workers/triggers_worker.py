#!/usr/bin/env python
import psycopg2
import datetime
import sys
import os
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def do_action(pg_cur, actuator_id, action, action_type_id):
    if action_type_id == 1:
        set_actuator(pg_cur, actuator_id, action)
    if action_type_id == 2:
        set_schedule(pg_cur, actuator_id, action)

def set_schedule(pg_cur, schedule_id, action):
    query = 'update schedules set active = ' + str(action) + ' where id= ' +str(schedule_id)
    try:
        pg_cur.execute(query)
    except psycopg2.Error as err:
        print str(err)
    
    print "set_schedule(): Set active=" + str(action) +" for schedule with id=" + str(schedule_id)
    return

def set_actuator(pg_cur, actuator_id, action):
    query = 'select name, state, "GPIO_pin", inverse from actuators where id = ' + str(actuator_id)
    try:
        pg_cur.execute(query)
    except psycopg2.Error, err:
        print str(err)
    
    rows = pg_cur.fetchall()
    gpio_pin = rows[0][2]
    state = rows[0][1]
    inv = rows[0][3]
    new_state = action
    if inv:
        new_state = not action
    GPIO.setup(gpio_pin, GPIO.OUT)
    GPIO.output(gpio_pin, not new_state)
    query = 'update actuators set state = ' + str(action) +' where id = ' + str(actuator_id)
    try:
        pg_cur.execute(query)
    except psycopg2.Error, err:
        print str(err)

    print "set_actuator(): Set actuator state to " + str(action) +" for actuator_id=" + str(actuator_id)
    if actuator_id < 4:
        arg = ""
        str_action = str(int(action == 'true'))
        for i in range (1,5):
            if i == actuator_id:
                arg += str_action
            else:
                arg += "x"
            if i < 4:
                arg += ","
        #os.system("sudo /usr/local/bin/neopixel_indication.py " + arg)
    return

try:
    pg_conn = psycopg2.connect("dbname='ldv80' user='ldv80' host='localhost' connect_timeout=10")
except psycopg2.DatabaseError, err:
    print "Unable to connect to the postgreSQL"
    print str(err)
    sys.exit(1)

pg_cursor = pg_conn.cursor()

query = "select trigger_name, sensor_value, var_value, compare_type, actuator_id, action, action_type_id from get_triggers()"
try:
    pg_cursor.execute(query)
except psycopg2.Error, err:
    print str(err)

now = datetime.datetime.now().time()
wday = datetime.datetime.now().weekday()

rows = pg_cursor.fetchall()
for row in rows:
    sensor_value = row[1]
    var_value = row[2]
    comp_type = row[3]
    actuator_id = row[4]
    action = row[5]
    action_type_id = row[6]

    if comp_type == 1 and float(sensor_value) >= float(var_value):
        do_action(pg_cursor, actuator_id, action, action_type_id)
        print "(" + row[0] +") " + sensor_value +" > " + var_value +" switch acuator " + str(actuator_id) + " into " + str(action)
    if comp_type == -1 and float(sensor_value) < float(var_value):
        do_action(pg_cursor, actuator_id, action, action_type_id)
        print "(" + row[0] + ") " + sensor_value +" < " + var_value +" switch acuator " + str(actuator_id) + " into " + str(action)
    if comp_type == 0 and float(sensor_value) == float(var_value):
        do_action(pg_cursor, actuator_id, action, action_type_id)
        print "(" + row[0] + ") " + sensor_value +" == " + var_value +" switch acuator " + str(actuator_id) + " into " + str(action)
#    print sensor_value, var_value, comp_type, actuator_id, action

pg_conn.commit()
pg_cursor.close()
pg_conn.close()   

