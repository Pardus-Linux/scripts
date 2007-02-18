#!/bin/bash

# Extract all the po files from the pspecs.

for i in tr de nl es pt_BR
do
./pspec2po.py import ../../../../pardus/devel $i $i.po
done
=
