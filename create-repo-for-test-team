#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to rsync the depositories and create
# a new repository for tester.


import os
import sys
import urllib2
import piksemel
import bz2


def rsyncTestandStable(rsyncTestandStable, dir):
    if not os.path.exists(dir):
        os.system("mkdir %s" % dir)

    os.system("rsync -avz %s %s/ --exclude=*.delta.pisi -n" % (rsyncTestandStable, dir))

    right = raw_input("Are the packages right? (yes/no)")
    if right == "yes":
        os.system("rsync -avz %s %s/ --exclude=*.delta.pisi" % (rsyncTestandStable, dir))

def copyPackageFromTestToStable(testDepoDir, testerDepoDir, packageListFile):

    packageList = open(packageListFile, "r")
    for package in packageList:
        if not os.path.exists("%s/%s" % (testerDepoDir, package)):
            os.system("cp -u %s/%s %s/" % (testDepoDir, package.strip(), testerDepoDir))
            print "cp -u %s/%s %s/" % (testDepoDir, package.strip(), testerDepoDir)

def updateStableRepo(svnStableRepoDir):
    os.system("svn up %s" % svnStableRepoDir)

def createIndex(svnStableRepoDir, testerDepoDir):
    os.system("pisi index %s  %s/ --skip-signing --skip-sources -o %s/pisi-index.xml" % (svnStableRepoDir, testerDepoDir, testerDepoDir))

def usage():
    print "usage :"
    print "          %s <tester depository directory> <stable rsync address> <test depository directory> <test rsync address> <stable repo dir> " % sys.argv[0]
    print
    print "example : %s testci-2009 rsync://x/2009-stable packages-test rsync://x/2009-test /home/x/pardus/2009/stable" % sys.argv[0]
    print


if __name__ == "__main__":
    """ main """
    if len(sys.argv) < 6:
        usage()
        sys.exit(1)

    testerDepoDir = sys.argv[1]
    stableRsync = sys.argv[2]
    testDepoDir = sys.argv[3]
    testRsync = sys.argv[4]
    svnStableRepoDir = sys.argv[5]

    rsyncTestandStable(stableRsync, testerDepoDir)
    rsyncTestandStable(testRsync, testDepoDir)

    packageListFile = raw_input("Please enter the package list file after controlling the last updated packages and packages come from the same source: ")
    copyPackageFromTestToStable(testDepoDir, testerDepoDir, packageListFile)

    updateStableRepo(svnStableRepoDir)

    createIndex(svnStableRepoDir, testerDepoDir)
