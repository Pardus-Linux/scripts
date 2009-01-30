#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009, TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version. Please read the COPYING file.
#
#
# Extracts and compares the CD-repo pisi indexes of two Pardus ISO image.
# Usage: cd-diff.py old_image.iso new_image.iso

import os
import re
import sys
import pisi
import time

# These have same histories with other packages, no need to provide redundant info.
duplicates = ["kernel-headers"]

comment_template = """\
<p>Updated on <em>%s</em> by <em>%s</em> to version <b>%s</b>, release: <b>%s</b></p>
<div style=\"border:1px solid #999999; background-color:#DDDDDD; padding:3px;\">%s</div>
"""

output = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type" />
    <title>Detailed changelog between Pardus 2008.1 Hyaena hyaena and Pardus 2008.2 Canis aureus</title>
</head>
<body>

    <h1><a name=\"top\">Pardus 2008.2 Canis aureus Statistics</a></h1>
    <a href=\"http://www.pardus.org.tr/eng\">http://www.pardus.org.tr/eng</a><br />
    <em>Generated on %s</em>

    <h2>Introduction</h2>
        <p>
        This is an automatically generated HTML document to provide some comparisons and statistics about a Pardus release.
        The tool which generates this document compares two ISO9660 Pardus disc images to find out the evolution of the included binary packages.
        </p>

    <h2>Table of Contents</h2>
    <ol>
        <li><a href="#istats">Image statistics</a></li>
        <li>
            <a href="#pstats">New packages</a>
            <ol>
                %s
            </ol>
        </li>
        <li>
            <a href="#pmstats">Package modifications</a>
            <ol>
                %s
            </ol>
        </li>
        <li>
            <a href="#bstats">Bugzilla statistics</a>
        </li>
    </ol>

    <hr />
    <br />
    <ol>
        <li>
            <h2><a name="istats">Image statistics</a> <a style=\"text-decoration:none;\" href=\"#top\">^^^</a></h2>
            <ul>
                <li><b>Image name:</b> <em>%s</em></li>
                <li><b>Image size:</b> <em>%s</em></li>
                <li><b>Date of release:</b> <em>%s</em></li>
                <li><b>Number of total packages:</b> <em>%d</em></li>
                <li><b>Number of new packages:</b> <em>%d</em></li>
                <li><b>Number of updated packages:</b> <em>%d</em></li>
                <li><b>Download page:</b> <a href=\"http://www.pardus.org.tr/eng/download.html\" target=\"_blank\">Click here</a></li>
            </ul>
        </li>

        <li>
            <h2><a name="pstats">New packages</a> <a style=\"text-decoration:none;\" href=\"#top\">^^^</a></h2>
            <ul>

"""

footer = """\
</ol>
<div align=\"center\">
<br />
<p>
    <a href="http://validator.w3.org/check?uri=referer"><img style=\"border:0px;\"
        src="http://www.w3.org/Icons/valid-xhtml10-blue"
        alt="Valid XHTML 1.0 Transitional" height="31" width="88" /></a>
  </p>
</body>
</html>
"""

total_fixed_bugs = {}
total_bugs = 0


def add_new_package_descriptions(news):
    global output
    for k in sorted(news.keys()):
        output += "<li><b><a name=\"%s\">%s</a></b>\n<p><em>%s</em></p></li>\n" % (k, k, news[k])

    output += "</ul></li>"

def add_package_modifications_header(nr, nr_new):
    global output
    header  = "\n\n<li><h2><a name=\"pmstats\">Package modification statistics</a> <a style=\"text-decoration:none;\" href=\"#top\">^^^</a></h2>\n"
    header += "<h3>%d of %d binary packages has been changed from the release of Pardus 2008.1 to this day:</h3>" % (nr_new, nr)
    output += header

def add_package_changes(p, diffp):
    global output
    data  = "\n<ul>\n<li><b><a name=\"%s\">%s</a></b>\n" % (p,p)
    for d in diffp:
        data += "%s\n" % (parse_comment(p,d).replace("\n", "<br />"))

    output += data + "</li>\n</ul>"

def parse_comment(p, update):
    # Sanitize comments
    m_comment = update.comment.replace("bug#", "#").replace("Bug#", "#").replace("bug #", "#").replace("Bug #", "#").replace("Fixes #", "#")\
                      .replace("fixes #", "#").replace("closes #", "#").replace("Closes #", "#").replace("bugzilla#", "#")

    bugs_pardus_org_tr = "http://bugs.pardus.org.tr/show_bug.cgi?id="
    cve_mitre_org = "http://cve.mitre.org/cgi-bin/cvename.cgi?name="

    # Hardcoded hack
    fixed_bugs = re.findall("#([0-9]+)", m_comment)

    if p != "e2fsprogs":
        for f in fixed_bugs:
            if len(f) > 4:
                fixed_bugs.remove(f)

        if fixed_bugs:
            if total_fixed_bugs.has_key(p):
                total_fixed_bugs[p].extend(fixed_bugs)
            else:
                total_fixed_bugs[p] = fixed_bugs[:]

            global total_bugs
            total_bugs += len(fixed_bugs)

            m_comment = re.sub("#([0-9]{1,4})", "<a href=\"%s\\1\" target=\"_blank\">#\\1</a>" % bugs_pardus_org_tr, m_comment)

    # Erase URL references to CVE's.
    m_comment = re.sub("\(http://.*CVE-[0-9]+-[0-9]+.*\)", "", m_comment)

    m_comment = re.sub("CVE-([0-9]+-[0-9]+)", "<a href=\"%sCVE-\\1\" target=\"_blank\">CVE-\\1</a>" % cve_mitre_org, m_comment)
    comment_data = "\n".join([l.strip() for l in m_comment.split("\n")])
    return comment_template % (update.date, update.name, update.version, update.release, comment_data)

def add_bugzilla_statistics():
    global output

    data  = "</li>\n\n<li><h2><a name=\"bstats\">Bugzilla statistics</a> <a style=\"text-decoration:none;\" href=\"#top\">^^^</a></h2>\n"
    data += "<h3>A total of %d bugs has been fixed from the release of Pardus 2008.1 to this day:</h3>\n<ul>\n" % total_bugs

    bugs = [(p, len(total_fixed_bugs[p])) for p in total_fixed_bugs.keys()]
    bugs.sort(cmp=lambda x,y: x[1]-y[1], reverse=True)
    for k,v in bugs:
        data += "<li style=\"padding:3px;\"><b>%s</b>\n" % k
        data += "<ul>"
        data += "\n".join(["<li><a href=\"http://bugs.pardus.org.tr/show_bug.cgi?id=%s\" target=\"_blank\">#%s</a></li>" % (b,b) for b in total_fixed_bugs[k]])
        data += "</ul></li>"

    output += data + "</ul></li>"


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "Usage: %s <old_image> <new_image>" % sys.argv[0]
        sys.exit(1)

    args = sys.argv[1:]

    print "Cleaning up directory.."
    os.system("rm -rf *xml*")

    print "Comparing %s and %s.." % (args[0], args[1])

    # Extract the two index files.

    old_index = "%s_%s" % (args[0], "pisi-index.xml")
    new_index = "%s_%s" % (args[1], "pisi-index.xml")

    os.system("/usr/bin/iso-read -i %s -e /repo/pisi-index.xml.bz2 -o %s.bz2" % (args[0], old_index))
    os.system("/usr/bin/iso-read -i %s -e /repo/pisi-index.xml.bz2 -o %s.bz2" % (args[1], new_index))

    print "Extracting index files.."
    os.system("/bin/bunzip2 -k -d %s.bz2" % old_index)
    os.system("/bin/bunzip2 -k -d %s.bz2" % new_index)

    print "Reading index files.."

    oi = pisi.index.Index()
    oi.read(old_index)

    ni = pisi.index.Index()
    ni.read(new_index)

    # Create package dictionaries
    oi_packages = dict([(p.name, p) for p in oi.packages])
    ni_packages = dict([(p.name, p) for p in ni.packages])

    # Extract package names
    oi_package_names = oi_packages.keys()
    ni_package_names = ni_packages.keys()

    # Extract intersection/difference for statistical purposes
    dropped_packages = list(set(oi_package_names).difference(ni_package_names))
    new_packages = list(set(ni_package_names).difference(oi_package_names))
    other_packages = list(set(oi_package_names).intersection(ni_package_names))

    # Now the serious part. We'll extract the package differences from history.
    print "Processing %d packages for history extraction.." % len(other_packages)
    diffs = {}
    for p in list(set(other_packages).difference(duplicates)):
        oh = oi_packages[p].history
        nh = ni_packages[p].history
        dh = nh[0:len(nh)-len(oh)]
        if dh:
            diffs[p] = dh

    add_new_package_descriptions(dict([(ni_packages[p].name, ni_packages[p].description['en']) for p in new_packages]))
    add_package_modifications_header(len(ni_packages), len(diffs.keys()))

    for p in sorted(diffs.keys()):
        add_package_changes(p, diffs[p])

    add_bugzilla_statistics()

    image_size = pisi.util.human_readable_size(os.path.getsize(args[1]))

    print "Generating HTML output.."
    f = open("stats.html", "wb")
    f.write(output % (time.asctime(),
                      "\n".join(["<li><a href=\"#%s\">%s</a></li>" % (p,p) for p in sorted(new_packages)]),
                      "\n".join(["<li><a href=\"#%s\">%s</a></li>" % (p,p) for p in sorted(diffs.keys())]),
                      args[1], "%.2f %s" % (image_size[0], image_size[1]), time.strftime("%d %b %Y"),
                      len(ni_package_names), len(new_packages), len(diffs.keys())))

    f.write(footer)
    f.close()
