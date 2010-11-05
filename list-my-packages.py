#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import sys
import lzma
import bz2
import piksemel
import urllib

countPackages = 0
myPackages = {}

def panic():
    print "Usage: list-my-packages <sourceRepoIndexFileURL.xz> <name> <surname>"
    print "       list-my-packages <sourceRepoIndexFileURL.bz2> <name> <surname>"
    sys.exit(1)

def downloadIndex(url, fileName):
    file_to_download = urllib.urlopen(url)
    downloaded_file = open(fileName, 'w')
    downloaded_file.write(file_to_download.read())
    downloaded_file.close()
    file_to_download.close()

def getMyPackages(index, me):
    global countPackages
    if index.endswith("xz"):
        doc = piksemel.parseString(lzma.decompress(file(index).read()))
    elif index.endswith("bz2"):
        doc = piksemel.parseString(bz2.decompress(file(index).read()))
    else:
        panic()

    for spec in doc.tags("Package"):
        packager = spec.getTag("Source").getTag("Packager").getTagData("Name")
        package = spec.getTag("Source").getTagData("Name")
        subPackage = spec.getTagData("Name")

        if packager == me:
            if myPackages.has_key(package):
                myPackages[package].append(subPackage)
            else:
                countPackages += 1
                myPackages[package] = [subPackage]

    return myPackages

def listMyPackages():
    global countPackages
    dashes = ""

    print "\n--------------------------"
    print "|      Package List      |"
    print "--------------------------"

    sortedPackages = myPackages.keys()
    sortedPackages.sort()

    for package in sortedPackages:
        print
        print package
        print myPackages[package]

    message = "| %s has %s packages in this repository |" % (me, countPackages)
    for i in range(len(message)-2): dashes += "-"
    print "\n" + dashes + "\n" + message + "\n"  + dashes + "\n"

if len(sys.argv) == 4:
    indexURL = sys.argv[1]
    indexName = sys.argv[1].split('/')[-1]
    me = sys.argv[2] + " " + sys.argv[3]

    downloadIndex(indexURL, indexName)
    getMyPackages(indexName, me)
    listMyPackages()
else:
    panic()
