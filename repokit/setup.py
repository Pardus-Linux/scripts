#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#

import sys
import os
import glob
import shutil
import parser

package = "repokit"
version = "0.1"

distfiles = """
    setup.py
    src/*.py
    po/repokit.pot
    po/*.po
"""

i18n_source_list = [ "src/repostats.py" ]

def update_messages():
    os.system("xgettext -o po/%s.pot %s" % (package, " ".join(i18n_source_list)))
    for item in os.listdir("po"):
        if item.endswith(".po"):
            os.system("msgmerge -q -o temp.po po/%s po/%s.pot" % (item, package))
            os.system("cp temp.po po/%s" % item)
    os.system("rm -f temp.po")

def make_dist():
    distdir = "%s-%s" % (package, version)
    list = []
    for t in distfiles.split():
        list.extend(glob.glob(t))
    if os.path.exists(distdir):
        shutil.rmtree(distdir)
    os.mkdir(distdir)
    for file_ in list:
        cum = distdir[:]
        for d in os.path.dirname(file_).split('/'):
            dn = os.path.join(cum, d)
            cum = dn[:]
            if not os.path.exists(dn):
                os.mkdir(dn)
        shutil.copy(file_, os.path.join(distdir, file_))
    os.popen("tar -czf %s %s" % (package + "-" + version + ".tar.gz", distdir))
    shutil.rmtree(distdir)

def install_file(source, prefix, dest):
    dest = os.path.join(prefix, dest)
    if os.path.islink(dest):
        os.unlink(dest)
    try:
        os.makedirs(os.path.dirname(dest))
    except:
        pass
    print "installing '%s' to '%s'" % (source, dest)
    os.system("cp %s %s" % (source, dest))

def install(args):
    if args == []:
        prefix = "/"
    else:
        prefix = args[0]
    
    install_file("src/ismail.py", prefix, "usr/bin/ismail.py")
    install_file("src/repostats.py", prefix, "usr/bin/repostats.py")
    
    for item in os.listdir("po"):
        if item.endswith(".po"):
            lang = item[:-3]
            dest = "usr/share/locale/%s/LC_MESSAGES/%s.mo" % (lang, package)
            try:
                os.makedirs(os.path.dirname(os.path.join(prefix, dest)))
            except:
                pass
            path = os.path.join(prefix, dest)
            print "compiling '%s' translation '%s'" % (lang, path)
            os.system("msgfmt po/%s -o %s" % (item, path))

def usage():
    print "setup.py install [prefix]"
    print "setup.py update_messages"
    print "setup.py dist"

def do_setup(args):
    if args == []:
        usage()
    
    elif args[0] == "install":
        install(args[1:])
    
    elif args[0] == "update_messages":
        update_messages()
    
    elif args[0] == "dist":
        make_dist()
    
    else:
        usage()

if __name__ == "__main__":
    do_setup(sys.argv[1:])
