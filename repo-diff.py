#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import os
import sys
from pisi.specfile import SpecFile
from pisi.util import join_path

def findPspec(folder):
    pspecList = []
    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            pspecList.append(root)
        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")
    return pspecList

def getVersion(pspecList):
    sources = {}
    for pspec in pspecList:
        specFile = SpecFile(join_path(pspec, "pspec.xml"))
        sources[specFile.source.name] = (specFile.getSourceVersion(), specFile.getSourceRelease())
    return sources

def listCompare(firstRepo, secondRepo):
    # form two sorted lists and 
    # find differences in a single pass
    # over the lists
    keys1 = list(firstRepo.keys())
    keys2 = list(secondRepo.keys())
    keys1.sort()
    keys2.sort()
    onlyinFR = list()
    onlyinSR = list()
    diffVersion = list()
    diffRelease = list()
    i=j=0
    len1 = len(keys1)
    len2 = len(keys2)
    while i < len1:
       while j < len2:
          if keys1[i] < keys2[j]:
             onlyinFR.append(keys1[i])
             i=i+1
          elif keys1[i] > keys2[j]:
             onlyinSR.append(keys2[j])
             j=j+1
          else:
            if firstRepo[keys1[i]][0] != secondRepo[keys2[j]][0]:
              diffVersion.append(keys1[i])
            elif firstRepo[keys1[i]][1] != secondRepo[keys2[j]][1]:
              diffRelease.append(keys1[i])
            #else:
              #same version and release, nothing to do
            i = i+1
            j = j+1
    
    return (onlyinFR, onlyinSR, diffVersion, diffRelease)

def usage(miniMe):
    print """Usage:
      %s    pathToSvn   component   (ex: %s /home/caglar/svn/pardus/ system/devel)
    """ % (miniMe, miniMe)

    sys.exit(1)

if __name__ == "__main__":
    try:
        svnRoot = sys.argv[1]
    except IndexError:
        usage(sys.argv[0])

    try:
        postfix = sys.argv[2]
    except IndexError:
        postfix = ""

    stable = getVersion(findPspec(join_path(svnRoot,"2007/", postfix)))
    devel = getVersion(findPspec(join_path(svnRoot, "devel/", postfix)))
    
    # find differences in given repos
    r = listCompare(stable, devel)
    
    print "Stable --> Devel (different version)"
    for i in r[2]:
       print "    %s: %s (r%s) -> %s (r%s)" % (i, stable[i][0], stable[i][1], devel[i][0], devel[i][1])
    print

    print "Stable --> Devel (different release)"
    for i in r[3]:
       print "    %s: %s (r%s) -> %s (r%s)" % (i, stable[i][0], stable[i][1], devel[i][0], devel[i][1])
    print

    print "Stable has, Devel hasn't"
    for i in r[0]:
       print "    %s" % i
    print

    print "Devel has, Stable hasn't"
    for i in r[1]:
       print "    %s" % i
    print
