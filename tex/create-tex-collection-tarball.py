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

# TeXLive collections in the texlive-core package:
# (corresponds to the "medium scheme" of TeX Live)
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

core_collections.extend(["langhungarian", "langlithuanian"])

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

def extract_lxma(module=False):
    # Extract all compressed packages, for future use
    if not module:
        for collection in os.listdir("."):
            if collection.endswith("tar.xz"):
                os.system("tar Jxf %s" % collection)
    else:
        os.system("tar Jxf %s.tar.xz" % module)




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

def collection_with_runfiles_pattern(collection_name):
    runfiles = []
    runfiles_found = False
    for line in open("tlpkg/tlpobj/%s.tlpobj" % collection_name, "r").readlines():
        if "runfiles" in line:
            runfiles_found = True
            continue

        if runfiles_found:
            if line.startswith(" "):
                runfiles.append(line.strip())

    module_names = []
    for line in runfiles:
        if "texmf-dist" in line:
            module_names.append(collection_name)

    return list(set(module_names))
#    return module_names


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
    download_module(["binextra", "fontutils"] , True)
    extract_lxma()

    core_modules = []
    extra_modules = []
    for collection in os.listdir("."):
        if collection.endswith("tar.xz"):

            module, revsion = extract_module(collection)
            core_modules.extend(module)

            # save the modules to look for runfile patterns later
            if "binextra" in collection or "fontutils" in collection:
                extra_modules.extend(module)

            os.remove(collection)

    download_module(core_modules, False)
    print core_modules
    print extra_modules

#    extra_modules = ['a2ping', 'asymptote', 'bibtex8', 'bibtexu', 'bundledoc', \
#                     'chktex', 'ctie', 'cweb', 'de-macro', 'detex', 'dtl', 'dvi2tty', 'dviasm', \
#                     'dvicopy', 'dvidvi', 'dviljk', 'dvipng', 'dvipos', 'dvisvgm', 'findhyph', \
#                     'fragmaster', 'installfont', 'lacheck', 'latex2man', 'latexdiff', 'latexmk', \
#                     'listings-ext', 'mkjobtexmf', 'patgen', 'pdfcrop', 'pdfjam', 'pdftools', \
#                     'pkfix', 'pkfix-helper', 'purifyeps', 'seetexk', 'sty2dtx', 'synctex', \
#                     'texcount', 'texdiff', 'texdirflatten', 'texdoc', 'texloganalyser', 'texware', \
#                     'tie', 'tpic2pdftex', 'web', 'xindy', 'accfonts', 'afm2pl', 'epstopdf', \
#                     'fontware', 'lcdftypetools', 'ps2pkm', 'pstools', 'psutils', 'dvipsconfig', \
#                     'fontinst', 'fontools', 'getafm', 't1utils', 'ttfutils']

    module_with_runfiles = []
    for module in extra_modules:
        extract_lxma(module)

        module = collection_with_runfiles_pattern(module)
        module_with_runfiles.extend(module)

    print module_with_runfiles


if __name__ == "__main__":
    sys.exit(main())



