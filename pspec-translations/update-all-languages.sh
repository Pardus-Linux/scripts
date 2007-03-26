#!/bin/bash

# Extract all the po files from the pspecs.

for i in tr de nl es pt_BR fr it ca
do
./pspec2po.py update ../../../../pardus/devel $i $i.po
done
