#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import urllib2

import logging

from bugspy.bugzilla import Bugzilla
from bugspy.config import BugspyConfig

SVN_LOG_FILE = "/var/www/bugzilla.pardus.org.tr/scripts/svn/svn.log"
SVN_ERROR_FILE = "/var/www/bugzilla.pardus.org.tr/scripts/svn/svn.error"

BUGSPY_CONFIG_FILE = "/var/www/bugzilla.pardus.org.tr/scripts/svn/bugspy.conf"

BUG_COMMENT_TEMPLATE = u"""Author: %(author)s
Repository: %(repo)s
Commit: %(commit_no)s

Changed Files:
%(changed)s

Commit Message:
%(log)s

See the changes at:
  http://websvn.pardus.org.tr/%(repo)s?view=revision&revision=%(commit_no)s
"""

# FIXME: Use FileHandler to write logs into file.
log = logging.getLogger("bugzilla")
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s"))
log.addHandler(ch)

def getAuthorName(author):
    accounts = urllib2.urlopen("http://svn.pardus.org.tr/uludag/trunk/common/accounts").readlines()
    for a in [l for l in accounts if l and not l.startswith("#")]:
        try:
            if a.split(":")[0] == author:
                # Match!
                return a.split(":")[1]
        except:
            pass

def arrayTostring(data):
    output = ""
    for i in data:
        output += i

    # do not include last \n
    return output.rstrip("\n")

def checkBUG(line):
    line = line.strip().split(':')
    if len(line) != 3:
        return []

    cmd = line[1]
    bug_id = line[2]
    return (cmd, bug_id)

def checkLOG(msg):
    for line in msg:
        if line.startswith("BUG:"):
            yield checkBUG(line)

def main(author, msg, commit_no, changed, repo):
    changed = arrayTostring(changed)
    msg = arrayTostring(msg)

    repo_name = os.path.basename(repo)
    if repo_name == "pisi":
        repo_name = "pardus"

    author_name = getAuthorName(author)
    if author_name:
        author = author_name

    thetext = BUG_COMMENT_TEMPLATE % {"author":author, "repo": repo_name, "commit_no": commit_no, "changed": changed, "log": msg}

    thetext=thetext.replace("'", "\"")
    thetext=thetext.replace(")", "\\)")
    thetext=thetext.replace("(", "\\(")
    thetext=thetext.replace(";", "")
    open(SVN_LOG_FILE, "w").write(thetext)

    c = BugspyConfig(BUGSPY_CONFIG_FILE)
    bugzilla = Bugzilla(c.bugzillaurl, c.username, c.password)
    bugzilla.login()

    def commentBUG(bug_id):
        log.info("Modifying bug...")
        bugzilla.modify(bug_id=bug_id,
                        comment=thetext)

    def fixBUG(bug_id):
        log.info("Fixing bug..")
        bugzilla.modify(bug_id=bug_id,
                        status="RESOLVED",
                        resolution="FIXED",
                        comment=thetext)

    for cmd, bug_id in checkLOG(msg.split('\n')):
        if cmd == "COMMENT":
            commentBUG(bug_id)
        elif cmd == "FIXED":
            fixBUG(bug_id)

if __name__ == "__main__":
    SVNLOOK='/usr/bin/svnlook'

    try:
        repo = sys.argv[1]
        commit_no = sys.argv[2]
        cmd = '%s log -r %s %s' % (SVNLOOK, commit_no, repo)
        msg = os.popen(cmd).readlines()

        cmd = '%s author -r %s %s' % (SVNLOOK, commit_no, repo)
        author = os.popen(cmd).readline().rstrip('\n')

        cmd = '%s changed -r %s %s' % (SVNLOOK, commit_no, repo)
        changed = os.popen(cmd).readlines()

        main(author, msg, commit_no, changed, repo)

    except Exception, e:
        open(SVN_ERROR_FILE, "w").write("error\n%s" % e)
        sys.exit(e)

    sys.exit(0)
