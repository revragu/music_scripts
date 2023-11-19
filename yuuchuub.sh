#!/bin/bash

req="$*"

virtualenv yuuchuub
source ./yuuchub/bin/activate

./yuuchub.py "$req"
