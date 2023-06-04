#!/bin/bash

CHECK_PROCESS=$(ps -aux -U "nonroot" | grep "data_collect.py" | wc -l)

if [[ $CHECK_PROCESS == 2 ]]
then
  exit 0;
else
  exit 1;
fi
