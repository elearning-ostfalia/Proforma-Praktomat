#!/usr/bin/env bash

curl -X POST -F "Testjunitgruendelcheckstyle.zip=@Testjunitgruendelcheckstyle.zip" http://127.0.0.1:8000/importTaskObject/V1.01 > ./test-output.html