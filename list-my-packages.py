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

import bz2
import lzma
import os
import piksemel
import sys
import urllib

countPackages = 0
myPackages = {}

def panic():
    print "Usage: list-my-packages <sourceRepoIndexFileURL.xz> <name> <surname>"
    print "       list-my-packages <sourceRepoIndexFileURL.bz2> <name> <surname>"
    sys.exit(1)

def get_and_save_user_info():
    name = "PACKAGER_NAME"
    email = "PACKAGER_EMAIL"

    conf_file = os.path.expanduser("~/.packagerinfo")
    if os.path.exists(conf_file):
        # Read from it
        name, email = open(conf_file, "r").read().strip().split(",")

    else:
        print "Please enter your full name as seen in pspec files"
        name = raw_input("> ")
        print "Please enter your e-mail as seen in pspec files"
        email = raw_input("> ")
        print "Saving packager info into %s" % conf_file

        open(conf_file, "w").write("%s,%s" % (name, email))

    return name

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

if __name__ == "__main__":

    if len(sys.argv) < 2:
        panic()
        sys.exit(1)

    indexURL = sys.argv[1]
    indexName = sys.argv[1].split('/')[-1]
    me = get_and_save_user_info()

    downloadIndex(indexURL, indexName)
    getMyPackages(indexName, me)
    listMyPackages()
