#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Gives a weekly bug change analysis
# The informatins are below:
# name of the person, total bug number, old bug number, longest comment bug id, comment number, newly bugs number added since last week, resolved bugs number since last week 
#
# Copyright 2009, Semen Cirit <scirit@pardus.org.tr>
#

import MySQLdb
from operator import itemgetter


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

N_allBugs = c.execute("SELECT * FROM `bugs`")
print "%s bugs found in total" % N_allBugs

N_allNotResolvedBugs = c.execute("SELECT * FROM `bugs` where bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED'")
print "%s bugs new, assigned or reopened." % N_allNotResolvedBugs

N_pardusMailedBugs = c.execute("SELECT userid FROM `profiles` where login_name like '%@pardus.org.tr'")

print "%s user login with pardus mail." % N_pardusMailedBugs

bugs = {}

bugFile = open("public_html/bugFiles/bugsAnalyze","w")
for userid in c.fetchall():

    #print userid
    N_bug = c.execute("SELECT * FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED')" % userid[0])
    login = c.execute("SELECT login_name FROM `profiles` where userid = %s" % userid[0])
    #print userid[0]

    loginName = c.fetchone()[0]

    if N_bug != 0:
        # total bugs of the person
        #print "%s has %s bugs new, assigned or reopened." % (loginName.split("@")[0], N_bug)

        # oldest bug of the person
        N_bug_id = c.execute("SELECT bug_id FROM `bugs` where assigned_to = %s and (bug_status = 'NEW' or bug_status = 'ASSIGNED' or bug_status = 'REOPENED') order by bug_id" % userid[0])

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

        # how many bugs the person fix since last week
        # bugs_activity.fieldid = 8 means bug_status was changed.
        fixedBug_N = c.execute("select bugs.bug_id from bugs, bugs_activity where bugs.bug_id = bugs_activity.bug_id and bugs_activity.fieldid = 8 and bugs.bug_status = 'RESOLVED' and bugs_activity.who = %s and bugs.delta_ts = bugs_activity.bug_when and bugs.delta_ts >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK)" %(userid[0]))

        #for fixedBug in c.fetchall():
        #        print fixedBug[0]

        # name, total bug number, old bug number, longest comment bug id, comment long, newly bugs added since last week, resolved bug number since last week
        print "%s & %s & %s &  %s & %s & %s & %s \\\ " % (loginName.split("@")[0], N_bug, oldBug, comment[0][0], comment[0][1], N_bug_last_week, fixedBug_N)

