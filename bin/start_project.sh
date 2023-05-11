#!/usr/bin/env bash

cd "$(dirname "$PWD")"

nohup uvicorn --host 0.0.0.0 --port 1701 --reload "main:app" > log/server.log 2>&1 &

