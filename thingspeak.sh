#!/bin/bash

api_key='TXMVSP5ZG7VZAMZ2'

hall_temp=`echo "select get_sensor_last_data('28FF846AA31503F4')" | psql -U ldv80| tail -3| head -1|cut -d',' -f1|cut -c3-`
outside_temp=`echo "select get_sensor_last_data('28FF404B69140448')" | psql -U ldv80| tail -3| head -1|cut -d',' -f1|cut -c3-`
boiler_state=`echo "SELECT state::integer FROM actuators where id=1;" | psql|tail -3|head -1|tr -d ' '`
bathRoom1_temp=`echo "select get_sensor_last_data('28FF0B4CA3150329')" | psql -U ldv80| tail -3| head -1|cut -d',' -f1|cut -c3-`

# post the data to thingspeak
#curl -k --data \
#	"api_key=$api_key&field1=$hall_temp&field2=$outside_temp\
#	" https://api.thingspeak.com/update

# post the data to ldv80.perets.su influxDB
curl -i -XPOST 'http://ldv80.perets.su:8086/write?db=ldv80' --data-binary "onewire_sensors,sensor=\"hall\" value=$hall_temp"
curl -i -XPOST 'http://ldv80.perets.su:8086/write?db=ldv80' --data-binary "onewire_sensors,sensor=\"outside\" value=$outside_temp"
curl -i -XPOST 'http://ldv80.perets.su:8086/write?db=ldv80' --data-binary "onewire_sensors,sensor=\"boiler_state\" value=$boiler_state"
curl -i -XPOST 'http://ldv80.perets.su:8086/write?db=ldv80' --data-binary "onewire_sensors,sensor=\"bathRoom1\" value=$bathRoom1_temp"
