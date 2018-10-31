#!/bin/bash

echo "select * from get_sensors_not_updates_last_hour()" | psql -t -A -F ';'
