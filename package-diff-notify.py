#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2010 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.

import sys
import os
import string
import bz2
import lzma
import urllib2
import piksemel
import pisi
import smtplib
from optparse import OptionParser

# URLs of Repositories
# It is recommended to define REPO_LIST as from newest repo to oldest one
REPO_LIST = (
                "http://svn.pardus.org.tr/pardus/2011/devel/pisi-index.xml.bz2",
                "http://svn.pardus.org.tr/pardus/corporate2/devel/pisi-index.xml.bz2",
                "http://svn.pardus.org.tr/pardus/2009/devel/pisi-index.xml.bz2"
            )


# Details about packages
# Structure : {packager_name -> {package_name -> [[[release1, version1],..,[releaseX, versionX]], [#package1,..,#packageX], [#patch1,..,#patchX], [distro_version1,..,distro_versionX] [packager_mail1,..,packager_mailX]]},..}
REPOS = {}
RELEASES, NRPACKAGES, NRPATCHES, DISTROS, MAILS = range(5)

# Option parser object
OPTIONS = None

# This stores packager list maintaining same package in different distributions
# Structure : { package_name -> [packager_name1,..,packager_nameX]}
CONFLICT_DICT = {}

# This is used to specify which distro repos entry such as #patch is for
DISTRO_LIST = []

# This is mapping of obsolete package to the new package
# Structure : {obsolete_package -> new_package}
OBSOLETE_DICT = {}

# Modify here if necessary
MAIL_SENDER = "sender_name_here"
MAIL_SENDER_USR = "sender@pardus.org.tr"
MAIL_SENDER_PWD = "pwd_here"
MAIL_SERVER = "mail.pardus.org.tr"

MAIL_TEMPLATE = """\
From: %s <%s>
To: %s
Subject: [Pardus] Package Summary
Content-Type: text/plain; charset="utf-8"

Dear Pardus contributor,

Here is a summary about your packages reside on our Pardus repositories. Please, take action
based on the report below:
-----------------------------------------------------------

%s

-----------------------------------------------------------
You're getting this e-mail because you have packages in our repositories.
If you think you shouldn't receive such e-mail, please contact with %s
"""

def process_cmd_line():
    global OPTIONS
    global REPO_LIST
    args = []

    # Initialization of option parser object
    usage_str = "Usage: package-diff-notify [options] [repoURL [repoURL ...]]"
    des_str = "This is a notifier script to give detailed info to packagers about their packages."
    epi_str = "repoURL:\t  compressed pisi-index file path in URL format as xz or bz2"

    parser = OptionParser(prog = "package-diff-notify", version = "%prog 1.0", usage = usage_str, description = des_str, epilog = epi_str)

    parser.add_option("-u", "--uselocal", dest = "uselocal", action = "store_true", default = False, help = "use local pisi-index files as xz or bz2. Use without <repoURL>")
    parser.add_option("-m", "--mail", dest = "mail", action = "store_true", default = False, help = "allow the util to send e-mails to packagers")
    parser.add_option("-n", "--noreport", dest = "noreport", action = "store_true", default = False, help = "prevent the output from being dumped into separate files")
    parser.add_option("-p", "--packager", dest = "packager", action = "store", type = "string", help = "filter the output to show details about specified packager(s) only")
    parser.add_option("-k", "--package", dest = "package", action = "store", type = "string", help = "filter the output to show details about the specified packager only")
    parser.add_option("-x", "--exclude", dest = "exclude", action = "store", type = "string", help = "filter out the given comma-separated component list")

    # Parse the command line
    (OPTIONS, args) = parser.parse_args()

    # Process the command line
    if OPTIONS.uselocal and args:
        parser.print_help()
        return False
    else:
        if OPTIONS.uselocal:
            REPO_LIST = []
            # In cwd, only .bz2 and .xz files are considered for now
            for root, dirs, files in os.walk(os.getcwd()):
                for name in files:
                    if name.endswith(".bz2") or name.endswith(".xz"):
                        REPO_LIST.append(name)
            if not REPO_LIST:
                parser.print_help()
                return False
        elif args:
            REPO_LIST = args

    return True

def handle_replaces(spec):
    ''' This function moves packagers of obsolete package into new package '''

    global CONFLICT_DICT
    global OBSOLETE_DICT

    # Interested in the sub-package that has same name with the source name
    # Ignoring other sub-packages if any
    for package in spec.packages:
        if package.name == spec.source.name:
            for replace in package.replaces:
                if not OBSOLETE_DICT.has_key(replace.package):
                    OBSOLETE_DICT[replace.package] = spec.source.name
                    # Move obsolete package as new package in CONFLICT_DICT
                    if CONFLICT_DICT.has_key(replace.package):
                        tmp_packager_list = CONFLICT_DICT[replace.package]
                        del CONFLICT_DICT[replace.package]
                        for tmp_packager in tmp_packager_list:
                            if tmp_packager not in CONFLICT_DICT[spec.source.name]:
                                CONFLICT_DICT[spec.source.name].append(tmp_packager)

def fetch_repos():
    ''' This function reads source pisi index file as remote or local and constructs "repos" structure based on this file '''

    global REPOS
    global CONFLICT_DICT
    global DISTRO_LIST

    pisi_index = pisi.index.Index()
    for order, repo in enumerate(REPO_LIST):
        print "Parsing index file %s" % repo
        if OPTIONS.uselocal:
            # Use the local index files

            if repo.endswith(".bz2"):
                decompressed_index = bz2.decompress(open(repo, "r").read())
            else:
                # Must be .xz
                decompressed_index = lzma.decompress(open(repo, "r").read())
        else:
            # Use the remote index files

            if repo.endswith(".bz2"):
                decompressed_index = bz2.decompress(urllib2.urlopen(repo).read())
            else:
                decompressed_index = lzma.decompress(urllib2.urlopen(repo).read())
        doc = piksemel.parseString(decompressed_index)
        pisi_index.decode(doc, [])

        # Populate DISTRO_LIST in order of iteration done for repositories
        DISTRO_LIST.append("%s %s" %(pisi_index.distribution.sourceName, pisi_index.distribution.version))

        exclude_list = ["desktop.kde", "kernel"]
        if OPTIONS.exclude:
            # Trim input coming from cmd line
            exclude_list.extend([pkg.strip() for pkg in OPTIONS.exclude.split(",")])

        for spec in pisi_index.specs:
            omitSpec = False
            # Not interested in component(s) excluded if any
            for component in exclude_list:
                if spec.source.partOf.startswith(component):
                    omitSpec = True
                    break
            if omitSpec:
                continue

            if not REPOS.has_key(spec.source.packager.name):
                REPOS[spec.source.packager.name] = {}
            if not REPOS[spec.source.packager.name].has_key(spec.source.name):
                REPOS[spec.source.packager.name][spec.source.name] = [[], [], [], [], []]

            REPOS[spec.source.packager.name][spec.source.name][RELEASES].append([spec.history[0].release, spec.history[0].version])
            REPOS[spec.source.packager.name][spec.source.name][NRPACKAGES].append(len(spec.packages))
            REPOS[spec.source.packager.name][spec.source.name][NRPATCHES].append(len(spec.source.patches))
            REPOS[spec.source.packager.name][spec.source.name][DISTROS].append(DISTRO_LIST[order])
            if spec.source.packager.email not in REPOS[spec.source.packager.name][spec.source.name][MAILS]:
                REPOS[spec.source.packager.name][spec.source.name][MAILS].append(spec.source.packager.email)

            # We may have multiple packagers as owner of the same package
            # residing on different repositories
            # In that case, we need to mark the package as in conflict and
            # be aware of it while sending mail to the packager
            if CONFLICT_DICT.has_key(spec.source.name):
                if spec.source.packager.name not in CONFLICT_DICT[spec.source.name]:
                    CONFLICT_DICT[spec.source.name].append(spec.source.packager.name)
            else:
                if OBSOLETE_DICT.has_key(spec.source.name):
                    # This control flow is redundant,if we have package in
                    # OBSOLETE_DICT, it should have been exist in CONFLICT_DICT
                    # The flow is here not to lose the track of code
                    if CONFLICT_DICT.has_key(OBSOLETE_DICT[spec.source.name]):
                        if spec.source.packager.name not in CONFLICT_DICT[OBSOLETE_DICT[spec.source.name]]:
                            CONFLICT_DICT[OBSOLETE_DICT[spec.source.name]].append(spec.source.packager.name)
                else:
                    CONFLICT_DICT[spec.source.name] = [spec.source.packager.name]

            # Replaces check and handling
            handle_replaces(spec)

def create_summary_entry(packager, package, distro):
    ''' This function creates a summary entry for given repo, say 2011 '''

    order = REPOS[packager][package][DISTROS].index(distro)

    summary_entry = [
                    package,
                    packager,
                    REPOS[packager][package][MAILS],
                    REPOS[packager][package][RELEASES][order][0],
                    REPOS[packager][package][RELEASES][order][1],
                    REPOS[packager][package][NRPACKAGES][order],
                    REPOS[packager][package][NRPATCHES][order],
                    ]

    return summary_entry

def create_stanza(summary_dict):
    ''' This function creates a stanza including info for each package '''

    section_list = ("Package Names", "Packager", "Email", "Release", "Version", "Number of Sub-Package", "Number of Patches")
    content = ""

    # Indexing to traverse summary_dict as in sectionList manner
    for order, section in enumerate(section_list):
        tmp_content = ""
        last_item = ""
        # Ignoring 'Email' item in sectionList, because handled it in prev loop
        if section == "Email":
            continue
        for distro in DISTRO_LIST:
            if summary_dict.has_key(distro):
                # Prevent content replication
                if not summary_dict[distro][order] == last_item:
                    if section == "Packager":
                        tmp_content += "    %-30s: %s <%s>\n" % (distro, summary_dict[distro][order], ",".join(summary_dict[distro][order + 1]))
                    else:
                        tmp_content += "    %-30s: %s\n" % (distro, summary_dict[distro][order])
                    last_item = summary_dict[distro][order]
                else:
                    tmp_content += "    %-30s:\n" % distro
        content += " %s:\n%s" % (section_list[order], tmp_content)

    return content

def is_summary_dict_empty(summary_dict):
    for item in summary_dict.values():
        if item:
            return False

    return True

def prepare_content_body(packager):
    ''' This function generates info about all packages of given packager '''

    content = ""
    package_history = []

    if OPTIONS.package:
        # Trim input coming from cmd line
        package_list = package_list.extend([pkg.strip() \
                for pkg in OPTIONS.package.split(",")])
    else:
        package_list = REPOS[packager].keys()

    for package in package_list:
        # No need to replicate same info for obsolete package in content
        # Must consider as reversible
        if OBSOLETE_DICT.has_key(package):
            if OBSOLETE_DICT[package] in package_history:
                continue
        omit_package = False
        for item in package_history:
            if OBSOLETE_DICT.has_key(item):
                if OBSOLETE_DICT[item] == package:
                    omit_package = True
                    break

        if omit_package:
            continue

        summary_dict = {}
        for distro in DISTRO_LIST:
            if REPOS[packager].has_key(package):
                if distro in REPOS[packager][package][3]:
                    summary_dict[distro] = create_summary_entry(packager, package, distro)
                else:
                    if OBSOLETE_DICT.has_key(package):
                        pck = OBSOLETE_DICT[package]
                    else:
                        pck = package

                    for pckgr in CONFLICT_DICT[pck]:
                        if REPOS[pckgr].has_key(pck):
                            if distro in REPOS[pckgr][pck][DISTROS]:
                                summary_dict[distro] = create_summary_entry(pckgr, pck, distro)
                        if OBSOLETE_DICT.has_key(package) and REPOS[pckgr].has_key(package):
                            if distro in REPOS[pckgr][package][DISTROS]:
                                summary_dict[distro] = create_summary_entry(pckgr, package, distro)

                    # Look for obsolete packages if no new package in distro
                    for obsolete, new in OBSOLETE_DICT.items():
                        # There may be more than one replace, no break
                        # {openoffice->libreoffice}, {openoffice3->libreoffice}
                        if new == package:
                            if CONFLICT_DICT.has_key(new):
                                for pckgr in CONFLICT_DICT[new]:
                                    if REPOS[pckgr].has_key(obsolete):
                                        if distro in REPOS[pckgr][obsolete][DISTROS]:
                                            summary_dict[distro] = create_summary_entry(pckgr, obsolete, distro)
        if not is_summary_dict_empty(summary_dict):
            package_history.append(package)
            content = "%s%s\n%s\n%s\n\n" % (content, package, len(package) * "-", create_stanza(summary_dict))

    return content

def prepare_receiver_mail_list(packager):
    ''' This function gathers emails a packager specified in his packages '''

    mail_list = []

    for package, info in REPOS[packager].items():
        for mail in info[MAILS]:
            if mail not in mail_list:
                mail_list.append(mail)

    return mail_list

def send_mail(receiver_list, content_body):
    ''' This function sends mail to the recipient whose details are passed  '''

    if not MAIL_SENDER_USR or not MAIL_SENDER_PWD or not MAIL_SERVER:
        print "No enough information to connect/authenticate to SMTP server."
        return False

    try:
        session = smtplib.SMTP(MAIL_SERVER)
    except smtplib.SMTPConnectError:
        print "Opening socket to SMTP server failed."
        return False

    try:
        session.login(MAIL_SENDER_USR, MAIL_SENDER_PWD)
    except smtplib.SMTPAuthenticationError:
        print "Authentication to SMTP server failed. Check your credentials."
        return False

    for receiver in receiver_list:
        msg = MAIL_TEMPLATE % (MAIL_SENDER, MAIL_SENDER_USR, receiver, content_body, MAIL_SENDER_USR)
        print "Sending e-mail to %s ..." % receiver,
        try:
            session.sendmail(MAIL_SENDER_USR, receiver, msg)
            print "OK"
        except (smtplib.SMTPSenderRefused, smtplib.SMTPDataError):
            print "FAILED"

    session.quit()

    return True

def traverse_repos():
    ''' This function traverses "repos" structure to send e-mail to the packagers about status of their package(s) and generates a report if requested '''

    if OPTIONS.packager:
        # Call unicode to match cmd line str with key data of repos structure
        packager_list = [unicode(OPTIONS.packager.strip())]
    else:
        packager_list = REPOS.keys()

    for packager in packager_list:
        # Case:
        # 'exclude' option is set and all packages of packager are filtered out
        if not REPOS.has_key(packager):
            continue

        # Optimization in case that we are interested in one packager only
        if OPTIONS.packager:
            if not packager == OPTIONS.packager:
                continue

        content_body = prepare_content_body(packager)

        # If content_body is empty, then there is nothing to report
        if content_body:
            if OPTIONS.mail:
                receiver_mail_list = prepare_receiver_mail_list(packager)
                if not send_mail(receiver_mail_list, content_body):
                    return False

            if not OPTIONS.noreport:
                print "Generating report for packager %s..." % packager
                fp = open("_".join(packager.split()), "w")
                fp.write("%s" % content_body)

    return True

def main():
    if not process_cmd_line():
        return 1
    fetch_repos()
    if not traverse_repos():
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
