#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, 2007 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

import pisi.specfile
import pisi.dependency
import time

# Global constants
Name = "Furkan Duman"
Email = "coderlord@gmail.com"
Comment = "Version bump"
MirrorURI = "mirrors://kde/unstable/%s/src/kde-l10n"

class PspecUpdater:
    header = '''<?xml version="1.0" ?>
<!DOCTYPE PISI SYSTEM "http://www.pardus.org.tr/projeler/pisi/pisi-spec.dtd">'''

    def __init__(self, filename):
        self.spec = pisi.specfile.SpecFile(filename)

    def getSourceName(self):
        return self.spec.source.name

    def getArchive(self):
        return self.spec.source.archive

    def updateDependencyVersionFrom(self, dependency):
        for package in self.spec.packages:
            for dep in package.packageDependencies:
                if dep.package == dependency.package:
                    dep.versionFrom = dependency.versionFrom

    def getLastRelease(self):
        return int(self.spec.getSourceRelease())

    def addHistory(self, history):
        self.spec.history.insert(0, history)

    def pspecXML(self):
        # Daha iyi bir yöntem bilen lütfen söylesin
        self.spec.write("/dev/null", True)
        return "%s\n%s" % (self.header, self.spec.doc.toPrettyString())

    def write(self, filename):
        f = open(filename, "w")
        try:
            f.write(self.pspecXML())
        finally:
            f.close()

def getArchiveType(filename):
    type = ""
    if filename.endswith("bz2"):
        type = "tarbz2"
    elif filename.endswith("gz"):
        type = "targz"
    elif filename.endswith("zip"):
        type = "zip"
    return type

update_dict = {}

''' Parses sha1sum file and fills update_dict dictionary '''
def parseSha1sumList(filename):
    f = open(filename, "r")
    try:
        for line in f.readlines():
            data = line.strip().split()
            key = data[1][:data[1].rindex("-")]
            update_dict[key] = data
    finally:
        f.close()

''' Updates pspec.xml '''
def update(filename, version):
    updater = PspecUpdater(filename)

    source = updater.getSourceName()

    if len(sys.argv) == 4:
        try:
            sha1sum = update_dict[source][0]
            archiveFilename = update_dict[source][1]
        except:
            print "Unable to find %s package in sha1sum list!" % source
            return
    else:
        oldArchive = updater.getArchive().uri[updater.getArchive().uri.rindex("/") + 1:]
        archiveFilename = oldArchive.replace(updater.spec.history[0].version, version)

    ''' Update archive '''
    archive = updater.getArchive()
    archive.uri = "%s/%s" % (MirrorURI % version, archiveFilename)
    archive.type = getArchiveType(archiveFilename)
    if len(sys.argv) == 4:
        archive.sha1sum = sha1sum

    ''' Update dependency versions '''
    dependency = pisi.dependency.Dependency()
    dependency.package = "kdelibs"
    dependency.versionFrom = version
    updater.updateDependencyVersionFrom(dependency)

    ''' Update history '''
    history = pisi.specfile.Update()
    history.release = str(updater.getLastRelease() + 1)
    history.version = version
    history.date = time.strftime("%Y-%m-%d")
    history.comment = Comment
    history.name = unicode(Name)
    history.email = Email
    updater.addHistory(history)
    updater.write(filename)

    if len(sys.argv) == 3:
        updater = PspecUpdater(filename)
        archive = updater.getArchive()
        print "Fetching source: %s ..." % archiveFilename
        pisi.api.build_until(filename, "fetch")
        print "Source fetched"
        archive.sha1sum = sha.new(file("/var/cache/pisi/archives/%s" % archiveFilename).read()).hexdigest()
        updater.write(filename)

    print "%s updated..." % source

import os
import sys
import pisi
import sha

if __name__ == "__main__":
    if len(sys.argv) > 4 or len(sys.argv) < 3:
        print "Usage: %s folder version [sha1sum.list]" % sys.argv[0]
        print "Example: %s /home/furkan/svn 3.6.6 sha1sum.list\n\t If sha1sum list is not given, source files are downloaded and shasums are computed from downloaded files. In this case script should be run with root privileges." % sys.argv[0]
        sys.exit()

    folder = sys.argv[1]
    version = sys.argv[2]
    if len(sys.argv) == 4:
        parseSha1sumList(sys.argv[3])

    for root, dirs, files in os.walk(folder):
        if "pspec.xml" in files:
            update(os.path.join(root, "pspec.xml"), version)
        if ".svn" in dirs:
            dirs.remove(".svn")
