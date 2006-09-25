#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005,2006 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.

# SHA1SUM.LIST file format should be:
# sha1sum filename.tar.bz2

import piksemel
import sys

archive_url = 'http://mirrors.dotsrc.org/kde/stable/%s/src/%s'

# Piksemel updater class
class Pspec:
    def __init__(self, pspecfile):
        try:
            self.doc = piksemel.parse(pspecfile)
        except:
            print 'Unable to parse file: %s' % pspecfile
            sys.exit(1)

    def addHistory(self, date, version, comment, name, email):
        # Try to find last release number
        history_node = self.doc.getTag('History')
        last_update_node = history_node.getTag('Update')
        # If found one increase it
        release = int(last_update_node.getAttribute('release')) + 1
        # Add new release
        new_update_node = last_update_node.prependTag('Update')
        new_update_node.setAttribute('release', str(release))
        new_update_node.insertTag('Date').insertData(date)
        new_update_node.insertTag('Version').insertData(version)
        new_update_node.insertTag('Comment').insertData(comment)
        new_update_node.insertTag('Name').insertData(name)
        new_update_node.insertTag('Email').insertData(email)
        return release

    def getArchive(self):
        list = []
        archive_node = self.doc.getTag('Source').getTag('Archive')
        list.append(archive_node.getAttribute('sha1sum'))
        list.append(archive_node.getAttribute('type'))
        list.append(self.doc.getTag('Source').getTagData('Archive'))
        return list

    def getSourceName(self):
        return self.doc.getTag('Source').getTagData('Name')

    ''' Update archive tag's sha1sum and filename '''
    def updateArchive(self, sha1sum, file_type, url):
        # Piksemel cheat for replacing archive data value
        old_archive_node = self.doc.getTag('Source').getTag('Archive')
        next_node = old_archive_node.next()
        old_archive_node.hide()
        new_archive_node = next_node.prependTag('Archive')
        new_archive_node.setAttribute('sha1sum', sha1sum)
        new_archive_node.setAttribute('type', file_type)
        new_archive_node.insertData(url)

    ''' Update runtime dep.'s version '''
    def updatePackageRuntimeDependency(self, version):
        dependency = self.doc.getTag('Package').getTag('RuntimeDependencies').getTag('Dependency')
        dependency.setAttribute('versionFrom', version)

    def prettyXml(self):
        return self.doc.toPrettyString()

import os
import datetime

class KdeLanguageUpdater:

    pspec_header = '''<?xml version="1.0" ?>
<!DOCTYPE PISI SYSTEM "http://www.pardus.org.tr/projeler/pisi/pisi-spec.dtd">
'''
    updatedict = {}

    def __init__(self, update_filename):
        self.__loadUpdateList(update_filename)

    def __loadUpdateList(self, filename):
        f = file(filename, 'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            data = line.strip().split()
            name = data[1][:data[1].rindex('-')]
            self.updatedict[name] = data

    def __writePspec(self, filename, pspec_xml):
        f = file(filename, 'w')
        f.writelines(self.pspec_header)
        f.writelines(pspec_xml + '\n')
        f.close()

    def updatePspec(self, pspec_filename, version, comment, name, email):
        pspec = Pspec(pspec_path)

        source_name = pspec.getSourceName()
        try:
            sha1sum = self.updatedict[source_name][0]
        except:
            print '%s not in update list' % (source_name)
            return

        archive_name = self.updatedict[source_name][1]

        archive = pspec.getArchive()
        url = archive_url % (version, archive_name)
        pspec.updateArchive(sha1sum, archive[1], url)
        date = datetime.date.today()
        datestr = '%d-%02d-%02d' % (date.year, date.month, date.day)

        pspec.addHistory(datestr, version, comment, name, email)

        pspec.updatePackageRuntimeDependency(version)
        self.__writePspec(pspec_filename, pspec.prettyXml())
        print '* File %s updated' % source_name

if __name__ == '__main__':
    print 'Kde i18n Pisi Package Updater v0.1'

    if len(sys.argv) != 7:
        print 'Usage: i18nupdate [path] [upfile] [version] [comment] [developer name] [developer mail]'
        print 'Example: i18nupdate /home/furkan/svn/devel/i18n/ sha1sum.list 3.4.3 "Version bump" "Furkan Duman" "coderlord at gmail.com"'
        sys.exit()

    updater = KdeLanguageUpdater(sys.argv[2])

    for root, dirs, files in os.walk(sys.argv[1]):
        if 'pspec.xml' in files:
            pspec_path = os.path.join(root, 'pspec.xml')
            updater.updatePspec(pspec_path, sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])

    print 'Finished...'
