#!/bin/bash

# Extract all the po files from the pspecs.

./pspec2po.py extract ../../../../pardus/devel tr tr.po
./pspec2po.py extract ../../../../pardus/devel de de.po
./pspec2po.py extract ../../../../pardus/devel nl nl.po

