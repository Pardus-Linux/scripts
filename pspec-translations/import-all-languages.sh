#!/bin/bash

# Extract all the po files from the pspecs.

./pspec2po.py import ../../../../pardus/devel tr tr.po
./pspec2po.py import ../../../../pardus/devel de de.po
./pspec2po.py import ../../../../pardus/devel nl nl.po

