#!/usr/bin/python
# -*- coding: utf-8 -*-

# Execute it in */tlpkg/tlpobj folder

import glob
import os

# TODO: naming should be argument parameter
map_file = "texlive-core.maps"

tlpobj_files = glob.glob("*.tlpobj")

map_list = []
mixedmap_list = []
for files in  tlpobj_files:
    for line in open(files, "r").readlines():
        splitline = line.split(" ", 2)
        if splitline[0] == "execute":
            command = splitline[1]
            parameter = splitline[2].strip()
            if command == "addMap":
                map_list.append(parameter)
            elif command == "addMixedMap":
                mixedmap_list.append(parameter)

if os.path.exists(map_file):
    os.remove(map_file)

temp_file = open(map_file, "a")
for entry in map_list:
    line = "Map " + entry + "\n"
    temp_file.write(line)

for entry in mixedmap_list:
    line = "MixedMap " + entry + "\n"
    temp_file.write(line)

temp_file.close()

print map_list
print mixedmap_list
