#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import pisi
import cPickle

installdb = pisi.db.installdb.InstallDB()
packagedb = pisi.db.packagedb.PackageDB()

def get_elf_list(package):
    # Eliminate symbolic links and return a list of all the files that needs to be investigated (ELF)
    files = [("/%s" % p.path) for p in installdb.get_files(package).list if os.path.exists("/%s" % p.path) and \
                                                                            (p.type == 'library' or p.type == 'executable') and \
                                                                            not os.path.islink("/%s" % p.path)]
    dyns = []
    execs = []

    for f in files:
        lines = os.popen("/usr/bin/readelf -h \"%s\" 2>&1" % f).readlines()
        if "Not an ELF file" in lines[0]:
            continue
        else:
            for line in [l.strip() for l in lines[1:]]:
                if "Type:" in line:
                    type = line.split()[1]
                    if type == "DYN":
                        dyns.append(f)
                    elif type == "EXEC":
                        execs.append(f)
                    else:
                        continue

    return (dyns, execs)

def get_unused_deps(f):
    return [l.strip() for l in os.popen("/usr/bin/ldd -u \"%s\"" % f).readlines()[2:]]

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

    elfs_to_check = []
    elf_to_package = {}
    real_deps = {}
    unused_deps = {}

    # Get them from pspecs
    actual_deps = {}

    # Gather the list of installed packages
    print "Gathering package list...",
    packages = pisi.api.list_installed()
    print "Done, found %d installed packages." % len(packages)

    if os.path.exists("elf.db"):
        print "Loading previously cached ELF mapping..",
        elf_to_package = cPickle.Unpickler(open("elf.db", "r")).load()
        print "Done."

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
            f.write('Actual runtime dependencies in repository:\n-------------------------------------------\n\n')
            f.write("\n".join(sorted(actual_deps)))
            f.write('\nReal runtime dependencies found by depchecker:\n-----------------------------------------------\n\n')
            f.write("\n".join(sorted(needed_deps)))
            f.write('\nMissing runtime dependencies found by depchecker:\n--------------------------------------------------\n\n')
            f.write("\n".join(sorted(missing_deps)))
            f.close()

            pindex += 1

    else:
        # Iterate over packages and generate ELF->Package mapping cache
        for p in packages:
            print "Checking package %s.." % p,
            (dyns, execs) = get_elf_list(p)
            elfs_to_check.extend(dyns)
            elfs_to_check.extend(execs)
            if len(dyns) > 0:
                elf_to_package.update(dict((k, p) for k in dyns))
                print " %d shared object(s) found and added to the mapping cache." % len(dyns)
            else:
                print " No shared object(s)."

        # Dump elf mapping dictionary for further usage
        print "Saving ELF mapping cache..",
        f = open("elf.db", "w")
        cPickle.Pickler(f, protocol=2)
        cPickle.dump(elf_to_package, f, protocol=2)
        f.close()
        print "Done."
