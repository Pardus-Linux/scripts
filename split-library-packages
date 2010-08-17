#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import pisi
import time

def is_in_system_base(package_name):
    """Checks whether the given package is in system.base."""
    packages = []
    cdb = pisi.db.componentdb.ComponentDB()
    for repo in pisi.db.repodb.RepoDB().list_repos():
        try:
            packages.extend(cdb.get_packages('system.base', repo))
        except:
            pass

    return package_name in packages

def split_translations(package_name):
    addition = """\
    <Package>
        <Name>%s-devel</Name>
        <Summary xml:lang="tr">%s için geliştirme dosyaları</Summary>
    </Package>
"""

    new_translations = ""

    with open("translations.xml", "r") as _file:
        for line in _file:
            if "</PISI>" in line:
                # Add new translations
                new_translations += "\n%s" % (addition % (package_name, package_name))
            new_translations += line

    open("translations.xml", "w").write(new_translations)


def split_devel_package(package_name):
    release = """\
    <History>
        <Update release="%s">
            <Date>%s</Date>
            <Version>%s</Version>
            <Comment>Split devel package.</Comment>
            <Name>%s</Name>
            <Email>%s</Email>
        </Update>
    """

    addition = """\
    <Package>
        <Name>%s-devel</Name>
"""

    if is_in_system_base(package_name):
        addition += """\
        <PartOf>system.devel</PartOf>
"""

    addition += """\
        <Summary>Development files for %s</Summary>
        <RuntimeDependencies>
            <Dependency release="%s">%s</Dependency>
        </RuntimeDependencies>
        <Files>
%s
            <!-- FIXME: Remove this if not necessary -->
            <Path fileType="man">/usr/share/man/man3</Path>
        </Files>
    </Package>

"""

    pspec = pisi.specfile.SpecFile("pspec.xml")
    next_release = int(pspec.history[0].release)+1
    current_version = pspec.history[0].version

    packager_name, packager_email = get_and_save_user_info()

    files = []
    new_pspec = ""

    with open("pspec.xml", "r") as _file:
        for line in _file:
            if 'fileType="header"' in line or \
                '/pkgconfig' in line:
                    files.append(line.rstrip("\n"))
                    continue
            if "<History>" in line:
                # Add the new package here
                new_pspec += addition % (package_name,
                                         package_name,
                                         next_release,
                                         package_name,
                                         "\n".join(files))
                # Bump package
                new_pspec += release % (next_release,
                                        time.strftime("%Y-%m-%d"),
                                        current_version,
                                        packager_name,
                                        packager_email)
                continue
            new_pspec += line


    open("pspec.xml", "w").write(new_pspec)

def split(package_name):
    split_translations(package_name)
    split_devel_package(package_name)

def usage():
    print """\
    Usage: %s        if in a source package's directory
           %s DIR    where DIR is a source package's directory.""" % (sys.argv[0], sys.argv[0])
    return 1

def get_and_save_user_info():
    name = "PACKAGER_NAME"
    email = "PACKAGER_EMAIL"

    conf_file = os.path.expanduser("~/.packagerinfo")
    if os.path.exists(conf_file):
        # Read from it
        name, email = open(conf_file, "r").read().strip().split(",")

    else:
        print "Please enter your full name as seen in pspec files"
        name = raw_input("> ")
        print "Please enter your e-mail as seen in pspec files"
        email = raw_input("> ")
        print "Saving packager info into %s" % conf_file

        open(conf_file, "w").write("%s,%s" % (name, email))

    return name, email

def main():
    if len(sys.argv) < 2:
        # Assuming that we are in a source package's directory
        if not os.path.exists("pspec.xml"):
            return usage()
        else:
            split(os.path.basename(os.getcwd()))

    else:
        package = sys.argv[1].rstrip("/")

        if os.path.isdir(package) and not os.path.exists(os.path.join(package, "pspec.xml")):
            return usage()
        else:
            os.chdir(package)
            split(os.path.basename(package))

if __name__ == "__main__":
    sys.exit(main())
