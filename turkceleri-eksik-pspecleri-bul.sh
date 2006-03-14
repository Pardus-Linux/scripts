#!/bin/bash

# cd to pardus devel ... change it necessarily
for p in `find ../../../pardus/devel/ -name pspec.xml`; do grep 'xml:lang' $p > /dev/null; \
if [ $? == "1" ]; then echo $p; fi; done > turkceleri-eksik-pspecler
