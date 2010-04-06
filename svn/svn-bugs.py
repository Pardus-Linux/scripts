#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import urllib2

import MySQLdb as mysql

BUG_COMMENT_SQL = """INSERT INTO longdescs (bug_id, who, bug_when, thetext, work_time, isprivate) VALUES (%(bug_id)s, %(user_id)d, '%(bug_when)s', '%(thetext)s', 0.0, 0)"""

BUG_ACTIVITY_STATUS_SQL = """INSERT INTO bugs_activity (bug_id, who, bug_when, fieldid, added, removed) VALUES ('%(bug_id)s', %(user_id)d, '%(bug_when)s', %(fieldid)d, '%(added)s', '%(removed)s')"""
BUG_ACTIVITY_RESOLUTION_SQL = """INSERT INTO bugs_activity (bug_id, who, bug_when, fieldid, added, removed) VALUES ('%(bug_id)s', %(user_id)d, '%(bug_when)s', %(fieldid)d, '%(added)s', '%(removed)s')"""

# Update lastdiffed timestamp
BUG_UPDATE_LASTDIFFED_SQL = "UPDATE bugs SET lastdiffed='%(cur_time)s' WHERE bug_id=%(bug_id)s"

# Query to set the status of a bug to RESOLVED:FIXED
BUG_FIXED_SQL = "UPDATE bugs SET bug_status='RESOLVED',resolution='FIXED' WHERE bug_id=%(bug_id)s"

# Fetch User id
BUG_USERID_SQL = "SELECT userid FROM `profiles` WHERE login_name='%(mail)s'"

# Fetch Bug status
BUG_STATUS_SQL = "SELECT bug_status FROM `bugs` WHERE bug_id='%(bug_id)s'"

# Fetch Bug resolution
BUG_RESOLUTION_SQL = "SELECT resolution FROM `bugs` WHERE bug_id='%(bug_id)s'"

BUG_COMMENT_TEMPLATE = u"""Author: %(author)s
Repository: %(repo)s
Commit: %(commit_no)s

Changed Files:
%(changed)s

Commit Message:
%(log)s

See the changes at:
  http://websvn.pardus.org.tr/pardus?view=revision&revision=%(commit_no)s
"""

def getAuthorMail(author):
        accounts = urllib2.urlopen("http://svn.pardus.org.tr/uludag/trunk/common/accounts").readlines()
        for a in [l for l in accounts if l and not l.startswith("#")]:
          try:
            if a.split(":")[0] == author:
              # Match!
              return a.split(":")[2].replace(" [at] ", "@")
          except:
            pass

def checkBUG(line):
    line = line.strip().split(':')
    if len(line) != 3:
        return []

    cmd = line[1]
    bug_id = line[2]
    return (cmd, bug_id)

def checkLOG(log):
    for line in log:
        if line.startswith("BUG:"):
            yield checkBUG(line)

def main(author, log, commit_no, changed, repo):
    thetext = BUG_COMMENT_TEMPLATE % {"author":author, "repo":os.path.basename(repo), "commit_no":commit_no, "changed": changed, "log": log}

    thetext=thetext.replace("'", "\"")
    thetext=thetext.replace(")", "\\)")
    thetext=thetext.replace("(", "\\(")
    thetext=thetext.replace(";", "")
    open("/tmp/svn-bugs.log", "w").write(thetext)

    # Connect to DB
    db = mysql.connect(host="localhost", user="", passwd="", db="")
    cur = db.cursor()

    cur_time = time.strftime("%Y-%m-%d %H:%M:%S")


    def getAuthorBugzillaID():
        author_mail = getAuthorMail(author)
        if cur.execute(BUG_USERID_SQL % {"mail": author_mail}) == 1:
            return cur.fetchone()[0]
        return 1

    def getOldBugStatus():
        if cur.execute(BUG_STATUS_SQL % {"bug_id": bug_id}) == 1:
            return cur.fetchone()[0]
        return 1

    def getOldResolution():
         if cur.execute(BUG_RESOLUTION_SQL % {"bug_id": bug_id}) == 1:
             return cur.fetchone()[0]
         return 1

    def commentBUG(bug_id):
        # FIXME author is 1...

        fieldid = 8
        added = "RESOLVED"
        cur.execute(BUG_ACTIVITY_STATUS_SQL % {"bug_id": bug_id, "user_id": getAuthorBugzillaID(), "bug_when": cur_time, "fieldid" : fieldid, "added" : added, "removed": getOldBugStatus()})
        db.commit()

        fieldid = 11
        added = "FIXED"
        cur.execute(BUG_ACTIVITY_RESOLUTION_SQL % {"bug_id": bug_id, "user_id": getAuthorBugzillaID(), "bug_when": cur_time, "fieldid" : fieldid, "added" : added, "removed": getOldBugResolution()})
        db.commit()

        cur.execute(BUG_COMMENT_SQL % {"bug_id": bug_id, "user_id": getAuthorBugzillaID(), "bug_when": cur_time, "thetext": thetext})
        db.commit()
        #cur.execute(BUG_UPDATE_LASTDIFFED_SQL % {"bug_id": bug_id, "cur_time": cur_time})

    def fixBUG(bug_id):
        commentBUG(bug_id)
        cur.execute(BUG_FIXED_SQL % {"bug_id": bug_id})
        db.commit()

    for cmd, bug_id in checkLOG(log):
        if cmd == "COMMENT":
            commentBUG(bug_id)
        elif cmd == "FIXED":
            fixBUG(bug_id)
        os.system("perl -T /var/www/bugzilla.pardus.org.tr/bugzilla/contrib/sendbugmail.pl %s admins@pardus.org.tr" % bug_id)

if __name__ == "__main__":
    SVNLOOK='/usr/bin/svnlook'

    try:
        repo = sys.argv[1]
        commit_no = sys.argv[2]
        cmd = '%s log -r %s %s' % (SVNLOOK, commit_no, repo)
        log = os.popen(cmd).readlines()

        cmd = '%s author -r %s %s' % (SVNLOOK, commit_no, repo)
        author = os.popen(cmd).readline().rstrip('\n')

        cmd = '%s changed -r %s %s' % (SVNLOOK, commit_no, repo)
        changed = os.popen(cmd).readlines()

        main(author, log, commit_no, changed, repo)

    except Exception, e:
        open("/tmp/svn-bugs.err", "w").write("error\n%s" % e)
