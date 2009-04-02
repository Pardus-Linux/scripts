#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import pisi
import cPickle
from optparse import OptionParser


# Pisi DB instances
installdb = pisi.db.installdb.InstallDB()
packagedb = pisi.db.packagedb.PackageDB()
componentdb = pisi.db.componentdb.ComponentDB()



def generate_elf_cache(path):
    # Iterate over packages and generate ELF->Package mapping cache
    elf_to_package = {}
    for p in pisi.api.list_installed():
        print "Checking package %s.." % p,
        (dyns, execs) = get_elf_list(p)
        if len(dyns) > 0:
            elf_to_package.update(dict((k, p) for k in dyns))
            print " %d shared object(s) found and added to the mapping cache." % len(dyns)
        else:
            print " No shared object(s)."

    # Dump elf mapping dictionary for further usage
    print "Saving ELF mapping cache..",
    f = open(path, "w")
    cPickle.Pickler(f, protocol=2)
    cPickle.dump(elf_to_package, f, protocol=2)
    f.close()
    print "Done."

def load_elf_cache(path):
    d = {}
    if os.path.exists(path):
        print "Loading previously cached ELF mapping..",
        d = cPickle.Unpickler(open(path, "r")).load()
        print "Done."

    return d

def get_elf_list(package):
    # Eliminate symbolic links and return a list of all the files that needs to be investigated (ELF)
    files = [("/%s" % p.path) for p in installdb.get_files(package).list if os.path.exists("/%s" % p.path)]

    dyns = []
    execs = []

    for f in files:
        elf_type = os.popen("/usr/bin/readelf -h \"%s\" 2>/dev/null | grep \"^  Type:\" | gawk '{ print $2 }'" % f).read().strip()
        if elf_type == "DYN":
            dyns.append(f)
        elif elf_type == "EXEC":
            execs.append(f)
        else:
            continue

    return (dyns, execs)

def get_unused_deps(f):
    return [l.strip() for l in os.popen("/usr/bin/ldd -r -u \"%s\"" % f).readlines()[2:]]

def get_needed_objects(f):
    objs = [l.strip().split()[1] for l in os.popen("/usr/bin/objdump -p \"%s\" | grep 'NEEDED'" % f).readlines()]

    # Get full path to the objects

    filemap = {}
    for l in [_l for _l in os.popen("/usr/bin/ldd \"%s\" 2> /dev/null" % f).readlines() if "=>" in _l]:
        # Filter these special objects
        if "linux-gate" in l or "ld-linux.so" in l:
            continue
        ls = l.split("=>")
        filemap[ls[0].strip()] = ls[1].split(" (")[0].strip()

    for i in range(len(objs)):
        if filemap.has_key(objs[i]):
            objs[i] = filemap[objs[i]]

    return objs


if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-C", "--color",
                      action="store_true",
                      dest="colorize",
                      default=False,
                      help="Colorize output")

    parser.add_option("-s", "--show-system-base",
                      action="store_true",
                      dest="show_system_base",
                      default=False,
                      help="List system.base dependencies as well")

    parser.add_option("-c", "--component",
                      action="store",
                      dest="component",
                      help="Check dependencies only for the given component")

    parser.add_option("-g", "--generate-elf-cache",
                      action="store_true",
                      dest="generate_elf_cache",
                      default=False,
                      help="Generate elf cache for pisi packages in /var/lib/pisi")

    (options, packages) = parser.parse_args()

    if options.generate_elf_cache:
        generate_elf_cache("/var/lib/pisi/elfcache.db")
        sys.exit(0)

    if options.component:
        packages = componentdb.get_packages(options.component)



    elfs_to_check = []
    elf_to_package = {}
    real_deps = {}
    unused_deps = {}

    # Get them from pspecs
    actual_deps = {}


    # Create results directory
    if not os.path.isdir("results"):
        os.makedirs("results")

    pindex = 1
    total = len(packages)
    for p in packages:
        # Iterate over packages and find the dependencies
        print "(%d/%d) Finding out the runtime dependencies of %s.." % (pindex, total, p)

        needed = set()
        actual_deps = set()
        missing_deps = set()
        needed_deps = set()

        (dyns, execs) = get_elf_list(p)
        for elf in dyns+execs:
            needed.update(set(get_needed_objects(elf)))

        needed_deps = set([elf_to_package.get(k, '<Not found>') for k in needed.intersection(elf_to_package.keys())])
        try:
            actual_deps = set([d.package for d in packagedb.get_package(p).runtimeDependencies()])
            missing_deps = needed_deps.difference(actual_deps)
        except:
            print "** %s cannot be found in package DB!" % p
            continue

        # Create text file to hold dependency information
        f = open('results/%s' % p, 'w')
        f.write('Actual runtime dependencies in repository:\n-------------------------------------------\n')

        hede = lambda x: "  (system.base)" if x in systembase else ""

        f.write("\n".join(["%30s%s" % (l, hede(l)) for l in sorted(actual_deps)]))
        f.write('\n\nReal runtime dependencies found by depchecker:\n-----------------------------------------------\n')
        f.write("\n".join(["%30s%s" % (l, hede(l)) for l in sorted(needed_deps)]))
        f.write('\n\nMissing runtime dependencies found by depchecker:\n--------------------------------------------------\n')
        f.write("\n".join(["%30s%s" % (l, hede(l)) for l in sorted(missing_deps)]))
        f.close()

        pindex += 1
