#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Dist Update planner using pisi api and piksemel
# This script resides because we need to check if we can
# update, to find out what is missing for update etc.
# without adding new distro repo / upgrading any packages
#

import os
import sys

import bz2
import lzma # install python-pyliblzma if you are using Pardus 2009
import urllib2

import piksemel
import pisi

defaultNextRepoURI = "http://packages.pardus.org.tr/pardus/2011/testing/i686/pisi-index.xml.xz"
defaultForceInstallPackageURI = "http://svn.pardus.org.tr/uludag/trunk/pardus-upgrade/2009_to_2011.list"


class DistupdatePlanner:
    def __init__(self, nextRepoUri=defaultNextRepoURI, forceInstallUri=defaultForceInstallPackageURI, Debug=False):
        self.debug = Debug
        self.forceInstallUri = forceInstallUri
        self.nextRepoUri = nextRepoUri

        self.nextRepoRaw = None
        # package[NAME] = [Replaces, PackageFile, PackageSize, InstalledSize, Checksum]
        self.nextRepoPackages = {}
        # package[NAME] = [replacedby1, replacedby2, ...]
        self.nextRepoReplaces = {}
        self.nextRepoObsoletes = []

        self.installedPackages = []
        self.packagesToInstall = []
        self.forceInstallPackages = []
        self.missingPackages = []
        self.graphobj = None

        self.sizeOfInstalledPackages = 0
        self.sizeOfInstalledPackagesAfterUpdate = 0
        self.sizeOfPackagesToDownload = 0
        self.sizeOfBiggestPackage = 0
        self.sizeOfNeededTotalSpace = 0

    def printDebug(self, debugstr):
        if self.debug:
            print debugstr

    def uniq(self, i):
        return list(set(i))

    def getIndex(self):
        uri = self.nextRepoUri
        self.printDebug("* Getting index from %s" % uri)

        try:
            if "://" in uri:
                rawdata = urllib2.urlopen(uri).read()
            else:
                rawdata = open(uri, "r").read()
        except IOError:
            print "could not fetch %s" % uri
            return None

        if uri.endswith("bz2"):
            data = bz2.decompress(rawdata)
        elif uri.endswith("xz") or uri.endswith("lzma"):
            data = lzma.decompress(rawdata)
        else:
            data = rawdata

        self.printDebug("    done")
        self.nextRepoRaw = data

    def convertToPisiRepoDB(self, ix):
        self.printDebug("* Converting package objects to db object")

        doc = piksemel.parseString(ix)
        dbobj = pisi.index.Index()
        dbobj.decode(doc, [])

        self.printDebug("    done")
        return dbobj

    def parseRepoIndex(self):
        self.printDebug("* Parsing package properties in new repo")

        pkgprop = {}
        obsoletelist = []
        ix = piksemel.parseString(self.nextRepoRaw)

        obsoleteParent = ix.getTag("Distribution").getTag("Obsoletes")
        for node in obsoleteParent.tags("Package"):
            obsoletelist.append(node.firstChild().data())

        for i in ix.tags("Package"):
            replaceslist = []

            pkgName = i.getTagData("Name")
            pkgURI = i.getTagData("PackageURI")
            pkgSize = int(i.getTagData("PackageSize"))
            pkgHash = i.getTagData("PackageHash")
            pkgInstalledSize = int(i.getTagData("InstalledSize"))

            replacedPackages = i.getTag("Replaces")

            if replacedPackages:
                for replaced in replacedPackages.tags("Package"):
                    replaceslist.append(replaced.firstChild().data())

            pkgprop[pkgName] = [replaceslist, pkgURI, pkgSize, pkgInstalledSize, pkgHash]

        self.printDebug("    found %d packages and %s obsoletelist" % (len(pkgprop.keys()), len(obsoletelist)))

        self.nextRepoPackages = pkgprop
        self.nextRepoObsoletes = obsoletelist

    def getInstalledPackages(self):
        self.printDebug("* Getting installed packages")

        a = pisi.api.list_installed()
        a.sort()

        self.printDebug("    found %d packages" % len(a))
        self.installedPackages = a

    def getForceInstallPackages(self):
        self.printDebug("* Getting force install packages")

        pkglist = urllib2.urlopen(self.forceInstallUri).read().split()

        self.printDebug("    found %d packages" % len(pkglist))
        self.forceInstallPackages = pkglist

    def calculateInstalledSize(self):
        self.printDebug("* Calculating disk space installed packages are using")

        totalsize = 0
        idb = pisi.db.installdb.InstallDB()

        for i in self.installedPackages:
            pkg = idb.get_package(i)
            totalsize += pkg.installedSize
            #print "%-30s %s" % (pkg.name, pkg.installedSize)

        self.printDebug("    total size = %d" % totalsize)
        self.sizeOfInstalledPackages = totalsize

    def calculateNextRepoSize(self):
        self.printDebug("* Calculating package size and installed size of new packages")

        for p in self.packagesToInstall:
            i = self.nextRepoPackages[p]

            self.sizeOfPackagesToDownload += i[2]
            self.sizeOfInstalledPackagesAfterUpdate += i[3]

            if i[2] > self.sizeOfBiggestPackage:
                self.sizeOfBiggestPackage = i[2]

        self.printDebug("    total download size = %d" % self.sizeOfPackagesToDownload)
        self.printDebug("    total install size  = %d" % self.sizeOfInstalledPackagesAfterUpdate)

    def calculeNeededSpace(self):
        self.printDebug("* Calculating needed space for distupate")

        neededspace = 0
        neededspace += self.sizeOfPackagesToDownload
        neededspace += (self.sizeOfInstalledPackagesAfterUpdate - self.sizeOfInstalledPackages)
        neededspace += 2 * self.sizeOfBiggestPackage

        self.sizeOfNeededTotalSpace = neededspace
        self.printDebug("    total needed space = %d" % neededspace)

    def findMissingPackages(self):
        self.printDebug("* Calculating package differences of old and new repos")

        pkglist = []
        replacedBy = {}
        neededPackages = []

        # we make a cache of replaced packages, not to iterate over and over on package dict
        for i in self.nextRepoPackages:
            pkglist.append(i)
            for r in self.nextRepoPackages[i][0]:
                pkglist.append(r)
                if r in replacedBy:
                    replacedBy[r].append(i)
                else:
                    replacedBy[r] = [i]

        self.nextRepoReplaces = replacedBy

        # and we package list of removed (replaced + obsoleted) packages
        pkglist.extend(self.nextRepoObsoletes)
        uniqpkglist = self.uniq(pkglist)

        for i in self.installedPackages:
            if i not in uniqpkglist:
                neededPackages.append(i)

        self.printDebug("    found %d obsoleted and replaced packages" % len(neededPackages))
        self.missingPackages = neededPackages

    def resolveDependencies(self, A, pkgdb):
        self.printDebug("* Find dependencies for packages to be installed")

        # this would be the system package db on a normal scenario
        # packagedb = pisi.db.packagedb.PackageDB()

        # repodict = dict((pkg.name, pkg) for pkg in pkgdb.packages)
        repodict = dict((pkg.name, pkg) for pkg in pkgdb.packages)

        # our lovely fake package db, we need to make up one since
        # we are working on a repository that is not added to system
        class PackageDB:
            def get_package(self, key, repo = None):
                return repodict[str(key)]

        packagedb = PackageDB()

        # write package names as a list for testing
        # A = repodict.keys()

        # construct G_f
        G_f = pisi.pgraph.PGraph(packagedb)

        # find the install closure graph of G_f by package
        # set A using packagedb
        for x in A:
            G_f.add_package(x)

        B = A
        while len(B) > 0:
            Bp = set()
            for x in B:
                pkg = packagedb.get_package(x)
                for dep in pkg.runtimeDependencies():

                    if not dep.package in G_f.vertices():
                        Bp.add(str(dep.package))
                    G_f.add_dep(x, dep)

            B = Bp

        installOrder = G_f.topological_sort()
        installOrder.reverse()

        return G_f, installOrder


    def planDistUpdate(self):
        self.printDebug("* Planning the whole distupdate process")

        # installed packages
        currentPackages = self.installedPackages

        toRemove = []
        toAdd = []

        # handle replaced packages
        for i in currentPackages:
            if i in self.nextRepoReplaces:
                toRemove.append(i)
                toAdd.extend(self.nextRepoReplaces[i])

        # remove "just obsoleted" packages
        toRemove.extend(self.nextRepoObsoletes)

        # this should never happen with normal usage, yet we need to calculate the scenario
        toRemove.extend(self.missingPackages)

        # new packages needed for the new distro version
        self.getForceInstallPackages()
        toAdd.extend(self.forceInstallPackages)

        currentPackages.extend(toAdd)
        currentPackages = list(set(currentPackages) - set(toRemove))

        indexstring = self.nextRepoRaw
        repodb = self.convertToPisiRepoDB(indexstring)

        self.graphobj, self.packagesToInstall = self.resolveDependencies(currentPackages, repodb)

        self.printDebug("    found %d packages to install" % (len(self.packagesToInstall)))

    def plan(self):
        self.printDebug("* Find missing packages for distupdate ")

        self.getIndex()
        self.parseRepoIndex()
        self.getInstalledPackages()
        self.calculateInstalledSize()
        self.findMissingPackages()
        self.planDistUpdate()
        self.calculateNextRepoSize()
        self.calculeNeededSpace()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        targetrepo = sys.argv[1]
    else:
        # targetrepo = "pisi-index.xml"
        targetrepo = defaultNextRepoURI

    weddingplanner = DistupdatePlanner(nextRepoUri=targetrepo, Debug=True)
    weddingplanner.plan()

    print
    print "*** Conclusion ***"
    print

    if len(weddingplanner.missingPackages):
        weddingplanner.printDebug("  found packages preventing distupdate")
        weddingplanner.printDebug(weddingplanner.missingPackages)
    else:
        weddingplanner.printDebug("  distupdate is good to go")

    print
    print "  installed size %d" % weddingplanner.sizeOfInstalledPackages
    print "  installed size after update %d" % weddingplanner.sizeOfInstalledPackagesAfterUpdate
    print "  download size %d" % weddingplanner.sizeOfPackagesToDownload
    print "  biggest package size %d" % weddingplanner.sizeOfBiggestPackage
    print "  total space needed for distupdate %d" % weddingplanner.sizeOfNeededTotalSpace


