#!/usr/bin/python
# -*- coding: utf-8 -*-

# A semi-automatic bump script

import os
import sys
import pisi
import time

PACKAGER = "YOUR NAME"
PACKAGER_EMAIL = "YOUR EMAIL"

RELEASE = """\
        <Update release="%s">
            <Date>%s</Date>
            <Version>%s</Version>
            <Comment>%s</Comment>
            <Name>%s</Name>
            <Email>%s</Email>
        </Update>
"""


TRANSLATIONS = """\
<?xml version="1.0" ?>
<PISI>
    <Source>
        <Name>%s</Name>
        <Summary xml:lang="tr">FIXME</Summary>
        <Description xml:lang="tr">FIXME</Description>
    </Source>
</PISI>
"""


def increment_release(pspec, ver, comment):
    release = int(pisi.specfile.SpecFile('pspec.xml').history[0].release)+1
    date = time.strftime("%Y-%m-%d")

    global RELEASE
    new_release = RELEASE % (release, date, ver, comment, PACKAGER, PACKAGER_EMAIL)

    return pspec.replace("<History>\n", "<History>\n%s" % new_release)

def update_sha1sum():
    fl = os.path.basename(pisi.specfile.SpecFile('pspec.xml').source.archive.uri)
    sh = os.popen("sha1sum /var/cache/pisi/archives/%s" % fl).read().split()[0]
    print sh

    if sh:
        ret = []
        for l in open("pspec.xml", "r").readlines():
            if "<Archive" in l:
                nls = l.split("sha1sum=\"")
                nl = nls[0] + "sha1sum=\"%s\"" % sh + nls[1].split("\"", 1)[1]
                ret.append(nl)
            else:
                ret.append(l)

        return "".join(ret)

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "Usage: %s <Bumped version> <Release comment>" % sys.argv[0]
        sys.exit(1)

    # First fetch the tarball
    os.system("pisi build pspec.xml --fetch")

    # Update sha1sum
    newpspec = update_sha1sum()
    print newpspec

    # Add translations.xml
    if not os.path.exists("translations.xml"):
        open("translations.xml", "w").write(TRANSLATIONS % os.path.basename(os.getcwd()))
        os.system("svn add translations.xml")

    # Increment release
    newpspec = increment_release(newpspec, sys.argv[1], sys.argv[2])
    open("pspec.xml", "w").write(newpspec)
