#!/usr/bin/python
# -*- coding: utf-8 -*-

import piksemel
import bz2
import sys
import os

def getXmlData(_file):
    if os.path.exists(_file):
        return piksemel.parse(_file)
    elif os.path.exists("%s.bz2" % _file):
        indexdata = bz2.decompress(file("%s.bz2" % _file).read())
        return piksemel.parseString(indexdata)
    else:
        print "%s not found" % indexfile
        sys.exit(1)

def fillPackageDict(tag, _hasSpecFile, packageOf):
        PackageName = tag.getTagData("Name")
        if _hasSpecFile:
            PackagePackagerName = tag.getTag("Packager").getTagData("Email")
        else:
            PackagePackagerName = tag.getTag("Source").getTag("Packager").getTagData("Email")

        packageOf[PackageName] = PackagePackagerName

def parseXmlData(_index):
    packageOf = {}
    hasSpecFile = _index.getTag("SpecFile")
    if hasSpecFile:
        for i in _index.tags("SpecFile"):
            parent = i.getTag("Source")
            fillPackageDict(parent, hasSpecFile, packageOf)
    else:
        for parent in _index.tags("Package"):
            fillPackageDict(parent, hasSpecFile, packageOf)

    return packageOf

def printPackagesOf(owner, xmldata, escape=""):
    packages = xmldata[owner]
    packages.sort()
    for package in packages:
        print "%s%s" % (escape, package)

def getFullList(indexfile):
    xmldata = getXmlData(indexfile)
    packagers = parseXmlData(xmldata)

    return packagers

