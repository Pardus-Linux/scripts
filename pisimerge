#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import locale
import piksemel
import tempfile
import subprocess

# You have to run this in pardus/200x folder which contains the stable and devel sub-folders.
# Usage: ./merge.py devel/kernel/default/kernel -> Will merge the differences of that package from the stable
# to the stable repository with a nice commit log. You can override the commit log with
# ./merge.py devel/kernel/default/kernel  "Just commit it, no fancy commit log."

def handle_user_choice(merge_tmp_file):
    editor = os.environ.get("EDITOR", "vi")

    while True:
        print "\nSelect one of the following:\n\t[M]erge, [E]dit, [A]bort?"
        choice = raw_input().lower()
        if choice.startswith("m"):
            return True
        elif choice.startswith("e"):
            # Edit
            subprocess.call([editor, merge_tmp_file])
        elif choice.startswith("a"):
            # Abort
            return False

def get_latest_change(path):
    os.system("svn up %s" % path)
    return int(os.popen("svn info %s | grep 'Last Changed Rev'" % path).read().strip().split(": ")[1])+1

def get_merge_log(path, rev):
    os.system("svn up devel/%s" % path)
    p = piksemel.parseString(os.popen("svn log --xml -r %d:HEAD devel/%s" % (rev, path)).read().strip())

    merge_log = """\
Merge from devel/%s:

""" % path

    for log in p.root().tags():
        rev = log.getAttribute('revision')
        msg = log.getTagData('msg')
        date = log.getTagData('date')
        author = log.getTagData('author')

        merge_log += "rev. %s, by %s on %s\n  %s\n\n" % (rev, author, date[:10], msg.rstrip("\n"))

    return merge_log.rstrip("\n")


if __name__ == "__main__":
    locale.setlocale(locale.LC_ALL, "C")

    merge_msg = ""
    path = sys.argv[1]

    if len(sys.argv) > 2:
        merge_msg = sys.argv[2]

    if path.startswith("devel/"):
        path = path.split("devel/", 1)[1]

    if not os.path.exists("stable/%s" % path):
        # New package
        os.system("svn up devel/%s stable/%s" % (path, path))

        print "Copying from devel/%s.." % path
        os.system("svn cp devel/%s stable/%s" % (path, path))

        os.system("svn ci stable/%s -m 'Ready for 2009'" % path)

    else:
        latest = get_latest_change("stable/%s" % path)

        if not merge_msg:
            merge_msg = get_merge_log(path, latest)

        # Generate safe temporary file
        (fd, merge_tmp_file) = tempfile.mkstemp(prefix='pisimerge')

        merge_tmp = open(merge_tmp_file, "w").write(merge_msg)

        # Dump merge message
        print merge_msg

        if handle_user_choice(merge_tmp_file):
            print "Merging from devel/%s.." % path
            merge_cmd = "svn merge -r %d:HEAD devel/%s stable/%s" %  (latest, path, path)
            commit_cmd = "svn ci stable/%s -F %s" % (path, merge_tmp_file)
            os.system(merge_cmd)
            os.system(commit_cmd)

        # Clean temporary file
        try:
            os.unlink(merge_tmp_file)
        except:
            pass

