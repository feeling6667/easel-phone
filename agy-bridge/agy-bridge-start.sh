#!/bin/bash
pkill -f agy-bridge.py || true
sleep 1
nohup python3 "$(dirname "$0")/agy-bridge.py" > /tmp/agy-bridge.log 2>&1 &
