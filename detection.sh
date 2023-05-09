#!/bin/sh

PASSWORD="root1234"
echo $PASSWORD | sudo -kS pkill -9 python3*

PYTHON=/usr/bin/python3
AI=/home/iist


sleep 1;
echo $PASSWORD | sudo -kS ${PYTHON} $AI/main.py&

sleep 1;
echo $PASSWORD | sudo -kS ${PYTHON} $AI/web.py
