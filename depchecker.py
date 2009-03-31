#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import pisi
import subprocess

installdb = pisi.db.installdb.InstallDB()

def is_elf_object(f):
    lines = os.popen("/usr/bin/readelf -h %s 2>&1" % f).readlines()
    if "Not an ELF file" in lines[0]:
        return False
    else:
        for line in [l.strip() for l in lines[1:]]:
            if "Type:" in line:
                if line.split()[1] in ["DYN", "EXEC"]:
                    return True
        return False

def get_elf_list(package):
    # Eliminate symbolic links and return a list of all the files that needs to be investigated (ELF)
    return [("/%s" % p.path) for p in installdb.get_files(package).list if os.path.exists("/%s" % p.path) and \
                                                                           not os.path.islink("/%s" % p.path) and \
                                                                           is_elf_object("/%s" % p.path)]

def get_unused_deps(f):
    return [l.strip() for l in os.popen("/usr/bin/ldd -u %s" % f).readlines()[2:]]

def get_needed_objects(f):
    objs = [l.strip().split()[1] for l in os.popen("/usr/bin/objdump -p %s | grep 'NEEDED'" % f).readlines()]

    # Get full path to the objects

    filemap = {}
    for l in [_l for _l in os.popen("/usr/bin/ldd %s" % f).readlines() if "=>" in _l]:
        if "linux-gate" in l or "ld-linux.so" in l:
            continue
        ls = l.split("=>")
        filemap[ls[0].strip()] = ls[1].split(" (")[0].strip()

    for i in range(len(objs)):
        if filemap.has_key(objs[i]):
            objs[i] = filemap[objs[i]]

    return objs


if __name__ == "__main__":

    packages = []

    if len(sys.argv) > 1:
        packages = sys.argv[1:]
    else:
        print "Gathering package list...",
        packages = pisi.api.list_installed()
        print "Done, found %d installed packages.\n\n" % len(packages)

    real_deps = {}
    unused_deps = {}

    # Get them from pspecs
    actual_deps = {}

    # Iterate over packages and
    for p in packages:
        print "Checking package %s.." % p
        files = get_elf_list(p)
        print "  %d ELF object(s) found." % len(files)

        unused_tmp = []
        real_tmp = []
        for f in files:
            unused_tmp.extend(get_unused_deps(f))
            real_tmp.extend(get_needed_objects(f))

        unused_deps[p] = list(set(unused_tmp[:]))
        real_deps[p] = list(set(real_tmp[:]))

        #print unused_deps[p]

        print "\nReal dependencies are:\n"
        print "\n".join(real_deps[p])
        break



