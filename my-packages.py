#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from pisi.specfile import SpecFile

# Enter your email
maintainer_email = ""

# Enter path to devel (e.g. /home/user/pardus/devel)
devel_path = ""


def get_specs(path):
    specs = []
    for root, dirs, files in os.walk(path):
        if "pspec.xml" in files:
            specs.append(root)
        if ".svn" in dirs:
            dirs.remove(".svn")

    return specs

if __name__ == "__main__":

    if not maintainer_email or not devel_path:
        print "Please write the necessary informations into %s" % sys.argv[0]
        sys.exit(1)

    specs = get_specs(devel_path)
    packages = []

    for s in specs:
        specfile = SpecFile(s + '/pspec.xml')
        email = specfile.source.packager.email
        if email == maintainer_email and email not in packages:
            packages.append(s.partition(devel_path)[-1])

    print "A total of %d packages are maintained by %s:\n" % (len(packages), maintainer_email)
    print "\n".join(packages)


