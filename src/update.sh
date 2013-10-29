#!/bin/bash

if [ -d pywsman ]
then
    rm -rf pywsman
fi

git clone https://github.com/eedgar/dell-wsman-client-api-python.git pywsman
