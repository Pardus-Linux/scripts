#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Download collection, parse TLPOBJ files and creates tarball for pisi files
Collections are disjoint, that means no collections conflicts with another
"""

import os
import sys
import commands
import shutil

# List of mirrors are: http://www.ctan.org/tex-archive/CTAN.sites
mirror = "http://mirror.informatik.uni-mannheim.de/pub/mirrors/tex-archive/systems/texlive/tlnet/archive/"

# Create several packages
name = sys.argv[1]
collection_name = "collection-" + name
collection_package = sys.argv[1] + ".tar.xz"
collection_url = mirror + collection_package

# Donload and extract main collection tarball
os.system("wget %s" % collection_url)
for collection in os.listdir("."):
    if collection.endswith("tar.xz"):
        os.system("tar Jxf %s" % collection)

# Remove collection tarball, it should not interrupt with module tarballs later
print "Removing base collection file ..."
os.remove(collection_package)

# Extract module information from the collection tarball
module_names = []
for line in open("tlpkg/tlpobj/%s.tlpobj" % collection_name, "r").readlines():
    if "depend" in line:
        line = line.strip().split(" ")
        if not line[1].startswith("collection"):
            module_names.append(line[1])
    elif "revision" in line:
        line = line.strip().split(" ")
        revision = line[1]

# Download each modules from the module_names list
for module in module_names:
   os.system("wget %s/%s" % (mirror, module))

# Create dir for packaging
package_name = "texlive"
if not os.path.exists(packagename):
    os.mkdir(packagename)

# Extract and remove archive packages
for module in os.listdir("."):
    if module.endswith("tar.xz"):
        os.system("tar Jxf %s -C %s" % (module,packagename))
        os.remove(module)

# Compress files to tar.bz2 package
#print "Compressing files ..."
#os.system("tar cjf %s.tar.bz2 %s" % (packagename,packagename))



