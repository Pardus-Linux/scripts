#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 2.
# See the file http://www.gnu.org/copyleft/gpl.txt.
#
# Eren Türkay <turkay.eren@gmail.com>, 2007-06-11

import os
import sys
import pisi
import pisi.api as api
import pisi.context as ctx

class Ldd2Dep:
    def __init__(self, executable=None):
           self.exe = executable

    def init(self):
        if not os.path.exists(self.exe):
            return False
        # 33261 is for executable files. If it's not executable, return False
        elif os.stat(self.exe)[0] != 33261:
            return False
        else:
            api.init(write=False)
            return True

    def search_file(self, path):
        """
        Search file, if path doesn't exist or there's no matched result return False else return package name and its component"""

        if path and path.startswith("/"):
            path = path.lstrip("/")

        pkgname = ctx.filesdb.get_file(path)
        if pkgname:
            # If a package has been built with pspec.xml and it'is not in the repository, look for installed packages
            try:
                partof = ctx.packagedb.get_package(pkgname[0]).partOf
                return (pkgname[0], partof)
            except pisi.packagedb.Error:
                metadata, files, repo = pisi.api.info_name(pkgname[0], True)
                return(pkgname[0], metadata.package.partOf)
        else:
            return None

    def run(self, *args, **kwargs):
        ldd = os.popen("/usr/bin/ldd %s" % self.exe).read()
        parse = ldd.split("\t")

        package_list = {}
        # First value is blank, start from 1st value
        for line in parse[1:]:
            try:
                # parses library paths like; libxml.so.2 => /usr/lib/libxml.so.2
                path = line.split()[2]
            except IndexError:
                # glibc libraries are shown like; /lib/ld-linux.so.2. So it can't be parsed and error occured. Control if first veriable starts with "/"
                if line.split()[0].startswith("/"):
                    path = line.split()[0]
                else:
                    path = None

            search = self.search_file(path)
            if search:
                # If the package is already in package_list, update its library veriable. There may be two or more library which are in the same package.
                if not search[0] in package_list:
                    package_list[search[0]] = []
                    package_list[search[0]].append({'partof': search[1], 'libs': [path]})
                else:
                    package_list[search[0]][0]['libs'].append(path)

        print "%s libraries that the application uses found!\nsystem.base dependencies will be shown as yellow, others as green.\n" % len(package_list)

        for pkgname in package_list:
            pkg = package_list[pkgname][0]

            libs = ""
            for lib in pkg['libs']:
                libs += "%s, " % lib

            if kwargs['show_base']:
                if pkg['partof'] == 'system.base':
                    print "\033[33m* %s (%s)" % (pkgname, libs[:-2]) # do not get last , and blank char
                else:
                    print "\033[32m* %s (%s)" % (pkgname, libs[:-2])
            elif not kwargs['show_base'] and pkg['partof'] != 'system.base':
                    print "\033[32m* %s (%s)" % (pkgname, libs[:-2])

if len(sys.argv) >= 2:
    ldd2dep = Ldd2Dep(sys.argv[1])
    if not ldd2dep.init():
        print "There is no such file or it's not executable"
    else:
        if len(sys.argv) >= 3 and sys.argv[2] == '-s':
            ldd2dep.run(show_base=True)
        else:
            ldd2dep.run(show_base=False)
else:
    print """Usage: ldd2dep [executable] [-s]
       -s means that show system.base dependencies as well"""
