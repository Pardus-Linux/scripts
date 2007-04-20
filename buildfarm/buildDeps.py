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
import os.path

import piksemel

import pisi.api as api
import pisi.context as ctx

from pisi.specfile import SpecFile

class InstallDirError(Exception):
    pass

def isBinary(_file):
    ret = os.popen("/usr/bin/file -b \"%s\"" % _file).read()
    return ret.startswith("ELF")

def getLinks(_file):
    links = []
    for link in os.popen("/usr/bin/ldd %s" % _file):
        link = link.strip()
        if "=>" in link:
            fn = link.split("=>")[1].split()[0]
            if not fn.startswith("("):
                links.append(fn)
    return links

def getBuildDependencies(folder):
    links = []
    for root, dirs, files in os.walk(folder):
        for _file in files:
            fn = os.path.join(root, _file)
            if isBinary(fn):
                for link in getLinks(fn):
                    if link not in links:
                        links.append(os.path.realpath(link))
    
    api.init(comar=False, database=True, write=False)
    
    def getPackageComponent(pack):
        return ctx.packagedb.get_package(pack).partOf
    
    def getFileOwner(_file):
        if not ctx.filesdb.has_file(_file):
            return None
        return ctx.filesdb.get_file(_file)[0]
    
    packages = []
    unowned = []
    for _file in links:
        package = getFileOwner(_file[1:])
        if not package:
            unowned.append(_file)
            continue
        if package not in packages:
            packages.append(package)
    
    api.finalize()
    return packages

def getSourceIndex(indexfile):
    if indexfile.endswith(".bz2"):
        import bz2
        data = file(indexfile).read()
        data = bz2.decompress(data)
        doc = piksemel.parseString(data)
    else:
        doc = piksemel.parse(indexfile)
    sources = {}
    base = []
    for tag in doc.tags("SpecFile"):
        name = tag.getTag("Source").getTagData("Name")
        sources[name] = {}
        version = tag.getTag('History').getTag('Update').getTagData('Version')
        release = tag.getTag('History').getTag('Update').getAttribute('release')
        sources[name]["version"] = "%s-%s" % (version, release)
        sources[name]["deps"] = []
        deps = tag.getTag("Source").getTag("BuildDependencies")
        if deps:
            sources[name]["deps"] = map(lambda x: x.firstChild().data(), deps.tags("Dependency"))
        if tag.getTag("Source").getTagData("PartOf") in ["system.base", "system.devel"]:
            base.append(name)
    sources["__base__"] = base
    return sources

def getAllDependencies(source_index, package_name):
    deps = set()
    deps.add(package_name)
    def collect(name):
        p = source_index[name]
        for item in p["deps"]:
            deps.add(item)
            collect(item)
    collect(package_name)
    deps.update(source_index["__base__"])
    return deps

def findMissingDependencies(source_index, package_name):
    installDir = "/var/pisi/%s-%s/install" % (package_name, source_index[package_name]["version"])
    if not os.path.isdir(installDir):
        raise InstallDirError, "Install directory does not exist."
    s1 = getAllDependencies(source_index, package_name)
    s2 = getBuildDependencies(installDir)
    return list(set(s2) - set(s1))

def main(args):
    if len(args) < 3:
        print "Usage: %s package path/to/pisi-index.xml path/to/pisi-index.xml" % args[0]
        return 1
    
    package_name = args[1]
    
    source_index = []
    for i in args[2:]:
        source_index.append(getSourceIndex(i))

    try:
        deps = findMissingDependencies(source_index, package_name)
    except InstallDirError:
        print "Install directory does not exist."
        return 1
    
    if deps:
        print "Missing build dependencies:"
        for package in deps:
            print "  %s" % package
    else:
        print "All build dependencies are on specfile."
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
