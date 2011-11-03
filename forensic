#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import os
import pisi
import sys
import time

IGNORE_DIRS = ('/root',
               '/tmp',
               '/home',
               '/media',
               '/mnt',
               '/proc',
               '/sys',
               '/dev',
               '/var/run',
               '/var/pisi',
               '/var/lib/pisi',
               '/var/tmp',
               '/var/log',
               '/var/db/sudo',
               '/var/lock/subsys',
               '/var/spool',
               '/var/cache',
               '/var/db/comar3/scripts',
               '/var/db/comar3/apps',
               '/var/lib/mysql/mysql',
               '/etc/mudur/services')

IGNORE_EXTS = ('.pyc',
               '.pid')

def get_hash(filepath):
    def _hash(_str):
        return hashlib.sha1(_str).hexdigest()

    if os.path.islink(filepath):
        data = os.path.realpath(filepath)
    else:
        data = file(filepath).read()

    return _hash(data)

def find_unowned(rootdir, last_unowned):
    db = pisi.db.installdb.InstallDB()
    all_files = []
    for package in pisi.api.list_installed():
        files = ['/' + x.path for x in db.get_files(package).list]
        all_files.extend(files)
    filepaths = []
    for root, dirs, files in os.walk(rootdir):
        if root in IGNORE_DIRS:
            while len(dirs):
                dirs.pop()
            continue
        for name in files:
            if name.endswith(IGNORE_EXTS):
                continue
            filepath = os.path.join(root, name)
            if filepath not in all_files and filepath not in last_unowned:
                sys.stdout.write("UNOWNED %s\n" % filepath)
                sys.stdout.flush()

def find_corrupted(rootdir, last_changed):
    for package in pisi.api.list_installed():
        check = pisi.api.check(package)

        for filepath in check['corrupted']:
            filepath = '/' + filepath
            if not filepath.startswith(rootdir):
                continue
            if filepath not in last_changed or last_changed[filepath] != get_hash(filepath):
                sys.stdout.write("CHANGED %s %s %s\n" % (get_hash(filepath), package, filepath))
                sys.stdout.flush()

        for filepath in check['missing']:
            filepath = '/' + filepath
            if not filepath.startswith(rootdir):
                continue
            sys.stdout.write("MISSING %s %s\n" % (package, filepath))
            sys.stdout.flush()

def main():
    try:
        rootdir = sys.argv[1]
    except IndexError:
        print "Find unowned, changed and missing files."
        print
        print "Usage: %s /path [last-log.txt]" % sys.argv[0]
        print
        print "Example:"
        print "  %s / | tee forensic.log" % sys.argv[0]
        print "  %s / forensic.log | tee forensic-new.log" % sys.argv[0]
        return

    if not rootdir.endswith('/'):
        rootdir += '/'

    if len(sys.argv) == 3:
        logfile = sys.argv[2]
    else:
        logfile = None

    last_unowned = []
    last_changed = {}

    if logfile:
        for line in file(logfile):
            line = line.strip()
            if line.startswith("UNOWNED"):
                _type, _filepath = line.split(' ', 1)
                last_unowned.append(_filepath)
            elif line.startswith("CHANGED"):
                _type, _hash, _package,_filepath = line.split(' ', 3)
                last_changed[_filepath] = _hash

    try:
        find_unowned(rootdir, last_unowned)
        find_corrupted(rootdir, last_changed)
    except KeyboardInterrupt:
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
