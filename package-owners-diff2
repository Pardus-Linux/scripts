#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
A script to compare two pisi indexes and print package
ownership differences between these indexes.

Given --print-missing option, the script prints missing packages
that are present in the first index but not in the second index.
It also prints those packages which are written as Replaces but
not written Obsoleted in distribution.xml

'''

import sys
import piksemel
import bz2
import lzma
import urllib2
from optparse import OptionParser

# REPO_LIST = [
#        "http://svn.pardus.org.tr/pardus/2011/devel/pisi-index.xml.xz",
#        "http://svn.pardus.org.tr/pardus/corporate2/devel/pisi-index.xml.bz2",
#        "http://svn.pardus.org.tr/pardus/2009/devel/pisi-index.xml.bz2"
#        ]

REPO1 = "http://svn.pardus.org.tr/pardus/2009/devel/pisi-index.xml.bz2"
REPO2 = "http://svn.pardus.org.tr/pardus/2011/devel/pisi-index.xml.bz2"

def download_and_read_index(repo):
    '''Fetches URL indexes if it is a remote path and reads
    the index files, returns the read string.
    '''

    if repo.startswith("http://"):
        print "%s is being downloaded." % repo
        if repo.endswith("bz2"):
            decompressed_index = bz2.decompress(urllib2.urlopen(repo).read())
        elif repo.endswith("xz"):
            decompressed_index = lzma.decompress(urllib2.urlopen(repo).read())
        else:
            decompressed_index = urllib2.urlopen(repo).read()
    else:
        # Local Repository
        if repo.endswith("bz2"):
            decompressed_index = bz2.decompress(open(repo, "r").read())
        elif repo.endswith("xz"):
            decompressed_index = lzma.decompress(open(repo, "r").read())
        else:
            decompressed_index = open(repo, "r").read()

    return decompressed_index

def parseIndex(ix):
    '''Given a piksemel parsed index, parses every package information,
    returns pkgdict, replacesdict and obsoletelist.
        pkgdict = { pkgr_name : { partOf : [pkg_name] } }
        replacesdict = { replaced_pack : pkg_name }
        obsoletelist = [pkgs]
    '''
    pkgdict = {}
    replacesdict = {}
    obsoletelist = []

    for node in ix.tags("SpecFile"):
        pkg_name = node.getTag("Source").getTagData("Name")
        pkgr_name = node.getTag("Source").getTag("Packager").getTagData("Name")
        partOf = node.getTag("Source").getTagData("PartOf")

        if pkgr_name not in pkgdict:
            pkgdict[pkgr_name] = {partOf:[pkg_name]}
        else:
            if partOf in pkgdict[pkgr_name].keys():
                pkgdict[pkgr_name][partOf].append(pkg_name)
            else:
                pkgdict[pkgr_name][partOf] = [pkg_name]

        for pkgnode in node.tags("Package"):
            replacedPackages = pkgnode.getTag("Replaces")
            if replacedPackages:
                for replaced in replacedPackages.tags("Package"):
                    replacesdict[replaced.firstChild().data()] = pkg_name

        obsoleteParent = ix.getTag("Distribution").getTag("Obsoletes")
        for node in obsoleteParent.tags("Package"):
            obsoletelist.append(node.firstChild().data())

    return pkgdict , replacesdict, obsoletelist

def print_pack_dict(the_dict):
    '''Prints the {packager:[packages]} dict'''
    for packgr, packages in the_dict.iteritems():
        print packgr
        for pack in packages:
            print "\t" + pack
        print

def print_different_owners(diff_owner_dict):
    '''Prints the {packager:[(package, new_pkgr, replaced_name)]}
    '''
    for packgr, pack_sets in diff_owner_dict.iteritems():
        print packgr
        for packset in pack_sets:
            if packset[0] == packset[2]:
                print "\t%-30s%-30s" % ( packset[0], packset[1] )
            else:
                print "\t%-30s%-35s%-30s" % ( packset[0], packset[1], packset[2] )


def find_pkgr(the_package, packageDist):
    '''Return the name of the packager of the_package
    in given packageDist.
    Returns None if the package is not in packageDist
    '''
    for packager, partof_and_packlist in packageDist.iteritems():
        for packagelist in partof_and_packlist.values():
            if the_package in packagelist:
                return packager

def argument():
    '''Command line argument parsing'''

    usage = ""

    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--exclude-component",
            action="append",
            dest="components",
            default=None,
            help="exclude packages under these components \
                                when running this script.")

    parser.add_option("-x", "--exclude",
            action="append",
            dest="excludes",
            default=None,
            help="exclude these packages when running this script.")

    parser.add_option("--print-missing",
            action="store_true",
            dest="print_missing",
            default=False,
            help="Print missing packages that exists \
                    in the first repo but not in the second.")

    return parser.parse_args()


if __name__ == "__main__":
    '''
    * This script gets two pisi indexes, parses the indexes and compares the packager information
    of the packages that locates in both indexes.
    * If a package in index1 is not present in index2, this script prints them too.
    * This script respects the renaming of packages among the indexes.
    '''

    # Options:
    #   -x packages          : exclude these packages
    #   -c components        : exclude packages in these components
    #   --print-missing      : print missing packs in index2, default on

    arg = argument()
    options = arg[0]
    INDEXES = arg[1]

    if INDEXES:
        if len(INDEXES) != 2:
            print "Please provide two indexes or none (use the default indexes)"
            sys.exit(1)
        else:
            REPO1 = INDEXES[0]
            REPO2 = INDEXES[1]

    FIRST_INDEX = piksemel.parseString(download_and_read_index(REPO1))
    SECOND_INDEX = piksemel.parseString(download_and_read_index(REPO2))

    first_packDict, first_replDict, OBSLIST1 = parseIndex(FIRST_INDEX)
    second_packDict, second_replDict, OBSLIST2 = parseIndex(SECOND_INDEX)

    missing_packs = {}
    different_owners = {}
    processed_pkgs = []
    blacklist = []
    comp_blacklist = []
    replaced_but_not_obsoleted = {}

    # pkgdict = {pkgr_name : {partOf : [pkg_name] } }
    # obsoletelist = [pkg_name]
    # replacesdict = {replaced_pack: pkg_name}

    if options.excludes:
        blacklist.extend(options.excludes)

    if options.components:
        comp_blacklist.extend(options.components)

    for pkgr, comp_and_packlist in first_packDict.iteritems():
        for component, packlist in comp_and_packlist.iteritems():
            if component in comp_blacklist:
                continue
            else:
                for pkg in packlist:
                    if pkg in blacklist:
                        continue

                    if pkg in second_replDict:
                        if pkg not in OBSLIST2:
                            replaced_but_not_obsoleted[pkg] = second_replDict[pkg]
                        search_pkg = second_replDict[pkg]
                    else:
                        search_pkg = pkg

                    second_repo_pkgr = find_pkgr(search_pkg, second_packDict)

                    if second_repo_pkgr:
                        if pkgr != second_repo_pkgr:
                            if pkgr in different_owners:
                                different_owners[pkgr].append( ( pkg, \
                                                second_repo_pkgr, search_pkg) )
                            else:
                                different_owners[pkgr] = [ ( pkg, \
                                                second_repo_pkgr, search_pkg) ]
                        else:
                            pass
                    elif not pkg in OBSLIST2:
                        if pkgr in missing_packs:
                            missing_packs[pkgr].append(pkg)
                        else:
                            missing_packs[pkgr] = [pkg]

    print "********************************************"
    print_different_owners(different_owners)

    if options.print_missing:
        print "********************************************"
        print "Missing packs in %s are:" % REPO2
        print "--------------------------------------------"
        print_pack_dict(missing_packs)

        print "********************************************"
        print "These are replaced but not obsoleted packages."
        print "First package is replaced by the second"
        print "--------------------------------------------"
        for k,v in replaced_but_not_obsoleted.iteritems():
            print "%-30s ---> %-30s" %(k,v)







