#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import pisi
import subprocess

# Outputs the undefined symbols and unused direct dependencies of every installed package or the packages
# given through the command line.

def parse_unused(s):
    if s:
        return [l.strip() for l in s.replace("\t", "").split("\n") if l][1:]

def parse_undefs(s):
    if s:
        return [re.sub("^undefined symbol: (.*)\((.*)\)$", "\\1", l) \
                for l in s.replace("\t", "").split("\n") if l.startswith("undefined symbol:")]

if __name__ == "__main__":

    redirected = not sys.stdout.isatty()
    installdb = pisi.db.installdb.InstallDB()

    # Check only the given packages or all the installed packages
    if len(sys.argv) > 1:
        packages = sys.argv[1:]
    else:
        packages = pisi.api.list_installed()

    for p in packages:
        files = set([os.path.realpath("/"+f.path) for f in installdb.get_files(p).list if f.type == 'library' or f.type == 'executable'])

        for f in files:
            elf_type = os.popen("/usr/bin/readelf -h \"%s\" 2>/dev/null | grep \"^  Type:\" | gawk '{ print $2 }'" % f).read().strip()
            if elf_type in ["DYN", "EXEC"]:
                (stdout, stderr) = subprocess.Popen(["ldd", "-u", "-r", f], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

                undef_symbs = parse_undefs(stderr)
                unused_deps = parse_unused(stdout)

                if unused_deps or undef_symbs:
                    if redirected:
                        print "%s (%s):" % (p ,f)
                    else:
                        print "\x1b[32;01m%s \x1b[33;01m(%s):" % (p ,f)

                    if unused_deps:
                        if redirected:
                            print " Unused direct dependencies: \n  > %s" % "\n  > ".join(unused_deps)
                        else:
                            print " \x1b[31;01mUnused direct dependencies: \x1b[0m\n  > %s" % "\n  > ".join(unused_deps)

                    if undef_symbs:
                        if redirected:
                            print " Undefined symbols: \n  > %s" % "\n  > ".join(undef_symbs)
                        else:
                            print " \x1b[31;01mUndefined symbols: \x1b[0m\n  > %s" % "\n  > ".join(undef_symbs)
