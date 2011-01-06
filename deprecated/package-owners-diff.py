#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
#from pisi.specfile import SpecFile
import piksemel

from optparse import OptionParser

first_repo = ""
second_repo = ""

component=""

def get_blacklist_pkgs(BFILE):
    bfile = open(BFILE, "r")
    blacklist_pkgs = []

    for pkg in bfile.readlines():
        if not pkg.startswith("#"):
            blacklist_pkgs.append(pkg.strip("\n"))

    return blacklist_pkgs

def get_obsoletes():
    obsolete_list = []
    distributionXML = piksemel.parse(second_repo + "/distribution.xml")
    for node in distributionXML.getTag("Obsoletes").tags():
        obsolete_list.append(node.firstChild().data())
    return obsolete_list

def get_packager(_xmlfile):
    return _xmlfile.getTag("Source").getTag("Packager").getTagData("Name")

def get_pspec_dict(root_dir, comp):
    pspec_dict = {}

    for root, dirs, files in os.walk("%s/%s" % (root_dir, comp)):
        if "pspec.xml" in files:
            xmlfile = piksemel.parse(root + "/pspec.xml")
            packager = get_packager(xmlfile)
            # Comment out as Description is mandatory in Pardus 2011 and
            #   Corporate 2 but not in Pardus 2009.
            #specfile = SpecFile(root + "/pspec.xml")
            #packager = specfile.source.packager.name

            pspec_dict[root.split("/")[-1]] = packager

        # dont walk into the versioned stuff
        if ".svn" in dirs:
            dirs.remove(".svn")

    return pspec_dict

def print_dict(dict):
    for k, v in dict.iteritems():
        print k + " ---> " + v

def print_dict_with_list_values(dict):
    for k, v in dict.iteritems():
        print k + " ---> " 
        for vi in v:
            print "\t\t%s" % vi

if __name__ == "__main__":

    usage = "usage: %s [OPTIONS]" % sys.argv[0]

    parser = OptionParser(usage=usage)
    parser.add_option("--first-repo",
                      action="store",
                      dest="first_repo",
                      type="string",
                      help="Specify the first repo.")

    parser.add_option("--second-repo",
                      action="store",
                      dest="second_repo",
                      type="string",
                      help="Specify the second repo.")

    parser.add_option("-b", "--blacklist",
                     action="store",
                     dest="blacklist_file",
                     help="Name of the blacklist file that contains pkgs to be ignored in the check.")

    parser.add_option("-c", "--component",
                     action="store",
                     dest="component",
                     type="string",
                     help="Check a spesific component.")

    parser.add_option("-m", "--missing",
                      action="store_true",
                      dest="missing",
                      default=False,
                      help="Print packages that are missing in the second repo.")

    parser.add_option("--plain",
                       action="store_true",
                       dest="plain",
                       default=False,
                       help="Only print owner-diff of the packages.")

    parser.add_option("--pwners",
                      action="store_true",
                      dest="pwners",
                      default=False,
                      help="Print previous owners too.")

    (options, paths) = parser.parse_args()

    if options.first_repo:
        first_repo = options.first_repo
    if options.second_repo:
        first_repo = options.second_repo
    if options.component:
        component = options.component

    if not first_repo or not second_repo:
        print "Please state first and second repo addresses."
        sys.exit(1)

    missing_packs = {}
    different_owners = {}
    blacklist = []

    # Parse the repos
    first_dict = get_pspec_dict(first_repo, component)
    second_dict = get_pspec_dict(second_repo, component)

    obsolete_pkgs = get_obsoletes()

    if options.blacklist_file:
        blacklist = get_blacklist_pkgs(options.blacklist_file)

    if not options.plain:
        print "first repo:\n\t%s" % first_repo
        print "second repo:\n\t%s" % second_repo

        print "-----------------------------------------------"

    for package, owner in first_dict.iteritems():
        # Filter if the pkg is in the blacklist
        if package in blacklist:
            pass

        ### Pkgs not in second repo ###
        elif package not in second_dict:
            # Is the pkg in obsoletes
            if package not in obsolete_pkgs:
                # List missing pkgs due to the owners
                if owner in missing_packs:
                    missing_packs[owner].append(package)
                else:
                    missing_packs[owner] = [package,]

        ### Pkgs in both repos ###
        else:
            # add to the list if the owners are different
            if owner != second_dict[package]:
                if owner in different_owners:
                    different_owners[owner].append([package,second_dict[package]])
                else:
                    different_owners[owner] =  [[package, second_dict[package]]]

    for owner, details in different_owners.iteritems():
        print owner
        for packs in details:
            if options.pwners:
                print "\t%-30s\t%-30s" % (packs[0], packs[1])
            else:
                print "\t%-30s\t" % packs[0]
        print

    if options.plain:
        sys.exit(1)

    if options.missing:
        print "-----------------------------------------------"
        print "Missing packages in the second repo %s:\n" % second_repo
        print_dict_with_list_values(missing_packs)

