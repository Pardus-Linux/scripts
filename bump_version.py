#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

import pisi.specfile

SUCCESS, FAIL = xrange(2)

NAME = unicode(os.environ.get("NAME", ""))
EMAIL = os.environ.get("EMAIL", "")

def buildPspecXML(doc):
    header = '''<?xml version="1.0" ?>
<!DOCTYPE PISI SYSTEM "http://www.pardus.org.tr/projeler/pisi/pisi-spec.dtd">'''
    return "%s\n\n%s\n" % (header, doc.toPrettyString())

def main():
    if len(sys.argv) != 4:
        print "Usage: %s specfile version url" % sys.argv[0]
        return FAIL

    specfile = sys.argv[1]
    try:
        spec = pisi.specfile.SpecFile(specfile)
    except:
        print "Can't parse: %s" % specfile
        return FAIL

    source = spec.source
    release = int(spec.getSourceRelease()) + 1

    version = sys.argv[2] # TODO: validate version
    url = sys.argv[3]

    if version == spec.getSourceVersion():
        print "Already at version %s" % version
        return FAIL

    type = ""
    if url.endswith("bz2"):
        type = "tarbz2"
    elif url.endswith("gz"):
        type = "targz"
    elif url.endswith("zip"):
        type = "zip"

    if not type:
        print "%s file type cannot be determined" % url
        return FAIL

    source.archive.uri = url
    source.archive.sha1sum = "???"
    source.archive.type = type

    update = pisi.specfile.Update()
    update.release = str(release)
    update.date = time.strftime("%Y-%m-%d")
    update.version = version
    update.comment = "Version bump"
    update.name = NAME
    update.email = EMAIL
    spec.history.insert(0, update)

    spec.write("/dev/null", True)
    specxml = buildPspecXML(spec.doc)

    f = open(sys.argv[1], "w")
    f.write(specxml)
    f.close()

    print "%s updated." % specfile

    return SUCCESS


if __name__ == "__main__":
    sys.exit(main())
