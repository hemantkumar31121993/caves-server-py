#!/bin/bash

ab -T application/json -p des.post -c 1000 -n 10000 https://localhost/desgen 2>&1 1> desgen.txt
