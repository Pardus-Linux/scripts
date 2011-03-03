#!/usr/bin/python
# -*- coding: utf-8 -*-

# Get updated packages regarding differences between pisi index and approved package list

import pisi
import os
import sys
import urllib2
import lzma


def parseXML(index):
    pkglist={}

    ix = pisi.index.Index(index)

    for pkg in ix.packages:
        pkglist[pkg.name] = [pkg.release, pkg.name + "-" + pkg.version + "-" + pkg.release + "-" + pkg.distribution + "-" + pkg.architecture + ".pisi"]
    #print pkglist

    return pkglist

def splitPackage(pkgs):
    pkglist = {}

    for pkg in pkgs:
        pkgname, pkgversion, pkgrelease, release, arch = pkg.rsplit("-", 4)
        pkglist[pkgname] = [pkgrelease, pkg]
    #print pkglist

    return pkglist

def getRepoDiff(newIndex, oldIndex):
    pkglist = {}

    for i in oldIndex.keys():
        if newIndex[i][0] > oldIndex[i][0]:
            pkglist[i] = [oldIndex[i][1],newIndex[i][1]]

    return pkglist

def usage():
    print "usage :"
    print "          %s  <pisi index file> <files to search for ....>" % sys.argv[0]
    print
    print "example : %s pisi-index.xml kernel-2.6.30.1-123-18.pisi bind-9.6.0_p1-22-2.pisi" % sys.argv[0]
    print

if __name__ == "__main__":

    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    index = sys.argv[1]
    packages = sys.argv[2:]

    newIndex = parseXML(index)
    oldIndex = splitPackage(packages)

    pkglist = getRepoDiff(newIndex, oldIndex)
    for i in pkglist.values():
        print i[0] + " upadted to " + i[1]

