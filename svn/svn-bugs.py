#!/usr/bin/python

import MySQLdb as mysql
import time
import os
import sys

COMMENT_SQL = """INSERT INTO longdescs (bug_id, who, bug_when, thetext, work_time, isprivate) VALUES (%(bug_id)s, %(user_id)d, '%(bug_when)s', '%(thetext)s', 0.0, 0)"""
#BUGS_COMMENT_SQL = "UPDATE bugs SET lastdiffed='%(cur_time)s' WHERE bug_id=%(bug_id)s"
BUGS_SQL = "UPDATE bugs SET bug_status='RESOLVED',resolution='FIXED' WHERE bug_id=%(bug_id)s"
USERID_SQL = "SELECT userid FROM `profiles` WHERE login_name='%(mail)s'"

COMMENT_TEMPLATE = u"""Author: %(author)s
Repository: %(repo)s
Commit: %(commit_no)s

Changed Files:
%(changed)s

Commit Message:
%(log)s
"""

def getAuthorMail(author):
    f = open("/uludag/trunk/common/accounts")
    for a in f:
    	a = a.split(":")
	if a[0] == author:
	    return a[2].replace(" [at] ", "@")

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
    thetext = COMMENT_TEMPLATE % {"author":author, "repo":os.path.basename(repo), "commit_no":commit_no, "changed": "".join(changed), "log": "".join(log)}
    thetext=thetext.replace("'", "\"")
    thetext=thetext.replace(")", "\\)")
    thetext=thetext.replace("(", "\\(")
    thetext=thetext.replace(";", "")
    open("/tmp/svn-bugs.log", "w").write(thetext)
    
    db = mysql.connect(host="localhost", user="", passwd="", db="")
    cur = db.cursor()

    cur_time = time.strftime("%Y-%m-%d %H:%M:%S")


    def getAuthorBugzillaID():
    	author_mail = getAuthorMail(author)
    	if cur.execute(USERID_SQL % {"mail": author_mail}) == 1:
	    return cur.fetchone()[0]
	return 1

    def commentBUG(bug_id):
        # FIXME author is 1...
        cur.execute(COMMENT_SQL % {"bug_id": bug_id, "user_id": getAuthorBugzillaID(), "bug_when": cur_time, "thetext": thetext})
        db.commit()
#        cur.execute(BUGS_COMMENT_SQL % {"bug_id": bug_id, "cur_time": cur_time})

    def fixBUG(bug_id):
        commentBUG(bug_id)
        cur.execute(BUGS_SQL % {"bug_id": bug_id})
        db.commit()

    for cmd, bug_id in checkLOG(log):
        if cmd == "COMMENT":
            commentBUG(bug_id)
        elif cmd == "FIXED":
            fixBUG(bug_id)
        os.chdir("/var/www/bugzilla.pardus.org.tr/bugzilla-3.2")
        os.system("perl -T contrib/sendbugmail.pl %s admins@pardus.org.tr" % bug_id)

if __name__ == "__main__":
    SVNLOOK='/usr/bin/svnlook'

    try:
    	repo = sys.argv[1]
    	commit_no = sys.argv[2]
        cmd = '%s log -r %s %s' % (SVNLOOK, commit_no, repo)
        log = os.popen(cmd, 'r').readlines()

        cmd = '%s author -r %s %s' % (SVNLOOK, commit_no, repo)
        author = os.popen(cmd, 'r').readline().rstrip('\n')

	cmd = '%s changed -r %s %s' % (SVNLOOK, commit_no, repo)
	changed = os.popen(cmd, 'r').readlines()

        main(author, log, commit_no, changed, repo)

    except Exception, e:
    	open("/tmp/svn-bugs.err", "w").write("error\n%s" % e)

