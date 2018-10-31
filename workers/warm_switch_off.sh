#!/bin/bash

echo "update schedules set active = false where name = 'warm'" | psql -q
