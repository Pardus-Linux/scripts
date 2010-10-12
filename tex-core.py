#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Fatih Arslan - 08.2010
Download ebuild and build tarball's for specified tex language package

Usage: ./tex-lang.py texlive-langfoo
i.e: "./tex-lang.py texlive-langafrican" creates the tarball lang-african-2009.tar.bz2
Thah tarball will be used for pisi packaging (pspec.xml)
"""

import os
import sys
import commands
import shutil

# Create variables for package
package = "texlive-core"
version = "2009"
version_release = "20091107"
packagename = package + "-" + version_release

# Download ebuild
gentoo_adress = "http://sources.gentoo.org/cgi-bin/viewvc.cgi/gentoo-x86/app-text/%s/%s-%s.ebuild" % (package,package,version)
os.system("wget %s" % gentoo_adress)

# Read ebuild, extract the module infos and save them to module_names
ebuild = package + "-" + version + ".ebuild"
module_names = []
for line in open(ebuild, "r").readlines():
    if "TL_CORE_BINEXTRA_MODULES="  in line:
        line = line.replace('"','') # Remove double quotes
        line = line.strip().split("=") # Split module names
        line = line[1].split(" ")
        module_names.extend(line)

    if "TL_CORE_BINEXTRA_DOC_MODULES="  in line:
        line = line.replace('"','')
        line = line.strip().split("=")
        line = line[1].split(" ")
        module_names.extend(line)

    if "TL_CORE_BINEXTRA_SRC_MODULES="  in line:
        line = line.replace('"','')
        line = line.strip().split("=")
        line = line[1].split(" ")
        module_names.extend(line)

    if "TL_CORE_EXTRA_MODULES="  in line:
        line = line.replace('"','') # Remove double quotes
        line = line.strip().split("=") # Split module names
        line = line[1].split(" ")
        module_names.extend(line)

    if "TL_CORE_EXTRA_DOC_MODULES="  in line:
        line = line.replace('"','')
        line = line.strip().split("=")
        line = line[1].split(" ")
        module_names.extend(line)

    if "TL_CORE_EXTRA_SRC_MODULES="  in line:
        line = line.replace('"','')
        line = line.strip().split("=")
        line = line[1].split(" ")
        module_names.extend(line)

# Download each modules from the module_names list
for module in module_names:
   os.system("wget http://ftp.linux.org.tr/gentoo/distfiles/texlive-module-%s-2009.tar.xz" % module)

#os.system("wget ftp://tug.org/texlive/historic/2009/texlive-%s-source.tar.xz" % version_release)

# Create dir for packaging
if not os.path.exists(packagename):
    os.mkdir(packagename)

# Extract and remove archive packages
for file in os.listdir("."):
    if file.endswith("tar.xz"):
        os.system("tar Jxf %s -C %s" % (file,packagename))
#        os.remove(file)

# Compress files to tar.bz2 package
print "Compressing files ..."
os.system("tar cjf %s.tar.bz2 %s" % (packagename,packagename))

# Clean ebuild and files
print "Removing uneccesary files ..."
shutil.rmtree(packagename)
os.remove(ebuild)



