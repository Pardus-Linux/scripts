#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Download collection, parse TLPOBJ files and creates tarball for pisi files
Collections are disjoint, that means no collections conflicts with another
"""

import os
import sys
import glob
import time
import shutil
import tarfile
import commands

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

core_collections.extend(["langhungarian", "langlithuanian", "bibtexextra", "fontutils"])

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

def download_tarxz(package, isCollection=False, dl_location="."):
    # Download modules
    mirror = "http://mirror.informatik.uni-mannheim.de/pub/mirrors/tex-archive/systems/texlive/tlnet/archive/"

    if isCollection:
        package = "collection-" + package

    os.system("wget %s%s.tar.xz -P %s" % (mirror, package, dl_location))

def extract_tarxz(module, extract_loc="."):
    # Extract all compressed packages, for future use
    os.system("tar Jxfv %s/%s -C %s" % (extract_loc, module, extract_loc))

def parse_modules(build_dir):
    modules = []

    for collection in glob.glob("%s/tlpkg/tlpobj/collection-*.tlpobj" % build_dir):
        # save the modules to look for runfile patterns later
        for line in open(collection, "r").readlines():
            if "depend" in line:
                line = line.strip().split(" ")
                if not line[1].startswith("collection") and not line[1].startswith("hyphen"):
                    modules.append(line[1])
            elif "revision" in line:
                line = line.strip().split(" ")
                # For future need
                revision = line[1]

    return modules

def collection_with_runfiles_pattern(build_dir):
    runfiles_found = False

    matched_modules = []
    for collection in glob.glob("%s/tlpkg/tlpobj/*.tlpobj" % build_dir):
        # gives us the "texdiff" from the "texlive_core/tlpkg/tlpobj/texdiff.tlpobj" string
        module_name = os.path.basename(os.path.splitext(collection)[0])

        for line in open(collection, "r").readlines():
            if "runfiles" in line:
                runfiles_found = True
                continue

            runfiles = []
            if runfiles_found:
                if line.startswith(" "):
                    runfiles.append(line.strip())

        for line in runfiles:
            if "texmf-dist" in line or "RELOC" in line:
                matched_modules.append(module_name)

    return list(set(matched_modules))

def parse_tlpobj_other(build_dir):
    modules = []

    for collection in glob.glob("%s/tlpkg/tlpobj/collection-*.tlpobj" % build_dir):
        # save the modules to look for runfile patterns later
        module_name = os.path.basename(os.path.splitext(collection)[0])

        for line in open(collection, "r").readlines():
            if "depend" in line:
                line = line.strip().split(" ")

                # These packages are included to texlive-core, don't ship with them
                if line[1] == "pgf" and module_name == "collection-pictures":
                    continue

                if line[1] == "iftex" and module_name == "collection-genericextra":
                    continue

                if (line[1] == "iftex" or line[1] == "ruhyphen") and module_name == "collection-langcyrillic":
                    continue

                # Finally add the dependency to the list
                if not line[1].startswith("collection") and not line[1].startswith("hyphen"):
                    modules.append(line[1])

    return modules

def create_archive_file(source_name, build_dir):
    tar_files = glob.glob("%s/*.tar.xz" % build_dir)
    tar = tarfile.open(source_name + ".tar.gz" , "w:gz")
    for name in tar_files:
        tar.add(name)
    tar.close()


def main():
    ############################
    # core collection packaging
    ############################

    build_dir = "texlive_core"
    for package in core_collections:
        download_tarxz(package, isCollection=True, dl_location=build_dir)

    for package in os.listdir(build_dir):
        if package.endswith("tar.xz"):
            extract_tarxz(package, build_dir)

    modules = parse_modules(build_dir)

    # remove files that are associated with collections
    shutil.rmtree("%s/tlpkg" % build_dir)
    filelist = glob.glob("%s/collection-*" % build_dir)
    for f in filelist:
        os.remove(f)

    # include these modules too
    core_additional = ["bidi", "iftex", "pgf", "ruhyphen", "ukrhyph"]
    modules.extend(core_additional)

    for package in modules:
        download_tarxz(package, isCollection=False, dl_location=build_dir)
    for package in os.listdir(build_dir):
        if package.endswith("tar.xz"):
            extract_tarxz(package, build_dir)

    # check for patterns
    modules_with_runfiles = collection_with_runfiles_pattern(build_dir)

    # Remove modules that does not match to the runfiles pattern
    modules_without_runfiles = set(modules) - set(modules_with_runfiles)

    for module in modules_without_runfiles:
        os.remove("%s/%s.tar.xz" % (build_dir, module))

    source_name = "texlive-core-" + time.strftime("%Y%m%d")
    create_archive_file(source_name, build_dir)

    ############################
    # other collection packaging
    ############################

    for package in other_collections:
        build_dir = "texlive-" + package
        download_tarxz(package, isCollection=True, dl_location=build_dir)
        extract_tarxz("collection-" + package + ".tar.xz", build_dir)
        modules = parse_tlpobj_other(build_dir)

        # remove files that are associated with collections
        shutil.rmtree("%s/tlpkg" % build_dir)
        filelist = glob.glob("%s/collection-*" % build_dir)
        for f in filelist:
            os.remove(f)

        for package in modules:
            download_tarxz(package, isCollection=False, dl_location=build_dir)

        for package in os.listdir(build_dir):
            if package.endswith("tar.xz"):
                extract_tarxz(package, build_dir)

        source_name = "texlive-" + package + "-" + time.strftime("%Y%m%d")
        create_archive_file(source_name, build_dir)

    print ""
    print "******************************************"
    print "* Don't remove the residual tar.xz files *"
    print "* You will need them to create maps file *"
    print "******************************************"

if __name__ == "__main__":
    sys.exit(main())

