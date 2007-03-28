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
import magic

import pisi.api as api
import pisi.context as ctx

from pisi.specfile import SpecFile

class InstallDirError(Exception):
    pass

def isBinary(_file):
    ms = magic.open(magic.MAGIC_NONE)
    ms.load()
    type = ms.file(_file)
    return type.startswith("ELF")

def getLinks(_file):
    links = []
    for link in os.popen("/usr/bin/ldd %s" % _file):
        link = link.strip()
        if "=>" in link:
            fn = link.split("=>")[1].split()[0]
            if not fn.startswith("("):
                links.append(fn)
    return links

def getBuildDependencies(folder, base=False):
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
            if getPackageComponent(package) == "system.base":
                if base:
                    packages.append(package)
            else:
                packages.append(package)
    
    api.finalize()
    return packages

def findMissingDependencies(_file, base=False):
    sf = SpecFile(_file)
    installDir = "/var/pisi/%s-%s-%s/install" % (sf.source.name, sf.getSourceVersion(), sf.getSourceRelease())
    if not os.path.isdir(installDir):
        raise InstallDirError, "Install directory does not exist."
    s1 = map(lambda x: x.package, sf.source.buildDependencies)
    s2 = getBuildDependencies(installDir, base)
    return list(set(s2) - set(s1))

def main(args):
    if len(args) < 2:
        print "Usage: %s path/to/pspec.xml"
        return 1
    
    try:
        deps = findMissingDependencies(args[1])
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
