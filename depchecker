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


### Helper functions

def dump_report_per_packager(results, output_dir):
    # Get system.base packages
    system_base = componentdb.get_packages("system.base")

    def _format(x):
        if x in system_base:
            x = "%s (*)" % x

        return x

    packagers = {}

    for p in [k for k in results.keys() if len(results[k][2]) > 0]:
        # We have a package now
        author = packagedb.get_package(p).source.packager.email
        if packagers.has_key(author):
            packagers[author] += "%s\n  %s\n\n" % (p, "\n  ".join([_format(m) for m in results[p][2]]))
        else:
            packagers[author] = "%s\n  %s\n\n" % (p, "\n  ".join([_format(m) for m in results[p][2]]))

    # Create path if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for p in packagers.keys():
        filename = os.path.join(output_dir, p).replace(".", "_").replace("@", "_")
        open(filename, "w").write(packagers[p])


def print_results(results, hide_system_base, colorize):
    def _colorize(s):
        if colorize:
            if "B" in s[:2]:
                s = "\x1b[1;33m" + s + "\x1b[0m"    # system.base -> yellow
            elif s.startswith("-"):
                s = "\x1b[1;31m" + s + "\x1b[0m"    # missing dep -> red
            elif s.startswith("+"):
                s = "\x1b[0;32m" + s + "\x1b[0m"    # written dep -> green
            else:
                pass
        return s

    # Get system.base packages
    system_base = componentdb.get_packages("system.base")

    for p in results.keys():
        # Get the lists
        real_deps = results[p][0]
        actual_deps = results[p][1]
        missing_deps = results[p][2]

        deps = []

        # Filter system.base if requested
        if hide_system_base:
            real_deps = [d for d in real_deps if d not in system_base]

        for d in real_deps:
            marker = ""
            if d in actual_deps:
                marker += "+"
            elif d in missing_deps:
                marker += "-"
            else:
                marker += " "

            if d in system_base:
                marker += "B"
            else:
                marker += " "

            deps.append("%s  %s" % (marker, d))

        print "\n".join([_colorize(d) for d in sorted(deps)])


def generate_elf_cache(path):
    # Iterate over packages and generate ELF->Package mapping cache
    elf_to_package = {}
    for p in pisi.api.list_installed():
        print "Checking package %s.." % p,
        (dyns, execs) = get_elf_list(p, True)
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
        d = cPickle.Unpickler(open(path, "r")).load()

    return d

def get_elf_list(package, dont_trust_packager):
    # Eliminate symbolic links and return a list of all the files that needs to be investigated (ELF)
    def filter_file(f):
        if os.path.exists("/%s" % f.path):
            if dont_trust_packager:
                return True
            else:
                return (f.type == 'library' or f.type == 'executable')
        else:
            return False

    files = [("/%s" % p.path) for p in installdb.get_files(package).list if filter_file(p)]
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

def check_single_file(pspec):
    import tempfile

    # Create pisi object
    p = pisi.package.Package(pspec)

    dirname = tempfile.mkdtemp(prefix='depchecker-')
    p.extract_install(dirname)

    # Recurse in dirname to find ELF objects

    # Cleanup directory
    os.removedirs(dirname)


### Entry point

if __name__ == "__main__":

    if len(sys.argv) == 1:
        sys.argv.append("--help")

    parser = OptionParser()
    parser.add_option("-C", "--color",
                      action="store_true",
                      dest="colorize",
                      default=False,
                      help="Colorize output")

    parser.add_option("-s", "--hide-system-base",
                      action="store_true",
                      dest="hide_system_base",
                      default=False,
                      help="Hide system.base dependencies")

    parser.add_option("-c", "--component",
                      action="store",
                      dest="component",
                      help="Check dependencies only for the given component")

    parser.add_option("-a", "--all",
                      action="store_true",
                      dest="all_packages",
                      default=False,
                      help="Check dependencies for all the installed packages")

    parser.add_option("-g", "--generate-elf-cache",
                      action="store_true",
                      dest="generate_elf_cache",
                      default=False,
                      help="Generate elf cache for pisi packages in /var/lib/pisi")

    parser.add_option("-D", "--dont-trust-packager",
                      action="store_true",
                      dest="dont_trust_packager",
                      default=False,
                      help="Checks for all the files regardless of their types in pspec.xml. This will bring a performance penalty.")

    parser.add_option("-d", "--output-directory",
                      action="store",
                      dest="output_directory",
                      help="If given, the dependency informations will be written into the output directory")

    (options, packages) = parser.parse_args()

    if options.generate_elf_cache:
        generate_elf_cache("/var/lib/pisi/elfcache.db")
        sys.exit(0)

    # Load elf cache
    elf_to_package = load_elf_cache("/var/lib/pisi/elfcache.db")
    if not elf_to_package:
        print "You first have to create the elf cache using -g parameter."
        sys.exit(1)

    # Get packages from the given component
    if options.component:
        packages = componentdb.get_packages(options.component)
    elif options.all_packages:
        packages = installdb.list_installed()
        print "No package given, processing all %d installed packages.." % len(packages)
    elif packages and packages[0].endswith(".pisi") and os.path.exists(packages[0]):
        # Single pisi file mode. Will check the dependencies without using a full
        # mapping cache but only against the libraries installed on the system.
        # Kudos goes to Fatih and Gokcen :)
        check_single_file(packages[0])
        sys.exit(0)

    # Some loop counters here
    pindex = 1
    total = len(packages)

    if total > 1 and not options.output_directory:
        # Automatically fallback to directory output if there are multiple packages
        options.output_directory = "results"

    # Results dictionary: (package->deps)
    results = {}

    # Iterate over packages and find the dependencies
    for p in packages:

        needed = set()
        actual_deps = set()
        missing_deps = set()
        real_deps = set()

        (dyns, execs) = get_elf_list(p, options.dont_trust_packager)
        for elf in dyns+execs:
            needed.update(set(get_needed_objects(elf)))

        real_deps = set([elf_to_package.get(k, '<Not found>') for k in needed.intersection(elf_to_package.keys())])
        try:
            actual_deps = set([d.package for d in packagedb.get_package(p).runtimeDependencies()])
            missing_deps = real_deps.difference(actual_deps)
        except:
            print "**** %s cannot be found in package DB, probably the package has been deleted from the repository." % p
            continue

        # Push the informations to the results dictionary filtering the current package from the sets
        results[p] = (real_deps.difference([p]),
                      actual_deps.difference([p]),
                      missing_deps.difference([p]))

        # Increment the counter
        pindex += 1

    if options.output_directory:
        print "Saving results..",
        #save_data_into(options.output_directory, results, options.hide_system_base)
        dump_report_per_packager(results, options.output_directory)
        print "done."
    else:
        # The informations will be printed to the screen
        print_results(results, options.hide_system_base, options.colorize)

    sys.exit(0)
