#!/usr/bin/python
# -*- coding: utf-8 -*-


# Execute it in */tlpkg/tlpobj folder

import glob

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

print map_list
print mixedmap_list
