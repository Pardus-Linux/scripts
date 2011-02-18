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

core_collections = [ "basic",
                     "context",
                     "genericrecommended",
                     "fontsrecommended",
                     "langczechslovak",
                     "langdutch",
                     "langfrench",
                     "langgerman",
                     "langitalian",
                     "langpolish",
                     "langportuguese",
                     "langspanish",
                     "langenglish",
                     "latex",
                     "latex3",
                     "latexrecommended",
                     "luatex",
                     "mathextra",
                     "metapost",
                     "texinfo",
                     "xetex"]

other_collections = [ "bibtexextra",
                      "fontsextra",
                      "formatsextra",
                      "games",
                      "genericextra",
                      "htmlxml",
                      "humanities",
                      "langcjk",
                      "langcyrillic",
                      "langgreek",
                      "latexextra",
                      "music",
                      "pictures",
                      "plainextra",
                      "pstricks",
                      "publishers",
                      "science"]
# Create several packages


def download_module(module_names, collection=False):
    # Download modules
    mirror = "http://mirror.informatik.uni-mannheim.de/pub/mirrors/tex-archive/systems/texlive/tlnet/archive/"

    for module in module_names:
        if collection:
            module = "collection-" + module
        os.system("wget %s%s.tar.xz" % (mirror, module))

def extract_lxma():
    # Extract all compressed packages, for future use
    for collection in os.listdir("."):
        if collection.endswith("tar.xz"):
            os.system("tar Jxf %s" % collection)


def extract_module(collection_name):
    # Extract module information from the collection tarballs

    # Remove .tar.xz extension, we could also use os.path.splitext()
    collection_name = collection_name[:-7]

    module_names = []
    for line in open("tlpkg/tlpobj/%s.tlpobj" % collection_name, "r").readlines():
        if "depend" in line:
            line = line.strip().split(" ")
            if not line[1].startswith("collection") and not line[1].startswith("hyphen"):
                module_names.append(line[1])
        elif "revision" in line:
            line = line.strip().split(" ")
            revision = line[1]

    return (module_names, revision)


# Create dir for packaging
#package_name = "texlive_" + name + "_2011_" + revision

## Extract and remove archive packages
#if not os.path.exists(package_name):
#    os.mkdir(package_name)

#for module in module_names:
#    os.system("tar Jxf %s.tar.xz -C %s" % (module,package_name))

## Compress files to tar.bz2 package
#print "Compressing files ..."
#os.system("tar cjf %s.tar.bz2 %s" % (package_name,package_name))

#def cleanup():
#    # Remove unused files
#    print "Removing unused files ..."
#    shutil.rtree(package_name)
#    shutil.rmtree("tlpkg")

#        os.remove(module + ".tar.xz")
#    # Remove collection tarball, it should not interrupt with module tarballs later
#    print "Removing base collection file ..."
#    os.remove(collection_package)


def main():
    download_module(core_collections , True)
    extract_lxma()

    module_names = []
    for collection in os.listdir("."):
        if collection.endswith("tar.xz"):
            module, revsion = extract_module(collection)
            module_names.extend(module)

    print module_names
#    download_module(module_names, False)

if __name__ == "__main__":
    sys.exit(main())



