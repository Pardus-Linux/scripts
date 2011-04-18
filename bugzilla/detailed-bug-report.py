#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Analyzes new, assigned or reopened bugs of 
# developers with pardus mailed address.
#
# Copyright 2009, Semen Cirit <scirit@pardus.org.tr>
#

import MySQLdb
from operator import itemgetter
import os

## Configs
## Configs
db_server = ""
db_user   = ""
db_pass   = ""
db_name   = ""

bugzilla_user_id = 1
##

db = MySQLdb.connect(db_server, db_user, db_pass, db_name)

# filter bugs
c = db.cursor()

print "Weekly Bug Report"
print "~~~~~~~~~~~~~~~~~"

N_allBugs = c.execute("SELECT * FROM `bugs`")
#print "%s bugs found in total\n" % N_allBugs

N_allNotResolvedBugs = c.execute("SELECT * FROM `bugs` where bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED'")
#print "%s bugs new, assigned or reopened.\n" % N_allNotResolvedBugs

N_allReslovedBugs = c.execute("select bugs.bug_id from bugs, bugs_activity where bugs.bug_id = bugs_activity.bug_id and bugs_activity.fieldid = 8 and bugs.bug_status = 'RESOLVED' and bugs_activity.bug_when >= DATE_SUB(CURDATE(), INTERVAL 7 month)")
#print "%s bugs resolved.\n" % N_allReslovedBugs

if not os.path.exists("accounts"):
    os.system("wget http://svn.pardus.org.tr/uludag/trunk/common/accounts")

devFile = open("accounts", "r")

for line in devFile.readlines():
    if "#" not in line.strip() and ":" in line.strip():
        devName = line.split(":")[1]
        #print devName

        #N_pardusMailedBugs = c.execute("SELECT userid FROM `profiles` where login_name like '%@pardus.org.tr'")
        N_DevBugs = c.execute("SELECT userid FROM `profiles` where realname like '%s'" % ("%"+devName+"%"))


        #print "%s user are Pardus Developper." % N_pardusMailedBugs

        bugs = {}

        bugFile = open("public_html/bugFiles/bugsAnalyze","w")
        for userid in c.fetchall():

            #print userid
            N_bug = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED')" % userid[0])
            login = c.execute("SELECT login_name FROM `profiles` where userid = %s" % userid[0])
            #print userid[0]

            loginName = c.fetchone()[0]
            #print loginName

            if N_bug != 0:
                # total bugs of the person
                #print "%s has %s bugs new, assigned or reopened." % (loginName.split("@")[0], N_bug)

                # oldest bug of the person
                N_bug_id = c.execute("SELECT bug_id FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED') order by creation_ts" % userid[0])

                oldBug = c.fetchone()[0]
                #print "%s is the oldest bug" % oldBug

                N_bug_id = c.execute("SELECT bug_id FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED')" % userid[0])

                comment = {}
                # long commented bug of the person
                for bugid in c.fetchall():
                    #print bugid[0]
                    N_comment = c.execute("SELECT comment_id FROM `longdescs` WHERE bug_id = %s" % bugid[0])
                    #print N_comment
                    comment[bugid[0]] = int(N_comment)


                # sort the bug_id is according to its comment number.
                comment = sorted(comment.items(), key=itemgetter(1), reverse = True)
                #print "%s is the most longest commented bug with %s comments" % (comment[0][0], comment[0][1])


                # newly created bug for the person
                N_bug_last_week = c.execute("SELECT bug_id FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED') and creation_ts >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK)" % userid[0])

                #print "%s bug added since last week." % N_bug_last_week

                openedBugs = []
                for openedbug in c.fetchall():
                    openedBugs.append(openedbug[0])

                # how many bugs the person fix since last week
                # bugs_activity.fieldid = 8 means bug_status was changed.

                query = """
                (
                SELECT bugs.bug_id
                FROM bugs, bugs_activity
                WHERE bugs.bug_id = bugs_activity.bug_id
                AND (
                bugs_activity.fieldid =8
                OR bugs_activity.fieldid =11
                )
                AND bugs.bug_status = 'RESOLVED'
                AND bugs_activity.who = $$userid$$
                AND bugs.delta_ts = bugs_activity.bug_when
                AND bugs_activity.bug_when >= DATE_SUB( CURDATE( ) , INTERVAL 1 WEEK )
                )
                UNION (

                SELECT bugs.bug_id
                FROM longdescs, bugs_activity, bugs
                WHERE longdescs.bug_id = bugs_activity.bug_id
                AND bugs.bug_id = bugs_activity.bug_id
                AND (
                bugs_activity.fieldid =8
                OR bugs_activity.fieldid =11
                )
                AND bugs.bug_status = 'RESOLVED'
                AND longdescs.who =6726
                AND longdescs.thetext LIKE '%$$devname$$%'
                AND bugs.delta_ts = bugs_activity.bug_when
                AND bugs_activity.bug_when >= DATE_SUB( CURDATE( ) , INTERVAL 1 WEEK )
                )
                LIMIT 0 , 30 """

                query = query.replace("$$userid$$", str(userid[0]))
                query = query.replace("$$devname$$", devName)

                fixedBug_N = c.execute(query)


                # name, total bug number, old bug number, longest comment bug id, comment long, newly bugs added since last week, fixed bug number
                print "%s" % devName
                print "============================================\n"
                print "New, Opened, Reopened Bug Number:"
                print "%s\n" % N_bug
                print "Oldest Bug Id:\n"
                print "http://bugs.pardus.org.tr/show_bug.cgi?id=%s\n" % oldBug
                print "Bug id that has longest comment:\n"
                print "http://bugs.pardus.org.tr/show_bug.cgi?id=%s\n" % comment[0][0]
                print "Comment Number of this bug comment: %s\n" % comment[0][1]
                print "Bugs reported since last week:"
                print "%s\n" % N_bug_last_week
                print "Resolved bug numbers since last week:"
                print "%s\n" % fixedBug_N

                print "Resolved Bug Links since Last Week:"
                print "-----------------------------------\n"
                for fixedBug in c.fetchall():
                    print "#. http://bugs.pardus.org.tr/show_bug.cgi?id=%s" % fixedBug[0]

                print "\n"
                print "New Bug Report Links since Last Week:"
                print "-------------------------------------"

                for bug in openedBugs:
                    print "#. http://bugs.pardus.org.tr/show_bug.cgi?id=%s" % bug
                print "\n"
