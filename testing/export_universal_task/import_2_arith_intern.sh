#!/usr/bin/env bash

curl -X POST -F "arith.xml=@./version_2/arithNewTask.xml" \
    http://127.0.0.1:8000/importTask > ./test-import-version2.html