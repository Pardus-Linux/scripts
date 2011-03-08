#!/usr/bin/python
# -*- coding: utf-8 -*-
# A script for grouping the packages in the ack list according to its components.

import sys

import pisi

if __name__ == "__main__":
    db = pisi.db.packagedb.PackageDB()
    components = {}

    for line in sys.stdin:
        package_file = line.strip()
        name = pisi.util.parse_package_name(package_file)[0]
        package = db.get_package(name)
        if package.partOf in components:
            components[package.partOf].append(package_file)
        else:
            components[package.partOf] = [package_file]

    for component in sorted(components.keys()):
        print component
        print "=" * len(component)
        for filename in components[component]:
            print filename
        print
