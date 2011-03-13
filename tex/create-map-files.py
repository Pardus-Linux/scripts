#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob

# List of texlive- folders
texlive_dirs = [name for name in os.listdir('.') \
                if os.path.isdir(os.path.join('.', name)) and name.startswith("texlive-")]

for package in texlive_dirs:
    map_file = package + ".maps"

    tlpobj_files = glob.glob("%s/tlpkg/tlpobj/*.tlpobj" % package)

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
