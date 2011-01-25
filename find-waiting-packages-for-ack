#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys

import urllib
import piksemel
import lzma
import bz2
import locale


locale.setlocale(locale.LC_ALL, "tr_TR.UTF-8")

repoOf = {
          '2009' : ('http://packages.pardus.org.tr/pardus-2009/pisi-index.xml.bz2', 'http://packages.pardus.org.tr/pardus-2009-test/pisi-index.xml.bz2', 'bzip2' ),
          #'2011' : ('http://packages.pardus.org.tr/pardus/2011/devel/x86_64-debug/pisi-index.xml.xz'),
          #'Corporate2' : ('http://packages.pardus.org.tr/pardus/corporate2/devel/x86_64-debug/pisi-index.xml.xz'),
}

usage = " %s PardusRelease\n    Finds packages that waiting for ACK in PardusRelease (which is one of %s)" % (sys.argv[0], ', '.join(sorted(repoOf.keys())))


def fail(message):
    print message
    sys.exit(1)


def readFileFrom(_url):
    try:
        return urllib.urlopen( _url )
    except IOError:
        fail("could not connect %s" % _url)


def getDocument( filetype, _url ):
    rawdata = readFileFrom( _url )
    if filetype == "xz":
        data = lzma.decompress( rawdata.read() )

    elif filetype == "bzip2":
        data = bz2.decompress( rawdata.read() )

    else:
        fail("not support filetype %s for decompress" % filetype)

    return piksemel.parseString(data)


class PendingPackages():

    packagerList = []
    listofPackagesByOwned = {}
    listofPackagesByModified = {}

    def addModifiedPackage(self, packageURI, package_owner, updateBy):

        if package_owner not in self.packagerList:
            self.packagerList.append(package_owner)

        if updateBy not in self.packagerList:
            self.packagerList.append( updateBy )

        self.listofPackagesByOwned.setdefault( package_owner, []).append( packageURI )


        if package_owner != updateBy:
            data = ( packageURI, package_owner )
            self.listofPackagesByModified.setdefault(updateBy, []).append( data )


    def printKnowledgePendingPackages(self):

        print "LISTOFPACKAGESWAITINGFORACK"
        print "=========================="

        self.packagerList.sort(cmp=locale.strcoll)
        for packager in self.packagerList:

            print "\n%s " % packager

            if packager in self.listofPackagesByOwned:
                self.listofPackagesByOwned[packager].sort()
                packages = self.listofPackagesByOwned[packager]
                for package in packages:
                    print  "    %s" % package

            if packager in self.listofPackagesByModified:
                self.listofPackagesByModified[packager].sort()
                packages = self.listofPackagesByModified[packager]
                for package, packager in packages:
                    print  "    %s      (%s)" % (package , packager)


if __name__ == "__main__":

    print

    if len(sys.argv) > 1 :
        which_release = sys.argv[1]
    else:
        fail(usage)

    if which_release in repoOf.keys():
        repos = repoOf.get( which_release )
        stable_repo_url = repos[0]
        test_repo_url = repos[1]
        filetype = repos[2]
    else:
        fail("Could not find release %s\nknown releases are:  \n  %s  " % (which_release, ", ".join(repoOf.keys())))

    pendingPackages = PendingPackages()

    '''get packageList of stable repo'''
    listofStablePackages = {} 

    doc = getDocument( filetype, stable_repo_url )

    packages_elements = doc.tags( "Package" )

    for package in packages_elements:
        package_name = package.getTagData('Name')
       # stableRepoPackageLastUpdataRelease = package.getTag("History").tags("Update").next().getAttribute("release")
       # listofStablePackages[ package_name ] = stableRepoPackageLastUpdataRelease
        packageURI =  package.getTagData("PackageURI")
        listofStablePackages[ package_name ] = packageURI

    '''compare with test repo'''
    doc = getDocument( filetype, test_repo_url )

    package_elements = doc.tags( "Package" )

    for package in package_elements:
        package_name = package.getTagData('Name')


        if package_name in listofStablePackages.keys():
            # update_element = package.getTag("History").tags("Update").next()
            # testRepoPackageLastUpdataRelease = update_element.getAttribute("release")
            packageURI = package.getTagData("PackageURI")

            if listofStablePackages[ package_name ] != packageURI:

                packageURI = package.getTagData("PackageURI")
                package_owner = package.getTag("Source").getTag("Packager").getTagData("Name")
                updateBy = package.getTag("History").tags("Update").next().getTagData('Name')

                pendingPackages.addModifiedPackage( packageURI, package_owner, updateBy )

            '''
            else: not update package
            '''


        '''
        else: first release
        '''


    pendingPackages.printKnowledgePendingPackages()



