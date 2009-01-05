#!/bin/bash

# Extract all the po files from the pspecs.

for i in tr de nl es pt_BR fr it ca sv pl
do 
./pspec2po.py extract ../../../../pardus/devel $i $i.po
done

