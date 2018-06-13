#!/bin/bash

echo "Running....at...`date`"
#*/5 * * * * source /home/ubuntu/linkedin/cron.sh 2>&1 /home/ubuntu/logs/checktaskqueue.log

source /home/ubuntu/.venv3/bin/activate
cd /home/ubuntu/linkedin

/home/ubuntu/.venv3/bin/python /home/ubuntu/linkedin/manage.py checktaskqueue

echo "Done."