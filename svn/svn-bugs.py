#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import urllib2
import string

import MySQLdb as mysql

BUG_COMMENT_SQL = """INSERT INTO longdescs (bug_id, who, bug_when, thetext, work_time, isprivate) VALUES (%(bug_id)s, %(user_id)d, '%(bug_when)s', '%(thetext)s', 0.0, 0)"""

BUG_ACTIVITY_STATUS_SQL = """INSERT INTO bugs_activity (bug_id, who, bug_when, fieldid, added, removed) VALUES ('%(bug_id)s', %(user_id)d, '%(bug_when)s', %(fieldid)d, '%(added)s', '%(removed)s')"""
BUG_ACTIVITY_RESOLUTION_SQL = """INSERT INTO bugs_activity (bug_id, who, bug_when, fieldid, added, removed) VALUES ('%(bug_id)s', %(user_id)d, '%(bug_when)s', %(fieldid)d, '%(added)s', '%(removed)s')"""

BUG_KEYWORDS_INSERT_SQL = """INSERT INTO keywords (bug_id, keywordid) VALUES ('%(bug_id)s', '%(keywordid)d')"""

# Update lastdiffed timestamp
BUG_UPDATE_LASTDIFFED_SQL = "UPDATE bugs SET lastdiffed='%(cur_time)s' WHERE bug_id=%(bug_id)s"

# Query to set the status of a bug to RESOLVED:FIXED
BUG_FIXED_SQL = "UPDATE bugs SET bug_status='RESOLVED',resolution='FIXED' WHERE bug_id=%(bug_id)s"

# Query to set the status of a bug to CLOSED
BUG_CLOSED_SQL = "UPDATE bugs SET bug_status='CLOSED' WHERE bug_id=%(bug_id)s"

# Fetch User id
BUG_USERID_SQL = "SELECT userid FROM `profiles` WHERE login_name='%(mail)s'"

# Fetch Bug status
BUG_STATUS_SQL = "SELECT bug_status FROM `bugs` WHERE bug_id='%(bug_id)s'"

# Fetch Bug resolution
BUG_RESOLUTION_SQL = "SELECT resolution FROM `bugs` WHERE bug_id='%(bug_id)s'"

# Fetch Keyword ID
BUG_KEYWORDS_SELECT_SQL = "SELECT id FROM `keyworddefs` WHERE name='%(name)s'"

BUG_COMMENT_TEMPLATE = u"""Author: %(author)s
Repository: %(repo)s
Revision: %(commit_no)s
Date: %(when)s

Changed Files:
%(changed)s

Commit Message:
%(log)s

See the changes at:
  http://websvn.pardus.org.tr/%(repo)s?view=revision&revision=%(commit_no)s
"""

verbose = False

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
    for line in log.split("\n"):
        if line.startswith("BUG:"):
            yield checkBUG(line)

def splitIDAndKEY(id_key):
    bug_id = ""
    for ch in id_key:
        if ch in string.digits:
            bug_id += ch
        else:
            index = id_key.find(ch)
            keyword = id_key[index:len(id_key)]
            return bug_id, keyword

def main(author, log, commit_no, changed, repo):
    cur_time = time.strftime("%Y-%m-%d %H:%M:%S")

    # repo is something like e.g. pisi or uludag after this
    repo = os.path.basename(repo)

    # FIXME: pardus repository is at /svn/pisi so we have to tweak this..
    repolink = "pardus" if repo == "pisi" else repo

    thetext = BUG_COMMENT_TEMPLATE % {
                                        "author"    : author,
                                        "repo"      : repolink,
                                        "commit_no" : commit_no,
                                        "changed"   : changed,
                                        "log"       : log,
                                        "when"      : cur_time,
                                     }

    thetext=thetext.replace("'", "\"").replace(")", "\\)").replace("(", "\\(").replace(";", "")

    if verbose:
        print thetext

    # Connect to DB
    db = mysql.connect(**dict([line.split("=") for line in open("%s/\x61\x75\x74\x68" % os.path.dirname(sys.argv[0])).read().strip().split("\n") if line != "" and not line.startswith("#")]))
    cur = db.cursor()

    def getAuthorBugzillaID():
        author_mail = getAuthorMail(author)
        if cur.execute(BUG_USERID_SQL % {"mail": author_mail}) == 1:
            return cur.fetchone()[0]
        return 1

    def getOldBugStatus():
        if cur.execute(BUG_STATUS_SQL % {"bug_id": bug_id}) == 1:
            return cur.fetchone()[0]
        return 1

    def getOldBugResolution():
         if cur.execute(BUG_RESOLUTION_SQL % {"bug_id": bug_id}) == 1:
             return cur.fetchone()[0]
         return 1

    def getKeyID(name):
         if cur.execute(BUG_KEYWORDS_SELECT_SQL % {"name": name}) == 1:
             return cur.fetchone()[0]
         return -1

    def commentBUG(bug_id):
        # FIXME author is 1...
        if verbose:
            print "commentBUG(%s)" % bug_id


        cur.execute(BUG_COMMENT_SQL % {"bug_id": bug_id, "user_id": getAuthorBugzillaID(), "bug_when": cur_time, "thetext": thetext})
        db.commit()
        #cur.execute(BUG_UPDATE_LASTDIFFED_SQL % {"bug_id": bug_id, "cur_time": cur_time})

    def fixBUG(bug_id):
        if verbose:
            print "fixBug(%s)" % bug_id
        commentBUG(bug_id)
        cur.execute(BUG_ACTIVITY_STATUS_SQL % {"bug_id": bug_id, "user_id": getAuthorBugzillaID(), "bug_when": cur_time, "fieldid" : 8, "added" : "RESOLVED", "removed": getOldBugStatus()})
        cur.execute(BUG_ACTIVITY_RESOLUTION_SQL % {"bug_id": bug_id, "user_id": getAuthorBugzillaID(), "bug_when": cur_time, "fieldid" : 11, "added" : "FIXED", "removed": getOldBugResolution()})
        db.commit()

        cur.execute(BUG_FIXED_SQL % {"bug_id": bug_id})
        db.commit()

    def closeBUG(bug_id):
        if verbose:
            print "closeBug(%s)" % bug_id
        commentBUG(bug_id)
        cur.execute(BUG_ACTIVITY_STATUS_SQL % {"bug_id": bug_id, "user_id": getAuthorBugzillaID(), "bug_when": cur_time, "fieldid" : 8, "added" : "CLOSED", "removed": getOldBugStatus()})
        db.commit()

        cur.execute(BUG_CLOSED_SQL % {"bug_id": bug_id})
        db.commit()

    def addKEY(bug_id):
        if verbose:
            print "addKEY(%s)" % bug_id
        bug_id, keyword = splitIDAndKEY(bug_id)
        keywordid = getKeyID(keyword)
        if keywordid == -1:
            return
        cur.execute(BUG_KEYWORDS_INSERT_SQL % {"bug_id": bug_id, "keywordid": keywordid})
        db.commit()

    for cmd, bug_id in checkLOG(log):
        if cmd == "COMMENT":
            commentBUG(bug_id)
        elif cmd == "FIXED":
            fixBUG(bug_id)
        elif cmd == "CLOSED":
            closeBUG(bug_id)
        elif cmd == "KEY":
            addKEY(bug_id)

        # Send e-mail
        if verbose:
            print "Sending e-mail.."
        os.chdir("/var/www/bugzilla.pardus.org.tr/bugzilla")
        os.system("perl -T contrib/sendbugmail.pl %s admins@pardus.org.tr" % bug_id)


if __name__ == "__main__":
    SVNLOOK='/usr/bin/svnlook'
    verbose = os.environ.has_key("VERBOSE")

    try:
        repo = sys.argv[1]
        commit_no = sys.argv[2]
        cmd = '%s log -r %s %s' % (SVNLOOK, commit_no, repo)
        log = os.popen(cmd).read()

        cmd = '%s author -r %s %s' % (SVNLOOK, commit_no, repo)
        author = os.popen(cmd).readline().rstrip('\n')

        cmd = '%s changed -r %s %s' % (SVNLOOK, commit_no, repo)
        changed = os.popen(cmd).read().strip()

        main(author, log, commit_no, changed, repo)

    except Exception, e:
        open("/tmp/svn-bugs.err", "w").write("error\n%s" % e)
        if verbose:
            print "error: %s" % e
