#!/bin/sh

PASSWORD="root1234"
echo $PASSWORD | sudo -kS pkill -9 python3*

PYTHON=/usr/bin/python3
#AI=/home/iist
AI=/usr/src/ultralytics/new_AI_box

sleep 1;
#echo $PASSWORD | sudo -kS ${PYTHON} $AI/main.py&
${PYTHON} $AI/main.py&


sleep 1;
#echo $PASSWORD | sudo -kS ${PYTHON} $AI/web.py
${PYTHON} $AI/web.py

