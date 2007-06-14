#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#

import os
import sys
import piksemel as iks
import zipfile

files = {}

def pisi_paks(path):
    paks = []
    for root, dirs, files in os.walk(path):
        for fn in files:
            if fn.endswith(".pisi"):
                paks.append(os.path.join(root, fn))
    return paks

def parse_paks():
    for pisi in pisi_paks(sys.argv[1]):
        zip = zipfile.ZipFile(pisi, "r")
        data = zip.read("metadata.xml")
        doc = iks.parseString(data)
        name = doc.getTag("Package").getTagData("Name")
        data = zip.read("files.xml")
        doc = iks.parseString(data)
        for fi in doc.tags("File"):
            path = fi.getTagData("Path")
            if fi.getTag("Hash"):
                if files.has_key(path):
                    files[path].append(name)
                else:
                    files[path] = [ name ]

    for path in files:
        if len(files[path]) > 1:
            print "File '%s' is duplicated in:" % path
            print "  %s" % "\n  ".join(files[path])
            print

parse_paks()

