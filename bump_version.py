#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time

import piksemel


SUCCESS, FAIL = xrange(2)

NAME = unicode(os.environ.get('NAME', ''))
EMAIL = os.environ.get('EMAIL', '')


def buildPspecXML(doc):
    header = '''<?xml version="1.0" ?>
<!DOCTYPE PISI SYSTEM 'http://www.pardus.org.tr/projeler/pisi/pisi-spec.dtd'>'''
    return '%s\n\n%s\n' % (header, doc.toPrettyString())


def main():
    if len(sys.argv) != 4:
        print 'Usage: %s specfile version url' % sys.argv[0]
        return FAIL

    try:
        doc = piksemel.parse(sys.argv[1])
    except:
        print 'Can\'t parse: %s' % shortpath
        return FAIL

    source = doc.getTag('Source')
    history = doc.getTag('History')
    package = source.getTagData('Name')
    release = int(history.getTag('Update').getAttribute('release')) + 1

    version = sys.argv[2] # TODO: validate version
    url = sys.argv[3]

    if version == history.getTag('Update').getTagData('Version'):
        print 'Already at version %s' % version
        return FAIL

    type = ''
    if sys.argv[3].endswith('bz2'):
        type = 'tarbz2'
    elif sys.argv[3].endswith('gz'):
        type = 'targz'
    elif sys.argv[3].endswith('zip'):
        type = 'zip'

    old_archive = source.getTag('Archive')

    archive = old_archive.appendTag('Archive')
    archive.insertData(url)
    archive.setAttribute('sha1sum', '???')
    archive.setAttribute('type', type)

    old_archive.hide()

    update = history.getTag('Update').prependTag('Update')
    update.setAttribute('release', str(release))
    update.insertTag('Date').insertData(time.strftime('%Y-%m-%d'))
    update.insertTag('Version').insertData(version)
    update.insertTag('Comment').insertData('Version bump')
    update.insertTag('Name').insertData(NAME)
    update.insertTag('Email').insertData(EMAIL)

    spec = buildPspecXML(doc)
    del doc

    f = open(sys.argv[1], 'w')
    f.write(spec)
    f.close()

    return SUCCESS


if __name__ == '__main__':
    sys.exit(main())
