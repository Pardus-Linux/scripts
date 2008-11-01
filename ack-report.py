#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob

from pisi.package import Package

# Generates detailed statistics about pisi files

test_path = "/var/cache/pisi/packages-test/"
stable_path = "/var/cache/pisi/packages/"

def get_package_name(filename):
    return filename.rstrip(".pisi").rsplit("-", 3)[0]

def get_package_build(filename):
    return int(filename.rstrip(".pisi").rsplit("-", 3)[3])

def get_package_release(filename):
    return int(filename.rstrip(".pisi").rsplit("-", 3)[2])

def get_latest_release(package):
    """ Returns the file name corresponding to the
    latest release of the package 'package_name' found in 'path'."""

    file_list = glob.glob1(stable_path, "%s-[0-9]*-[0-9]*-[0-9]*.pisi" % get_package_name(package))
    file_list.sort(cmp=lambda x,y:get_package_build(x)-get_package_build(y), reverse=True)
    return get_package_release(file_list[0])

def main(file_list):

    files = open(file_list, "rb").read().strip().split("\n")
    print "Total number of packages in '%s': %d" % (file_list, len(files))

    d = {}

    for f in files:
        if not os.path.exists(os.path.join(test_path, f)):
            continue

        name = get_package_name(f)
        current_release = get_package_release(f)
        stable_release = get_latest_release(f)

        metadata = Package(os.path.join(test_path, f)).get_metadata()
        packager = "%s <%s>" % (metadata.source.packager.name, metadata.source.packager.email.replace('@', '_at_'))

        history = metadata.package.history[0:current_release-stable_release]
        if history:
            for h in history:
                changes += """\
                        Package release: %s\
                        Package version: %s\
                        Update type: %s\
                        Update time: %s\
                        Comments:\n%s\
                        Modifier: %s\n\n""" % (h.release, h.version, h.type, h.date,
                                           "\n".join([l.strip() for l in h.comment.split('\n')]),
                                           "%s <%s>" % (h.name, h.email.replace('@', '_at_')))

        else:
            changes = "No changes between two packages.\n\n"

        d[name] = [current_release, stable_release, packager, changes]

    for p in d.keys():
        print "\nName: %s" % p
        print "Packager: %s" % d[p][2]
        print "-"*55
        print d[p][3]

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print "Usage: %s <file_list>" % sys.argv[0]
        sys.exit(1)

    else:
        file_list = sys.argv[1]
        if not os.path.exists(file_list):
            print "%s doesn't exists!" % file_list
            sys.exit(1)

        sys.exit(main(file_list))



