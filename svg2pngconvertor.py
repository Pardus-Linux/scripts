#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# SVG to png ikon set creator
# Requires inkscape and imagemagick

import os
import sys
import shutil

srcDir = "/tmp/sil/milky/scalable"
targetDir = "/tmp/sil/milky-png"

inkscapecmd = "inkscape --without-gui --export-dpi=72 --export-background-opacity=0 \
               --export-width=256 --export-height=256 \
               --export-png=%s %s > /dev/null"

convertcmd = "convert -filter Sinc -resize %sx%s %s %s"

typeDirs = ["actions",
            "alternativ",
            "animations",
            "apps",
            "categories",
            "devices",
            "emblems",
            "emotes",
            "filesystems",
            "intl",
            "mimetypes",
            "places",
            "scalable",
            "small",
            "status"]

sizes = ["16", "22", "32", "48", "64", "128"]

def findFiles(d, ext):
    filelist = []
    for root, dirs, files in os.walk(d):
        #for name in dirs:
        #    shelltools.chmod(os.path.join(root, name), 0755)
        for name in files:
            if name.endswith(ext):
                filelist.append(os.path.join(root, name))

    return filelist

def makeSubDirs(d, i):
    for t in typeDirs:
        sizedir = "%sx%s/%s" % (i, i, t)
        os.makedirs(os.path.join(d, sizedir))

def makeTargetDir(d):
    if os.path.exists(d):
        shutil.rmtree(d)

    os.makedirs(d)
    for i in sizes:
        makeSubDirs(d, i)

    makeSubDirs(d, "256")

def svgToPng(f):
    os.system(inkscapecmd % (f.replace(srcDir.replace("/scalable", ""), targetDir).replace("scalable", "256x256").replace(".svg", ".png"), f))
    # print inkscapecmd % (f.replace(srcDir.replace("/scalable", ""), targetDir).replace("scalable", "256x256").replace(".svg", ".png"), f)

def pngToSizes(f):
    src = f.replace(srcDir.replace("/scalable", ""), targetDir).replace("scalable", "256x256").replace(".svg", ".png")
    for s in sizes:
        target = src.replace("256x256", "%sx%s" % (s, s))
        os.system(convertcmd % (s, s, src, target))
        # print convertcmd % (s, s, src, target)
        # sys.exit()

svglist = findFiles(srcDir, ".svg")
makeTargetDir(targetDir)
testlist = ["/tmp/sil/milky/scalable/actions/go-down-search.svg",
            "/tmp/sil/milky/scalable/actions/mail-send.svg",
            "/tmp/sil/milky/scalable/actions/vcs_diff.svg"]

for i in svglist:
# for i in testlist:
    svgToPng(i)
    pngToSizes(i)


