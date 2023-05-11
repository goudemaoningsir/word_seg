#!/usr/bin/env bash

#!/bin/bash

# 找到所有Python进程的进程ID
process_ids=$(ps -ef | grep "uvicorn" | grep -v "grep" | grep -v "$0" | awk '{print $2}')

# 如果找到了进程ID，就结束所有uvicorn进程
if [[ -n $process_ids ]]; then
    echo "Stopping all uvicorn processes..."
    for pid in $process_ids; do
        echo "Killing process ID: $pid"
        kill -9 $pid
    done
    echo "All uvicorn processes have been stopped."
else
    echo "No uvicorn processes found."
fi